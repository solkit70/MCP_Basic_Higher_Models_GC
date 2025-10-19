# One-click WebSocket echo demo
# - Starts local echo server
# - Runs client to send/receive a test message
# - Captures outputs into logs

$ErrorActionPreference = 'Stop'
. "${PSScriptRoot}\..\..\02-env-setup\scripts\activate.ps1"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\"))
$logsDir = Join-Path $repoRoot "logs"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
$stamp = Get-Date -Format yyyyMMdd_HHmmss
$serverLog = Join-Path $logsDir "echo_server_$stamp.out.txt"
$serverErr = Join-Path $logsDir "echo_server_$stamp.err.txt"
$clientLog = Join-Path $logsDir "echo_client_$stamp.txt"

# Start server (background)
$serverScript = Join-Path $repoRoot "clients\python\ws_echo_server.py"
$server = Start-Process -FilePath "python" -ArgumentList @("`"$serverScript`"", "--host", "127.0.0.1", "--port", "9000") -NoNewWindow -PassThru -RedirectStandardOutput $serverLog -RedirectStandardError $serverErr
Start-Sleep -Seconds 1

try {
  # Run client echo test
  $clientScript = Join-Path $repoRoot "clients\python\ws_client.py"
  $msg = "hello-echo-$(Get-Date -Format HHmmss)"
  python $clientScript "ws://127.0.0.1:9000" --message "$msg" --timeout 3.0 | Tee-Object -FilePath $clientLog
}
finally {
  # Stop server
  if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force }
}

Write-Host "Echo demo completed." -ForegroundColor Green
Write-Host "Server stdout: $serverLog"
Write-Host "Server stderr: $serverErr"
Write-Host "Client log: $clientLog"
