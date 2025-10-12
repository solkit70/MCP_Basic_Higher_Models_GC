# Save current package snapshot to docs/pip-freeze.txt (timestamped)
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
$target = Join-Path $repoRoot "docs\pip-freeze_$(Get-Date -Format yyyyMMdd_HHmmss).txt"

if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Warning "pip not available. Activate venv first: ./02-env-setup/scripts/activate.ps1"
    return
}

pip freeze | Out-File -FilePath $target -Encoding utf8
Write-Host "Saved to $target"
