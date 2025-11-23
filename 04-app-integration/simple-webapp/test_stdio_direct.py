"""
Direct test of stdio adapter with echo.py server
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.mcp_client import McpClient, McpClientConfig

def main():
    print("=" * 80)
    print("Testing StdioAdapter with echo.py")
    print("=" * 80)

    # Configure for stdio mode
    venv_python = Path(__file__).parent.parent.parent / ".venv" / "Scripts" / "python.exe"
    echo_py = Path(__file__).parent.parent.parent / "03-discover-servers" / "servers" / "echo.py"

    config = McpClientConfig(
        mode="stdio",
        exec_path=f"{venv_python} {echo_py}",
        timeout_default=10
    )

    try:
        print("\n[1] Creating MCP client...")
        client = McpClient(config)
        print("[SUCCESS] Client created and server initialized")

        print("\n[2] Getting health status...")
        health = client.health()
        print(f"[SUCCESS] Health: {health}")

        print("\n[3] Listing tools...")
        tools = client.list_tools()
        print(f"[SUCCESS] Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        print("\n[4] Calling echo_tool...")
        result, latency = client.call_tool("echo_tool", {"text": "Hello from StdioAdapter!"})
        print(f"[SUCCESS] Result (latency: {latency}ms):")
        print(f"  {result}")

        print("\n[5] Calling echo_tool with empty text...")
        result2, latency2 = client.call_tool("echo_tool", {"text": ""})
        print(f"[SUCCESS] Result (latency: {latency2}ms):")
        print(f"  {result2}")

        print("\n" + "=" * 80)
        print("All tests passed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
