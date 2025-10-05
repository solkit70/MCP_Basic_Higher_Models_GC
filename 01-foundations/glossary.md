# MCP 용어집 (M1)

[검증]
- 공식 문서: https://modelcontextprotocol.io/ — 확인일: 2025-10-05
- 프로토콜 사양: https://spec.modelcontextprotocol.io/ — 확인일: 2025-10-05
- GitHub 조직: https://github.com/modelcontextprotocol — 확인일: 2025-10-05

용어
1) MCP (Model Context Protocol): LLM 앱과 외부 도구/데이터를 표준 인터페이스로 연결하는 오픈 프로토콜
2) Client: MCP 서버에 연결해 도구/리소스를 탐색/호출하는 애플리케이션(IDE, 챗, 에이전트 등)
3) Server: 도메인 기능을 MCP Tools/Resources 형태로 노출하는 백엔드 프로세스/서비스
4) Tool: 동작을 수행하는 호출 가능한 엔드포인트(입력/출력 스키마 보유)
5) Resource: 읽기 전용 또는 스트리밍 가능한 데이터 자원(문서, 로그, 메트릭 등)
6) Transport: 통신 방식. STDIO 또는 Streamable HTTP(SSE) 등을 사용
7) STDIO: 표준 입출력 파이프를 통한 로컬 프로세스 간 통신 방식
8) Streamable HTTP (SSE): 서버-발신 이벤트 기반 스트리밍 HTTP 연결로 결과를 점진적으로 전송
9) Initialization: 세션 시작 시 교환되는 핸드셰이크로, 버전 협상과 기능/메타데이터 교환 포함
10) Version Negotiation: 사양 버전(YYYY-MM-DD 문자열)의 합의 절차
11) Schema: 요청/응답/오류에 대한 구조 정의(JSON 스키마 등)
12) Error Model: 도구 실행 실패/검증 오류/권한 오류 등을 표준 형태로 전달하는 규칙
13) Streaming: 대용량/장시간 처리에서 중간 결과를 순차 전송하는 방식
14) Backpressure: 생산/소비 속도 불균형 시 흐름 제어를 위한 신호/메커니즘
15) Capability Discovery: 서버가 제공하는 도구/리소스/설정 범위를 나열·질의
16) Authentication: 서버 접근 제어를 위한 토큰/키/자격 증명 처리(필요한 서버에 한함)
17) Observability: 로깅/메트릭/트레이싱으로 가시성 확보
18) Timeout/Retry/Backoff: 안정성을 위한 호출 정책(클라이언트 래퍼 레벨에서 적용 권장)
19) Contract Test(계약 테스트): 입력/출력/오류 스키마 준수 여부를 자동 검증하는 테스트
20) Reference Server: 공식 레포의 예시/데모 서버(예: Filesystem, Git, Memory 등)
21) Registry: 공개 MCP 서버를 색인/발견하기 위한 레지스트리 서비스(예: https://github.com/modelcontextprotocol/registry)
22) SDK: 서버/클라이언트 구현을 돕는 언어별 라이브러리(예: Python/TypeScript SDK)
