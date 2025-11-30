"""
Direct File Server Test (Simplified)

간단한 테스트로 file_server.py가 정상 작동하는지 확인합니다.

Created: 2025-11-30
"""

import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_file_server():
    """Test File Server"""

    print("=" * 60)
    print("File Server Direct Test")
    print("=" * 60)

    server_script = Path(__file__).parent / "file_server.py"
    test_samples_dir = Path(__file__).parent / "test_samples"

    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize
            print("\n[1] Initializing...")
            init_result = await session.initialize()
            print(f"  OK Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

            # List tools
            print("\n[2] Listing tools...")
            tools_result = await session.list_tools()
            print(f"  OK Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"    - {tool.name}")

            # Test read_file
            print("\n[3] Testing read_file...")
            sample1 = str(test_samples_dir / "sample1.txt")
            result = await session.call_tool("read_file", arguments={"path": sample1})
            content = result.content[0].text
            print(f"  OK Read {len(content)} bytes")
            print(f"  OK First line: {content.split(chr(10))[0]}")

            # Test list_files
            print("\n[4] Testing list_files...")
            result = await session.call_tool("list_files", arguments={"directory": str(test_samples_dir)})
            files_json = result.content[0].text
            files = json.loads(files_json)
            print(f"  OK Found {len(files)} files/folders")
            for f in files:
                print(f"    - {f['name']} ({f['size']} bytes)")

    print("\n" + "=" * 60)
    print("Test Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_file_server())
