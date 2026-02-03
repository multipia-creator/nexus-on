#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Please edit .env and set API keys."
fi

mkdir -p data/gdrive_mirror
docker compose -f docker/docker-compose.nexus.yml up -d --build
echo "UI: http://localhost:8000/ui"
