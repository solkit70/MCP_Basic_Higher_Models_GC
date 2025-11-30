# File Operations Server - MCP 커스텀 서버

**작성일**: 2025-11-30
**버전**: 1.0.0

## 개요

파일 시스템 작업을 수행하는 MCP 서버입니다. FastMCP SDK를 사용하여 구현되었습니다.

## 제공 도구

### 1. read_file

파일 내용을 읽어서 반환합니다.

**파라미터**:
- `path` (string, 필수): 읽을 파일의 경로

**반환값**: 파일의 텍스트 내용

**에러**:
- `FileNotFoundError`: 파일이 존재하지 않을 때
- `IsADirectoryError`: 경로가 디렉토리일 때
- `PermissionError`: 파일 접근 권한이 없을 때
- `UnicodeDecodeError`: 텍스트 파일이 아닐 때

### 2. list_files

디렉토리 내의 파일과 폴더 목록을 조회합니다.

**파라미터**:
- `directory` (string, 필수): 조회할 디렉토리 경로
- `pattern` (string, 선택): 파일 패턴 (예: "*.txt"), 기본값 "*"

**반환값**: JSON 형식의 파일 목록
```json
[
  {
    "name": "sample1.txt",
    "type": "file",
    "size": 256
  },
  {
    "name": "subfolder",
    "type": "directory",
    "size": 0
  }
]
```

**에러**:
- `FileNotFoundError`: 디렉토리가 존재하지 않을 때
- `NotADirectoryError`: 경로가 디렉토리가 아닐 때
- `PermissionError`: 디렉토리 접근 권한이 없을 때

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install fastmcp
```

### 2. 서버 독립 실행 (테스트용)

```bash
python file_server.py
```

서버가 stdio 모드로 실행되며, stdin/stdout을 통해 MCP 프로토콜 통신을 수행합니다.

### 3. 테스트 클라이언트 실행

```bash
python test_file_server.py
```

**테스트 항목**:
1. 서버 초기화 (initialize)
2. 도구 목록 조회 (list_tools)
3. read_file 테스트 (sample1.txt)
4. read_file 테스트 (sample2.txt)
5. list_files 테스트 (전체 파일)
6. list_files 테스트 (*.txt 패턴)
7. 에러 케이스 테스트

**결과**: `test_results.json` 파일에 저장됩니다.

## 파일 구조

```
05-build-server/
├── file_server.py          # MCP 서버 메인 코드
├── test_file_server.py     # 독립 테스트 클라이언트
├── test_samples/           # 테스트용 샘플 파일
│   ├── sample1.txt
│   ├── sample2.txt
│   └── config.json
├── test_results.json       # 테스트 실행 결과
└── README.md               # 이 파일
```

## FastAPI 앱과 통합

이 서버를 기존 FastAPI 앱과 통합하려면:

1. `.env` 파일 수정:
```bash
MCP_MODE=stdio
MCP_EXEC_PATH=python C:\path\to\05-build-server\file_server.py
```

2. FastAPI 앱 재시작:
```bash
cd 04-app-integration/simple-webapp
uvicorn app.main:app --reload
```

3. HTTP API로 테스트:
```bash
# 도구 목록 조회
GET http://localhost:8000/mcp/tools

# read_file 호출
POST http://localhost:8000/mcp/actions/read_file
{
  "path": "C:/path/to/file.txt"
}

# list_files 호출
POST http://localhost:8000/mcp/actions/list_files
{
  "directory": "C:/path/to/directory",
  "pattern": "*.txt"
}
```

## 보안 고려사항

현재 구현은 학습 목적으로 모든 경로에 접근할 수 있습니다.

프로덕션 환경에서는 다음을 추가해야 합니다:

1. **경로 제한**: 특정 디렉토리로만 접근 허용
```python
ALLOWED_BASE = Path("/allowed/directory")

def is_safe_path(path: str) -> bool:
    resolved = Path(path).resolve()
    return resolved.is_relative_to(ALLOWED_BASE)
```

2. **파일 크기 제한**: 대용량 파일 읽기 방지
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if file_path.stat().st_size > MAX_FILE_SIZE:
    raise ValueError("파일이 너무 큽니다")
```

3. **타임아웃**: 장시간 작업 방지

4. **감사 로깅**: 모든 파일 접근 기록

## 확장 아이디어

1. **파일 쓰기 도구**:
```python
@mcp.tool()
def write_file(path: str, content: str) -> str:
    """파일에 내용을 씁니다"""
    ...
```

2. **파일 삭제 도구**:
```python
@mcp.tool()
def delete_file(path: str) -> str:
    """파일을 삭제합니다"""
    ...
```

3. **파일 검색 도구**:
```python
@mcp.tool()
def search_files(directory: str, keyword: str) -> str:
    """키워드가 포함된 파일을 검색합니다"""
    ...
```

4. **파일 정보 조회**:
```python
@mcp.tool()
def get_file_info(path: str) -> str:
    """파일의 상세 정보를 조회합니다"""
    ...
```

## 트러블슈팅

### 서버가 시작되지 않음

- FastMCP가 설치되어 있는지 확인: `pip list | grep fastmcp`
- Python 버전 확인: Python 3.8 이상 필요

### 파일을 읽을 수 없음

- 파일 경로가 정확한지 확인
- 파일 인코딩이 UTF-8인지 확인
- 파일 접근 권한 확인

### 테스트 클라이언트가 실행되지 않음

- MCP Python SDK 설치 확인: `pip install mcp`
- test_samples 폴더에 샘플 파일이 있는지 확인

## 라이선스

MIT License

## 기여

이슈와 PR은 언제나 환영합니다!

## 참고 자료

- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
