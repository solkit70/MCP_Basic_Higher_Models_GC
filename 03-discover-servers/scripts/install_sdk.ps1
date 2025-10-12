# Install MCP Python SDK(s) [검증 필요]
# 목적: 재현 가능한 버전 고정 설치. 공식 패키지명 확인 후 아래 라인 수정.

$ErrorActionPreference = 'Stop'

. "${PSScriptRoot}\..\..\02-env-setup\scripts\activate.ps1"

Write-Host "Installing MCP-related SDK packages..."

# TODO: Replace with official packages once confirmed
# Minimal dependencies for connectivity/tests
pip install websockets==12.0 httpx==0.27.2 pydantic==2.9.2

Write-Warning "[검증 필요] 공식 MCP Python SDK 패키지명을 확인 후 설치 라인을 업데이트하세요."
Write-Host "Done."
