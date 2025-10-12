# M3: 기존 MCP 서버 탐색·평가·연결

목표
- 공개 MCP 서버 2~3개 후보 조사, 비교, 기본 연결(헬스/툴 목록) 시도
- stdio/웹소켓(ws) 설정/권한/경로 오류 점검(로드맵 체크리스트 반영)

구성
- configs/.env.example: 토큰, URI, 실행 경로 등 예시
- configs/server_profiles.json: 서버 프로필 목록(타입, 경로/URI, 인증 등)
- scripts/install_sdk.ps1: MCP Python SDK 설치(버전 고정, [검증] 반영 예정)
- scripts/health_check.ps1: 프로필별 기본 검증 및 로그 저장(실행만 하면 됨)
- clients/python/*.py: stdio/ws 클라이언트 샘플(드라이런 지원)
- logs/: 실행 로그 저장 경로

사용법(권장 순서)
1) configs/.env.example를 참고해 .env 작성(필요 시)
2) configs/server_profiles.json에서 사용할 프로필의 enabled를 true로 설정
3) ./03-discover-servers/scripts/install_sdk.ps1 실행(SDK 설치) [검증 후 적용]
4) ./03-discover-servers/scripts/health_check.ps1 실행 → 결과는 logs/에 저장

결과물
- servers_catalog.md: 후보 비교표(기능/인증/문서/라이선스)
- logs/health_*.txt: 프로필별 검증/연결 로그
- docs/connection_report.md: 성공/실패 및 이슈 정리

트러블슈팅 포인트(ws/stdio)
- stdio: 실행 파일 경로/권한, 인코딩, 작업 디렉터리, 환경변수
- ws: URI 스킴(ws/wss), DNS/방화벽/프록시, 인증 토큰 만료
