# NEXUS Architecture v1.8 (Gemini First + OpenAI Optional)

구성요소
- Supervisor (FastAPI): 작업 생성/조회/콜백 수신, LLM 테스트 엔드포인트
- RabbitMQ: task queue (AMQP)
- Agent Worker (Python): 큐 소비, 작업 처리, 결과 콜백
- LLM Provider Layer: Gemini 기본, OpenAI 옵션

기본 흐름(Vertical Slice)
1) Client → Supervisor `POST /excel-kakao`
2) Supervisor: task_id 생성, status=queued 저장, 큐 publish
3) Agent: 큐 consume → status=running 콜백(선택) → 처리 → succeeded/failed 콜백
4) Client → Supervisor `GET /tasks/{task_id}` 로 결과 조회

LLM 호출 원칙
- `LLM_PROVIDER=gemini` 기본 (GEMINI_API_KEY 필요)
- `LLM_PROVIDER=openai` 옵션 (OPENAI_API_KEY 필요)
- 키가 없을 경우 개발 편의상 degrade(LLM_DISABLED)로 처리(운영에서는 키 필수 권장)

포트
- Supervisor: 8000
- RabbitMQ: 5672, 15672

운영 확장(후속)
- Task Store: in-memory → Redis/Postgres
- Retry/DLQ: 계약 문서(docs/CONTRACT.md) 기준으로 적용
- Agent: task_type 별 수평 확장
