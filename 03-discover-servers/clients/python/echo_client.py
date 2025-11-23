"""
MCP client for testing echo.py server (learning purposes)

This script demonstrates MCP protocol by:
1. Initializing connection to echo.py server
2. Listing available tools
3. Calling echo_tool with test data
4. Capturing all frames for learning
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> int:
    print("="*80)
    print("MCP Echo Client Test")
    print("="*80)

    repo_root = Path(__file__).resolve().parents[3]
    server_path = repo_root / "03-discover-servers" / "servers" / "echo.py"

    if not server_path.exists():
        print(f"[ERROR] Server script not found: {server_path}")
        return 2

    print(f"\n[INFO] Starting echo.py server: {server_path}")

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
        env=dict(os.environ),
    )

    results = {
        "server": "echo.py",
        "tests": []
    }

    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                # Step 1: Initialize
                print("\n" + "="*80)
                print("Step 1: INITIALIZE")
                print("="*80)
                init_result = await session.initialize()
                print(f"[SUCCESS] Initialized")
                print(f"  Server name: {init_result.serverInfo.name}")
                print(f"  Server version: {init_result.serverInfo.version}")
                print(f"  Protocol version: {init_result.protocolVersion}")
                results["tests"].append({
                    "step": "initialize",
                    "status": "success",
                    "server_name": init_result.serverInfo.name,
                    "server_version": init_result.serverInfo.version
                })

                # Step 2: List tools
                print("\n" + "="*80)
                print("Step 2: LIST TOOLS")
                print("="*80)
                tools = await session.list_tools()
                print(f"[SUCCESS] Found {len(tools.tools)} tool(s)")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                results["tests"].append({
                    "step": "list_tools",
                    "status": "success",
                    "tools": [{"name": t.name, "description": t.description} for t in tools.tools]
                })

                # Step 3: Call echo_tool (success case)
                print("\n" + "="*80)
                print("Step 3: CALL echo_tool (Success)")
                print("="*80)
                test_message = "Hello MCP! This is a test from Claude Code."
                print(f"[INFO] Sending message: {test_message}")

                res = await session.call_tool("echo_tool", arguments={"text": test_message})
                print(f"[SUCCESS] Tool executed")
                print(f"  Response content:")
                for content_item in res.content:
                    from mcp import types as _types
                    if isinstance(content_item, _types.TextContent):
                        print(f"    {content_item.text}")
                        results["tests"].append({
                            "step": "call_echo_tool",
                            "status": "success",
                            "input": test_message,
                            "output": content_item.text
                        })

                # Step 4: Test with empty text (edge case)
                print("\n" + "="*80)
                print("Step 4: CALL echo_tool (Empty text)")
                print("="*80)
                empty_message = ""
                print(f"[INFO] Sending empty message")

                res = await session.call_tool("echo_tool", arguments={"text": empty_message})
                print(f"[SUCCESS] Tool executed")
                print(f"  Response content:")
                for content_item in res.content:
                    from mcp import types as _types
                    if isinstance(content_item, _types.TextContent):
                        print(f"    '{content_item.text}'")
                        results["tests"].append({
                            "step": "call_echo_tool_empty",
                            "status": "success",
                            "input": empty_message,
                            "output": content_item.text
                        })

        print("\n" + "="*80)
        print("[SUCCESS] All tests completed!")
        print("="*80)

        # Save results
        output_file = repo_root / "docs" / "echo_client_test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[INFO] Results saved to: {output_file}")

        return 0

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        results["tests"].append({
            "step": "error",
            "status": "failed",
            "error": str(e)
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
