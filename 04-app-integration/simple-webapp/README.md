# Simple Web App (FastAPI)

작은 FastAPI 앱으로 `/health` 엔드포인트를 제공합니다. M4 학습 목표는 스모크 테스트(서버 미기동)와 실제 HTTP 호출을 모두 검증하고, 실행/로그를 표준화하는 것입니다.

## 폴더 개요
- `app/main.py` — FastAPI 앱 팩토리/엔트리
- `app/routers/health.py` — `/health` 라우트(상태/버전/시간)
- `tests_smoke/health_smoke.py` — 인프로세스 스모크 테스트(TestClient)
- `scripts/run_health_smoke.ps1` — 스모크 테스트 원클릭 실행(로그 JSONL 생성)
- `scripts/run_web.ps1` — uvicorn으로 서버 기동(포트 8000)

## 사전 준비(Windows PowerShell)
- Python 3.11 + venv(.venv) 준비
- 의존성 설치: 루트의 `02-env-setup/scripts/setup.ps1` 사용 권장
- 활성화: `02-env-setup/scripts/activate.ps1`

## 빠른 시작
### 1) 스모크 테스트(서버 미기동)
아래 스크립트는 앱을 직접 import하여 `/health`를 테스트하고, 결과를 한 줄 JSON으로 `docs/`에 기록합니다.

```powershell
# 리포 루트에서 실행
powershell -NoProfile -ExecutionPolicy Bypass -File .\04-app-integration\simple-webapp\scripts\run_health_smoke.ps1
```

- 생성 파일: `docs/health_smoke_YYYYMMDD_HHMMSS.jsonl`
- 예시 한 줄 JSON:

```json
{"timestamp":"2025-11-02T14:17:43.478536Z","status_code":200,"ok":true,"json":{"status":"ok","version":"0.1.0","time":"2025-11-02T14:17:43.476514+00:00"}}
```

### 2) 실제 서버 실행 후 HTTP 호출
다음 스크립트로 uvicorn 서버를 기동하고, 별도 터미널 또는 같은 터미널에서 HTTP를 호출해 확인합니다.

```powershell
# 서버 기동(포트 8000)
.\04-app-integration\simple-webapp\scripts\run_web.ps1

# 다른 터미널에서 확인 (둘 중 하나)
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health | Select-Object -Expand Content
curl.exe -s http://127.0.0.1:8000/health
```

- 서버 중지는 서버가 떠 있는 터미널에서 `Ctrl+C`
- 한 번에 실행/확인/종료까지 하고 싶다면(참고):

```powershell
$repo='C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\04-app-integration\simple-webapp'; \
. 'C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\02-env-setup\scripts\activate.ps1'; \
$env:PYTHONPATH=$repo; \
$p=Start-Process -FilePath python -ArgumentList '-m','uvicorn','app.main:app','--port','8000','--app-dir',$repo -PassThru; \
Start-Sleep -Seconds 1; \
$r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/health'; $r.Content; \
Stop-Process -Id $p.Id -Force
```

## 트러블슈팅(Windows)
- 실행 정책(ExecutionPolicy): 스크립트 실행 시 Bypass를 권장합니다.
  - 예) `powershell -NoProfile -ExecutionPolicy Bypass -File .\...\run_health_smoke.ps1`
- 모듈 import 실패: `ModuleNotFoundError: No module named 'app'`
  - 스크립트는 자동으로 `PYTHONPATH`를 설정합니다. 수동 실행 시에는 앱 루트를 `PYTHONPATH`로 지정하세요.
  - 예) `$env:PYTHONPATH = (Resolve-Path 'C:\...\04-app-integration\simple-webapp').Path`
- 포트 충돌(8000): 점유 프로세스 확인/종료 후 재시도
  - 확인: `netstat -ano | findstr :8000`
  - 종료: `taskkill /PID <PID> /F`
- 의존성 문제: 루트의 `02-env-setup/requirements.txt` 버전 고정 확인 후 재설치
  - `powershell -NoProfile -ExecutionPolicy Bypass -File .\02-env-setup\scripts\setup.ps1`

## 로그/아티팩트
- 스모크: `docs/health_smoke_*.jsonl`
- WorkLog: `docs/20251102_M4_작업기록.md` — 실행 결과와 로그 경로 기록

## 버전 정보
- FastAPI: 0.115.0, uvicorn: 0.31.1, pydantic: 2.11.4, httpx: 0.28.1
- MCP SDK(참고): mcp[cli] 1.18.0
