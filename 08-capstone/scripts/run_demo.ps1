#Requires -Version 5.1
<#
.SYNOPSIS
    M8 Capstone - 실시간 모니터링 시스템 데모

.DESCRIPTION
    이 스크립트는 MCP 웹 애플리케이션의 모니터링 기능을 데모합니다.
    - FastAPI 서버 시작
    - 초기 시스템 상태 확인
    - MCP 도구 호출 (메트릭 생성)
    - 모니터링 API를 통한 메트릭 조회
    - 헬스 체크 확인

.NOTES
    작성일: 2025-12-14
    작성자: Claude Sonnet 4.5
#>

$ErrorActionPreference = 'Stop'

# ============================================================
# Configuration
# ============================================================

$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$WebAppRoot = Join-Path $RepoRoot "04-app-integration\simple-webapp"
$LogDir = Join-Path $PSScriptRoot "..\logs"
$LogFile = Join-Path $LogDir "demo_output_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

$Port = 8000
$BaseUrl = "http://localhost:$Port"

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# ============================================================
# Helper Functions
# ============================================================

function Write-Step {
    param([string]$Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $output = "`n[$timestamp] === $Message ==="
    Write-Host $output -ForegroundColor Cyan
    Add-Content -Path $LogFile -Value $output
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor White
    Add-Content -Path $LogFile -Value "  $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
    Add-Content -Path $LogFile -Value "  [OK] $Message"
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor Yellow
    Add-Content -Path $LogFile -Value "  [WARN] $Message"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  [ERROR] $Message" -ForegroundColor Red
    Add-Content -Path $LogFile -Value "  [ERROR] $Message"
}

function Invoke-ApiCall {
    param(
        [string]$Method = "GET",
        [string]$Endpoint,
        [string]$Body = $null,
        [string]$Description
    )

    Write-Info "$Description..."

    try {
        $uri = "$BaseUrl$Endpoint"
        $params = @{
            Uri = $uri
            Method = $Method
            UseBasicParsing = $true
            TimeoutSec = 10
        }

        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }

        $response = Invoke-WebRequest @params
        $content = $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

        Write-Success "$Description (Status: $($response.StatusCode))"
        Write-Host "    Response:" -ForegroundColor Gray
        Write-Host $content -ForegroundColor Gray

        Add-Content -Path $LogFile -Value "    Response:"
        Add-Content -Path $LogFile -Value $content
        Add-Content -Path $LogFile -Value ""

        return $response
    }
    catch {
        Write-Error-Custom "$Description - Failed: $_"
        return $null
    }
}

# ============================================================
# Main Demo Script
# ============================================================

Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "  M8 Capstone - Monitoring System Demo  " -ForegroundColor Magenta
Write-Host "========================================`n" -ForegroundColor Magenta

Add-Content -Path $LogFile -Value "========================================="
Add-Content -Path $LogFile -Value "M8 Capstone - Monitoring System Demo"
Add-Content -Path $LogFile -Value "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Content -Path $LogFile -Value "=========================================`n"

try {
    # ============================================================
    # Step 1: Environment Setup
    # ============================================================
    Write-Step "Step 1: Environment Setup"

    Write-Info "Activating virtual environment..."
    $activateScript = Join-Path $RepoRoot "02-env-setup\scripts\activate.ps1"
    if (Test-Path $activateScript) {
        . $activateScript
        Write-Success "Virtual environment activated"
    }
    else {
        Write-Warning-Custom "Activate script not found, assuming environment is ready"
    }

    Write-Info "Current directory: $(Get-Location)"
    Write-Info "WebApp root: $WebAppRoot"
    Write-Info "Log file: $LogFile"

    # ============================================================
    # Step 2: Start FastAPI Server
    # ============================================================
    Write-Step "Step 2: Starting FastAPI Server"

    Write-Info "Checking if port $Port is available..."
    $portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Warning-Custom "Port $Port is already in use. Trying to kill existing process..."
        $processId = $portInUse.OwningProcess | Select-Object -First 1
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }

    Write-Info "Starting uvicorn on port $Port..."
    Set-Location $WebAppRoot
    $env:PYTHONPATH = $WebAppRoot

    # Start uvicorn in background
    $uvicornProcess = Start-Process -FilePath "python" `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--port", $Port, "--log-level", "info" `
        -PassThru `
        -WindowStyle Hidden

    Write-Info "Waiting for server to start..."
    $maxWait = 15
    $waited = 0
    $serverReady = $false

    while ($waited -lt $maxWait -and -not $serverReady) {
        try {
            $response = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $serverReady = $true
            }
        }
        catch {
            Start-Sleep -Seconds 1
            $waited++
        }
    }

    if ($serverReady) {
        Write-Success "FastAPI server started successfully (PID: $($uvicornProcess.Id))"
    }
    else {
        throw "Failed to start FastAPI server within $maxWait seconds"
    }

    Start-Sleep -Seconds 2

    # ============================================================
    # Step 3: Initial System Status Check
    # ============================================================
    Write-Step "Step 3: Initial System Status Check"

    Invoke-ApiCall -Endpoint "/health" -Description "App health check"
    Invoke-ApiCall -Endpoint "/monitoring/status" -Description "Initial monitoring status"
    Invoke-ApiCall -Endpoint "/monitoring/metrics" -Description "Initial metrics (should be empty)"

    # ============================================================
    # Step 4: Generate Metrics by Calling MCP Tools
    # ============================================================
    Write-Step "Step 4: Generating Metrics (Calling MCP Tools)"

    Write-Info "Listing available MCP tools..."
    Invoke-ApiCall -Endpoint "/mcp/tools" -Description "List MCP tools"

    Write-Info "Calling 'read_file' tool 10 times..."
    for ($i = 1; $i -le 10; $i++) {
        $body = @{
            params = @{
                path = "test_samples\sample1.txt"
            }
        } | ConvertTo-Json

        $response = Invoke-ApiCall `
            -Method "POST" `
            -Endpoint "/mcp/actions/read_file" `
            -Body $body `
            -Description "Call read_file (attempt $i/10)"

        Start-Sleep -Milliseconds 100
    }

    Write-Info "Calling 'list_files' tool 5 times..."
    for ($i = 1; $i -le 5; $i++) {
        $body = @{
            params = @{
                directory = "test_samples"
                pattern = "*"
            }
        } | ConvertTo-Json

        $response = Invoke-ApiCall `
            -Method "POST" `
            -Endpoint "/mcp/actions/list_files" `
            -Body $body `
            -Description "Call list_files (attempt $i/5)"

        Start-Sleep -Milliseconds 100
    }

    Write-Success "Generated metrics from 15 API calls"

    # ============================================================
    # Step 5: View Collected Metrics
    # ============================================================
    Write-Step "Step 5: Viewing Collected Metrics"

    Invoke-ApiCall -Endpoint "/monitoring/metrics" -Description "View all metrics"
    Invoke-ApiCall -Endpoint "/monitoring/metrics?tool=read_file" -Description "View read_file metrics only"
    Invoke-ApiCall -Endpoint "/monitoring/status" -Description "System status with metrics"

    # ============================================================
    # Step 6: Health Check
    # ============================================================
    Write-Step "Step 6: Health Check"

    Start-Sleep -Seconds 3  # Wait for background health checker

    Invoke-ApiCall -Endpoint "/monitoring/health" -Description "View all server health"
    Invoke-ApiCall -Endpoint "/monitoring/health/file_server" -Description "View file_server health details"

    # ============================================================
    # Step 7: Reset Metrics (Optional)
    # ============================================================
    Write-Step "Step 7: Reset Metrics (Optional)"

    $resetBody = @{ confirm = $true } | ConvertTo-Json
    Invoke-ApiCall `
        -Method "POST" `
        -Endpoint "/monitoring/reset" `
        -Body $resetBody `
        -Description "Reset metrics"

    Invoke-ApiCall -Endpoint "/monitoring/metrics" -Description "View metrics after reset (should be empty)"

    # ============================================================
    # Step 8: Final Summary
    # ============================================================
    Write-Step "Step 8: Final Summary"

    Write-Host "`n" -NoNewline
    Write-Host "  Demo Summary:" -ForegroundColor Cyan
    Write-Info "- Started FastAPI server with monitoring enabled"
    Write-Info "- Generated 15 API calls (10x read_file, 5x list_files)"
    Write-Info "- Collected and viewed metrics"
    Write-Info "- Checked server health status"
    Write-Info "- Reset metrics successfully"
    Write-Host "`n"

    Write-Success "Demo completed successfully!"
    Write-Info "Full log saved to: $LogFile"

}
catch {
    Write-Error-Custom "Demo failed: $_"
    Write-Host "`nStack Trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
}
finally {
    # ============================================================
    # Cleanup
    # ============================================================
    Write-Step "Cleanup"

    if ($uvicornProcess -and -not $uvicornProcess.HasExited) {
        Write-Info "Stopping FastAPI server (PID: $($uvicornProcess.Id))..."
        Stop-Process -Id $uvicornProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Write-Success "Server stopped"
    }

    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
