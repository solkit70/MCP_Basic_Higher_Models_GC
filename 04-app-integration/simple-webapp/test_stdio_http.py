"""
Test stdio MCP endpoints via HTTP
"""
import requests
import subprocess
import sys
import time
from pathlib import Path

def main():
    print("=" * 80)
    print("Testing MCP Stdio Endpoints via HTTP")
    print("=" * 80)

    app_root = Path(__file__).parent
    venv_python = app_root.parent.parent / ".venv" / "Scripts" / "python.exe"

    # Start server
    print("\n[1] Starting FastAPI server...")
    proc = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=str(app_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)

    try:
        base_url = "http://localhost:8000"

        # Test /mcp/health
        print("\n[2] Testing GET /mcp/health...")
        r = requests.get(f"{base_url}/mcp/health")
        r.raise_for_status()
        print(f"[SUCCESS] {r.json()}")

        # Test /mcp/tools
        print("\n[3] Testing GET /mcp/tools...")
        r = requests.get(f"{base_url}/mcp/tools")
        r.raise_for_status()
        print(f"[SUCCESS] {r.json()}")

        # Test /mcp/actions/echo_tool
        print("\n[4] Testing POST /mcp/actions/echo_tool...")
        r = requests.post(
            f"{base_url}/mcp/actions/echo_tool",
            json={"text": "Hello from HTTP client!"}
        )
        r.raise_for_status()
        print(f"[SUCCESS] {r.json()}")

        # Test with empty text
        print("\n[5] Testing POST /mcp/actions/echo_tool (empty)...")
        r = requests.post(
            f"{base_url}/mcp/actions/echo_tool",
            json={"text": ""}
        )
        r.raise_for_status()
        print(f"[SUCCESS] {r.json()}")

        print("\n" + "=" * 80)
        print("All HTTP tests passed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print("\n[CLEANUP] Stopping server...")
        proc.terminate()
        proc.wait(timeout=5)

    return 0

if __name__ == "__main__":
    sys.exit(main())
