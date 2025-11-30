# stdio transport와 타입 힌트 완벽 가이드

**작성일**: 2025-11-30
**작성자**: Claude Code (Anthropic)
**목적**: MCP 개발의 핵심인 stdio transport와 타입 힌트를 완전히 이해하기

---

## 목차

1. [stdio transport란?](#1-stdio-transport란)
2. [stdio transport의 동작 원리](#2-stdio-transport의-동작-원리)
3. [타입 힌트의 중요성](#3-타입-힌트의-중요성)
4. [실전 적용](#4-실전-적용)

---

## 1. stdio transport란?

### 기본 개념

**stdio = Standard Input/Output (표준 입출력)**

모든 프로그램은 3가지 기본 통로가 있습니다:
- **stdin** (표준 입력): 키보드 입력 받는 통로
- **stdout** (표준 출력): 화면에 출력하는 통로
- **stderr** (에러 출력): 에러 메시지 출력하는 통로

---

### 일반적인 사용 예시

```python
# 일반적으로 우리가 하는 것
name = input("이름을 입력하세요: ")  # stdin으로 입력 받음
print(f"안녕하세요 {name}님!")        # stdout으로 출력
```

터미널에서:
```
이름을 입력하세요: 홍길동
안녕하세요 홍길동님!
```

---

### MCP에서의 stdio transport

MCP는 **이 stdin/stdout을 통신 채널로 사용**합니다!

#### 시각적 설명

```
[FastAPI 앱]                    [file_server.py]
    |                               |
    | subprocess.Popen으로 실행     |
    |------------------------------>|
    |                               |
    | stdin으로 JSON 전송           |
    |==============================>|
    | {"method": "tools/list"}      |
    |                               |
    |                               | 도구 목록 조회
    |                               |
    | stdout으로 JSON 응답          |
    |<==============================|
    | {"result": {"tools": [...]}}  |
    |                               |
```

---

## 2. stdio transport의 동작 원리

### 클라이언트 측 (FastAPI - stdio adapter)

#### 1) 서버 프로세스 시작

```python
# 04-app-integration/simple-webapp/app/services/mcp_client.py
# Lines 133-313

# 서버 프로세스 시작
self._proc = subprocess.Popen(
    ["python", "file_server.py"],
    stdin=subprocess.PIPE,   # stdin 파이프 열기
    stdout=subprocess.PIPE,  # stdout 파이프 열기
    stderr=subprocess.PIPE,  # 에러 로그용
    text=True,               # 문자열 모드
    bufsize=1                # 라인 버퍼링
)
```

**설명**:
- `subprocess.Popen`: 외부 프로그램을 실행하는 Python 함수
- `stdin=subprocess.PIPE`: stdin을 파이프로 연결 (우리가 데이터를 보낼 수 있음)
- `stdout=subprocess.PIPE`: stdout을 파이프로 연결 (서버에서 데이터를 받을 수 있음)
- `text=True`: 바이너리가 아닌 텍스트 모드
- `bufsize=1`: 한 줄씩 버퍼링

#### 2) stdin으로 요청 보내기

```python
# JSON-RPC 요청 생성
request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1,
    "params": {}
}

# JSON을 문자열로 변환하고 개행 추가
request_json = json.dumps(request) + "\n"

# stdin으로 전송
self._proc.stdin.write(request_json)
self._proc.stdin.flush()  # 즉시 전송
```

**중요 포인트**:
- **반드시 `\n` (개행) 추가**: 한 줄당 하나의 JSON 메시지
- **flush() 호출**: 버퍼에 있는 데이터를 즉시 전송

#### 3) stdout에서 응답 읽기

```python
# stdout에서 한 줄 읽기
response_line = self._proc.stdout.readline()

# JSON 파싱
response = json.loads(response_line)

# 결과 추출
result = response["result"]
```

**중요 포인트**:
- `readline()`: 한 줄씩 읽음 (개행까지)
- stdout에서 오는 **모든 것이 JSON이어야 함**

---

### 서버 측 (file_server.py)

```python
from fastmcp import FastMCP

mcp = FastMCP("File Operations Server")

@mcp.tool()
def read_file(path: str) -> str:
    """파일 내용 읽기"""
    with open(path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    # FastMCP가 자동으로 처리:
    # 1. stdin에서 JSON-RPC 요청 읽기
    # 2. JSON 파싱
    # 3. 메서드에 따라 적절한 함수 호출
    # 4. 결과를 JSON-RPC 응답으로 변환
    # 5. stdout으로 응답 전송
    mcp.run(transport="stdio")
```

**FastMCP가 자동으로 하는 일**:

```python
# 내부적으로 이런 일이 벌어짐 (의사 코드)
while True:
    # stdin에서 한 줄 읽기
    line = sys.stdin.readline()
    if not line:
        break

    # JSON 파싱
    request = json.loads(line)

    # 메서드 처리
    if request["method"] == "tools/list":
        tools = [...]  # 등록된 도구 목록
        response = {"result": {"tools": tools}}

    elif request["method"] == "tools/call":
        tool_name = request["params"]["name"]
        args = request["params"]["arguments"]

        # 실제 함수 호출
        result = call_registered_tool(tool_name, args)
        response = {"result": result}

    # stdout으로 응답 전송
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
```

---

### 왜 print()를 사용하면 안 되는가?

#### 문제 상황

```python
# file_server.py (잘못된 예)
if __name__ == "__main__":
    print("서버를 시작합니다...")  # 🚫 이것이 문제!
    print("도구: read_file, list_files")  # 🚫 이것도 문제!
    mcp.run(transport="stdio")
```

#### 무슨 일이 벌어지나?

```
[클라이언트]                    [서버]
    |                             |
    | 서버 시작                   |
    |<----------------------------|
    |  stdout: "서버를 시작합니다..." ⚠️
    |  stdout: "도구: read_file..." ⚠️
    |                             |
    | JSON-RPC 요청 전송         |
    |  {"method": "tools/list"}   |
    |---------------------------->|
    |                             |
    |                             | 응답 생성
    |<----------------------------|
    |  stdout: {"result": {...}}  ✅
    |                             |
    | 첫 번째 줄 읽기:            |
    | "서버를 시작합니다..."      |
    | JSON 파싱 시도              |
    | ❌ 에러! JSON이 아님!       |
```

**문제의 핵심**:
- 클라이언트는 stdout에서 오는 **모든 것을 JSON-RPC 메시지로 기대**
- `print()`는 stdout에 출력됨
- JSON이 아닌 텍스트가 섞이면 파싱 실패

#### 실제 에러 메시지

```
Failed to parse JSONRPC message from server
ValidationError: Invalid JSON: expected value at line 1 column 2
input_value='[File Server] Starting MCP server...\r'
```

---

### 올바른 방법

#### 방법 1: print 사용하지 않기

```python
# file_server.py (올바른 예)
if __name__ == "__main__":
    # print 대신 아무것도 출력하지 않음
    mcp.run(transport="stdio")
```

#### 방법 2: stderr에 로그 출력

```python
import sys

if __name__ == "__main__":
    # stderr는 통신에 사용되지 않으므로 안전
    print("서버 시작", file=sys.stderr)
    mcp.run(transport="stdio")
```

#### 방법 3: 로깅 라이브러리 사용

```python
import logging

# stderr로 로그 출력 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    stream=sys.stderr  # stdout 대신 stderr
)

if __name__ == "__main__":
    logging.info("서버 시작")
    mcp.run(transport="stdio")
```

---

### stdio transport의 특징

| 특징 | 설명 | 비고 |
|------|------|------|
| **장점: 간단함** | 소켓이나 HTTP 서버 불필요 | 설정이 매우 쉬움 |
| **장점: 방화벽 우회** | 네트워크 연결이 아니므로 방화벽 문제 없음 | 로컬 개발에 최적 |
| **장점: 보안** | 같은 머신 내에서만 통신 | 외부 접근 불가 |
| **단점: 로컬 전용** | 네트워크를 통한 원격 연결 불가 | 같은 컴퓨터에서만 |
| **단점: 1:1 연결** | 한 프로세스당 하나의 연결만 | 여러 클라이언트 불가 |
| **사용처** | - CLI 도구<br>- 로컬 MCP 서버<br>- 개발 및 테스트 | VSCode Extension 등 |

---

### 다른 transport와 비교

#### stdio vs WebSocket

```
[stdio transport]
클라이언트 ←stdin/stdout→ 서버 (같은 머신)

[WebSocket transport]
클라이언트 ←ws://→ 서버 (네트워크 가능)
```

| 특징 | stdio | WebSocket |
|------|-------|-----------|
| **네트워크** | ✗ | ✅ |
| **원격 접속** | ✗ | ✅ |
| **여러 클라이언트** | ✗ | ✅ |
| **설정 복잡도** | 낮음 | 높음 |
| **보안 설정** | 불필요 | 필요 (TLS, 인증 등) |

---

## 3. 타입 힌트의 중요성

### 기본 개념

**타입 힌트 = 변수/파라미터/반환값의 타입을 명시**

### 타입 힌트 없는 경우

```python
@mcp.tool()
def read_file(path):
    """파일을 읽습니다"""
    with open(path, 'r') as f:
        return f.read()
```

**문제점**:
- `path`가 문자열인지? 숫자인지? 리스트인지? **모름!**
- 반환값이 무엇인지? **모름!**
- 클라이언트가 어떻게 사용해야 하는지? **모름!**

### 타입 힌트 있는 경우

```python
@mcp.tool()
def read_file(path: str) -> str:
    """파일을 읽습니다"""
    with open(path, 'r') as f:
        return f.read()
```

**명확함**:
- `path`는 문자열 (str) ✅
- 반환값도 문자열 (str) ✅
- 클라이언트가 정확히 알 수 있음 ✅

---

### 타입 힌트가 하는 일

#### 1) 자동 JSON Schema 생성

```python
@mcp.tool()
def read_file(path: str) -> str:
    """파일 내용 읽기"""
    ...
```

↓ FastMCP가 **자동 생성** ↓

```json
{
  "name": "read_file",
  "description": "파일 내용 읽기",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "읽을 파일의 경로"
      }
    },
    "required": ["path"]
  }
}
```

**결과**: 클라이언트가 도구의 사용법을 자동으로 알 수 있음!

---

#### 2) 클라이언트가 도구 정보를 알 수 있음

```python
# 클라이언트 코드
tools = await session.list_tools()

for tool in tools:
    print(f"도구: {tool.name}")
    print(f"설명: {tool.description}")
    print(f"입력 스키마: {tool.inputSchema}")
    # 👆 이 정보가 타입 힌트에서 자동 생성됨!
```

**출력**:
```
도구: read_file
설명: 파일 내용 읽기
입력 스키마: {
  "properties": {
    "path": {"type": "string"}
  },
  "required": ["path"]
}
```

**장점**:
- 문서를 따로 작성할 필요 없음
- 코드와 문서가 자동으로 동기화됨
- 클라이언트가 정확한 사용법을 알 수 있음

---

#### 3) 자동 타입 검증

```python
# 클라이언트가 잘못된 타입으로 호출 시
await session.call_tool("read_file", arguments={"path": 123})
                                                        # 👆 숫자!
```

FastMCP가 **자동으로 에러 반환**:
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params: path must be string, got integer"
  }
}
```

**장점**:
- 타입 오류를 빠르게 발견
- 서버 코드가 실행되기 전에 검증
- 명확한 에러 메시지

---

### 실제 비교 예시

#### 타입 힌트 없음 😰

```python
@mcp.tool()
def list_files(directory, pattern):
    """파일 목록"""
    # pattern이 선택적인지? 필수인지? 모름!
    # 기본값이 뭔지? 모름!
    # directory가 꼭 문자열인지? 모름!
    ...
```

**클라이언트 입장**:
```python
# 어떻게 호출해야 하지? 🤔
await call_tool("list_files", {"directory": "C:/temp"})
# pattern을 안 줘도 되나? 에러나나?

await call_tool("list_files", {"directory": "C:/temp", "pattern": "*"})
# 이게 맞나? pattern의 기본값이 뭔지 모름...
```

#### 타입 힌트 있음 😊

```python
@mcp.tool()
def list_files(directory: str, pattern: str = "*") -> str:
    """파일 목록 조회"""
    ...
```

**자동 생성된 스키마**:
```json
{
  "properties": {
    "directory": {
      "type": "string"
    },
    "pattern": {
      "type": "string",
      "default": "*"
    }
  },
  "required": ["directory"]
}
```

**클라이언트 입장**:
```python
# 명확함! 👍
# directory는 필수 (required)
# pattern은 선택 (기본값 "*")

await call_tool("list_files", {"directory": "C:/temp"})
# ✅ OK! pattern은 자동으로 "*"

await call_tool("list_files", {
    "directory": "C:/temp",
    "pattern": "*.txt"
})
# ✅ OK! pattern을 명시적으로 지정
```

---

### 복잡한 타입 예시

#### 기본 타입

```python
@mcp.tool()
def example_basic(
    text: str,           # 문자열
    number: int,         # 정수
    decimal: float,      # 소수
    flag: bool           # 참/거짓
) -> str:
    """기본 타입 예시"""
    return f"처리 완료"
```

#### 리스트와 딕셔너리

```python
from typing import List, Dict

@mcp.tool()
def example_complex(
    items: List[str],              # 문자열 리스트
    config: Dict[str, int],        # 문자열→정수 딕셔너리
    optional: str = "default"      # 선택적 파라미터
) -> List[Dict[str, str]]:         # 딕셔너리 리스트 반환
    """복잡한 타입 예시"""
    return [{"result": item} for item in items]
```

**생성된 스키마**:
```json
{
  "properties": {
    "items": {
      "type": "array",
      "items": {"type": "string"}
    },
    "config": {
      "type": "object",
      "additionalProperties": {"type": "integer"}
    },
    "optional": {
      "type": "string",
      "default": "default"
    }
  },
  "required": ["items", "config"]
}
```

---

#### Pydantic 모델 (권장!)

```python
from pydantic import BaseModel

class FileInfo(BaseModel):
    """파일 정보"""
    path: str
    encoding: str = "utf-8"
    max_size: int = 1024000

@mcp.tool()
def read_file_advanced(info: FileInfo) -> str:
    """Pydantic 모델 사용 예시"""
    with open(info.path, 'r', encoding=info.encoding) as f:
        content = f.read(info.max_size)
    return content
```

**Pydantic의 장점**:
- ✅ 더 명확한 스키마
- ✅ 자동 검증 강화
- ✅ 기본값 지원
- ✅ 중첩된 구조 표현 가능
- ✅ 문서화 자동 생성

**생성된 스키마**:
```json
{
  "properties": {
    "info": {
      "type": "object",
      "properties": {
        "path": {"type": "string"},
        "encoding": {"type": "string", "default": "utf-8"},
        "max_size": {"type": "integer", "default": 1024000}
      },
      "required": ["path"]
    }
  }
}
```

---

### 타입 힌트의 진짜 가치

#### 시나리오 1: 타입 힌트 없을 때

```python
# 서버
@mcp.tool()
def read_file(path):
    with open(path, 'r') as f:
        return f.read()

# 개발자 A (클라이언트 개발)
await call_tool("read_file", {"path": 123})
# 😰 에러 발생!
# TypeError: expected str, bytes or os.PathLike object, not int
# 왜 안 되지? 문서를 찾아봐야 함...
# 시간 낭비 10분...

# 개발자 B (클라이언트 개발)
await call_tool("read_file", {"file": "test.txt"})
# 😰 에러 발생!
# KeyError: 'path'
# 아, 파라미터 이름이 path였구나...
# 시간 낭비 5분...
```

#### 시나리오 2: 타입 힌트 있을 때

```python
# 서버
@mcp.tool()
def read_file(path: str) -> str:
    """파일 내용 읽기"""
    with open(path, 'r') as f:
        return f.read()

# 개발자 A (클라이언트 개발)
tools = await session.list_tools()
# {"name": "read_file", "inputSchema": {
#   "properties": {"path": {"type": "string"}}
# }}

# 😊 스키마를 보고 정확히 알 수 있음!
await call_tool("read_file", {"path": "test.txt"})
# ✅ 성공! 시간 낭비 0분!

# 만약 실수로 잘못 보내면?
await call_tool("read_file", {"path": 123})
# 즉시 명확한 에러:
# "Invalid params: path must be string, got integer"
# 😊 빠르게 수정 가능!
```

---

## 4. 실전 적용

### file_server.py에서의 적용

```python
@mcp.tool()
def read_file(path: str) -> str:
    """
    파일 내용을 읽어서 반환합니다.

    Args:
        path: 읽을 파일의 경로 (절대 경로 또는 상대 경로)

    Returns:
        파일의 텍스트 내용
    """
    # 구현...
```

**결과**:
- ✅ `path`가 문자열임을 명시
- ✅ 반환값이 문자열임을 명시
- ✅ docstring으로 추가 설명
- ✅ 클라이언트가 정확히 사용 가능

---

### 체크리스트

MCP 도구를 만들 때:

- [ ] `@mcp.tool()` 데코레이터 사용
- [ ] **모든 파라미터에 타입 힌트** (`param: str`)
- [ ] **반환 타입 힌트** (`-> str`)
- [ ] **docstring 작성** (`"""설명"""`)
- [ ] 복잡한 타입은 Pydantic 모델 사용
- [ ] 선택적 파라미터는 기본값 지정
- [ ] **stdio 모드에서 print() 사용 금지**

---

## 5. 핵심 정리

### stdio transport

```
✅ stdin/stdout = 통신 채널
✅ JSON-RPC 메시지를 stdin으로 보내고 stdout에서 받음
✅ print() 사용 금지 (stdout을 오염시킴)
✅ 로컬 프로세스 간 통신에 최적
✅ 간단하고 방화벽 문제 없음
```

### 타입 힌트

```
✅ 함수 파라미터와 반환값의 타입 명시
✅ 자동 JSON Schema 생성
✅ 클라이언트가 도구 사용법을 알 수 있음
✅ 자동 타입 검증
✅ 문서화 자동 완성
✅ 개발 시간 단축 및 버그 감소
```

### 좋은 예 vs 나쁜 예

#### ❌ 나쁜 예

```python
# 서버
if __name__ == "__main__":
    print("서버 시작")  # stdout 오염!
    mcp.run(transport="stdio")

@mcp.tool()
def my_tool(x, y):  # 타입 힌트 없음!
    return x + y
```

#### ✅ 좋은 예

```python
# 서버
if __name__ == "__main__":
    # print 사용 안 함
    mcp.run(transport="stdio")

@mcp.tool()
def my_tool(x: int, y: int) -> int:
    """두 정수를 더합니다"""
    return x + y
```

---

## 6. 참고 자료

- **오늘의 구현**: `05-build-server/file_server.py`
- **stdio adapter**: `04-app-integration/simple-webapp/app/services/mcp_client.py` (lines 133-313)
- **Python typing 문서**: https://docs.python.org/3/library/typing.html
- **Pydantic 문서**: https://docs.pydantic.dev/

---

## 7. 다음 단계

이제 stdio transport와 타입 힌트를 완전히 이해했으니:

1. ✅ stdio transport 동작 원리 이해
2. ✅ 왜 print()를 사용하면 안 되는지 이해
3. ✅ 타입 힌트의 중요성 이해
4. ✅ 자동 스키마 생성 원리 이해
5. 🔜 **Phase 3**: FastAPI 앱과 통합

---

**작성 완료**: 2025-11-30
**다음**: Phase 3 - FastAPI 통합
