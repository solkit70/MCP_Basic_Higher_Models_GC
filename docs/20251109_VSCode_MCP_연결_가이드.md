# VS Code에서 외부 MCP 서버 연결 가이드 (학습용)

이 문서는 "VS Code + MCP 지원 확장"을 사용하여 외부 MCP 서버와 연결해 보는 학습 절차를 정리한 것입니다. 특정 확장의 상세 키 이름이나 UI는 각 확장 문서를 우선 참조하세요. 여기서는 공통 개념과 전형적인 설정 항목(placeholder)을 제공합니다.

## 개념 요약
- MCP 서버: Model Context Protocol을 구현한 프로세스(로컬 실행 또는 원격 WebSocket).
- 전송(transport):
  - stdio: 로컬 프로세스를 실행하고 표준입출력으로 JSON-RPC 교신.
  - ws: 원격/로컬 WebSocket(ws://, wss://)으로 JSON-RPC 교신.
- VS Code 측 클라이언트: MCP를 지원하는 확장(예: MCP 호환 확장). 각 확장에서 MCP 서버를 설정/등록하는 방법이 제공됩니다.

## 준비물 체크리스트
1) VS Code에 MCP를 지원하는 확장을 설치합니다.
2) 연결하려는 MCP 서버를 결정합니다.
   - stdio 서버인 경우: 실행 파일 경로, 필요한 인자(args), 작업 디렉터리(cwd), 환경 변수(env)를 파악.
   - WebSocket 서버인 경우: ws:// 또는 wss:// URL, 인증 헤더(필요 시)를 파악.
3) 네트워크/실행 권한 확인(Windows 방화벽, 실행 정책 등).

## 설정 템플릿(일반형)
아래는 확장 설정에 흔히 필요한 항목을 "개념 템플릿"으로 보여줍니다. 실제 키 이름은 사용하는 확장 문서에 맞춰 매핑하세요.

### 1) stdio 서버 등록
```json
{
  "name": "my-local-stdio",
  "transport": "stdio",
  "command": "C:\\path\\to\\your-mcp-server.exe",
  "args": ["--flag", "value"],
  "cwd": "C:\\path\\to",
  "env": {
    "MY_ENV": "value"
  }
}
```
- name: 사람이 알아보기 쉬운 이름
- transport: "stdio"
- command: 실행 파일 절대 경로(Windows는 백슬래시 이스케이프 주의)
- args: 서버가 요구하는 인자 배열(없으면 생략)
- cwd: 서버가 상대경로를 가정할 때 기준이 되는 작업 디렉터리(필요 시)
- env: 서버가 필요로 하는 환경 변수(key-value)

### 2) WebSocket 서버 등록
```json
{
  "name": "my-ws",
  "transport": "ws",
  "url": "ws://localhost:5173",
  "headers": {
    "Authorization": "Bearer <token-if-needed>"
  }
}
```
- name: 표시용 이름
- transport: "ws"
- url: ws:// 또는 wss:// 주소
- headers: 인증/커스텀 헤더가 필요한 경우(없으면 생략)

## 동작 확인 절차(일반형)
1) VS Code에서 MCP 확장의 "Servers" 또는 "Tools" 보기를 열어 서버가 인식되었는지 확인합니다.
2) 서버가 노출하는 tools 목록이 보이는지 확인합니다(list_tools).
3) 간단한 tool(예: ping/echo 등)을 호출해 응답이 오는지 확인합니다.
4) 실패 시 확장 로그/Output 패널을 확인하고, 아래 트러블슈팅을 참고합니다.

## 트러블슈팅
- 서버가 보이지 않음
  - stdio: command 경로, 권한, cwd 유효성 점검. 백신/Defender가 실행을 막는지 확인.
  - ws: URL 접근 가능 여부, 방화벽, 프록시, 인증 헤더 확인.
- tools 목록 비어 있음
  - 서버가 MCP initialize 후 capabilities/tools를 올바르게 제공하는지 서버 로그 확인.
- 호출 시 타임아웃/에러
  - 확장 설정의 timeout(있다면) 상향. 서버 측 처리 시간/에러 메시지 확인.
- 인증 문제
  - ws 헤더/토큰 갱신. wss인 경우 인증서 체인 이슈 점검.

## 이 저장소(학습 프로젝트)와의 연동 힌트
- 현재 앱(`04-app-integration/simple-webapp`)은 클라이언트 관점에서 MCP 서버에 연결하는 구조를 준비 중입니다.
- .env에서 다음 변수를 사용합니다(아래 .env.example 참고).
  - MCP_MODE: mock | stdio | ws
  - MCP_EXEC_PATH: stdio 서버 실행 파일 경로
  - MCP_SERVER_URI: WebSocket 서버 주소(ws:// 또는 wss://)
  - MCP_TIMEOUT_DEFAULT: 기본 타임아웃(초)
  - MCP_RETRY_MAX: 재시도 횟수(향후 사용)
- VS Code에서 외부 MCP 서버를 먼저 직접 연결해 "동작/도구 목록/호출" 감을 잡은 후, 본 앱의 MCP_MODE를 ws 또는 stdio로 바꿔서 동일 서버에 붙이는 식으로 학습 폭을 넓히는 것을 권장합니다.

## Windows 팁
- PowerShell 실행 정책으로 인해 스크립트 실행이 막히면, 학습 중 필요한 범위에서만 Bypass/RemoteSigned를 고려하세요(보안 정책 준수).
- 방화벽 팝업이 뜨면 로컬 개발 상황에 맞게 허용/차단을 결정합니다.
- 경로에 공백이 있으면 command/cwd 값에 큰따옴표를 적용하거나 백슬래시 이스케이프에 주의하세요.

## 다음 단계(학습 로드맵)
1) VS Code 확장에서 stdio 서버 1개 등록 → tools 확인/호출
2) 같은 서버의 ws 모드가 있다면 ws도 등록 → 둘의 차이를 비교
3) 이 저장소 앱의 `.env`에서 MCP_MODE=ws, MCP_SERVER_URI 설정 → 앱 라우터 `/mcp/*`로 실제 서버 호출 테스트(서버 어댑터 구현 후)
4) 에러/타임아웃/재시도 로직을 케이스별로 실험해 보고 문서화

> 주의: 이 문서는 특정 확장의 고유 설정 스키마를 대신하지 않습니다. 실제 사용 중인 확장 문서를 우선 참고하고, 위 템플릿의 필드를 해당 스키마에 맞게 매핑하세요.
