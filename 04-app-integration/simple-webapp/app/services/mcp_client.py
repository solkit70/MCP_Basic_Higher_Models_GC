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

import os
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
            self._adapter = _NotImplementedAdapter("stdio")
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
