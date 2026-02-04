# Google Cloud TTS 통합 가이드

**작성일**: 2026-02-04  
**목적**: NEXUS-ON에 고품질 한국어 여성 TTS 통합  
**음성**: Google Cloud TTS `ko-KR-Wavenet-A` (여성, 최고 품질)

---

## 📋 개요

NEXUS-ON은 **Google Cloud Text-to-Speech API**를 사용하여 고품질 한국어 음성 합성을 제공합니다.

### 주요 특징
- ✅ **최고 품질**: WaveNet 기술 기반의 자연스러운 한국어 음성
- ✅ **여성 음성**: `ko-KR-Wavenet-A` (한국어 여성, 자연스럽고 부드러운 음성)
- ✅ **빠른 응답**: ~1-2초 내 음성 생성
- ✅ **무료 티어**: 월 1~400만 글자 무료
- ✅ **립싱크 지원**: Live2D 캐릭터와 동기화

---

## 🚀 설정 방법

### Step 1: Google Cloud 프로젝트 생성

1. **Google Cloud Console 접속**: https://console.cloud.google.com/

2. **새 프로젝트 생성** (또는 기존 프로젝트 선택)
   - 프로젝트 이름: `nexus-on-tts` (예시)

3. **Text-to-Speech API 활성화**
   - API 및 서비스 → 라이브러리
   - "Cloud Text-to-Speech API" 검색
   - "사용 설정" 클릭

4. **서비스 계정 생성**
   - IAM 및 관리자 → 서비스 계정
   - "서비스 계정 만들기" 클릭
   - 이름: `nexus-tts-service`
   - 역할: `Cloud Text-to-Speech API 사용자`

5. **JSON 키 다운로드**
   - 생성한 서비스 계정 클릭
   - "키" 탭 → "키 추가" → "새 키 만들기"
   - 유형: JSON
   - 다운로드된 JSON 파일 저장 (예: `nexus-tts-credentials.json`)

---

### Step 2: Backend 설정

#### A. 의존성 설치

```bash
cd /home/user/webapp/backend
pip install -r requirements.txt
```

**requirements.txt**에 이미 포함됨:
```
google-cloud-texttospeech>=2.14.0
```

#### B. 환경변수 설정

**방법 1: `.env` 파일 생성** (로컬 개발용)

```bash
# /home/user/webapp/backend/.env
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/nexus-tts-credentials.json
```

**방법 2: 환경변수 직접 설정**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/nexus-tts-credentials.json"
```

**방법 3: Docker/Production**

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/nexus-tts-credentials.json
    volumes:
      - ./nexus-tts-credentials.json:/app/credentials/nexus-tts-credentials.json:ro
```

#### C. Backend 재시작

```bash
cd /home/user/webapp/backend
python3 nexus_supervisor/app.py
```

서버 로그에서 확인:
```
✅ Google Cloud TTS initialized successfully
✅ TTS service enabled (Google Cloud TTS)
```

---

### Step 3: 테스트

#### A. Backend TTS 생성 테스트

```python
# Python 콘솔에서 테스트
from shared.tts_service import generate_tts

result = generate_tts("안녕하세요, 저는 NEXUS AI 비서입니다.")
print(result)
# Output:
# {
#   'audio_path': '/tmp/nexus_tts/tts_abc123def456.mp3',
#   'audio_url': '/tts/tts_abc123def456.mp3',
#   'duration_ms': 3500,
#   'text': '안녕하세요, 저는 NEXUS AI 비서입니다.',
#   'voice': 'ko-KR-Wavenet-A'
# }
```

#### B. Frontend 재생 테스트

브라우저 콘솔:
```javascript
// 1. SSE 연결 확인
window.live2dAgent.sseClient.eventSource.readyState  // 1 = OPEN

// 2. 수동 TTS 테스트 (Backend에서 /chat/send 호출 후 확인)
// Console에서 다음 로그 확인:
// [Live2D Agent] TTS started: 안녕하세요...
// [Live2D Agent] Playing TTS audio: /tts/tts_abc123def456.mp3
// [Live2D Agent] TTS audio playback finished
```

#### C. 통합 테스트

1. **채팅 입력**:
   - 페이지에서 채팅 메시지 전송
   - Live2D 캐릭터가 `speaking` 상태로 전환
   - 고품질 한국어 음성 재생
   - 립싱크 애니메이션 (구현된 경우)

2. **Network 탭 확인**:
   - SSE 이벤트: `tts_start` (audio_url 포함)
   - HTTP 요청: `GET /tts/tts_*.mp3` (200 OK)

---

## 🎤 음성 품질 설정

### 사용 가능한 한국어 음성

| 음성 이름 | 성별 | 품질 | 추천 |
|-----------|------|------|------|
| `ko-KR-Wavenet-A` | 여성 | ⭐⭐⭐⭐⭐ | ✅ 기본값 (최고 품질) |
| `ko-KR-Wavenet-B` | 여성 | ⭐⭐⭐⭐⭐ | 대안 1 (부드러운 음성) |
| `ko-KR-Wavenet-C` | 남성 | ⭐⭐⭐⭐⭐ | 남성 음성 |
| `ko-KR-Wavenet-D` | 남성 | ⭐⭐⭐⭐⭐ | 남성 음성 대안 |
| `ko-KR-Standard-A` | 여성 | ⭐⭐⭐ | 저비용 옵션 |

### 음성 파라미터 조정

**Backend**: `/home/user/webapp/backend/shared/tts_service.py`

```python
tts_result = generate_tts(
    text="안녕하세요",
    voice_name="ko-KR-Wavenet-A",  # 음성 모델
    speaking_rate=1.0,               # 속도 (0.25 ~ 4.0)
    pitch=0.0                        # 피치 (-20.0 ~ 20.0)
)
```

**설정 예시**:
- **빠른 속도**: `speaking_rate=1.2`
- **느린 속도**: `speaking_rate=0.8`
- **높은 음높이**: `pitch=5.0`
- **낮은 음높이**: `pitch=-5.0`

---

## 💰 비용 관리

### Google Cloud TTS 가격

| 사용량 | 가격 (Standard) | 가격 (WaveNet) |
|--------|----------------|----------------|
| 월 0 ~ 100만 글자 | 무료 | 무료 |
| 월 100만 ~ 400만 글자 | 무료 | 무료 |
| 월 400만 글자 초과 | $4.00 / 100만 글자 | $16.00 / 100만 글자 |

### 예상 비용

**시나리오**: 1,000명 사용자, 평균 하루 10개 응답 (각 50자)

```
월 총 글자 수 = 1,000명 × 10개 × 50자 × 30일 = 15,000,000 글자 (1,500만)
비용 = (15,000,000 - 4,000,000) × ($16 / 1,000,000) = $176/월
```

### 비용 절감 팁

1. **캐싱**: 동일한 텍스트는 재사용 (이미 구현됨 - MD5 해시 기반)
2. **Standard 음성**: 비용 25% 절감 (품질 다소 낮음)
3. **짧은 응답**: 불필요한 문장 줄이기
4. **Lazy TTS**: 사용자가 재생 버튼을 누를 때만 생성

---

## 🔧 문제 해결

### 문제 1: "TTS service not enabled"

**원인**: `GOOGLE_APPLICATION_CREDENTIALS` 설정 안 됨

**해결**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
# Backend 재시작
```

### 문제 2: "google-cloud-texttospeech not installed"

**원인**: Python 패키지 미설치

**해결**:
```bash
pip install google-cloud-texttospeech>=2.14.0
```

### 문제 3: "Audio file not found (404)"

**원인**: TTS 파일이 생성되지 않았거나 삭제됨

**해결**:
1. Backend 로그 확인: `🎤 Generating TTS...`
2. 파일 확인: `ls /tmp/nexus_tts/`
3. 권한 확인: `chmod 755 /tmp/nexus_tts`

### 문제 4: "Permission denied (credentials)"

**원인**: JSON 키 파일 권한 문제

**해결**:
```bash
chmod 600 nexus-tts-credentials.json
chown user:user nexus-tts-credentials.json
```

---

## 📊 모니터링

### Backend 로그

```bash
# TTS 생성 로그
2026-02-04 10:30:15 INFO [tts_service] 🎤 Generating TTS for text (length: 25): 안녕하세요, 저는 NEXUS AI 비서입니다...
2026-02-04 10:30:17 INFO [tts_service] ✅ TTS generated successfully: /tmp/nexus_tts/tts_abc123.mp3 (3500ms)

# TTS 이벤트 전송 로그
2026-02-04 10:30:17 DEBUG [tts_start] tenant_abc123
2026-02-04 10:30:17 DEBUG [tts_end] tenant_abc123
```

### Frontend 콘솔

```javascript
[Live2D Agent] TTS started: 안녕하세요, 저는 NEXUS AI 비서입니다
[Live2D Agent] Playing TTS audio: /tts/tts_abc123def456.mp3
[Live2D Agent] TTS audio playback finished
[Live2D Agent] TTS ended, duration: 3500
```

---

## 🎉 완료!

이제 NEXUS-ON은 고품질 한국어 여성 TTS를 사용합니다!

**다음 단계**:
1. ✅ Google Cloud TTS 설정 완료
2. ✅ Backend TTS 생성 구현
3. ✅ Frontend 오디오 재생
4. ⏳ 립싱크 애니메이션 세밀 조정
5. ⏳ 음질 테스트 및 피드백

---

**문서 작성**: 2026-02-04  
**최종 업데이트**: 2026-02-04  
**버전**: v1.0
