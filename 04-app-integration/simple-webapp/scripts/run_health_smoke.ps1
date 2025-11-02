$ErrorActionPreference = 'Stop'
. "${PSScriptRoot}\..\..\..\02-env-setup\scripts\activate.ps1"

$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\"))
$logDir = Join-Path $repo "..\..\..\docs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $logDir "health_smoke_$ts.jsonl"

Push-Location $repo
try {
    Write-Host "Running FastAPI /health smoke test from $repo"
    # Ensure Python can import the 'app' package by adding repo to PYTHONPATH
    if ($env:PYTHONPATH) {
        $env:PYTHONPATH = "$repo;" + $env:PYTHONPATH
    } else {
        $env:PYTHONPATH = $repo
    }
    $result = python -u ".\tests_smoke\health_smoke.py" 2>&1 | Tee-Object -Variable Output
    $jsonLine = $Output | Select-Object -Last 1
    $jsonLine | Out-File -FilePath $logPath -Encoding utf8
    Write-Host "Smoke JSON: $jsonLine"
    Write-Host "Saved smoke test log to $logPath"
    if ($jsonLine -match '"ok":\s*true') {
        Write-Host "[OK] /health responded 200"
        exit 0
    } else {
        Write-Host "[FAIL] /health test did not return ok=true"
        exit 1
    }
}
finally {
    Pop-Location
}
