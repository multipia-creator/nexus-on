# NEXUS P0 Local UI (Zero-build)

이 문서는 로컬 PC(개발/데모)에서 **캐릭터 비서 채팅 + 자율 에이전트(보고 스트림) + 유튜브 검색/재생**을 빠르게 검증하기 위한 최소 실행 가이드입니다.

## 1) 실행

1. `./.env` 생성
   - `.env.example`를 복사 후, 최소 `NEXUS_API_KEY`, `REDIS_URL`을 설정합니다.
   - 유튜브 기능을 쓰려면 `YOUTUBE_API_KEY`를 추가합니다.

2. Redis 실행(권장)
   - Docker가 있다면 `docker/docker-compose.nexus.yml`에서 redis 서비스만 띄워도 됩니다.
   - 또는 로컬 redis를 `6379`로 실행합니다.

3. Supervisor 실행
   - `pip install -r nexus_supervisor/requirements.txt`
   - `uvicorn nexus_supervisor.app:app --host 0.0.0.0 --port 8000`

## 2) 접속

브라우저에서 `http://localhost:8000/` 접속.

- 상단에 `X-API-Key`(=NEXUS_API_KEY) 입력
- `x-org-id`, `x-project-id`는 기본값(`default/default`) 그대로 테스트 가능
- **Connect SSE** 버튼을 누르면 Dashboard가 실시간 갱신됩니다.

## 3) 유튜브

채팅 입력창에서:

- `/yt lo-fi` → `youtube.search` 실행(검색 결과가 YouTube 패널에 뜸)
- 결과의 **Play** 버튼 → `youtube.play` 실행(iframe embed)

`YOUTUBE_API_KEY` 미설정 시에는 YELLOW 성격의 보고/Ask로 처리됩니다.

## 4) 보안 메모

로컬 Zero-build UI는 **EventSource 제한(헤더 미지원)** 때문에 SSE 연결에 `api_key`/`org_id`/`project_id`를 query로 전달합니다.

- 운영(SaaS) 환경에서는 반드시 **헤더 기반**으로 통일하고,
- UI는 빌드된 프론트엔드에서 `Authorization`/cookie 기반 세션을 권장합니다.
