# MCP Web Application - Docker Integration Test Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MCP Web Application - Docker Integration Tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [hashtable]$Body = $null
    )

    Write-Host "[$Name]" -ForegroundColor Yellow
    try {
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10
        } else {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $Url -Method Post -Body $jsonBody -ContentType "application/json" -TimeoutSec 10
        }

        Write-Host "  OK Test passed" -ForegroundColor Green
        return @{
            Success = $true
            Response = $response
        }
    } catch {
        Write-Host "  FAIL Test failed: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

# Test 1: Health Check
$result = Test-Endpoint -Name "Test 1: Health Check" -Method "GET" -Url "$baseUrl/mcp/health"
if ($result.Success) {
    Write-Host "    Status: $($result.Response.status)" -ForegroundColor Cyan
    Write-Host "    Server Type: $($result.Response.server_type)" -ForegroundColor Cyan
    $testsPassed++
} else {
    $testsFailed++
}
Write-Host ""

# Test 2: List Tools
$result = Test-Endpoint -Name "Test 2: List Tools" -Method "GET" -Url "$baseUrl/mcp/tools"
if ($result.Success) {
    Write-Host "    Tools count: $($result.Response.tools.Count)" -ForegroundColor Cyan
    foreach ($tool in $result.Response.tools) {
        Write-Host "    - $($tool.name)" -ForegroundColor Gray
    }
    $testsPassed++
} else {
    $testsFailed++
}
Write-Host ""

# Test 3: Read File
$readFileBody = @{
    params = @{
        path = "/app/test_samples/sample1.txt"
    }
}
$result = Test-Endpoint -Name "Test 3: Read File" -Method "POST" -Url "$baseUrl/mcp/actions/read_file" -Body $readFileBody
if ($result.Success) {
    $textLength = $result.Response.data.text.Length
    Write-Host "    File size: $textLength bytes" -ForegroundColor Cyan
    Write-Host "    Latency: $($result.Response.latency_ms) ms" -ForegroundColor Cyan
    $testsPassed++
} else {
    $testsFailed++
}
Write-Host ""

# Test 4: List Files
$listFilesBody = @{
    params = @{
        directory = "/app/test_samples"
        pattern = "*"
    }
}
$result = Test-Endpoint -Name "Test 4: List Files" -Method "POST" -Url "$baseUrl/mcp/actions/list_files" -Body $listFilesBody
if ($result.Success) {
    $files = $result.Response.data.text | ConvertFrom-Json
    Write-Host "    Files found: $($files.Count)" -ForegroundColor Cyan
    foreach ($file in $files) {
        Write-Host "    - $($file.name) ($($file.size) bytes)" -ForegroundColor Gray
    }
    Write-Host "    Latency: $($result.Response.latency_ms) ms" -ForegroundColor Cyan
    $testsPassed++
} else {
    $testsFailed++
}
Write-Host ""

# Test 5: List Files with Pattern
$listFilesPatternBody = @{
    params = @{
        directory = "/app/test_samples"
        pattern = "*.txt"
    }
}
$result = Test-Endpoint -Name "Test 5: List Files (pattern: *.txt)" -Method "POST" -Url "$baseUrl/mcp/actions/list_files" -Body $listFilesPatternBody
if ($result.Success) {
    $files = $result.Response.data.text | ConvertFrom-Json
    Write-Host "    .txt files found: $($files.Count)" -ForegroundColor Cyan
    $testsPassed++
} else {
    $testsFailed++
}
Write-Host ""

# Test 6: Error Handling (non-existent file)
$errorTestBody = @{
    params = @{
        path = "/app/test_samples/nonexistent.txt"
    }
}
$result = Test-Endpoint -Name "Test 6: Error Handling" -Method "POST" -Url "$baseUrl/mcp/actions/read_file" -Body $errorTestBody
if (-not $result.Success) {
    Write-Host "  OK Error correctly handled" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  FAIL Should have returned an error" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
Write-Host "Total:  $($testsPassed + $testsFailed)" -ForegroundColor Cyan
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed. Please check the logs." -ForegroundColor Red
    exit 1
}
