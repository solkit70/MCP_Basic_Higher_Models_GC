# Run FastAPI app via uvicorn
$ErrorActionPreference = 'Stop'
. "${PSScriptRoot}\..\..\..\02-env-setup\scripts\activate.ps1"

$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\"))
$scriptRootDisplay = $PSScriptRoot
Write-Host "PSScriptRoot: $scriptRootDisplay"
Write-Host "Resolved simple-webapp path: $repo"
$envPath = Join-Path $repo "config\.env"

# Prepare optional --env-file argument for uvicorn
$envFileArgs = @()
if (Test-Path $envPath) {
	Write-Host "Loading .env from $envPath"
	$envFileArgs = @('--env-file', $envPath)
}

# Default port if not provided as environment variable
$port = 8000
if ($env:PORT) { $port = [int]$env:PORT }

Write-Host "Starting uvicorn on port $port"
Write-Host "Working directory: $repo"
# Ensure child processes (like uvicorn reloader) can import the 'app' package
$env:PYTHONPATH = $repo
Write-Host "PYTHONPATH set to: $env:PYTHONPATH"
Push-Location $repo
try {
	# With CWD at simple-webapp, the 'app' package is importable.
	$appDir = $repo
	python -m uvicorn "app.main:app" --port $port --log-level info --app-dir $appDir @envFileArgs
}
finally {
	Pop-Location
}
