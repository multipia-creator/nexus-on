# Cloudflare API 토큰 갱신 가이드

## 🔐 토큰 재발급이 필요한 경우
- 토큰이 공개 채팅/코드에 노출된 경우
- 정기적인 보안 갱신 (권장: 3-6개월마다)
- 토큰이 탈취/악용 의심될 때

---

## 📋 재발급 절차

### 1️⃣ Cloudflare Dashboard 접속
```
https://dash.cloudflare.com/profile/api-tokens
```

### 2️⃣ 기존 토큰 삭제
1. "API Tokens" 페이지에서 기존 토큰 찾기
2. 토큰 오른쪽의 "Roll" 또는 "Delete" 버튼 클릭
3. 확인 팝업에서 "Delete" 선택

### 3️⃣ 새 토큰 생성

#### A. 토큰 템플릿 선택
- "Create Token" → "Edit Cloudflare Workers" 템플릿

#### B. 권한 설정
```
Account Permissions:
  ✅ Cloudflare Pages - Edit
  ✅ Account Settings - Read (선택)

Zone Permissions (선택):
  ✅ Workers Routes - Edit
```

#### C. 추가 보안 설정 (권장)
- **Client IP Address Filtering**: 본인 IP만 허용
- **TTL**: 6개월 후 자동 만료 설정

#### D. 토큰 생성
- "Continue to summary" → "Create Token"
- ⚠️ **토큰 복사** (한 번만 표시!)

---

## 🧪 새 토큰 테스트

### 로컬 환경에서 테스트
```bash
# 1. 환경 변수 설정 (임시)
export CLOUDFLARE_API_TOKEN="새-토큰-여기-붙여넣기"

# 2. Wrangler 인증 확인
wrangler whoami

# 예상 출력:
# Getting User settings...
# 👋 You are logged in with an API Token, associated with the email '이메일@example.com'!
# ┌──────────────────────┬──────────────────────────────────┐
# │ Account Name         │ Account ID                        │
# ├──────────────────────┼──────────────────────────────────┤
# │ 본인 계정명           │ abc123...                         │
# └──────────────────────┴──────────────────────────────────┘

# 3. 테스트 배포
cd /home/user/webapp/frontend
wrangler pages deploy dist --project-name nexus-frontend
```

---

## 🔒 토큰 안전하게 보관

### ✅ 권장 방법
1. **로컬 환경 변수 파일** (`.env.local`)
   ```bash
   # /home/user/webapp/.env.local
   CLOUDFLARE_API_TOKEN=새-토큰-여기
   ```
   
   ⚠️ `.gitignore`에 반드시 추가:
   ```
   .env.local
   .env
   ```

2. **CI/CD 환경** (GitHub Actions)
   - GitHub Repository → Settings → Secrets and variables → Actions
   - "New repository secret" → `CLOUDFLARE_API_TOKEN`

3. **비밀번호 관리자**
   - 1Password, Bitwarden, LastPass 등에 안전하게 저장

### ❌ 절대 하면 안 되는 것
- ❌ 코드에 직접 하드코딩
- ❌ Git에 커밋
- ❌ 공개 채팅/이슈에 붙여넣기
- ❌ 스크린샷/동영상에 노출

---

## 🚨 토큰 탈취 의심 시 즉시 조치

1. **즉시 토큰 삭제**
   ```
   https://dash.cloudflare.com/profile/api-tokens → Delete
   ```

2. **Cloudflare 계정 활동 로그 확인**
   - Audit Logs에서 비정상 활동 확인

3. **새 토큰 생성 후 재배포**

---

## 📝 재발급 후 업데이트 필요한 곳

### 로컬 개발 환경
```bash
# ~/.bashrc 또는 ~/.zshrc
export CLOUDFLARE_API_TOKEN="새-토큰"

# 또는 프로젝트별 .env.local
echo "CLOUDFLARE_API_TOKEN=새-토큰" > /home/user/webapp/.env.local
```

### CI/CD (GitHub Actions)
- Repository Settings → Secrets → `CLOUDFLARE_API_TOKEN` 업데이트

### 팀원 공유 (Private Repository)
- Secure channel로만 전달 (Signal, 1Password 등)
- ❌ Slack/이메일/채팅으로 전달 금지

---

## ✅ 체크리스트

- [ ] 기존 토큰 삭제 완료
- [ ] 새 토큰 생성 완료
- [ ] 토큰 안전한 곳에 보관 (비밀번호 관리자)
- [ ] `wrangler whoami` 테스트 성공
- [ ] 테스트 배포 성공
- [ ] `.env.local` 파일에 저장 (`.gitignore`에 추가)
- [ ] CI/CD Secrets 업데이트 (해당되는 경우)
- [ ] 기존 토큰이 사용된 모든 곳 업데이트 확인

---

## 📞 문제 발생 시

### Wrangler 인증 실패
```bash
# 에러: "Authentication error"
# 해결: 토큰 권한 확인
# → Cloudflare Pages - Edit 권한 있는지 확인
```

### 배포 실패
```bash
# 에러: "Unable to deploy to Cloudflare Pages"
# 해결:
wrangler logout
export CLOUDFLARE_API_TOKEN="새-토큰"
wrangler whoami
wrangler pages deploy dist --project-name nexus-frontend
```

---

## 🔗 참고 문서
- [Cloudflare API Tokens 공식 문서](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [Wrangler Authentication](https://developers.cloudflare.com/workers/wrangler/ci-cd/)
