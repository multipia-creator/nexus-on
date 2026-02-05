#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

API_KEY="${NEXUS_API_KEY:-dev-key}"

echo "[1] health"
curl -s "http://localhost:8000/health" | python -m json.tool

echo "[2] metrics (head)"
curl -s "http://localhost:8000/metrics" | head -n 20

echo "[3] llm generate (optional)"
curl -s -X POST "http://localhost:8000/llm/generate"   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{"input":"한국어로 한 줄 공지문 예시를 작성해줘. 주제=세미나 공지"}' | python -m json.tool || true

echo "[4] create task"
RESP="$(curl -s -X POST "http://localhost:8000/excel-kakao"   -H "Content-Type: application/json"   -H "X-API-Key: ${API_KEY}"   -d '{"requested_by":"admin","payload":{"sheet_id":"demo","group_name":"CSD-공지","members":[{"name":"홍길동","phone":"+821012345678"},{"name":"김영희","phone":"+821099988877"}]}}')"
echo "$RESP" | python -m json.tool

TASK_ID="$(python - <<'PY'
import json,sys
print(json.loads(sys.stdin.read()).get('task_id',''))
PY
<<< "$RESP")"
if [ -z "$TASK_ID" ]; then
  echo "task_id missing"; exit 1
fi

echo "[5] poll task"
for i in {1..30}; do
  OUT="$(curl -s "http://localhost:8000/tasks/${TASK_ID}" -H "X-API-Key: ${API_KEY}")"
  STATUS="$(python - <<'PY'
import json,sys
print(json.loads(sys.stdin.read()).get('status',''))
PY
<<< "$OUT")"
  echo "  - $i status=$STATUS"
  if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "failed" ]; then
    echo "$OUT" | python -m json.tool
    exit 0
  fi
  sleep 1
done

echo "timeout"
exit 2
