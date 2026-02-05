# NEXUS Engine - Windows 설치 가이드

## 🎯 5분 설치 (초보자용)

### 방법 1: 자동 설치 스크립트 (권장)

1. **PowerShell을 관리자 권한으로 실행**
   - Windows 키를 누르고 `powershell` 입력
   - 우클릭 → "관리자 권한으로 실행"

2. **설치 명령어 실행**
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; `
   iex ((New-Object System.Net.WebClient).DownloadString('https://nexus-3bm.pages.dev/downloads/windows/bootstrap.ps1'))
   ```

3. **완료!**
   - 약 3~5분 소요
   - 브라우저에서 http://localhost:7100 접속하여 확인

---

### 방법 2: Setup.exe 설치 (GUI)

1. **다운로드**
   - [NEXUS-Engine-Windows-x64-Setup.exe](https://nexus-3bm.pages.dev/downloads/windows/NEXUS-Engine-Windows-x64-Setup.exe) (약 50MB)

2. **설치 마법사 실행**
   - 더블클릭하여 실행
   - "관리자 권한 허용" 클릭
   - 설치 경로 선택 (기본: `C:\Program Files\NEXUS-Engine`)
   - 데이터 폴더 선택 (기본: `내 문서\NEXUS-Data`, 최소 5GB 여유 공간)

3. **API 키 설정**
   - 설치 완료 후 자동으로 열리는 `.env` 파일에 API 키 입력:
     ```env
     # Anthropic Claude (권장)
     ANTHROPIC_API_KEY=sk-ant-api...
     
     # OpenAI GPT (대체)
     OPENAI_API_KEY=sk-proj-...
     
     # Google Cloud TTS (선택)
     GOOGLE_CLOUD_API_KEY=AIza...
     ```

4. **서비스 시작**
   - Windows 서비스로 자동 등록됨
   - 시스템 시작 시 자동 실행
   - 수동 시작: `서비스` 앱에서 "NEXUS Engine Service" 시작

---

## 📋 시스템 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| **OS** | Windows 10 (64-bit) | Windows 11 (64-bit) |
| **CPU** | Intel Core i3 / AMD Ryzen 3 | Intel Core i5+ / AMD Ryzen 5+ |
| **RAM** | 4GB | 8GB 이상 |
| **디스크** | 5GB 여유 공간 | 10GB 여유 공간 (SSD) |
| **네트워크** | 인터넷 연결 필수 | 광대역 인터넷 |
| **소프트웨어** | Python 3.11+ (자동 설치) | Python 3.11+ (자동 설치) |

---

## 🔧 설치 후 확인

### 1. Health Check
브라우저에서 http://localhost:7100/health 접속:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 3600,
  "engine": "windows-x64"
}
```

### 2. 서비스 상태 확인
PowerShell에서:
```powershell
Get-Service NEXUSEngine
```
출력:
```
Status   Name               DisplayName
------   ----               -----------
Running  NEXUSEngine        NEXUS Engine Service
```

### 3. 로그 확인
- 위치: `C:\Program Files\NEXUS-Engine\logs\nexus.log`
- PowerShell에서 실시간 로그:
  ```powershell
  Get-Content "C:\Program Files\NEXUS-Engine\logs\nexus.log" -Wait
  ```

---

## 🛠️ 고급 설정

### 환경 변수 (`.env` 파일)

```env
# === 필수 설정 ===
PORT=7100
DATA_DIR=C:\Users\YourName\Documents\NEXUS-Data
LOG_LEVEL=INFO

# === LLM 설정 ===
# Primary: Anthropic Claude
LLM_PRIMARY_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Fallback: OpenAI GPT
LLM_FALLBACK_PROVIDERS=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

# === TTS 설정 ===
# ElevenLabs (권장, 한국어 최적)
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Google Cloud TTS (대체)
GOOGLE_CLOUD_API_KEY=AIza...

# === RAG 설정 ===
RAG_FOLDER=/data/gdrive_mirror
RAG_AUTO_INGEST=true
RAG_SCHEDULE_HOUR=3
RAG_SCHEDULE_MINUTE=0

# === 멀티테넌트 설정 ===
DEFAULT_ORG_ID=default
DEFAULT_PROJECT_ID=default

# === 보안 설정 ===
API_KEY_REQUIRED=false
CALLBACK_SECRETS_JSON={}

# === 디버그 설정 ===
DEBUG=false
PRETTY_LOGS=false
```

---

## 🚨 문제 해결

### 문제 1: 서비스가 시작되지 않음
**증상**: `Get-Service NEXUSEngine` 실행 시 "Stopped" 상태

**해결 방법**:
1. 이벤트 뷰어 확인:
   ```powershell
   Get-EventLog -LogName Application -Source NEXUSEngine -Newest 10
   ```
2. `.env` 파일 검증:
   - API 키가 올바른지 확인
   - `DATA_DIR` 경로에 쓰기 권한이 있는지 확인
3. 수동 실행으로 디버깅:
   ```powershell
   cd "C:\Program Files\NEXUS-Engine"
   .\nexus-engine.exe
   ```

---

### 문제 2: Port 7100이 이미 사용 중
**증상**: `Address already in use`

**해결 방법**:
1. 사용 중인 프로세스 확인:
   ```powershell
   netstat -ano | findstr :7100
   ```
2. 프로세스 종료 (PID 확인 후):
   ```powershell
   Stop-Process -Id <PID> -Force
   ```
3. 또는 `.env`에서 다른 포트 사용:
   ```env
   PORT=7101
   ```

---

### 문제 3: API 호출 실패
**증상**: 세리아가 응답하지 않음

**해결 방법**:
1. API 키 유효성 검증:
   ```powershell
   curl http://localhost:7100/health
   ```
2. 로그 확인:
   ```powershell
   Get-Content "C:\Program Files\NEXUS-Engine\logs\nexus.log" | Select-String "error"
   ```
3. 키 갱신:
   - Anthropic: https://console.anthropic.com/settings/keys
   - OpenAI: https://platform.openai.com/api-keys

---

### 문제 4: 한글(HWP) 파일 RAG 실패
**증상**: HWP 파일이 검색되지 않음

**해결 방법**:
1. HWP를 PDF/TXT로 변환:
   - 한컴오피스에서 "다른 이름으로 저장" → PDF 선택
   - 동일한 파일명으로 저장 (예: `문서.hwp` → `문서.pdf`)
2. 같은 폴더에 배치:
   ```
   C:\Users\YourName\Documents\NEXUS-Data\
   ├── 보고서.hwp
   └── 보고서.pdf  ← 이 파일이 RAG에 인덱싱됨
   ```
3. 재인덱싱 트리거:
   ```powershell
   curl -X POST http://localhost:7100/ops/rag/ingest
   ```

---

## 📚 참고 자료

- **공식 홈페이지**: https://nexus-3bm.pages.dev
- **GitHub 저장소**: https://github.com/multipia-creator/nexus-on
- **백엔드 API 문서**: http://localhost:7100/docs (설치 후)
- **CLAUDE.md 규칙**: https://github.com/multipia-creator/nexus-on/blob/main/backend/CLAUDE.md

---

## 🎓 다음 단계

1. **프론트엔드 연결**
   - 브라우저에서 https://nexus-3bm.pages.dev 접속
   - 설정 → "로컬 엔진 연결" → `http://localhost:7100` 입력

2. **Google 계정 연결**
   - 대시보드 → "Google 연결" → OAuth 인증
   - Gmail, Calendar, Drive 권한 승인

3. **첫 번째 작업 시도**
   - 세리아에게 "내 메일함 요약해줘" 또는
   - "오늘 일정 알려줘" 요청

---

**설치 완료를 축하합니다! 🎉**

문제가 있으면 GitHub Issues에 제보해 주세요:
https://github.com/multipia-creator/nexus-on/issues
