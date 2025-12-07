# MCP Web Application - Build and Run Script
# This script builds the Docker image and runs the container

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MCP Web Application - Docker Build and Run" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Stop"

# Change to project root directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "[1/5] Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose -f 06-deployment/docker-compose.yml down 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Existing containers removed" -ForegroundColor Green
} else {
    Write-Host "  INFO No existing containers to remove" -ForegroundColor Gray
}
Write-Host ""

Write-Host "[2/5] Building Docker image..." -ForegroundColor Yellow
docker-compose -f 06-deployment/docker-compose.yml build
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  OK Image built successfully" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Starting container..." -ForegroundColor Yellow
docker-compose -f 06-deployment/docker-compose.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR Failed to start container" -ForegroundColor Red
    exit 1
}
Write-Host "  OK Container started" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] Waiting for application to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$isReady = $false

while ($retryCount -lt $maxRetries -and -not $isReady) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/mcp/health" -Method Get -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $isReady = $true
            Write-Host "  OK Application is ready!" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Write-Host "  Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    }
}

if (-not $isReady) {
    Write-Host "  ERROR Application failed to start within timeout" -ForegroundColor Red
    Write-Host ""
    Write-Host "Container logs:" -ForegroundColor Yellow
    docker-compose -f 06-deployment/docker-compose.yml logs
    exit 1
}
Write-Host ""

Write-Host "[5/5] Running health checks..." -ForegroundColor Yellow
try {
    # Health check
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/mcp/health" -Method Get
    Write-Host "  OK Health: $($healthResponse.status)" -ForegroundColor Green

    # List tools
    $toolsResponse = Invoke-RestMethod -Uri "http://localhost:8000/mcp/tools" -Method Get
    Write-Host "  OK Tools: $($toolsResponse.tools.Count) tools available" -ForegroundColor Green
    foreach ($tool in $toolsResponse.tools) {
        Write-Host "    - $($tool.name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  WARNING Health check completed with warnings" -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/mcp/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:     docker-compose -f 06-deployment/docker-compose.yml logs -f" -ForegroundColor Gray
Write-Host "  Stop:          docker-compose -f 06-deployment/docker-compose.yml down" -ForegroundColor Gray
Write-Host "  Restart:       docker-compose -f 06-deployment/docker-compose.yml restart" -ForegroundColor Gray
Write-Host ""
