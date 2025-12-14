# M8 Capstone - 데모 실행 가이드

**프로젝트**: MCP Web Application - Monitoring System Demo
**작성일**: 2025-12-14
**작성자**: Claude Sonnet 4.5 (Anthropic)

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [데모 시나리오](#데모-시나리오)
3. [단계별 실행 가이드](#단계별-실행-가이드)
4. [예상 결과](#예상-결과)
5. [문제 해결](#문제-해결)
6. [결과 분석](#결과-분석)

---

## 사전 준비

### 환경 요구사항

**필수:**
- Windows 10/11 with PowerShell 5.1+
- Python 3.11+
- 가상환경 설정 완료

**선택:**
- curl 또는 Postman (API 테스트용)
- VS Code (로그 파일 확인용)

### 사전 확인 체크리스트

```powershell
# 1. 프로젝트 디렉토리로 이동
cd C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC

# 2. 가상환경 활성화
.\02-env-setup\scripts\activate.ps1

# 3. Python 버전 확인
python --version  # Python 3.11 이상

# 4. 의존성 확인
pip list | Select-String -Pattern "fastapi|uvicorn|pydantic"

# 5. MCP 서버 파일 확인
Test-Path ".\05-build-server\file_server.py"  # True

# 6. 테스트 샘플 파일 확인
Test-Path ".\04-app-integration\simple-webapp\test_samples\sample1.txt"  # True
```

### 환경 변수 설정

```powershell
# MCP 서버 설정
$env:MCP_MODE = "stdio"
$env:MCP_EXEC_PATH = "python C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\05-build-server\file_server.py"
$env:MCP_TIMEOUT_DEFAULT = "10"

# 확인
echo "MCP_MODE: $env:MCP_MODE"
echo "MCP_EXEC_PATH: $env:MCP_EXEC_PATH"
```

---

## 데모 시나리오

### 시나리오 개요

이 데모는 다음을 보여줍니다:
1. **모니터링 시스템 시작**: FastAPI 서버와 백그라운드 헬스 체커
2. **메트릭 생성**: MCP 도구를 여러 번 호출하여 메트릭 데이터 생성
3. **메트릭 조회**: 수집된 메트릭을 API를 통해 조회
4. **헬스 확인**: MCP 서버의 헬스 상태 확인
5. **데이터 리셋**: 메트릭 초기화 및 시스템 재시작

### 예상 소요 시간

- **자동 데모**: 약 2-3분
- **수동 데모**: 약 5-10분

---

## 단계별 실행 가이드

### 방법 1: 자동 데모 스크립트 (권장)

**한 번에 모든 단계 실행:**

```powershell
# 데모 스크립트 실행
.\08-capstone\scripts\run_demo.ps1
```

**실행 내용:**
- ✅ 환경 활성화
- ✅ FastAPI 서버 자동 시작
- ✅ 초기 상태 확인
- ✅ MCP 도구 15회 호출 (read_file x10, list_files x5)
- ✅ 메트릭 조회
- ✅ 헬스 체크
- ✅ 메트릭 리셋
- ✅ 자동 정리

**출력:**
- 콘솔에 실시간 진행 상황 표시
- `08-capstone/logs/demo_output_YYYYMMDD_HHMMSS.txt`에 전체 로그 저장

---

### 방법 2: 수동 단계별 실행

#### Step 1: 서버 시작

```powershell
# 1. 가상환경 활성화
.\02-env-setup\scripts\activate.ps1

# 2. WebApp 디렉토리로 이동
cd .\04-app-integration\simple-webapp

# 3. PYTHONPATH 설정
$env:PYTHONPATH = (Get-Location).Path

# 4. uvicorn 서버 시작
uvicorn app.main:app --port 8000 --reload
```

**예상 출력:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**✅ 성공 확인:**
- 브라우저에서 `http://localhost:8000/docs` 열기
- Swagger UI가 표시됨

#### Step 2: 초기 상태 확인

**새 PowerShell 창 열기** (서버는 계속 실행):

```powershell
# 앱 헬스 체크
curl http://localhost:8000/health

# 모니터링 상태
curl http://localhost:8000/monitoring/status

# 메트릭 (아직 비어있음)
curl http://localhost:8000/monitoring/metrics
```

**예상 결과:**

`/health`:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "time": "2025-12-14T10:30:00+00:00"
}
```

`/monitoring/status`:
```json
{
  "status": "no_servers",
  "timestamp": "2025-12-14T10:30:00Z",
  "uptime_seconds": 10,
  "servers": [],
  "metrics_summary": {
    "total_calls": 0,
    "total_successes": 0,
    "total_errors": 0,
    "success_rate": 0.0,
    "avg_latency_ms": 0.0
  }
}
```

#### Step 3: MCP 도구 목록 확인

```powershell
curl http://localhost:8000/mcp/tools
```

**예상 결과:**
```json
{
  "tools": [
    {
      "name": "read_file",
      "description": "파일 내용을 읽어서 반환합니다."
    },
    {
      "name": "list_files",
      "description": "디렉토리 내의 파일과 폴더 목록을 조회합니다."
    }
  ]
}
```

#### Step 4: MCP 도구 호출 (메트릭 생성)

**read_file 호출 (10회):**

```powershell
for ($i=1; $i -le 10; $i++) {
    curl -X POST http://localhost:8000/mcp/actions/read_file `
         -H "Content-Type: application/json" `
         -d '{"params":{"path":"test_samples/sample1.txt"}}'

    Write-Host "Called read_file $i/10"
    Start-Sleep -Milliseconds 100
}
```

**list_files 호출 (5회):**

```powershell
for ($i=1; $i -le 5; $i++) {
    curl -X POST http://localhost:8000/mcp/actions/list_files `
         -H "Content-Type: application/json" `
         -d '{"params":{"directory":"test_samples","pattern":"*"}}'

    Write-Host "Called list_files $i/5"
    Start-Sleep -Milliseconds 100
}
```

#### Step 5: 메트릭 조회

```powershell
# 전체 메트릭
curl http://localhost:8000/monitoring/metrics

# 특정 도구 (read_file)
curl "http://localhost:8000/monitoring/metrics?tool=read_file"

# 시스템 상태
curl http://localhost:8000/monitoring/status
```

**예상 결과 (`/monitoring/metrics`):**
```json
{
  "timestamp": "2025-12-14T10:35:00Z",
  "uptime_seconds": 300,
  "tools": [
    {
      "name": "list_files",
      "total_calls": 5,
      "success_calls": 5,
      "error_calls": 0,
      "success_rate": 1.0,
      "avg_latency_ms": 45.6,
      "min_latency_ms": 30,
      "max_latency_ms": 65,
      "last_call_time": "2025-12-14T10:34:55Z"
    },
    {
      "name": "read_file",
      "total_calls": 10,
      "success_calls": 10,
      "error_calls": 0,
      "success_rate": 1.0,
      "avg_latency_ms": 28.3,
      "min_latency_ms": 20,
      "max_latency_ms": 40,
      "last_call_time": "2025-12-14T10:34:50Z"
    }
  ]
}
```

#### Step 6: 헬스 체크

```powershell
# 3초 대기 (백그라운드 헬스 체커 실행 대기)
Start-Sleep -Seconds 3

# 모든 서버 헬스
curl http://localhost:8000/monitoring/health

# 특정 서버 (file_server)
curl http://localhost:8000/monitoring/health/file_server
```

**예상 결과 (`/monitoring/health/file_server`):**
```json
{
  "server_name": "file_server",
  "server_type": "stdio",
  "status": "ok",
  "last_check_time": "2025-12-14T10:35:30Z",
  "last_success_time": "2025-12-14T10:35:30Z",
  "consecutive_failures": 0,
  "total_checks": 6,
  "total_successes": 6,
  "total_failures": 0,
  "uptime_percentage": 100.0,
  "response_time_ms": 25,
  "server_info": {
    "status": "ok",
    "server_type": "stdio"
  }
}
```

#### Step 7: 메트릭 리셋 (선택)

```powershell
curl -X POST http://localhost:8000/monitoring/reset `
     -H "Content-Type: application/json" `
     -d '{"confirm":true}'

# 리셋 후 메트릭 확인 (비어있어야 함)
curl http://localhost:8000/monitoring/metrics
```

#### Step 8: 서버 중지

```powershell
# 첫 번째 PowerShell 창에서 Ctrl+C
# 또는 프로세스 직접 종료:
Get-Process | Where-Object {$_.Name -eq "python"} | Stop-Process -Force
```

---

## 예상 결과

### 성공 기준

#### 1. 서버 시작 성공
- ✅ uvicorn 시작 로그 표시
- ✅ `/health` 엔드포인트 200 응답
- ✅ Swagger UI 접근 가능

#### 2. 메트릭 수집 성공
- ✅ API 호출 후 `total_calls` 증가
- ✅ 응답 시간 통계 계산됨 (avg, min, max)
- ✅ 성공률 100% (에러 없음)

#### 3. 헬스 체크 성공
- ✅ file_server 상태 "ok"
- ✅ uptime_percentage 100%
- ✅ last_check_time 최신

#### 4. 전체 시스템 상태
- ✅ `/monitoring/status`에서 "ok" 상태
- ✅ servers 리스트에 file_server 존재
- ✅ metrics_summary 올바른 통계

### 성능 메트릭

**예상 응답 시간:**
- `/monitoring/status`: < 50ms
- `/monitoring/metrics`: < 30ms
- `/monitoring/health/{server}`: < 20ms
- MCP 도구 호출: 20-60ms

**메모리 사용량:**
- FastAPI 프로세스: ~100MB
- 메트릭 데이터: < 1MB

---

## 문제 해결

### 문제 1: 서버 시작 실패

**증상:**
```
Error: [WinError 10048] Only one usage...
```

**원인:** 포트 8000이 이미 사용 중

**해결:**
```powershell
# 포트 사용 프로세스 찾기
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# 프로세스 종료
Stop-Process -Id <PID> -Force
```

### 문제 2: MCP 도구 호출 실패

**증상:**
```json
{
  "error": {
    "code": "connection_error",
    "message": "Server executable not found"
  }
}
```

**원인:** MCP_EXEC_PATH 설정 오류

**해결:**
```powershell
# 경로 확인
$env:MCP_EXEC_PATH

# 올바른 경로로 설정
$env:MCP_EXEC_PATH = "python C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\05-build-server\file_server.py"

# MCP 서버 수동 테스트
python .\05-build-server\file_server.py
# (Ctrl+C로 중지)
```

### 문제 3: 헬스 체크 데이터 없음

**증상:** `/monitoring/health` 응답이 빈 리스트 `[]`

**원인:** 백그라운드 헬스 체커가 아직 실행되지 않음

**해결:**
```powershell
# 30초 이상 대기 (첫 번째 헬스 체크까지)
Start-Sleep -Seconds 35

# 다시 조회
curl http://localhost:8000/monitoring/health
```

### 문제 4: test_samples 파일 없음

**증상:**
```json
{
  "error": {
    "message": "파일을 찾을 수 없습니다: test_samples/sample1.txt"
  }
}
```

**해결:**
```powershell
# test_samples 디렉토리 생성
cd .\04-app-integration\simple-webapp
mkdir -Force test_samples

# 샘플 파일 생성
"This is a test file." | Out-File -FilePath "test_samples\sample1.txt" -Encoding UTF8
"Another test file." | Out-File -FilePath "test_samples\sample2.txt" -Encoding UTF8
```

---

## 결과 분석

### 메트릭 해석

**1. success_rate (성공률)**
- **100%**: 완벽 (모든 호출 성공)
- **95-99%**: 양호 (소수 에러)
- **< 95%**: 주의 (문제 조사 필요)

**2. avg_latency_ms (평균 응답 시간)**
- **< 50ms**: 우수
- **50-100ms**: 양호
- **> 100ms**: 느림 (최적화 필요)

**3. consecutive_failures (연속 실패)**
- **0**: 정상
- **1-2**: 일시적 문제 (degraded)
- **≥ 3**: 심각 (error)

### 시스템 상태 판단

**상태별 의미:**
- **"ok"**: 모든 서버 정상
- **"degraded"**: 일부 서버에 문제
- **"error"**: 심각한 장애
- **"no_servers"**: 서버 미등록 (초기 상태)

---

## 추가 실험

### 실험 1: 에러 시뮬레이션

```powershell
# 존재하지 않는 파일 읽기
curl -X POST http://localhost:8000/mcp/actions/read_file `
     -H "Content-Type: application/json" `
     -d '{"params":{"path":"nonexistent.txt"}}'

# 메트릭 확인 (error_calls 증가)
curl http://localhost:8000/monitoring/metrics
```

### 실험 2: 대량 호출

```powershell
# 100회 호출 (부하 테스트)
for ($i=1; $i -le 100; $i++) {
    curl -X POST http://localhost:8000/mcp/actions/read_file `
         -H "Content-Type: application/json" `
         -d '{"params":{"path":"test_samples/sample1.txt"}}' | Out-Null

    if ($i % 10 -eq 0) {
        Write-Host "Progress: $i/100"
    }
}

# 메트릭 확인
curl http://localhost:8000/monitoring/metrics
```

### 실험 3: 장기 모니터링

```powershell
# 5분간 주기적으로 상태 확인
for ($i=1; $i -le 10; $i++) {
    Write-Host "`n=== Check $i/10 ==="
    curl http://localhost:8000/monitoring/status
    Start-Sleep -Seconds 30
}
```

---

## 데모 완료 후 확인 사항

### 확인 체크리스트

- [ ] 모든 API 엔드포인트 정상 응답
- [ ] 메트릭 데이터 정확히 수집됨
- [ ] 헬스 체크 주기적 실행 확인
- [ ] 로그 파일 저장 확인
- [ ] 서버 정상 종료

### 다음 단계

1. **프론트엔드 대시보드 개발**
   - React/Vue.js로 시각화
   - 차트 라이브러리 통합

2. **영속성 추가**
   - PostgreSQL 연동
   - 히스토리 데이터 저장

3. **알림 설정**
   - 임계값 설정
   - 이메일/Slack 알림

4. **프로덕션 배포**
   - Docker 컨테이너화
   - Kubernetes 배포

---

## 참고 자료

- [README.md](README.md) - 프로젝트 개요
- [DESIGN.md](DESIGN.md) - 아키텍처 설계
- [API 문서](http://localhost:8000/docs) - Swagger UI
- [M8 학습 계획](../docs/20251214_WorkLog_M8_학습계획.md)

---

**데모 완료를 축하합니다!** 🎉

이 데모를 통해 다음을 경험했습니다:
- ✅ 실시간 모니터링 시스템 구축
- ✅ RESTful API 설계 및 구현
- ✅ 백그라운드 작업 관리
- ✅ 프로덕션 준비 시스템 개발

**MCP 학습 여정의 마지막 단계를 완성했습니다!** 🎓
