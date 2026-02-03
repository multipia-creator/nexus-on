# NEXUS 운영 리허설 스코어카드 (v6.22 / PR-08 자동 생성)

환경
- 날짜/시간(UTC): 2026-01-31 09:40:33
- 배포 버전: 6.22.0
- 실행 환경(단일/멀티 노드, Redis 유무): single+redis
- 사용 Provider(우선/옵션): gemini-first

0. Baseline Governance
#### Baseline Governance Status
- 2인 승인(require_two_person): True
- 승인 baseline 존재: True
- candidate 존재: True
- 마지막 승인(UTC): 2026-01-31T09:29:53Z
- 승인자: admin / ops-lead
- baseline sha256: b574c4682b4b…

A. 30분 스모크
1) LLM 호출/응답: NG
2) cost ledger 기록: NG
3) finops_report 생성: MANUAL
- 증적: logs/finops_rehearsal.md 존재 여부를 확인
4) 알림 배선: MANUAL
- 증적: Slack/Teams 수신 확인(웹훅은 외부 시스템)

B. 2시간 리허설
5) Dedupe hit 확인: NG
6) 태깅(team/project) 분리: NG
7) 저강도 부하(p50/p95, fail율): MANUAL
- 증적: tools/rehearsal_load_test.py 출력 기록

D. 캐릭터 리허설 (하드 게이트)
10) GoldenSet 자동채점: OK
- 평균 점수/케이스: 100.0/60
- 커버리지(필수 prefix): OK (missing=[])
- 카테고리 수: 13
- 베이스라인 비교: OK
- 증적(out): logs/character_rehearsal_evidence.jsonl (rc=0)
- 요약(summary): logs/character_rehearsal_summary.json

C. 1일 리허설
8) 크론 스케줄 동작: MANUAL
9) 장애–복구 라운드트립: MANUAL

최종 판정
- FAIL
- Top 3 Fixes:
  1) Provider 키/네트워크/timeout 설정 점검 (LLM 호출 실패)
  2) LLM_COST_LEDGER_PATH 권한/경로 점검 (ledger 미기록)
  3) LLM_DEDUPE_ENABLED/TTL/목적(purpose) 및 Redis 연결 점검 (dedupe 미작동)

비고
- MANUAL 항목은 외부 시스템/운영 환경 의존(웹훅 수신, 크론, 장애 유도 등)이라 자동화에서 제외했습니다.
