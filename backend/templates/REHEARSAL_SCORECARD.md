# NEXUS 운영 리허설 스코어카드 (v6.10)

환경
- 날짜/시간(UTC/KST):
- 배포 버전:
- 실행 환경(단일/멀티 노드, Redis 유무):
- 사용 Provider(우선/옵션):

A. 30분 스모크
1) LLM 호출/응답: OK / NG
- 증적: (audit 줄 링크/스니펫)
2) cost ledger 기록: OK / NG
- actual_cost_usd / approx_tokens 비율:
3) finops_report 생성: OK / NG
- out 파일:
4) 알림 배선: OK / NG
- Slack/Teams 수신 확인:

B. 2시간 리허설
5) Dedupe hit 확인: OK / NG
- hit ratio(대략):
6) 태깅(team/project) 분리: OK / NG
7) 저강도 부하(p50/p95, fail율): OK / NG
- 결과:

C. 1일 리허설
8) 크론 스케줄 동작: OK / NG
9) 장애–복구 라운드트립: OK / NG
- 장애 유형:
- MTTD(탐지): 
- MTTR(복구):

최종 판정
- PASS / FAIL
- Top 3 Fixes:
  1)
  2)
  3)
