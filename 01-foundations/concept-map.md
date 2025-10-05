# MCP 개념 맵과 핵심 흐름 (M1)

[검증]
- 공식 사이트: https://modelcontextprotocol.io/ (소개/아키텍처/가이드) — 확인일: 2025-10-05
- 프로토콜 사양: https://spec.modelcontextprotocol.io/ (현재 버전: 2025-06-18 표시) — 확인일: 2025-10-05
- GitHub 조직 소개: https://github.com/modelcontextprotocol — 확인일: 2025-10-05
- 레퍼런스 서버 목록: https://github.com/modelcontextprotocol/servers — 확인일: 2025-10-05

요약
- MCP는 LLM 앱(클라이언트)과 외부 데이터/도구(서버)를 표준 계약으로 연결하는 개방형 프로토콜입니다.
- 서버는 Tools/Resources를 정의·제공하고, 클라이언트는 이를 탐색·호출합니다.
- 전송은 STDIO 또는 Streamable HTTP(SSE)를 사용합니다. 버전 협상은 초기화 단계에서 수행됩니다.

## 아키텍처 개념 맵
```mermaid
flowchart LR
    subgraph Client[Client (LLM App / IDE / Agent)]
      CConf[Config]
      CDisc[Discovery]
      CTools[List/Call Tools]
      CRes[Read Resources]
      CErr[Error/Retry/Timeout]
    end

    subgraph Transport[Transport]
      STDIO[STDIO]
      SSE[Streamable HTTP (SSE)]
    end

    subgraph Server[MCP Server]
      Init[Initialize & Version Negotiate]
      T[Tools]
      R[Resources]
      Auth[(Auth/Secrets?)]
      Obs[(Logging/Metrics)]
      Err[Errors]
      Stream[Streaming/Backpressure]
    end

    Client <--> Transport <--> Server
    CConf --> Init
    CTools --> T
    CRes --> R
    T --> Stream
    R --> Stream
    Server --> Err
    Client --> CErr
```

핵심 컴포넌트
- Client: MCP 서버에 연결해 Tools/Resources를 탐색·호출하는 애플리케이션(예: IDE, 채팅 UI, 에이전트 런타임).
- Server: 도메인 기능을 Tools(행위)·Resources(읽기 전용/스트리밍 가능)로 노출.
- Transport: STDIO, Streamable HTTP(SSE) 등. 구현/배포 환경에 맞춰 선택.
- Contract: 요청/응답 스키마, 오류 모델, 스트리밍/백프레셔 신호.

요청–응답·스트리밍 흐름 요약
1) Initialize: 클라이언트–서버가 프로토콜 버전 협상(사양의 YYYY-MM-DD 문자열)을 통해 합의
2) Discover: 서버의 metadata, tool 목록, resource 인덱스 조회
3) Call Tool / Read Resource: 입력 검증 → 실행 → 결과(부분/최종) 스트리밍 또는 단일 응답
4) Errors: 계약 위반·시간초과·취소·권한문제 등을 표준화된 오류로 전달
5) Backpressure: 클라/서버 양쪽에서 소비 속도 조절을 위한 신호 처리

## 전송 선택 기준(요약)
- STDIO
  - 장점: 단순/로컬 개발 용이, 프로세스 간 파이프 기반, 네트워킹 의존 최소화
  - 주의: 원격 배포/스케일아웃에는 부적합, 프로세스 생명주기 관리 필요
- Streamable HTTP(SSE)
  - 장점: 원격/클라우드 친화, 방화벽/프록시 우회 용이, 관찰성/배포 표준 활용
  - 주의: 인프라 구성 필요(인증/보안/레이트리밋/로깅), SSE 특성 이해 필요

적용 가이드
- 로컬 실습/단일 머신: STDIO 우선, 디버깅·개발 속도 최적화
- 원격/팀 공유/서비스화: Streamable HTTP(SSE) 우선, 인증·관찰성·확장성 고려

리스크·대응
- 스펙 업데이트 리스크: [사양] 버전 고지(예: 2025-06-18) 확인 후 사용 범위 명시
- 전송 혼동(ws vs sse): 최신 문서 기준으로 SSE/Streamable HTTP 표기를 따르고, 사용 클라이언트 호환성 체크
- 스키마 불일치: pydantic/zod 등으로 입출력 검증 계층 추가
