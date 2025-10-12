# PowerShell 5.1: Activate local venv
$venvPath = Join-Path $PSScriptRoot "..\..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating venv at: $venvPath"
    . $venvPath
} else {
    Write-Warning "Venv not found. Run setup.ps1 first."
}
