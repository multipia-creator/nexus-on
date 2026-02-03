#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/docker"

echo "[NEXUS] docker compose up (build)..."
docker compose -f docker-compose.nexus.yml up --build -d

echo "[NEXUS] done."
echo "Supervisor: http://localhost:8000/docs"
echo "Metrics:    http://localhost:8000/metrics"
echo "RabbitMQ:   http://localhost:15672 (guest/guest)"
