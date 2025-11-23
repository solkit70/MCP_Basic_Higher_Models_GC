# MCP 실전 개발 가이드

**작성일**: 2025-11-23
**작성자**: Claude Code (Anthropic)
**목적**: 실제 애플리케이션에서 MCP 서버를 통합하고 프로그래밍하는 방법에 대한 참조 가이드

---

## 📑 목차

1. [핵심 코드 위치](#핵심-코드-위치)
2. [MCP 프로토콜 이해](#mcp-프로토콜-이해)
3. [stdio Transport 구현](#stdio-transport-구현)
4. [FastAPI 통합 패턴](#fastapi-통합-패턴)
5. [에러 처리 전략](#에러-처리-전략)
6. [실전 시나리오](#실전-시나리오)
7. [체크리스트](#체크리스트)

---

## 핵심 코드 위치

### 1. MCP 클라이언트 어댑터 (가장 중요)

**파일**: [app/services/mcp_client.py](../04-app-integration/simple-webapp/app/services/mcp_client.py)

**핵심 섹션**: Lines 133-313 (`_StdioAdapter` 클래스)

이 클래스가 **실제 MCP 서버와 통신하는 핵심 로직**입니다.

```python
class _StdioAdapter:
    """
    MCP 서버와 stdin/stdout으로 통신하는 어댑터
    실제 프로덕션 코드에서 이 패턴을 그대로 사용할 수 있음
    """

    def __init__(self, exec_path: str, timeout: int = 10):
        # 1. 서버 프로세스 시작
        self._start_server()

        # 2. MCP 세션 초기화
        self._initialize()

    def _start_server(self):
        # subprocess.Popen으로 MCP 서버 실행
        cmd_parts = self.exec_path.split()
        self._proc = subprocess.Popen(
            cmd_parts,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def _send_request(self, method: str, params: Optional[Dict] = None):
        # JSON-RPC 2.0 요청 전송
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }
        self._proc.stdin.write(json.dumps(request) + "\n")
        self._proc.stdin.flush()

        # 응답 대기 (타임아웃 적용)
        response_line = self._read_line_with_timeout(self.timeout)
        return json.loads(response_line)

    def _read_line_with_timeout(self, timeout: int):
        # threading으로 타임아웃 구현
        result = {"line": None}
        def read_line():
            result["line"] = self._proc.stdout.readline()

        thread = threading.Thread(target=read_line, daemon=True)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise McpClientError("timeout", f"No response within {timeout}s")

        return result["line"]
```

**왜 중요한가?**
- 이 코드가 **실제 MCP 서버(echo.py, 또는 다른 MCP 서버)와 통신**하는 부분
- subprocess로 외부 프로세스를 관리하는 방법
- JSON-RPC 프로토콜을 구현하는 방법
- 타임아웃을 크로스 플랫폼으로 처리하는 방법
- 모든 것을 한 곳에서 볼 수 있음

---

### 2. FastAPI 라우터 통합

**파일**: [app/routers/mcp.py](../04-app-integration/simple-webapp/app/routers/mcp.py)

**핵심**: HTTP 엔드포인트에서 MCP 클라이언트를 호출하는 패턴

```python
@router.get("/mcp/tools")
async def list_tools():
    """MCP 도구 목록 조회"""
    try:
        tools = mcp_client.list_tools()
        return {"tools": tools}
    except McpClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/actions/{tool_name}")
async def call_tool(tool_name: str, payload: dict):
    """MCP 도구 호출"""
    try:
        result, latency = mcp_client.call_tool(tool_name, payload)
        return {"result": result, "latency_ms": latency}
    except McpClientError as e:
        if e.code == "tool_not_found":
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

**왜 중요한가?**
- 웹 애플리케이션에서 MCP를 어떻게 노출하는지 보여줌
- HTTP → MCP 변환 패턴
- 에러를 HTTP 상태 코드로 매핑하는 방법

---

### 3. 환경 설정

**파일**: [04-app-integration/simple-webapp/.env](../04-app-integration/simple-webapp/.env)

```bash
# MCP 모드 선택 (mock/stdio/ws)
MCP_MODE=stdio

# stdio 모드: MCP 서버 실행 명령어
MCP_EXEC_PATH=C:\path\to\python.exe C:\path\to\echo.py

# 기본 타임아웃 (초)
MCP_TIMEOUT_DEFAULT=10
```

**파일**: [app/main.py](../04-app-integration/simple-webapp/app/main.py)

```python
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
```

**왜 중요한가?**
- 개발/스테이징/프로덕션 환경을 쉽게 전환
- 하드코딩 없이 설정 관리
- 서버 경로를 환경 변수로 관리

---

## MCP 프로토콜 이해

### JSON-RPC 2.0 기반

MCP는 JSON-RPC 2.0 프로토콜을 사용합니다. 모든 메시지는 다음 형식을 따릅니다:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "echo_tool",
    "arguments": {
      "text": "Hello"
    }
  }
}
```

### 3단계 통신 시퀀스

```
1. initialize
   ↓
2. tools/list (도구 목록 조회)
   ↓
3. tools/call (도구 호출)
```

**테스트 결과 예시**: [docs/echo_client_test_results.json](../docs/echo_client_test_results.json)

```json
{
  "step1_initialize": {
    "request": {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "initialize",
      "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
      }
    },
    "response": {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "protocolVersion": "2024-11-05",
        "serverInfo": {"name": "Echo Server", "version": "1.18.0"}
      }
    }
  }
}
```

**핵심 포인트**:
- 한 줄당 하나의 JSON 메시지
- 반드시 `\n`으로 메시지 구분
- `id` 필드로 요청-응답 매칭
- 에러는 `error` 필드에 포함

---

## stdio Transport 구현

### 핵심 개념

stdio transport는 **stdin/stdout을 통한 양방향 통신**입니다.

```
[Your App] ←stdin/stdout→ [MCP Server Process]
```

### 구현 체크리스트

1. **프로세스 시작**
```python
self._proc = subprocess.Popen(
    cmd_parts,
    stdin=subprocess.PIPE,   # 서버로 보낼 파이프
    stdout=subprocess.PIPE,  # 서버에서 받을 파이프
    stderr=subprocess.PIPE,  # 에러 로그용
    text=True,               # 문자열 모드
    bufsize=1                # 라인 버퍼링
)
```

2. **요청 전송**
```python
request_json = json.dumps(request) + "\n"  # 반드시 개행 추가!
self._proc.stdin.write(request_json)
self._proc.stdin.flush()  # 즉시 전송
```

3. **응답 읽기 (타임아웃 포함)**
```python
def _read_line_with_timeout(self, timeout: int):
    result = {"line": None}

    def read_line():
        result["line"] = self._proc.stdout.readline()

    thread = threading.Thread(target=read_line, daemon=True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        raise TimeoutError("Server did not respond in time")

    return result["line"]
```

4. **리소스 정리**
```python
def __del__(self):
    if self._proc:
        self._proc.terminate()
        self._proc.wait(timeout=5)
```

### 주의사항

- **버퍼링 문제**: `bufsize=1`로 라인 버퍼링 활성화
- **개행 문자**: 모든 JSON 메시지는 `\n`으로 끝나야 함
- **타임아웃 필수**: 외부 프로세스는 언제든 멈출 수 있음
- **에러 스트림**: stderr를 별도로 처리하거나 로깅

---

## FastAPI 통합 패턴

### 어댑터 패턴 사용

```python
class McpClient:
    def __init__(self, config: McpClientConfig):
        if config.mode == "mock":
            self._adapter = _MockAdapter()
        elif config.mode == "stdio":
            self._adapter = _StdioAdapter(config.exec_path, config.timeout_default)
        elif config.mode == "ws":
            self._adapter = _WebSocketAdapter(config.ws_url, config.timeout_default)
        else:
            raise ValueError(f"Unknown mode: {config.mode}")

    def list_tools(self):
        return self._adapter.list_tools()

    def call_tool(self, name: str, params: dict, timeout: Optional[int] = None):
        return self._adapter.call_tool(name, params, timeout)
```

**장점**:
- 모드 전환이 환경 변수 하나로 가능
- 테스트 시 mock 사용, 프로덕션에서 stdio/ws 사용
- 새로운 transport 추가가 쉬움

### 의존성 주입

```python
# app/dependencies.py
def get_mcp_client() -> McpClient:
    return mcp_client

# app/routers/mcp.py
@router.get("/mcp/tools")
async def list_tools(client: McpClient = Depends(get_mcp_client)):
    return {"tools": client.list_tools()}
```

---

## 에러 처리 전략

### 3계층 에러 처리

```
1. Transport 계층 (subprocess, 네트워크)
   ↓
2. Protocol 계층 (JSON-RPC 에러)
   ↓
3. Application 계층 (비즈니스 로직)
```

### 구현 예시

```python
class McpClientError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

# Transport 에러
if not response_line:
    raise McpClientError("transport_error", "No response from server")

# Protocol 에러
if "error" in response:
    error = response["error"]
    raise McpClientError(f"rpc_{error['code']}", error["message"])

# Application 에러 (라우터에서)
try:
    result = client.call_tool(name, params)
except McpClientError as e:
    if e.code == "tool_not_found":
        raise HTTPException(status_code=404, detail=str(e))
    else:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 실전 시나리오

### 시나리오 1: 기존 Python 스크립트를 MCP 서버로 변환

**상황**: 데이터베이스 쿼리를 수행하는 Python 스크립트가 있음

**단계**:

1. **FastMCP로 서버 생성**
```python
# my_db_server.py
from fastmcp import FastMCP

mcp = FastMCP("Database Query Server")

@mcp.tool()
def query_users(limit: int = 10) -> str:
    """사용자 목록 조회"""
    # 기존 DB 쿼리 로직
    users = db.query(User).limit(limit).all()
    return json.dumps([u.to_dict() for u in users])

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

2. **.env 설정**
```bash
MCP_MODE=stdio
MCP_EXEC_PATH=python C:\path\to\my_db_server.py
```

3. **FastAPI에서 사용**
```python
@router.get("/users")
async def get_users(limit: int = 10):
    result, _ = mcp_client.call_tool("query_users", {"limit": limit})
    return json.loads(result)
```

---

### 시나리오 2: 여러 MCP 서버 동시 사용

**상황**: DB 서버, 파일 서버, AI 서버를 동시에 사용

**구현**:

```python
# app/services/mcp_multi_client.py
class McpMultiClient:
    def __init__(self):
        self.db_client = McpClient(McpClientConfig(
            mode="stdio",
            exec_path="python C:\\servers\\db_server.py"
        ))
        self.file_client = McpClient(McpClientConfig(
            mode="stdio",
            exec_path="python C:\\servers\\file_server.py"
        ))
        self.ai_client = McpClient(McpClientConfig(
            mode="ws",
            ws_url="ws://ai-server.example.com/mcp"
        ))

    def query_and_save(self, query: str, filename: str):
        # 1. DB에서 데이터 조회
        data, _ = self.db_client.call_tool("query", {"sql": query})

        # 2. 파일로 저장
        result, _ = self.file_client.call_tool("save_file", {
            "path": filename,
            "content": data
        })

        return result
```

---

### 시나리오 3: 비동기 MCP 호출 (병렬 처리)

**상황**: 여러 도구를 동시에 호출해야 함

**구현**:

```python
import asyncio

async def call_tool_async(client: McpClient, tool_name: str, params: dict):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        client.call_tool,
        tool_name,
        params
    )

@router.get("/parallel-query")
async def parallel_query():
    # 3개 도구를 동시에 호출
    results = await asyncio.gather(
        call_tool_async(mcp_client, "get_weather", {"city": "Seoul"}),
        call_tool_async(mcp_client, "get_news", {"topic": "tech"}),
        call_tool_async(mcp_client, "get_stocks", {"symbol": "AAPL"})
    )

    return {
        "weather": results[0][0],
        "news": results[1][0],
        "stocks": results[2][0]
    }
```

---

## 체크리스트

### MCP 서버 개발 시

- [ ] FastMCP 라이브러리 설치 (`pip install fastmcp`)
- [ ] `@mcp.tool()` 데코레이터로 도구 정의
- [ ] 입력 파라미터 타입 힌트 추가
- [ ] docstring으로 도구 설명 작성
- [ ] `mcp.run(transport="stdio")` 추가
- [ ] 독립 실행 테스트 (echo_client.py 참조)

### MCP 클라이언트 개발 시

- [ ] `_StdioAdapter` 패턴 참조
- [ ] subprocess.Popen 설정 확인
- [ ] 타임아웃 처리 구현
- [ ] JSON-RPC 에러 핸들링
- [ ] 리소스 정리 (`__del__` 또는 context manager)
- [ ] .env 파일로 설정 관리

### FastAPI 통합 시

- [ ] McpClient를 싱글톤 또는 의존성으로 관리
- [ ] HTTP 에러를 적절히 매핑
- [ ] 타임아웃 설정 (기본값: 10초)
- [ ] 로깅 추가 (요청/응답, latency)
- [ ] 단위 테스트 작성 (pytest)
- [ ] 통합 테스트 작성 (실제 서버)

### 배포 전

- [ ] .env.example 파일 작성
- [ ] 프로덕션용 MCP 서버 경로 확인
- [ ] 타임아웃 값 튜닝
- [ ] 에러 로깅 설정
- [ ] 헬스 체크 엔드포인트 추가
- [ ] 모니터링 설정 (latency, error rate)

---

## 참고 파일

- **공식 문서**: https://modelcontextprotocol.io/
- **FastMCP GitHub**: https://github.com/jlowin/fastmcp
- **오늘의 WorkLog**: [docs/20251123_M5_stdio_작업기록.md](./20251123_M5_stdio_작업기록.md)
- **테스트 결과**: [docs/echo_client_test_results.json](./echo_client_test_results.json)
- **로드맵**: [docs/roadmap.md](./roadmap.md)

---

## 마무리

이 가이드는 2시간의 실습을 통해 얻은 **실전 경험**을 바탕으로 작성되었습니다.

**핵심을 요약하면**:

1. **MCP 프로토콜은 단순함** - JSON-RPC 2.0 + stdin/stdout
2. **Adapter 패턴이 핵심** - transport를 추상화하면 확장이 쉬움
3. **타임아웃은 필수** - 외부 프로세스는 언제든 멈출 수 있음
4. **에러 처리는 계층별로** - Transport, Protocol, Application을 구분
5. **환경 설정으로 유연하게** - mock/stdio/ws 전환을 쉽게

이 파일을 참조하면 새로운 MCP 서버를 만들거나, 기존 앱에 MCP를 통합하는 것이 훨씬 쉬워질 것입니다.

**Happy MCP Coding!**
