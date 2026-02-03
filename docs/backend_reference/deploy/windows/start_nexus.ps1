# Run once (PowerShell) from nexus_backend_p0
# Requires: Docker Desktop running
docker compose -f docker/docker-compose.nexus.yml up -d --build
Write-Host "UI: http://localhost:8000/ui"
