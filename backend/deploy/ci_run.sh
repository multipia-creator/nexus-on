#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[CI] bring up services"
docker compose -f docker/docker-compose.nexus.yml up --build -d

echo "[CI] wait for supervisor health"
for i in {1..60}; do
  if curl -fsS "http://localhost:8000/health" >/dev/null; then
    echo "[CI] supervisor up"
    break
  fi
  sleep 2
done

echo "[CI] run ruff check .
mypy shared nexus_supervisor agents || true
pytest"
python -m pip install --upgrade pip >/dev/null
pip install -r requirements-dev.txt >/dev/null
ruff check .
mypy shared nexus_supervisor agents || true
pytest

echo "[CI] tear down"
docker compose -f docker/docker-compose.nexus.yml down -v
