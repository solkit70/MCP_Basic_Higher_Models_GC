"""
File Server - MCP 서버 구현 예제

이 서버는 파일 시스템 작업을 위한 두 가지 도구를 제공합니다:
1. read_file: 파일 내용 읽기
2. list_files: 디렉토리 내 파일 목록 조회

작성일: 2025-11-30
작성자: Claude Code (Anthropic)
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from mcp.server.fastmcp import FastMCP

# MCP 서버 인스턴스 생성
mcp = FastMCP("File Operations Server")


@mcp.tool()
def read_file(path: str) -> str:
    """
    파일 내용을 읽어서 반환합니다.

    Args:
        path: 읽을 파일의 경로 (절대 경로 또는 상대 경로)

    Returns:
        파일의 텍스트 내용

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        IsADirectoryError: 경로가 디렉토리일 때
        PermissionError: 파일 접근 권한이 없을 때
        UnicodeDecodeError: 텍스트 파일이 아닐 때
    """
    file_path = Path(path)

    # 파일 존재 확인
    if not file_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    # 디렉토리 체크
    if file_path.is_dir():
        raise IsADirectoryError(f"디렉토리입니다. 파일 경로를 지정하세요: {path}")

    # 파일 읽기 시도
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except PermissionError:
        raise PermissionError(f"파일 접근 권한이 없습니다: {path}")
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            'utf-8', b'', 0, 1,
            f"텍스트 파일이 아닙니다. 바이너리 파일은 읽을 수 없습니다: {path}"
        )


@mcp.tool()
def list_files(directory: str, pattern: str = "*") -> str:
    """
    디렉토리 내의 파일과 폴더 목록을 조회합니다.

    Args:
        directory: 조회할 디렉토리 경로
        pattern: 파일 패턴 (예: "*.txt", "*.py"), 기본값은 "*" (모든 파일)

    Returns:
        JSON 형식의 파일 목록 문자열
        각 항목은 {"name": "파일명", "type": "file"|"directory", "size": 바이트수} 형태

    Raises:
        FileNotFoundError: 디렉토리가 존재하지 않을 때
        NotADirectoryError: 경로가 디렉토리가 아닐 때
        PermissionError: 디렉토리 접근 권한이 없을 때
    """
    dir_path = Path(directory)

    # 디렉토리 존재 확인
    if not dir_path.exists():
        raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {directory}")

    # 디렉토리 타입 체크
    if not dir_path.is_dir():
        raise NotADirectoryError(f"디렉토리가 아닙니다: {directory}")

    # 파일 목록 수집
    try:
        files_info = []

        # glob 패턴으로 파일 검색
        for item in dir_path.glob(pattern):
            try:
                info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                }
                files_info.append(info)
            except (PermissionError, OSError):
                # 개별 파일 접근 실패는 건너뜀
                continue

        # JSON 문자열로 변환 (보기 좋게 포맷팅)
        return json.dumps(files_info, ensure_ascii=False, indent=2)

    except PermissionError:
        raise PermissionError(f"디렉토리 접근 권한이 없습니다: {directory}")


# 서버 실행 (stdio transport)
if __name__ == "__main__":
    # Note: stdio mode에서는 stdout이 JSON-RPC 통신에 사용되므로 print 사용 금지
    mcp.run(transport="stdio")
