# Start local Meilisearch for Job Discovery dev (port 7700).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$bin = Join-Path $root "bin\meilisearch.exe"
$dataDir = Join-Path $root "data\meilisearch"

if (-not (Test-Path $bin)) {
  Write-Error "Missing $bin — download meilisearch-windows-amd64.exe from GitHub releases into backend/bin/meilisearch.exe"
}

if (-not (Test-Path $dataDir)) {
  New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

Set-Location $dataDir
Write-Host "Starting Meilisearch on http://127.0.0.1:7700 (master key: dev_key)"
& $bin --master-key dev_key --http-addr "127.0.0.1:7700"
