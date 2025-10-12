# Health check runner for MCP server profiles (ws/stdio basic validations)
$ErrorActionPreference = 'Stop'

. "${PSScriptRoot}\..\..\02-env-setup\scripts\activate.ps1"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\"))
$configPath = Join-Path $repoRoot "configs\server_profiles.json"
$logsDir = Join-Path $repoRoot "logs"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
$logFile = Join-Path $logsDir ("health_{0}.txt" -f (Get-Date -Format yyyyMMdd_HHmmss))

function Log($msg) { $msg | Tee-Object -FilePath $logFile -Append }

Log "=== M3 Health Check Start: $(Get-Date) ==="
Log "Config: $configPath"

if (-not (Test-Path $configPath)) { throw "Config not found: $configPath" }

$json = Get-Content $configPath -Raw | ConvertFrom-Json
$profiles = $json.profiles

foreach ($p in $profiles) {
  if (-not $p.enabled) { Log "[SKIP] $($p.name) (enabled=false)"; continue }
  Log "-- Profile: $($p.name) | type=$($p.type) --"

  if ($p.type -eq 'stdio') {
    if (-not $p.exec_path) { Log "[ERROR] exec_path missing"; continue }
    if (Test-Path $p.exec_path) {
      Log "[OK] exec_path exists: $($p.exec_path)"
    } else {
      Log "[ERROR] exec_path not found: $($p.exec_path)"
      continue
    }
    Log "[INFO] Would run (dry-run): `"$($p.exec_path)`" $($p.args -join ' ')"
  }
  elseif ($p.type -eq 'ws') {
    if (-not $p.uri) { Log "[ERROR] uri missing"; continue }
    try {
      $uri = [System.Uri]::new($p.uri)
      Log "[OK] URI parsed: $($uri.AbsoluteUri)"
      # Basic DNS check
      $dnsHost = $uri.DnsSafeHost
      try { Resolve-DnsName -Name $dnsHost -ErrorAction Stop | Out-Null; Log "[OK] DNS resolved: $dnsHost" }
      catch { Log "[WARN] DNS resolve failed or local: $dnsHost | $_" }
      Log "[INFO] Headers: $($p.headers | ConvertTo-Json -Compress)"
      Log "[INFO] Would connect (dry-run) to $($uri.Scheme)://$($dnsHost):$($uri.Port)"
    } catch {
      Log "[ERROR] Invalid URI: $($p.uri) | $_"
    }
  }
  else {
    Log "[ERROR] Unknown profile type: $($p.type)"
  }
}

Log "=== M3 Health Check End: $(Get-Date) ==="
Write-Host "Health check finished. Log: $logFile" -ForegroundColor Green
