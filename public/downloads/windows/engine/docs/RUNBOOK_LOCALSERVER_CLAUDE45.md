# NEXUS 로컬 상주형 서버 (Claude Sonnet 4.5) 최종 실행 가이드

목표: 내 PC에 설치하여 NEXUS가 항상 켜져 있고, 캐릭터 비서 UI(대화형 채팅) + 자율 에이전트 + YouTube + RAG(구글 드라이브 미러)까지 동작하는 상태를 만든다.

---

## 1) 구성 요약
- Backend(슈퍼바이저): FastAPI + SSE(/agent/reports/stream) + Sidecar(/sidecar/command) + Approvals
- Frontend: `/ui` 단일 HTML(백엔드에 내장)
- Queue/Store: RabbitMQ + Redis
- YouTube: Data API(검색) + iframe embed(재생)
- RAG: 로컬 폴더 ingest → NaiveRAG(초기형) + HWP 외부 변환 파이프라인

---

## 2) 준비물
1) Docker Desktop 설치(Windows/macOS/Linux)
2) Anthropic API Key (Claude Sonnet 4.5)
3) (선택) YouTube Data API Key
4) (권장) 구글 드라이브 미러링 도구(rclone) 또는 Drive Desktop 동기화

---

## 3) 초기 설정
### 3.1 .env 설정
`nexus_backend_p0/.env.example` → `.env`로 복사 후 아래를 채운다.

필수:
- `NEXUS_API_KEY`
- `LLM_PRIMARY_PROVIDER=anthropic`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_MODEL=claude-sonnet-4-5-20250929`

선택(YouTube 검색):
- `YOUTUBE_API_KEY`

선택(RAG 자동 ingest):
- `RAG_AUTO_INGEST_ENABLED=true`
- `RAG_AUTO_INGEST_PATH=/data/gdrive_mirror`
- `RAG_AUTO_INGEST_HOUR=3`
- `RAG_AUTO_INGEST_MINUTE=0`

### 3.2 구글 드라이브 미러링 폴더
컨테이너는 호스트의 `nexus_backend_p0/data`를 `/data`로 마운트합니다.
- 권장 경로: `nexus_backend_p0/data/gdrive_mirror`
- 이 폴더로 Google Drive 파일이 내려오도록 설정합니다.

권장 방식:
- Drive Desktop(Windows/macOS)로 특정 폴더를 로컬 동기화
- 또는 `rclone sync`를 크론/작업 스케줄러로 주기 실행

---

## 4) 실행
리포지토리 루트(`nexus_backend_p0`)에서:

```bash
docker compose -f docker/docker-compose.nexus.yml up --build
```

브라우저:
- UI: `http://localhost:8000/ui`
- Health: `http://localhost:8000/health`

---

## 5) 기능별 검증 시나리오(권장)
1) SSE 연결 확인
- UI를 열고, 새 메시지 입력 → 응답이 “Worklog/Asks/Autopilot”에 반영되는지

2) Approvals(RED 흐름)
- 외부 공유/전송 타입 커맨드 요청 → Ask 생성 → 승인 버튼 → SSE 후속 report로 상태 전이 확인

3) YouTube
- `youtube.search` → 결과 표시
- `youtube.queue.add` → 큐 반영
- `youtube.queue.next` → 재생 프레임 변경

4) RAG
- `data/gdrive_mirror`에 pdf/docx/txt 넣기
- 수동: `rag.folder.ingest` 실행
- 자동: 03:00 KST 스케줄(테스트 시 임시로 시간을 변경하여 확인)

5) HWP
- `.hwp`는 ingest 시 pending 처리됩니다.
- 같은 basename의 `.pdf` 또는 `.txt`를 생성해 폴더에 두면 정상 인덱싱됩니다.

---

## 6) Always-on(상시 실행) 운영
### Windows (권장)
- Docker Desktop을 “로그인 시 자동 시작”으로 설정
- 작업 스케줄러에서 부팅 시 다음 명령 실행:
  - `docker compose -f docker/docker-compose.nexus.yml up -d`

### Linux (systemd)
- `deploy/systemd/nexus.service`를 참조해 유닛 등록 후 enable

---

## 7) 트러블슈팅
- UI가 멈춘 것처럼 보이면: SSE가 끊겼는지 확인(브라우저 개발자 도구)
- YouTube 검색 실패: `YOUTUBE_API_KEY` 유효성/쿼터 확인
- RAG 자동 ingest가 안 도는 경우:
  - `.env`에서 `RAG_AUTO_INGEST_ENABLED=true` 확인
  - 컨테이너에 `/data/gdrive_mirror`가 마운트되었는지 확인
- HWP는 “변환 전”에는 정상적으로 텍스트 추출이 불가(의도된 동작)
