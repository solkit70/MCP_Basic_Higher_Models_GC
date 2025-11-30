"""
File Server Test Client (Simple Version)

Tests file_server.py independently using the official MCP Python SDK.

Created: 2025-11-30
"""

import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_file_server():
    """Test all File Server functionality"""

    print("=" * 60)
    print("File Server Test Started")
    print("=" * 60)

    # Server script path
    server_script = Path(__file__).parent / "file_server.py"
    test_samples_dir = Path(__file__).parent / "test_samples"

    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env=None
    )

    results = {}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Step 1: Initialize
            print("\n[Step 1] Initializing server...")
            await session.initialize()
            server_info = session.server_info
            print(f"  OK Server name: {server_info.name}")
            print(f"  OK Server version: {server_info.version}")
            results["initialize"] = {
                "status": "success",
                "server_name": server_info.name,
                "server_version": server_info.version
            }

            # Step 2: List tools
            print("\n[Step 2] Listing tools...")
            tools_result = await session.list_tools()
            print(f"  OK Available tools: {len(tools_result.tools)}")
            for tool in tools_result.tools:
                print(f"    - {tool.name}: {tool.description}")
            results["list_tools"] = {
                "status": "success",
                "tools": [
                    {"name": t.name, "description": t.description}
                    for t in tools_result.tools
                ]
            }

            # Step 3: read_file test - sample1.txt
            print("\n[Step 3] Testing read_file (sample1.txt)...")
            sample1_path = str(test_samples_dir / "sample1.txt")
            result = await session.call_tool("read_file", arguments={"path": sample1_path})
            content = result.content[0].text
            print(f"  OK File read successful")
            print(f"  OK Content length: {len(content)} bytes")
            print(f"  OK First line: {content.split(chr(10))[0][:50]}...")
            results["read_file_sample1"] = {
                "status": "success",
                "path": sample1_path,
                "content_length": len(content),
                "first_line": content.split('\n')[0]
            }

            # Step 4: read_file test - sample2.txt
            print("\n[Step 4] Testing read_file (sample2.txt)...")
            sample2_path = str(test_samples_dir / "sample2.txt")
            result = await session.call_tool("read_file", arguments={"path": sample2_path})
            content = result.content[0].text
            print(f"  OK File read successful")
            print(f"  OK Content length: {len(content)} bytes")
            results["read_file_sample2"] = {
                "status": "success",
                "path": sample2_path,
                "content_length": len(content)
            }

            # Step 5: list_files test - test_samples directory
            print("\n[Step 5] Testing list_files (test_samples/)...")
            result = await session.call_tool(
                "list_files",
                arguments={"directory": str(test_samples_dir)}
            )
            files_json = result.content[0].text
            files_list = json.loads(files_json)
            print(f"  OK Files listed successfully")
            print(f"  OK File/folder count: {len(files_list)}")
            for file_info in files_list:
                file_type = "[DIR]" if file_info["type"] == "directory" else "[FILE]"
                print(f"    {file_type} {file_info['name']} ({file_info['size']} bytes)")
            results["list_files"] = {
                "status": "success",
                "directory": str(test_samples_dir),
                "count": len(files_list),
                "files": files_list
            }

            # Step 6: list_files test - pattern filter (*.txt)
            print("\n[Step 6] Testing list_files (pattern: *.txt)...")
            result = await session.call_tool(
                "list_files",
                arguments={
                    "directory": str(test_samples_dir),
                    "pattern": "*.txt"
                }
            )
            files_json = result.content[0].text
            txt_files = json.loads(files_json)
            print(f"  OK .txt files found: {len(txt_files)}")
            for file_info in txt_files:
                print(f"    [FILE] {file_info['name']}")
            results["list_files_pattern"] = {
                "status": "success",
                "pattern": "*.txt",
                "count": len(txt_files),
                "files": txt_files
            }

            # Step 7: Error case test - nonexistent file
            print("\n[Step 7] Testing error case (nonexistent file)...")
            try:
                await session.call_tool(
                    "read_file",
                    arguments={"path": "nonexistent_file.txt"}
                )
                print("  ERROR: No error occurred (unexpected)")
                results["error_test"] = {"status": "unexpected"}
            except Exception as e:
                print(f"  OK Expected error occurred: {str(e)[:60]}...")
                results["error_test"] = {
                    "status": "success",
                    "error_message": str(e)[:100]
                }

    print("\n" + "=" * 60)
    print("Test Completed!")
    print("=" * 60)

    # Save results to JSON
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {results_file}")

    return results


if __name__ == "__main__":
    asyncio.run(test_file_server())
