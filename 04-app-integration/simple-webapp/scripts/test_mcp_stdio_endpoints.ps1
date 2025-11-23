# Test MCP endpoints with stdio mode
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$appRoot = Join-Path $repoRoot "04-app-integration\simple-webapp"

Write-Host "=" * 80
Write-Host "Testing MCP Stdio Endpoints"
Write-Host "=" * 80

# Start server in background
Write-Host "`n[1] Starting FastAPI server..."
cd $appRoot
$env:PYTHONPATH = $appRoot
$serverProc = Start-Process -FilePath "$repoRoot\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" `
    -PassThru `
    -WindowStyle Hidden

Start-Sleep -Seconds 2

try {
    # Test /mcp/health
    Write-Host "`n[2] Testing GET /mcp/health..."
    $health = Invoke-RestMethod -Uri "http://localhost:8000/mcp/health" -Method Get
    Write-Host "[SUCCESS] Health: $($health | ConvertTo-Json -Compress)"

    # Test /mcp/tools
    Write-Host "`n[3] Testing GET /mcp/tools..."
    $tools = Invoke-RestMethod -Uri "http://localhost:8000/mcp/tools" -Method Get
    Write-Host "[SUCCESS] Tools: $($tools | ConvertTo-Json -Compress)"

    # Test /mcp/actions/echo_tool
    Write-Host "`n[4] Testing POST /mcp/actions/echo_tool..."
    $body = @{ text = "Hello from FastAPI via stdio!" } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "http://localhost:8000/mcp/actions/echo_tool" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    Write-Host "[SUCCESS] Result: $($result | ConvertTo-Json -Compress)"

    Write-Host "`n" + "=" * 80
    Write-Host "All endpoint tests passed!"
    Write-Host "=" * 80

} finally {
    Write-Host "`n[CLEANUP] Stopping server..."
    Stop-Process -Id $serverProc.Id -Force
    Write-Host "[DONE]"
}
