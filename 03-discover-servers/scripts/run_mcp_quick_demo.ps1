$ErrorActionPreference = 'Stop'
. "${PSScriptRoot}\..\..\02-env-setup\scripts\activate.ps1"

$clientPath = Join-Path $PSScriptRoot "..\clients\python\mcp_quick_client.py"
$logDir = Join-Path $PSScriptRoot "..\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$stdoutLog = Join-Path $logDir "mcp_quick_stdout_$ts.jsonl"
$stderrLog = Join-Path $logDir "mcp_quick_stderr_$ts.log"

Write-Host "Running MCP quick client: $clientPath"
# Determine python executable (prefer venv python)
$pyExe = "$($env:VIRTUAL_ENV)\Scripts\python.exe"
if (-not (Test-Path $pyExe)) {
    if ($env:PYTHONEXECUTABLE -and (Test-Path $env:PYTHONEXECUTABLE)) {
        $pyExe = $env:PYTHONEXECUTABLE
    } else {
        $pyExe = "python"
    }
}

# Use ProcessStartInfo to capture stdout/stderr without PowerShell erroring on stderr
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $pyExe
$psi.Arguments = "-u `"$clientPath`""
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$null = $proc.Start()
$stdOutText = $proc.StandardOutput.ReadToEnd()
$stdErrText = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()
$exitCode = $proc.ExitCode
Set-Content -LiteralPath $stdoutLog -Value $stdOutText -Encoding UTF8
Set-Content -LiteralPath $stderrLog -Value $stdErrText -Encoding UTF8

if ($exitCode -eq 0) {
    Write-Host "[OK] Client finished. Logs:"
    Write-Host "  stdout: $stdoutLog"
    Write-Host "  stderr: $stderrLog"
    exit 0
} else {
    Write-Host "[FAIL] Client exited with code $exitCode"
    Write-Host "  stdout: $stdoutLog"
    Write-Host "  stderr: $stderrLog"
    exit $exitCode
}
