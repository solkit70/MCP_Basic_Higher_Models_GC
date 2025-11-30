"""
MCP client wrapper (prep for M5): transport-agnostic facade with a safe mock mode.

Goals
- Provide a small, testable API for listing tools and invoking a tool action.
- Support future stdio/ws transports via adapters, but default to a local mock
  so endpoints and tests work without external servers.

Config via env (optional)
- MCP_MODE: mock | stdio | ws  (default: mock)
- MCP_EXEC_PATH: path to executable (for stdio)
- MCP_SERVER_URI: ws:// or wss:// (for ws)
- MCP_TIMEOUT_DEFAULT: seconds (int, default 10)
- MCP_RETRY_MAX: int (default 3)  — future use

Error model
- Raise McpClientError with code/message; router will convert to HTTP error JSON.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


class McpClientError(Exception):
    def __init__(self, code: str, message: str, detail: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail or {}


@dataclass
class McpClientConfig:
    mode: str = "mock"  # mock | stdio | ws
    exec_path: Optional[str] = None
    server_uri: Optional[str] = None
    timeout_default: int = 10
    retry_max: int = 3

    @classmethod
    def from_env(cls) -> "McpClientConfig":
        return cls(
            mode=os.getenv("MCP_MODE", "mock").lower(),
            exec_path=os.getenv("MCP_EXEC_PATH"),
            server_uri=os.getenv("MCP_SERVER_URI"),
            timeout_default=int(os.getenv("MCP_TIMEOUT_DEFAULT", "10")),
            retry_max=int(os.getenv("MCP_RETRY_MAX", "3")),
        )


class McpClient:
    def __init__(self, config: Optional[McpClientConfig] = None) -> None:
        self.config = config or McpClientConfig.from_env()

        # Select adapter
        mode = self.config.mode
        if mode == "mock":
            self._adapter = _MockAdapter()
        elif mode == "stdio":
            if not self.config.exec_path:
                raise McpClientError("config_error", "MCP_EXEC_PATH required for stdio mode")
            self._adapter = _StdioAdapter(self.config.exec_path, self.config.timeout_default)
        elif mode == "ws":
            self._adapter = _NotImplementedAdapter("ws")
        else:
            raise McpClientError("config_error", f"Unsupported MCP_MODE: {mode}")

    # public API
    def list_tools(self) -> List[Dict[str, Any]]:
        return self._adapter.list_tools()

    def health(self) -> Dict[str, Any]:
        return self._adapter.health()

    def call_tool(self, name: str, params: Dict[str, Any], timeout: Optional[int] = None) -> Tuple[Dict[str, Any], int]:
        """Call a tool and return (data, latency_ms).

        timeout: seconds override; adapter should honor when applicable.
        """
        start = time.perf_counter()
        data = self._adapter.call_tool(name, params, timeout=timeout or self.config.timeout_default)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return data, latency_ms


class _MockAdapter:
    """Local adapter for development and tests.

    Tools:
    - echo: returns { echo: params }
    - sum: expects { numbers: [number, ...] } returns { sum: float }
    """

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {"name": "echo", "description": "Echo back the provided parameters"},
            {"name": "sum", "description": "Sum a list of numbers: {numbers: [..]}"},
        ]

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "server_type": "mock"}

    def call_tool(self, name: str, params: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        if name == "echo":
            return {"echo": params}
        if name == "sum":
            numbers = params.get("numbers")
            if not isinstance(numbers, list):
                raise McpClientError("validation_error", "'numbers' must be a list of numbers")
            try:
                total = sum(float(x) for x in numbers)
            except Exception as e:  # noqa: BLE001
                raise McpClientError("validation_error", f"Invalid numbers: {e}")
            return {"sum": total}
        raise McpClientError("tool_not_found", f"Unknown tool: {name}")


class _NotImplementedAdapter:
    def __init__(self, kind: str) -> None:
        self.kind = kind

    def list_tools(self) -> List[Dict[str, Any]]:
        raise McpClientError("not_implemented", f"{self.kind} adapter not implemented yet")

    def health(self) -> Dict[str, Any]:
        raise McpClientError("not_implemented", f"{self.kind} adapter not implemented yet")

    def call_tool(self, name: str, params: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        raise McpClientError("not_implemented", f"{self.kind} adapter not implemented yet")


class _StdioAdapter:
    """Adapter for MCP servers over stdio transport.

    Manages a subprocess running an MCP server and communicates via stdin/stdout
    using JSON-RPC 2.0 protocol.
    """

    def __init__(self, exec_path: str, timeout: int = 10) -> None:
        self.exec_path = exec_path
        self.timeout = timeout
        self._request_id = 0
        self._proc = None
        self._server_info = None
        self._lock = threading.Lock()

        # Start server and initialize
        self._start_server()
        self._initialize()

    def _start_server(self) -> None:
        """Start MCP server as subprocess."""
        try:
            # Parse exec_path (e.g., "python echo.py" or "C:\\path\\server.exe")
            cmd_parts = self.exec_path.split()

            self._proc = subprocess.Popen(
                cmd_parts,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # Explicitly use UTF-8 for MCP JSON-RPC communication
                bufsize=1  # Line buffered
            )
        except FileNotFoundError as e:
            raise McpClientError("connection_error", f"Server executable not found: {self.exec_path}", {"detail": str(e)})
        except Exception as e:
            raise McpClientError("connection_error", f"Failed to start server: {e}", {"detail": str(e)})

    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send JSON-RPC request and wait for response."""
        if not self._proc or self._proc.poll() is not None:
            raise McpClientError("connection_closed", "Server process is not running")

        with self._lock:
            self._request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params or {}
            }

            try:
                # Send request
                request_line = json.dumps(request) + "\n"
                self._proc.stdin.write(request_line)
                self._proc.stdin.flush()

                # Read response with timeout
                response_line = self._read_line_with_timeout(self.timeout)
                response = json.loads(response_line)

                # Check for JSON-RPC error
                if "error" in response:
                    error = response["error"]
                    raise McpClientError(
                        str(error.get("code", "rpc_error")),
                        error.get("message", "Unknown RPC error"),
                        {"detail": error.get("data")}
                    )

                return response.get("result", {})

            except json.JSONDecodeError as e:
                raise McpClientError("protocol_error", f"Invalid JSON response: {e}")
            except McpClientError:
                raise
            except Exception as e:
                raise McpClientError("communication_error", f"Communication failed: {e}")

    def _read_line_with_timeout(self, timeout: int) -> str:
        """Read one line from stdout with timeout."""
        result = {"line": None, "error": None}

        def read_line():
            try:
                line = self._proc.stdout.readline()
                if not line:
                    result["error"] = "EOF: Server closed connection"
                else:
                    result["line"] = line
            except Exception as e:
                result["error"] = str(e)

        thread = threading.Thread(target=read_line, daemon=True)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise McpClientError("timeout", f"Server did not respond within {timeout} seconds")

        if result["error"]:
            raise McpClientError("connection_error", result["error"])

        if result["line"] is None:
            raise McpClientError("connection_closed", "No response from server")

        return result["line"]

    def _initialize(self) -> None:
        """Initialize MCP session."""
        try:
            result = self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "fastapi-mcp-client",
                    "version": "0.1.0"
                }
            })
            self._server_info = result
        except Exception as e:
            # Cleanup on init failure
            if self._proc:
                self._proc.terminate()
            raise McpClientError("initialization_error", f"Failed to initialize MCP session: {e}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server."""
        result = self._send_request("tools/list")
        tools = result.get("tools", [])

        # Convert MCP tool schema to simplified format
        return [
            {
                "name": tool.get("name"),
                "description": tool.get("description", "")
            }
            for tool in tools
        ]

    def call_tool(self, name: str, params: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        result = self._send_request("tools/call", {
            "name": name,
            "arguments": params
        })

        # Extract text content from MCP response
        # MCP returns: { "content": [{ "type": "text", "text": "..." }, ...] }
        if "content" in result:
            for item in result["content"]:
                if isinstance(item, dict) and item.get("type") == "text":
                    return {"text": item["text"]}

        # Fallback: return raw result
        return result

    def health(self) -> Dict[str, Any]:
        """Get server health status."""
        if not self._proc or self._proc.poll() is not None:
            return {
                "status": "error",
                "server_type": "stdio",
                "message": "Server process not running"
            }

        return {
            "status": "ok",
            "server_type": "stdio",
            "server_info": self._server_info
        }

    def __del__(self):
        """Cleanup: terminate server process."""
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=2)
            except Exception:
                pass  # Best effort cleanup
