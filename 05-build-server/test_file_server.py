"""
File Server 테스트 클라이언트

file_server.py를 독립적으로 테스트하기 위한 클라이언트입니다.
공식 MCP Python SDK를 사용하여 서버와 통신합니다.

작성일: 2025-11-30
"""

import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_file_server():
    """File Server의 모든 기능을 테스트합니다."""

    print("=" * 60)
    print("File Server 테스트 시작")
    print("=" * 60)

    # 서버 실행 경로 설정
    server_script = Path(__file__).parent / "file_server.py"
    test_samples_dir = Path(__file__).parent / "test_samples"

    # 서버 파라미터 설정
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env=None
    )

    results = {}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Step 1: 초기화 (initialize)
            print("\n[Step 1] 서버 초기화 중...")
            await session.initialize()
            server_info = session.server_info
            print(f"  ✓ 서버 이름: {server_info.name}")
            print(f"  ✓ 서버 버전: {server_info.version}")
            results["initialize"] = {
                "status": "success",
                "server_name": server_info.name,
                "server_version": server_info.version
            }

            # Step 2: 도구 목록 조회 (list_tools)
            print("\n[Step 2] 도구 목록 조회 중...")
            tools_result = await session.list_tools()
            print(f"  ✓ 사용 가능한 도구 수: {len(tools_result.tools)}")
            for tool in tools_result.tools:
                print(f"    - {tool.name}: {tool.description}")
            results["list_tools"] = {
                "status": "success",
                "tools": [
                    {"name": t.name, "description": t.description}
                    for t in tools_result.tools
                ]
            }

            # Step 3: read_file 테스트 - sample1.txt 읽기
            print("\n[Step 3] read_file 도구 테스트 (sample1.txt)...")
            sample1_path = str(test_samples_dir / "sample1.txt")
            result = await session.call_tool("read_file", arguments={"path": sample1_path})
            content = result.content[0].text
            print(f"  ✓ 파일 읽기 성공")
            print(f"  ✓ 내용 길이: {len(content)} 바이트")
            print(f"  ✓ 첫 줄: {content.split(chr(10))[0][:50]}...")
            results["read_file_sample1"] = {
                "status": "success",
                "path": sample1_path,
                "content_length": len(content),
                "first_line": content.split('\n')[0]
            }

            # Step 4: read_file 테스트 - sample2.txt 읽기
            print("\n[Step 4] read_file 도구 테스트 (sample2.txt)...")
            sample2_path = str(test_samples_dir / "sample2.txt")
            result = await session.call_tool("read_file", arguments={"path": sample2_path})
            content = result.content[0].text
            print(f"  ✓ 파일 읽기 성공")
            print(f"  ✓ 내용 길이: {len(content)} 바이트")
            results["read_file_sample2"] = {
                "status": "success",
                "path": sample2_path,
                "content_length": len(content)
            }

            # Step 5: list_files 테스트 - test_samples 디렉토리
            print("\n[Step 5] list_files 도구 테스트 (test_samples/)...")
            result = await session.call_tool(
                "list_files",
                arguments={"directory": str(test_samples_dir)}
            )
            files_json = result.content[0].text
            files_list = json.loads(files_json)
            print(f"  ✓ 파일 목록 조회 성공")
            print(f"  ✓ 파일/폴더 수: {len(files_list)}")
            for file_info in files_list:
                file_type = "📁" if file_info["type"] == "directory" else "📄"
                print(f"    {file_type} {file_info['name']} ({file_info['size']} bytes)")
            results["list_files"] = {
                "status": "success",
                "directory": str(test_samples_dir),
                "count": len(files_list),
                "files": files_list
            }

            # Step 6: list_files 테스트 - 패턴 필터 (*.txt)
            print("\n[Step 6] list_files 도구 테스트 (패턴: *.txt)...")
            result = await session.call_tool(
                "list_files",
                arguments={
                    "directory": str(test_samples_dir),
                    "pattern": "*.txt"
                }
            )
            files_json = result.content[0].text
            txt_files = json.loads(files_json)
            print(f"  ✓ .txt 파일 수: {len(txt_files)}")
            for file_info in txt_files:
                print(f"    📄 {file_info['name']}")
            results["list_files_pattern"] = {
                "status": "success",
                "pattern": "*.txt",
                "count": len(txt_files),
                "files": txt_files
            }

            # Step 7: 에러 케이스 테스트 - 존재하지 않는 파일
            print("\n[Step 7] 에러 테스트 (존재하지 않는 파일)...")
            try:
                await session.call_tool(
                    "read_file",
                    arguments={"path": "nonexistent_file.txt"}
                )
                print("  ✗ 에러가 발생하지 않았습니다 (예상하지 못한 결과)")
                results["error_test"] = {"status": "unexpected"}
            except Exception as e:
                print(f"  ✓ 예상된 에러 발생: {str(e)[:60]}...")
                results["error_test"] = {
                    "status": "success",
                    "error_message": str(e)[:100]
                }

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

    # 결과를 JSON 파일로 저장
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n결과가 저장되었습니다: {results_file}")

    return results


if __name__ == "__main__":
    asyncio.run(test_file_server())
