# NEXUS Deploy Guide (v1.8)

## 1) 준비
- Docker / Docker Compose 설치
- `.env` 생성: `.env.example` 복사 후 GEMINI_API_KEY 설정 권장

## 2) 배포
```bash
bash deploy/nexus_deploy.sh
```

## 3) 점검
```bash
bash deploy/smoke_test.sh
```

## 4) 접속
- Supervisor: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672 (guest/guest)
