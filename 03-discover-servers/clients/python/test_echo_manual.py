"""
Manual test script to observe MCP protocol frames from echo.py server

This script will:
1. Start the echo.py server as a subprocess
2. Send initialize, list_tools, and call_tool requests
3. Capture and display all JSON-RPC frames for learning purposes
"""
import json
import subprocess
import sys
from pathlib import Path

def send_request(proc, request):
    """Send a JSON-RPC request and read response"""
    request_json = json.dumps(request)
    print(f"\n[SEND] Request:")
    print(json.dumps(request, indent=2))

    # Write request with newline
    proc.stdin.write(request_json + "\n")
    proc.stdin.flush()

    # Read response
    response_line = proc.stdout.readline()
    if response_line:
        response = json.loads(response_line)
        print(f"\n[RECV] Response:")
        print(json.dumps(response, indent=2))
        return response
    return None

def main():
    # Path to echo.py
    echo_py = Path(__file__).parent.parent.parent / "servers" / "echo.py"
    if not echo_py.exists():
        print(f"[ERROR] echo.py not found at {echo_py}")
        return

    print("=" * 80)
    print("Starting echo.py MCP Server (stdio mode)")
    print("=" * 80)

    # Start echo server
    proc = subprocess.Popen(
        [sys.executable, str(echo_py)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # 1. Initialize
        print("\n" + "=" * 80)
        print("Step 1: INITIALIZE")
        print("=" * 80)
        init_response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "manual-test-client",
                    "version": "1.0"
                }
            }
        })

        # 2. List tools
        print("\n" + "=" * 80)
        print("Step 2: LIST TOOLS")
        print("=" * 80)
        tools_response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })

        # 3. Call echo tool (success case)
        print("\n" + "=" * 80)
        print("Step 3: CALL TOOL - echo_tool (Success)")
        print("=" * 80)
        echo_response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "echo_tool",
                "arguments": {
                    "text": "Hello MCP! 안녕하세요!"
                }
            }
        })

        # 4. Call echo tool (error case - missing parameter)
        print("\n" + "=" * 80)
        print("Step 4: CALL TOOL - echo_tool (Error - missing param)")
        print("=" * 80)
        error_response = send_request(proc, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "echo_tool",
                "arguments": {}
            }
        })

        print("\n" + "=" * 80)
        print("[SUCCESS] All tests completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        proc.terminate()
        proc.wait(timeout=2)
        print("\n[STOP] Server stopped")

if __name__ == "__main__":
    main()
