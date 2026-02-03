# Cloudflare API 토큰 발급 - 5분 완성 가이드

## 🚀 빠른 시작 (5분 완료)

---

### **1단계: 접속 (30초)**

브라우저에서 아래 링크 클릭:
```
https://dash.cloudflare.com/profile/api-tokens
```

---

### **2단계: 토큰 만들기 (1분)**

1. 파란색 버튼 **"토큰 만들기"** 또는 **"Create Token"** 클릭
2. 아래로 스크롤하여 **"⚙️ Cloudflare Workers 편집"** 찾기
3. 우측의 **"템플릿 사용"** 버튼 클릭

---

### **3단계: 권한 확인 (1분)**

**반드시 확인:**
```
계정 권한 (Account Permissions):
  ✅ Cloudflare Pages - 편집 (Edit)
```

**확인 후:**
- 우측 하단 **"요약으로 계속"** 클릭

---

### **4단계: 토큰 생성 (1분)**

1. 권한 요약 확인
2. **"토큰 만들기"** 클릭
3. ⚠️ **즉시 "복사" 버튼 클릭!** (한 번만 표시됨)

**토큰 형식 예시:**
```
AbCdEf1234567890GhIjKlMnOpQrStUvWxYz_AbCdEf1234567890
```

---

### **5단계: 토큰 테스트 (2분)**

터미널에서 실행:

```bash
# 1. 환경 변수 설정 (토큰 붙여넣기)
export CLOUDFLARE_API_TOKEN="복사한-토큰-여기-붙여넣기"

# 2. 자동 테스트
cd /home/user/webapp
./test-cloudflare-token.sh
```

**성공 메시지:**
```
🎉 모든 테스트 통과!
✅ 새 Cloudflare API 토큰이 정상적으로 작동합니다
```

---

## ✅ **완료!**

이제 토큰을 안전하게 저장하세요:

```bash
# .env.local 파일에 저장 (권장)
echo "CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN" > /home/user/webapp/.env.local
```

---

## 📞 **문제 발생 시**

### ❌ "Cloudflare Workers 편집" 템플릿이 안 보여요
**해결:** 페이지를 끝까지 스크롤하거나, "사용자 지정 토큰"으로 수동 설정

### ❌ 토큰을 복사 안 하고 창을 닫았어요
**해결:** 해당 토큰 삭제 후 다시 생성

### ❌ wrangler whoami에서 에러
**해결:** 
```bash
# 토큰 재확인
echo $CLOUDFLARE_API_TOKEN

# 다시 설정
export CLOUDFLARE_API_TOKEN="토큰-다시-붙여넣기"
```

---

## 🔗 **더 자세한 가이드**

- 📘 **전체 가이드**: `/home/user/webapp/docs/CLOUDFLARE_TOKEN_KOREAN_GUIDE.md`
- 📺 **화면별 가이드**: `/home/user/webapp/docs/CLOUDFLARE_TOKEN_SCREENS_GUIDE.md`
- 🔧 **테스트 스크립트**: `/home/user/webapp/test-cloudflare-token.sh`

---

**생성일**: 2026-02-03  
**예상 소요 시간**: 5분  
**난이도**: ⭐ 쉬움
