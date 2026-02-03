# NEXUS_세리아 AI 에이전트 시스템

## 프로젝트 개요
- **프로젝트명**: NEXUS_세리아 AI 에이전트 시스템
- **목표**: 차세대 AI 에이전트 시스템 구축
- **기술 스택**: Hono + TypeScript + Cloudflare Pages

## 현재 완료된 기능
- ✅ 프로젝트 기본 구조 설정 완료
- ✅ Hono 프레임워크 초기화
- ✅ Git 저장소 설정
- ✅ PM2 설정 완료
- ✅ Cloudflare Pages 배포 준비

## 현재 기능별 URI 요약
- `GET /` - 메인 페이지 (기본 템플릿)

## 미구현 기능
- 🔲 AI 에이전트 핵심 로직
- 🔲 데이터베이스 연동
- 🔲 API 엔드포인트 구축
- 🔲 프론트엔드 UI/UX 개발

## 개발 추천 순서
1. 요구사항 및 기능 명세 정의
2. 데이터 모델 설계
3. API 엔드포인트 개발
4. 프론트엔드 UI 개발
5. AI 에이전트 로직 구현

## URL 정보
- **로컬 개발**: http://localhost:3000
- **프로덕션**: (배포 후 업데이트 예정)
- **GitHub**: (연동 후 업데이트 예정)

## 데이터 아키텍처
- **데이터 모델**: (추후 정의)
- **스토리지 서비스**: (추후 선택 - Cloudflare D1/KV/R2)
- **데이터 흐름**: (추후 설계)

## 사용자 가이드
(개발 완료 후 작성 예정)

## 배포 정보
- **플랫폼**: Cloudflare Pages
- **상태**: 🟡 개발 중
- **마지막 업데이트**: 2026-02-03

## 로컬 개발 환경 실행

### 빌드
```bash
npm run build
```

### 개발 서버 실행 (PM2 사용)
```bash
# 포트 정리
npm run clean-port

# PM2로 서비스 시작
pm2 start ecosystem.config.cjs

# 서비스 확인
pm2 list
pm2 logs nexus-seria-ai-agent --nostream

# 서비스 테스트
npm test
```

### Git 명령어
```bash
npm run git:status  # 상태 확인
npm run git:commit "커밋 메시지"  # 커밋
npm run git:log  # 로그 확인
```

## 프로젝트 구조
```
nexus-seria-ai-agent/
├── src/
│   ├── index.tsx      # 메인 애플리케이션 진입점
│   └── renderer.tsx   # JSX 렌더러
├── public/            # 정적 파일
├── .git/              # Git 저장소
├── .gitignore         # Git 제외 파일
├── ecosystem.config.cjs  # PM2 설정
├── wrangler.jsonc     # Cloudflare 설정
├── package.json       # 의존성 및 스크립트
├── tsconfig.json      # TypeScript 설정
├── vite.config.ts     # Vite 빌드 설정
└── README.md          # 프로젝트 문서
```
