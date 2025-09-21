# MCP 학습 로드맵 (Python + Simple Web App + 내장 MCP 클라이언트)

- 날짜: 2025-09-21 (주 6시간, 총 6주 권장: 1~2달 범위)
- 대상: Windows + PowerShell 5.1, Python 최신, Docker 사용 가능, 방화벽/프록시 없음
- 목표 산출물: 
  - Simple 웹 애플리케이션(예: FastAPI) + 기존 MCP 서버 연동 + 커스텀 MCP 서버 구현/통합
  - 팀용 가이드 문서, GitHub 공개, 샘플/템플릿 배포

요약 일정(권장)
- 주1: M1(개요) + M2(환경)
- 주2: M3(기존 MCP 서버 탐색/연결)
- 주3: M4(웹앱 스켈레톤)
- 주4: M5(웹앱에 기존 MCP 서버 통합)
- 주5: M6(커스텀 MCP 서버 구현)
- 주6: M7(배포/문서/템플릿) + M8(캡스톤)

공통 폴더 구조(루트: `c:\AI_study\Projects\MCP\MCP_Basic_Higher_Models`)
```
01-foundations/
02-env-setup/
03-discover-servers/
04-app-integration/   # simple-webapp 포함
05-build-server/
06-advanced-server/
07-release-share/
08-capstone/
```

사실성/최신성 주의
- MCP Python SDK의 정확한 패키지명/설치/사용법은 “공식 문서”로 확인해 적용. 아래 내용은 절차/형식을 제시하며, [검증] 단계를 포함해 진행한다.
- 모든 명령은 Windows PowerShell 기준. 가상환경, 경로, 인코딩 이슈를 항상 점검한다.

---

## M1. MCP 개요와 핵심 개념 (0.5일)
- 학습 목표
  - MCP의 Server/Client/Tools/Resources/Transport(stdio/ws) 개념과 역할을 설명한다.
  - stdio vs WebSocket 선택 기준을 설명한다.
  - 공개 MCP 서버의 기능(툴/리소스) 카탈로그를 표로 만든다.
- 주요 개념
  - 계약(요청/응답 스키마), 에러 모델, 스트리밍, 백프레셔 개요
- 환경 준비(PS)
  - `python --version`; `docker --version`
- 필수 레퍼런스(예)
  - MCP 사양/SDK/예제 저장소: 공식 문서 우선. [검증: 최신 링크 확인]
- 실습 과제
  1) `01-foundations/`에 개념 맵/용어집 작성(Markdown/mermaid)
  2) 공개 MCP 서버 2~3개 조사, 툴/리소스 목록/인증/라이선스 비교표 작성
- 산출물/DoD
  - `01-foundations/concept-map.md`, `glossary.md`, `server-comparison.md`
- 체크리스트(예)
  - 전송 2가지 차이/장단점 설명 가능? 에러 모델/스트리밍 용어 정리됨?
- 트러블슈팅: 용어 혼동 → 용어집 상시 보정

## M2. 로컬 환경 세팅 (0.5~1일)
- 학습 목표
  - Python 전용 개발 환경/가상환경 구성과 재현 가능한 스크립트화
  - Docker 기반 실행 토대 마련
- 환경 준비(PS)
  - `py -3.11 -m venv .venv`; `./.venv/Scripts/Activate.ps1`
  - `python -m pip install --upgrade pip`
  - 필요 시: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`
- 실습 과제
  1) `02-env-setup/`에 venv 활성화 스크립트, `requirements.txt`/`requirements-dev.txt` 작성
  2) 베이스 `Dockerfile` 초안 준비(런타임/포트/헬스체크 주석 포함)
- 산출물/DoD
  - venv 활성화/패키지 설치 OK, `pip list` 스냅샷, Dockerfile 빌드 테스트 기록
- 체크리스트: venv 활성/비활성 절차 숙지, Docker 빌드 성공
- 트러블슈팅: 실행 정책/경로/인코딩 이슈 해결법 문서화

## M3. 기존 MCP 서버 탐색·평가·연결 (1일)
- 학습 목표
  - 후보 3개 평가, 1~2개를 실제 연결해 툴/리소스 조회와 헬스체크 수행
- 레퍼런스(예)
  - 공식 레지스트리/문서, GitHub 토픽 “model context protocol”, “mcp server” [검증]
- 실습 과제
  1) 평가 기준 표준화(기능/인증/안정성/문서/유지보수/라이선스)
  2) Python SDK로 샘플 클라이언트 코드 스케치
     - [검증] `pip install <공식 MCP Python SDK 패키지>` 후 툴 목록/헬스 호출 샘플
  3) stdio 또는 WebSocket으로 최소 호출(툴 1개) 성공
- 산출물/DoD
  - `03-discover-servers/` 비교표, 연결 로그/스크립트, 간단 호출 예제
- 체크리스트: 전송 선택 근거/인증 유무/라이선스 확인 완료
- 트러블슈팅: ws/stdio 설정/권한/경로 오류 점검

## M4. Simple Web App 스켈레톤 (1일)
- 학습 목표
  - FastAPI(또는 Flask) 기반 최소 웹앱 구성, 라우팅/설정/로깅 분리
- 환경 준비/설치(PS)
  - `python -m pip install fastapi uvicorn[standard] pydantic python-dotenv`
  - 실행: `uvicorn app.main:app --reload`
- 실습 과제
  1) `04-app-integration/simple-webapp/` 구조
     - `app/main.py`, `app/routers/`, `app/services/`, `config/.env`
  2) `/health` 엔드포인트, 설정 로딩, 구조화 로깅 추가
- 산출물/DoD
  - 로컬 실행 OK, `/health` 200, README에 실행/테스트 절차
- 체크리스트: 설정 주입/로그 포맷/포트 충돌 없음
- 트러블슈팅: 가상환경/포트/윈도우 경로 문제 해결

## M5. 기존 MCP 서버를 웹앱에 통합 (1~2일)
- 학습 목표
  - 앱 내 MCP 클라이언트 래퍼(타임아웃/리트라이/입출력 검증) 구현, 엔드포인트 연동
- 환경 준비/설치(예)
  - SDK 요구사항에 따라: `python -m pip install httpx` 또는 `websockets` 등
  - `.env` 예: `MCP_SERVER_URI`, `MCP_EXEC_PATH` 등
- 실습 과제
  1) `app/services/mcp_client.py`: 연결/호출/오류 매핑/타임아웃/백오프
  2) `/mcp/actions/<tool>` → 서버 호출 → 응답 검증(pydantic 모델)
  3) 계약 테스트: 입력/출력 스키마 + 예외 케이스
- 산출물/DoD
  - 동작 데모(스크린샷/로그), 통합 테스트 스크립트, 구성 문서
- 체크리스트: 타임아웃/백오프/취소 처리, 로깅/메트릭 최소화, 입력 검증
- 트러블슈팅: stdio 실행 경로/권한, ws 연결 실패, 응답 스키마 불일치

## M6. 커스텀 MCP 서버 (2일)
- 학습 목표
  - Python SDK로 최소 기능(툴 1~2개) 제공 MCP 서버 구현/로컬 연결
- 환경 준비/설치
  - [검증] `pip install <공식 MCP Python 서버 SDK 패키지>`
- 실습 과제
  1) `05-build-server/server/` 도메인/툴 스키마(pydantic) 설계
  2) 핸들러와 에러 모델 구현, 필요 시 스트리밍 1개 예제
  3) 계약 테스트 + 샘플 클라이언트로 E2E 검증
- 산출물/DoD
  - 서버 코드/스키마/테스트, README에 사용법/예제/제한
- 체크리스트: 실패 케이스/경계값 테스트, 리소스/메모리 로그 확인
- 트러블슈팅: 프로세스 생명주기, Windows 경로/인코딩 문제

## M7. 배포·문서화·공유 (1일)
- 학습 목표
  - Docker/템플릿 패키징, GitHub 공개, 팀 가이드 작성
- 환경 준비/명령(PS)
  - `docker build -t simple-mcp-app:dev .`
  - `docker run -p 8000:8000 simple-mcp-app:dev`
- 실습 과제
  1) 앱/서버 각각의 Dockerfile 또는 멀티스테이지 설계
  2) 템플릿/샘플 프로젝트 구조화(cookiecutter 또는 템플릿 폴더)
  3) 팀 가이드(설치/실행/확장/FAQ)와 CHANGELOG/라이선스 정리
- 산출물/DoD
  - `07-release-share/` 템플릿, Docker 이미지, 공개 리포지토리(README/CHANGELOG/LICENSE)
- 체크리스트: 재현 가능한 빌드/실행, 1분 내 데모 가동
- 트러블슈팅: Windows 파일 권한/라인 엔딩, 컨테이너 포트 충돌

## M8. 캡스톤 (1일)
- 학습 목표
  - “웹앱 + 기존 MCP 서버 + 커스텀 MCP 서버” 단일 시나리오 통합 데모 완성
- 실습 과제
  1) 사용자 가치 중심 유즈케이스 1개 구현(엔드투엔드 플로우)
  2) 통합/계약 테스트 모두 통과, 회귀 테스트 스크립트 포함
  3) 데모 스크립트/스크린샷/짧은 영상 가이드
- 산출물/DoD
  - `08-capstone/` 재현 스크립트, 테스트 로그, 데모 가이드, 팀 가이드 최종본
- 체크리스트: 장애/폴백 시나리오, 로그로 원인 추적 가능

---

운영 체크리스트(요약)
- 전송 선택: stdio vs ws 기준 명확화(지연/상태/네트워킹)
- 안정성: 타임아웃/재시도/백오프/취소/백프레셔
- 품질: 단위/통합/계약 테스트, 프로토콜 호환 체크
- 보안 기본: 시크릿 분리(현재 제약 없음이지만 관례 유지), 로깅에서 PII 최소화
- 문서화: README, 팀 가이드, 변경 이력, 사용 사례

향후 조정
- 공식 MCP Python SDK 이름/버전/예제는 문서 확인 즉시 본 로드맵 내 [검증] 항목을 치환/고도화한다.
