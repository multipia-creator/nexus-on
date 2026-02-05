# ROADMAP (World-class Top-tier)

이 문서는 “현재 P0(동작) → P1(안정/확장) → P2(제품화)” 로드맵을 담습니다.

## P0 (지금: 로컬 상주형 동작)
- [x] 단일 UI(`/ui`) + SSE 스트림 + Approvals(2PC)
- [x] LLM 게이트웨이(Claude Sonnet 4.5 포함)
- [x] YouTube 검색/재생(큐 포함)
- [x] RAG 폴더 ingest + HWP 외부 변환 계약

## P1 (월드베스트를 위한 ‘체감 품질’)
1) 자율 에이전트 신뢰성
- 리포트 스키마(done/next/blocked/undo/risk/rationale/ui_hint) 엄격화
- 실패 시 “자동 되돌림(undo)” 경로를 기본 제공
- Tool 실행 결과의 idempotency + dedupe 강화(tenant+correlation_id)

2) RAG 품질
- 문서 정규화 파이프라인(형식별 extractor) 표준화
- chunking: 섹션/헤더 기반, 테이블/슬라이드 구조 메타 보존
- 하이브리드 검색(BM25+벡터) + rerank(LLM or local cross-encoder)
- “학습(ingest) 03:00”은 실제로는 인덱스 업데이트(증분)로 명확히 정의

3) UI/UX
- 캐릭터 스테이지(음성/자막) ↔ Dock ↔ Dashboard 동기화(이미 LOCKED v1.1)
- 작업 캔버스(Plan/To-do/Artifacts) 도입: sidecar command 결과를 캔버스로 핸드오프
- ‘놀아주는 기능’(Play 모드): 대화/퀴즈/가벼운 작업/목표 달성형 미션(친밀도 엔진 연동)

4) 로컬 운영성
- Windows 서비스화(부팅 자동 실행, 장애 자동 재시작)
- 로컬 보안(DLP/비밀키) + 파일 접근 범위(allowlist) + 감사 로그 뷰어
- 오프라인 모드(로컬 LLM fallback: llama.cpp/Ollama 옵션)

## P2 (SaaS 제품화)
- 멀티테넌트 콘솔(Org/Project, 비용, 감사, 키 관리)
- 커넥터(Gmail/GCal/Drive) 정식 OAuth + 권한 스코프 + 승인 UX
- 레이트리밋/서킷브레이커/비용 예산(soft/hard) 운영 자동화
