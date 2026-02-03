# PowerShell bootstrap for Windows
Set-Location (Split-Path $MyInvocation.MyCommand.Path)\..
if (!(Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "Created .env. Please edit and set keys."
}
New-Item -ItemType Directory -Force -Path data\gdrive_mirror | Out-Null
docker compose -f docker\docker-compose.nexus.yml up -d --build
Write-Host "UI: http://localhost:8000/ui"
