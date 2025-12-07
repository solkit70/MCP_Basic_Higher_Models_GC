"""
Example 1: Simple File Query

This example demonstrates basic usage of the MCP Web Application API
to read file contents.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def main():
    print("=" * 60)
    print("Example 1: Simple File Query")
    print("=" * 60)
    print()

    # Step 1: Check server health
    print("[1] Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/mcp/health")
        response.raise_for_status()
        health = response.json()
        print(f"    Status: {health['status']}")
        print(f"    Server Type: {health['server_type']}")
        print()
    except Exception as e:
        print(f"    ERROR: {e}")
        print("    Make sure the server is running!")
        return

    # Step 2: List available tools
    print("[2] Listing available tools...")
    try:
        response = requests.get(f"{BASE_URL}/mcp/tools")
        response.raise_for_status()
        tools_data = response.json()
        tools = tools_data['tools']
        print(f"    Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool['name']}")
        print()
    except Exception as e:
        print(f"    ERROR: {e}")
        return

    # Step 3: Read a file
    print("[3] Reading file contents...")
    file_path = "/app/test_samples/sample1.txt"

    try:
        response = requests.post(
            f"{BASE_URL}/mcp/actions/read_file",
            json={
                "params": {
                    "path": file_path
                }
            }
        )
        response.raise_for_status()
        result = response.json()

        # Extract content
        content = result['data']['text']
        latency = result['latency_ms']

        print(f"    File: {file_path}")
        print(f"    Size: {len(content)} bytes")
        print(f"    Latency: {latency} ms")
        print()
        print("    Content preview (first 100 chars):")
        print(f"    {content[:100]}...")
        print()

    except requests.HTTPError as e:
        print(f"    HTTP ERROR: {e}")
        print(f"    Response: {e.response.text}")
    except Exception as e:
        print(f"    ERROR: {e}")

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
