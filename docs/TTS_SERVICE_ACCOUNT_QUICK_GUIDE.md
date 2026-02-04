# Google Cloud TTS 서비스 계정 JSON 키 발급 가이드

**교수님께서 받으신 API 키로는 TTS를 사용할 수 없습니다.**
**서비스 계정 JSON 키 파일**이 필요합니다.

---

## 🚀 빠른 설정 (5분)

### Step 1: Google Cloud Console 접속

1. https://console.cloud.google.com/ 접속
2. 기존 프로젝트 선택 또는 새 프로젝트 생성

---

### Step 2: Text-to-Speech API 활성화

1. 좌측 메뉴 → **API 및 서비스** → **라이브러리**
2. 검색창에 **"Cloud Text-to-Speech API"** 입력
3. **"사용 설정"** 버튼 클릭

![TTS API 활성화](https://i.imgur.com/example1.png)

---

### Step 3: 서비스 계정 생성

1. 좌측 메뉴 → **IAM 및 관리자** → **서비스 계정**
2. **"서비스 계정 만들기"** 클릭

**서비스 계정 정보**:
- 이름: `nexus-tts-service`
- ID: `nexus-tts-service` (자동 생성)
- 설명: `NEXUS-ON TTS service account`

3. **"만들기 및 계속하기"** 클릭

---

### Step 4: 역할 부여

**역할 선택**:
- 검색: "Cloud Text-to-Speech API 사용자"
- 또는: "Text-to-Speech API User"

![역할 선택](https://i.imgur.com/example2.png)

**"계속"** → **"완료"** 클릭

---

### Step 5: JSON 키 다운로드

1. 생성된 서비스 계정 클릭
2. **"키"** 탭 선택
3. **"키 추가"** → **"새 키 만들기"**
4. **키 유형**: JSON 선택
5. **"만들기"** 클릭

→ **자동으로 JSON 파일 다운로드됨**

파일명 예시: `nexus-on-123456-abc123def456.json`

---

### Step 6: JSON 파일 저장

다운로드된 JSON 파일을 안전한 위치에 저장:

```bash
# 예시 경로
/home/user/webapp/backend/credentials/nexus-tts-credentials.json
```

**⚠️ 중요**: 이 파일은 **절대 GitHub에 커밋하지 마세요!**

---

### Step 7: 환경변수 설정

```bash
cd /home/user/webapp/backend

# 환경변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="/home/user/webapp/backend/credentials/nexus-tts-credentials.json"

# 또는 .env 파일에 추가
echo 'GOOGLE_APPLICATION_CREDENTIALS=/home/user/webapp/backend/credentials/nexus-tts-credentials.json' >> .env
```

---

### Step 8: 의존성 설치 및 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python3 nexus_supervisor/app.py
```

**성공 로그**:
```
✅ Google Cloud TTS initialized successfully
✅ TTS service enabled (Google Cloud TTS)
```

---

## 🎉 완료!

이제 고품질 한국어 여성 음성을 사용할 수 있습니다!

---

## 📸 스크린샷 참고

자세한 화면은 다음 문서 참고:
- `/home/user/webapp/docs/GOOGLE_CLOUD_TTS_SETUP_2026-02-04.md`
