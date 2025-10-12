# M2: 로컬 환경 세팅 (Windows PowerShell 5.1)

목표
- 원클릭으로 Python 가상환경(venv) 생성, 패키지 설치, 환경 검증
- 이후 M3~M6에서 재사용 가능한 표준 스캐폴딩 준비

빠른 시작
1. PowerShell을 열고 리포지토리 루트로 이동
2. 다음을 실행
   - scripts/setup.ps1: venv 생성/업데이트 + 검증까지 자동화

예상 실행 흐름
- .venv 생성 → pip 업그레이드 → requirements 설치 → env_check.py 실행 → 결과 요약 표시

생성 파일
- requirements.txt: 런타임 의존성(현재 최소)
- requirements-dev.txt: 개발용 도구(black, ruff, pytest)
- scripts/activate.ps1: venv 활성화 전용
- scripts/setup.ps1: 전체 자동화(권장)
- scripts/pip-freeze.ps1: 패키지 스냅샷 저장
- tools/env_check.py: 환경 점검 스크립트

실행 방법 (PowerShell 5.1)
- 일시적 실행 정책 우회 필요 시: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
- venv 활성화: ./02-env-setup/scripts/activate.ps1
- 원클릭 세팅: ./02-env-setup/scripts/setup.ps1

검증 포인트
- venv 활성화 후 python -V, pip list 정상 동작
- tools/env_check.py 출력에서 OS, Python, 인코딩, venv 경로 확인

트러블슈팅
- ExecutionPolicy 오류: 위 일시 우회 명령 사용 후 재실행
- 경로 문제: PowerShell에서 루트 경로가 리포지토리 루트인지 확인
- 인코딩/한글: 파일은 UTF-8; 콘솔 글꼴과 코드페이지 영향 가능

다음 단계(미리보기: M3)
- MCP Python SDK 설치 및 샘플 클라이언트 실행
- 03-discover-servers/ 폴더에 비교표/연결 스크립트 추가 예정
