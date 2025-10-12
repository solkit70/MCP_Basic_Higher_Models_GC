# PowerShell 5.1 compatible setup script
# Creates .venv, upgrades pip, installs requirements, validates environment.

$ErrorActionPreference = 'Stop'

function Ensure-ExecutionPolicy {
    try {
        $policy = Get-ExecutionPolicy -Scope Process
        Write-Host "Process ExecutionPolicy: $policy"
    } catch {
        Write-Warning "Unable to read ExecutionPolicy. You may need to run PowerShell as Administrator."
    }
}

function Ensure-Venv {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
    Set-Location $repoRoot

    $python = "py"
    $venvDir = Join-Path $repoRoot ".venv"

    if (-not (Test-Path $venvDir)) {
        Write-Host "Creating venv at $venvDir"
        & $python -3.11 -m venv .venv
    } else {
        Write-Host "Venv already exists at $venvDir"
    }

    $activate = Join-Path $venvDir "Scripts\Activate.ps1"
    Write-Host "Activating venv..."
    . $activate

    Write-Host "Upgrading pip..."
    python -m pip install --upgrade pip
}

function Install-Requirements {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
    $req = Join-Path $repoRoot "02-env-setup\requirements.txt"
    $reqDev = Join-Path $repoRoot "02-env-setup\requirements-dev.txt"

    if (Test-Path $req) { pip install -r $req }
    if (Test-Path $reqDev) { pip install -r $reqDev }
}

function Validate-Env {
    $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
    $tool = Join-Path $repoRoot "02-env-setup\tools\env_check.py"
    if (Test-Path $tool) {
        Write-Host "Running env_check.py..."
        python $tool
    }

    Write-Host "Saving package snapshot to docs/pip-freeze.txt"
    $freezeOut = Join-Path $repoRoot "docs\pip-freeze_$(Get-Date -Format yyyyMMdd_HHmmss).txt"
    pip freeze | Out-File -FilePath $freezeOut -Encoding utf8

    Write-Host "Installed packages:"
    pip list
}

Ensure-ExecutionPolicy
Ensure-Venv
Install-Requirements
Validate-Env

Write-Host "Setup completed successfully." -ForegroundColor Green
