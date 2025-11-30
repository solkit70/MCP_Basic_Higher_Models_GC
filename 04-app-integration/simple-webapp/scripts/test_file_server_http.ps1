# Test File Server via HTTP API
# Tests the file_server.py integration with FastAPI

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "File Server HTTP Integration Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# Test 1: Health Check
Write-Host "[Test 1] Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mcp/health" -Method Get
    Write-Host "  OK Status: $($response.status)" -ForegroundColor Green
    Write-Host "  OK Server Type: $($response.server_type)" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: List Tools
Write-Host "[Test 2] List Tools" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mcp/tools" -Method Get
    Write-Host "  OK Found $($response.tools.Count) tools:" -ForegroundColor Green
    foreach ($tool in $response.tools) {
        Write-Host "    - $($tool.name): $($tool.description)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Read File (sample1.txt)
Write-Host "[Test 3] Read File (sample1.txt)" -ForegroundColor Yellow
$samplePath = "C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\05-build-server\test_samples\sample1.txt"
$body = @{
    path = $samplePath
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mcp/actions/read_file" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK File read successful" -ForegroundColor Green
    Write-Host "  OK Latency: $($response.latency_ms) ms" -ForegroundColor Green
    $firstLine = ($response.result -split "`n")[0]
    Write-Host "  OK First line: $firstLine" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: List Files (test_samples directory)
Write-Host "[Test 4] List Files (test_samples/)" -ForegroundColor Yellow
$testDir = "C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\05-build-server\test_samples"
$body = @{
    directory = $testDir
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mcp/actions/list_files" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK Files listed successfully" -ForegroundColor Green
    Write-Host "  OK Latency: $($response.latency_ms) ms" -ForegroundColor Green
    $files = $response.result | ConvertFrom-Json
    Write-Host "  OK Found $($files.Count) files/folders:" -ForegroundColor Green
    foreach ($file in $files) {
        $icon = if ($file.type -eq "directory") { "[DIR]" } else { "[FILE]" }
        Write-Host "    $icon $($file.name) ($($file.size) bytes)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: List Files with Pattern (*.txt)
Write-Host "[Test 5] List Files (pattern: *.txt)" -ForegroundColor Yellow
$body = @{
    directory = $testDir
    pattern = "*.txt"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mcp/actions/list_files" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  OK Files listed successfully" -ForegroundColor Green
    Write-Host "  OK Latency: $($response.latency_ms) ms" -ForegroundColor Green
    $files = $response.result | ConvertFrom-Json
    Write-Host "  OK Found $($files.Count) .txt files:" -ForegroundColor Green
    foreach ($file in $files) {
        Write-Host "    [FILE] $($file.name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Error Case - Nonexistent File
Write-Host "[Test 6] Error Test (nonexistent file)" -ForegroundColor Yellow
$body = @{
    path = "C:\nonexistent\file.txt"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/mcp/actions/read_file" -Method Post -Body $body -ContentType "application/json"
    Write-Host "  ERROR: Should have failed but succeeded" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  OK Expected error occurred (HTTP $statusCode)" -ForegroundColor Green
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Test Completed!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
