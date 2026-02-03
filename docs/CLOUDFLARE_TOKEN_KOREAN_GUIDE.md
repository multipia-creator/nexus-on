# Cloudflare 한글 대시보드 - API 토큰 발급 가이드

## 🔐 새 API 토큰 발급하기 (한글 UI)

---

### **1단계: Cloudflare 대시보드 접속**

#### 방법 1: 직접 링크
```
https://dash.cloudflare.com/profile/api-tokens
```

#### 방법 2: 대시보드에서 이동
1. https://dash.cloudflare.com/ 접속
2. 우측 상단 **프로필 아이콘** (이메일 주소) 클릭
3. **"내 프로필"** 또는 **"My Profile"** 클릭
4. 좌측 메뉴에서 **"API 토큰"** 또는 **"API Tokens"** 클릭

---

### **2단계: 기존 토큰 삭제 (선택사항)**

⚠️ **보안을 위해 기존에 노출된 토큰은 반드시 삭제하세요**

#### 한글 UI:
1. "API 토큰" 페이지에서 기존 토큰 찾기
2. 토큰 오른쪽의 **"⋮" (점 3개)** 또는 **"작업"** 버튼 클릭
3. **"삭제"** 또는 **"Delete"** 선택
4. 확인 팝업에서 **"삭제"** 클릭

#### 영문 UI:
1. "API Tokens" 페이지에서 기존 토큰 찾기
2. 토큰 오른쪽의 **"⋮"** 또는 **"Actions"** 클릭
3. **"Delete"** 선택
4. 확인 팝업에서 **"Delete"** 클릭

---

### **3단계: 새 토큰 생성**

#### A. 토큰 생성 시작

**한글 UI:**
- **"토큰 만들기"** 또는 **"Create Token"** 버튼 클릭

**영문 UI:**
- **"Create Token"** 버튼 클릭

---

#### B. 템플릿 선택

**권장 템플릿**: **"Cloudflare Workers 편집"** 또는 **"Edit Cloudflare Workers"**

이 템플릿을 찾으려면:
1. 페이지를 아래로 스크롤
2. "API 토큰 템플릿" 섹션에서 찾기
3. **"Cloudflare Workers 편집"** 템플릿의 **"템플릿 사용"** 또는 **"Use template"** 클릭

---

#### C. 토큰 권한 설정

**필수 권한 (반드시 확인하세요!):**

| 한글 | 영문 | 설정 |
|------|------|------|
| **계정** | **Account** | |
| └ Cloudflare Pages | └ Cloudflare Pages | **편집** 또는 **Edit** |

**설정 화면:**
```
┌─────────────────────────────────────────┐
│ 권한 (Permissions)                       │
├─────────────────────────────────────────┤
│ 계정 권한 (Account Permissions)          │
│ ┌─────────────────────────────────────┐ │
│ │ Cloudflare Pages     [편집 ▼]       │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**추가 권한 (선택사항):**
- **Account Settings** → **읽기** (Read) - 계정 정보 확인용

---

#### D. 계정 리소스 선택

**한글:**
- **"계정 리소스"** 섹션에서 본인 계정 선택
- **"모든 계정"** 또는 **"특정 계정"** 선택 가능

**영문:**
- **"Account Resources"** 섹션에서 본인 계정 선택
- **"All accounts"** 또는 특정 계정 선택

---

#### E. 추가 보안 설정 (선택사항 - 권장)

**1. Client IP 주소 필터링**
- 특정 IP에서만 토큰 사용 허용
- 본인 개발 환경 IP 입력

**2. TTL (Time To Live) - 토큰 만료 기간**
- 권장: **6개월** 또는 **1년**
- 보안 강화를 원하면 더 짧게 설정

---

#### F. 토큰 생성 완료

1. 모든 설정 확인 후 **"요약으로 계속"** 또는 **"Continue to summary"** 클릭
2. 권한 요약 확인
3. **"토큰 만들기"** 또는 **"Create Token"** 클릭

---

### **4단계: 토큰 복사 및 저장**

⚠️ **매우 중요: 토큰은 이 화면에서 단 한 번만 표시됩니다!**

#### 토큰 복사
1. 생성된 토큰이 표시되면 **즉시 복사**
2. **"복사"** 또는 **"Copy"** 버튼 클릭

#### 토큰 형식
```
예시: AbCdEf1234567890GhIjKlMnOpQrStUvWxYz_AbCdEf1234567890
```

#### 안전하게 저장
✅ **권장 방법:**
- 비밀번호 관리자 (1Password, Bitwarden, LastPass)
- 로컬 `.env.local` 파일 (Git에 커밋하지 않기!)

❌ **절대 금지:**
- 코드에 하드코딩
- Git에 커밋
- 공개 채팅/이슈에 붙여넣기

---

### **5단계: 토큰 테스트**

#### 로컬 터미널에서 테스트

```bash
# 1. 환경 변수 설정
export CLOUDFLARE_API_TOKEN="복사한-토큰-여기-붙여넣기"

# 2. 자동 테스트 스크립트 실행
cd /home/user/webapp
./test-cloudflare-token.sh
```

**예상 출력:**
```
🔐 Cloudflare API 토큰 테스트
================================

✅ 환경 변수 CLOUDFLARE_API_TOKEN 확인됨

📦 Wrangler 설치 확인 중...
✅ Wrangler 설치됨: 4.61.1

🔑 Wrangler 인증 테스트 중...
✅ Wrangler 인증 성공!

Getting User settings...
👋 You are logged in with an API Token, associated with the email '이메일@example.com'!

🎉 모든 테스트 통과!
```

#### 수동 테스트 (선택)

```bash
# Wrangler 인증 확인
wrangler whoami

# 예상 출력:
# Getting User settings...
# 👋 You are logged in with an API Token, associated with the email '이메일@example.com'!
```

---

## 📝 **빠른 참조 가이드**

### 토큰 생성 단계 요약
```
1. https://dash.cloudflare.com/profile/api-tokens 접속
2. "토큰 만들기" (Create Token) 클릭
3. "Cloudflare Workers 편집" 템플릿 선택
4. 권한 확인: Account → Cloudflare Pages → 편집 (Edit)
5. "토큰 만들기" 클릭
6. 토큰 복사 (⚠️ 한 번만 표시!)
7. 안전한 곳에 저장
```

### 필수 권한 설정
```
Account Permissions:
  ✅ Cloudflare Pages - Edit

선택 권한:
  ⭕ Account Settings - Read
```

### 테스트 명령어
```bash
export CLOUDFLARE_API_TOKEN="새-토큰"
cd /home/user/webapp
./test-cloudflare-token.sh
```

---

## 🔍 **UI 용어 대조표 (한글 ↔ 영문)**

| 한글 | 영문 |
|------|------|
| 내 프로필 | My Profile |
| API 토큰 | API Tokens |
| 토큰 만들기 | Create Token |
| 템플릿 사용 | Use template |
| Cloudflare Workers 편집 | Edit Cloudflare Workers |
| 권한 | Permissions |
| 계정 권한 | Account Permissions |
| 편집 | Edit |
| 읽기 | Read |
| 계정 리소스 | Account Resources |
| 요약으로 계속 | Continue to summary |
| 복사 | Copy |
| 삭제 | Delete |
| 작업 | Actions |

---

## 🚨 **문제 해결 (Troubleshooting)**

### 문제 1: "Cloudflare Workers 편집" 템플릿이 안 보여요
**해결:**
1. 페이지를 끝까지 스크롤
2. 또는 **"사용자 지정 토큰"** (Custom token) 사용:
   - "토큰 만들기" → "사용자 지정 토큰" 선택
   - 수동으로 권한 추가: Account → Cloudflare Pages → Edit

### 문제 2: 토큰을 복사하지 못하고 창을 닫았어요
**해결:**
- 토큰은 다시 볼 수 없습니다
- 해당 토큰을 삭제하고 새로 생성하세요

### 문제 3: wrangler whoami에서 인증 실패
**해결:**
```bash
# 1. 환경 변수 다시 확인
echo $CLOUDFLARE_API_TOKEN

# 2. 토큰 권한 확인
# → Cloudflare Dashboard → API 토큰 → 해당 토큰의 권한 확인

# 3. 토큰 재생성 (필요시)
```

---

## ✅ **최종 체크리스트**

```markdown
[ ] 1. Cloudflare 대시보드 접속
[ ] 2. "API 토큰" 페이지 이동
[ ] 3. (선택) 기존 토큰 삭제
[ ] 4. "토큰 만들기" 클릭
[ ] 5. "Cloudflare Workers 편집" 템플릿 선택
[ ] 6. 권한 확인: Cloudflare Pages - Edit
[ ] 7. "토큰 만들기" 최종 클릭
[ ] 8. 토큰 복사 (⚠️ 한 번만 표시!)
[ ] 9. 토큰 안전하게 저장
[ ] 10. ./test-cloudflare-token.sh 실행으로 테스트
[ ] 11. wrangler whoami 성공 확인
```

---

## 📞 **추가 도움이 필요하시면**

- Cloudflare 공식 문서: https://developers.cloudflare.com/fundamentals/api/get-started/create-token/
- NEXUS 토큰 갱신 가이드: `/home/user/webapp/docs/CLOUDFLARE_TOKEN_RENEWAL.md`

---

**생성일**: 2026-02-03  
**프로젝트**: NEXUS v2  
**문서 위치**: `/home/user/webapp/docs/CLOUDFLARE_TOKEN_KOREAN_GUIDE.md`
