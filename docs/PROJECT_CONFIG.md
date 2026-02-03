# NEXUS 프로젝트 설정

## 프로젝트 정보
- **이름**: NEXUS (세리아 AI 에이전트 시스템)
- **도메인**: nexus
- **버전**: 0.1.0
- **상태**: 개발 중

## 기술 스택

### Frontend
- HTML5
- CSS3 (Tailwind CSS via CDN)
- JavaScript (Vanilla JS)
- FontAwesome Icons

### Backend
- Hono Framework (TypeScript)
- Cloudflare Workers/Pages
- Vite (Build Tool)

### Infrastructure
- Cloudflare Pages (Hosting)
- Cloudflare Workers (Edge Computing)
- Git (Version Control)
- PM2 (Process Management)

## 데이터베이스 (예정)
- Cloudflare D1 (SQLite)
- Cloudflare KV (Key-Value Store)
- Cloudflare R2 (Object Storage)

## 개발 환경 설정

### 필수 도구
- Node.js 18+
- npm 9+
- Git
- Wrangler CLI

### 환경 변수
`.dev.vars` 파일 생성 필요 (로컬 개발용)
```
# API Keys
API_KEY=your_api_key_here

# Database
DATABASE_URL=your_database_url_here
```

## 배포 설정

### Cloudflare Pages
- Project Name: nexus
- Production Branch: main
- Build Command: npm run build
- Build Output Directory: dist

### 환경별 설정
- **개발**: http://localhost:3000
- **스테이징**: (추후 설정)
- **프로덕션**: https://nexus.pages.dev (예정)

## 다음 단계
1. ✅ 프로젝트 기본 구조 설정 완료
2. ✅ 도메인명 nexus로 변경 완료
3. ⏳ 설계 문서 업로드 대기 중
4. ⏳ Python 코드 및 구조 문서 업로드 대기 중
5. ⏳ 시스템 아키텍처 구현
6. ⏳ API 엔드포인트 개발
7. ⏳ 프론트엔드 UI 개발
8. ⏳ 데이터베이스 연동
9. ⏳ 배포 및 테스트
