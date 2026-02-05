"""
NEXUS-ON Public Pages v2 - Complete Edition
- Enhanced Intro page with developer bio
- Korean translations for modules
- Hero input UI (text + voice)
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("nexus_supervisor")
DATA_DIR = Path(__file__).parent.parent / "data"


def load_modules_data() -> List[Dict[str, Any]]:
    """Load modules.json data."""
    try:
        with open(DATA_DIR / "modules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load modules.json: {e}")
        return []


def load_benchmark_data() -> List[Dict[str, Any]]:
    """Load benchmark.json data."""
    try:
        with open(DATA_DIR / "benchmark.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load benchmark.json: {e}")
        return []


# 모듈 한글 번역 매핑
MODULE_TRANSLATIONS = {
    "Character Assistant Core": {
        "name_ko": "캐릭터 비서 코어",
        "tagline_ko": "Live2D 캐릭터 + Claude Sonnet 4.5 대화형 에이전트",
        "description_ko": "NEXUS의 심장부. Claude Sonnet 4.5 기반 Live2D 캐릭터 대화형 AI. 4가지 애니메이션 상태(Idle, Speaking, Listening, Thinking)로 시각적 피드백을 제공하며, 세션 간 멀티턴 컨텍스트를 유지합니다. SSE를 통한 실시간 스트리밍으로 UI를 에이전트 활동과 동기화합니다."
    },
    "Human-in-the-loop Approval System": {
        "name_ko": "승인 시스템",
        "tagline_ko": "GREEN/YELLOW/RED 위험도 기반 승인 워크플로우",
        "description_ko": "내장된 승인 게이트로 NEXUS가 무분별하게 행동하지 않도록 보장합니다. 모든 작업은 위험도 평가를 거칩니다: GREEN(자동 실행), YELLOW(알림), RED(명시적 승인 필요). 2단계 커밋 프로토콜로 사용자 동의 없이 외부 공유나 파일 삭제를 방지합니다."
    },
    "RAG Engine (Token Overlap)": {
        "name_ko": "RAG 엔진",
        "tagline_ko": "토큰 오버랩 기반 검색, 한글 HWP 네이티브 지원",
        "description_ko": "한국 학술 워크플로우에 최적화된 검색 증강 생성 엔진. 외부 변환 폴백을 통한 HWP(한글 워드 프로세서) 파일 네이티브 지원. 토큰 오버랩 기반 랭킹(간단하지만 효과적). 매일 03:00 KST 자동 수집. 증거 추적에는 doc_id, chunk_id, page, offset이 포함됩니다."
    },
    "YouTube Integration": {
        "name_ko": "YouTube 연동",
        "tagline_ko": "검색, 큐 관리, 임베디드 플레이어와 테넌트 격리",
        "description_ko": "연구 및 학습 워크플로우를 위한 완전한 YouTube 통합. YouTube Data API v3를 통한 검색(1시간 캐싱). Redis 기반 큐 관리(테넌트+세션 격리). 임베디드 플레이어 지원. Live2D 캐릭터가 비디오 큐에 추가될 때 콘텐츠를 설명합니다."
    },
    "Canvas Workspace": {
        "name_ko": "캔버스 작업공간",
        "tagline_ko": "로컬 초안 저장 및 다중 형식 내보내기",
        "description_ko": "문서 작성 및 편집을 위한 협업 작업 공간. 브라우저 로컬 스토리지(서버 업로드 없음). 다중 형식 내보내기(Markdown, TXT, JSON). 긴 초안 작성 중 Live2D 캐릭터가 Thinking 상태 표시. 빠른 메모 작성과 완전한 데이터 제어가 필요한 연구자를 위해 설계되었습니다."
    },
    "Multi-tenant Context": {
        "name_ko": "멀티테넌트 컨텍스트",
        "tagline_ko": "조직 ID 및 프로젝트 ID 범위 지정과 자격 증명 격리",
        "description_ko": "팀 배포를 위한 엔터프라이즈급 멀티테넌시. 모든 요청은 조직 ID 및 프로젝트 ID 헤더로 범위가 지정됩니다. 자격 증명 금고는 테넌트별로 API 키를 격리합니다. 비용 태깅 및 감사 추적으로 완전한 책임성을 보장합니다."
    },
    "Node Management (Windows Pairing)": {
        "name_ko": "노드 관리",
        "tagline_ko": "Windows 노드 페어링, 명령 큐, 리포트 업로드",
        "description_ko": "NEXUS를 Windows 데스크톱 환경으로 확장. 6자리 코드를 통한 노드 페어링(5분 TTL). HTTP 롱 폴링을 통한 명령 큐(인바운드 포트 불필요). 로컬 폴더 수집 및 리포트 업로드 지원. Live2D 캐릭터가 노드 작업 실행 중 Busy 글로우 표시."
    },
    "Observability Stack": {
        "name_ko": "관찰 가능성 스택",
        "tagline_ko": "Prometheus 메트릭과 correlation_id 전파",
        "description_ko": "프로덕션 배포를 위한 모니터링 및 관찰 가능성. 작업 생성, LLM 호출, 콜백 속도, 큐 실패에 대한 Prometheus 메트릭. Correlation_id 전파로 완전한 요청 추적 보장. 로그에서 PII 마스킹(이메일, 전화, API 키)."
    }
}


# i18n Translations (확장판)
TRANSLATIONS = {
    "ko": {
        "nav_home": "홈",
        "nav_intro": "소개",
        "nav_modules": "모듈",
        "nav_pricing": "가격",
        "nav_dashboard": "대시보드",
        "nav_canvas": "캔버스",
        "nav_login": "로그인",
        
        "hero_title": "잠들지 않는<br>당신만의 AI 캐릭터 비서",
        "hero_subtitle": "항상 깨어있는 당신만의 AI 캐릭터 비서",
        "hero_tagline": "Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만<br>중요한 결정은 항상 당신의 승인을 받습니다.",
        "hero_input_placeholder": "무엇을 도와드릴까요?",
        "hero_voice_button": "🎤 음성",
        "hero_text_button": "전송",
        "hero_cta_primary": "무료로 시작하기",
        "hero_cta_secondary": "데모 보기",
        
        "value1_title": "항상 화면에 존재",
        "value1_desc": "화면에 항상 존재하는 Live2D 캐릭터 비서.<br>5가지 상태로 현재 작업을 시각적으로 표현합니다.",
        "value2_title": "자율적이지만 통제 가능",
        "value2_desc": "자율적으로 작업을 수행하지만,<br>중요한 결정은 항상 당신의 승인을 받습니다.",
        "value3_title": "한국어 네이티브",
        "value3_desc": "한국어 네이티브 지원.<br>HWP 파일을 완벽하게 처리합니다.",
        
        "footer_text": "잠들지 않는 당신만의 AI 캐릭터 비서",
        "footer_dev": "개발: 남현우 교수, 서경대학교",
        
        # Intro page - 대폭 강화
        "intro_title": "NEXUS-ON 소개",
        "intro_subtitle": "신뢰할 수 있는 AI 파트너",
        
        "intro_vision_title": "비전",
        "intro_vision_content": "NEXUS-ON은 단순한 AI 도구가 아닙니다. 화면에 항상 존재하는 Live2D 캐릭터를 통해 사용자와 감정적 유대감을 형성하고, 자율적으로 작업을 수행하면서도 중요한 순간에는 반드시 사용자의 승인을 구하는 '신뢰할 수 있는 AI 파트너'를 지향합니다.",
        
        "intro_concept_title": "핵심 개념",
        "intro_concept1_title": "🎭 항상 존재하는 캐릭터",
        "intro_concept1_desc": "Live2D 캐릭터가 화면에 항상 존재하며, Idle, Listening, Thinking, Speaking, Busy 5가지 상태로 현재 작업을 시각적으로 표현합니다.",
        "intro_concept2_title": "🤖 자율적이지만 통제 가능",
        "intro_concept2_desc": "AI가 자율적으로 작업을 수행하지만, 위험도 평가(GREEN/YELLOW/RED)를 통해 중요한 결정은 반드시 사용자의 승인을 받습니다.",
        "intro_concept3_title": "🇰🇷 한국어 네이티브 지원",
        "intro_concept3_desc": "HWP(한글 문서) 파일을 네이티브로 지원하며, 한국 학술 및 기업 환경에 최적화된 RAG 엔진을 탑재했습니다.",
        "intro_concept4_title": "🏠 로컬 우선 아키텍처",
        "intro_concept4_desc": "민감한 데이터를 클라우드에 업로드하지 않고 로컬에서 처리하여, 데이터 주권과 보안을 최우선으로 합니다.",
        
        "intro_tech_title": "기술 스택",
        "intro_tech_frontend": "프론트엔드: React + TypeScript + Vite + TailwindCSS",
        "intro_tech_backend": "백엔드: FastAPI + Redis + RabbitMQ + Claude Sonnet 4.5",
        "intro_tech_live2d": "캐릭터: Live2D Cubism SDK + 5단계 애니메이션",
        "intro_tech_deployment": "배포: Docker Compose + Cloudflare Pages",
        
        "intro_developer_title": "개발자 소개",
        "intro_developer_name": "남현우 교수",
        "intro_developer_affiliation": "서경대학교 AI융합학부",
        "intro_developer_website": "웹사이트",
        "intro_developer_bio": "AI 에이전트 시스템과 Human-in-the-loop 연구에 전념하고 있으며, NEXUS-ON은 그 연구 결과물입니다. 자율 AI가 인간과 협력하는 새로운 방식을 제시하고, 한국 학술 및 산업 현장에 실질적으로 기여할 수 있는 AI 시스템을 개발하는 것이 목표입니다.",
        "intro_developer_research": "주요 연구 분야",
        "intro_developer_research_items": "AI 에이전트, Human-in-the-loop, RAG, 한국어 NLP",
        "intro_developer_contact": "문의",
        "intro_developer_contact_desc": "dxpia.com을 통해 연락 가능",
        
        "modules_title": "모듈 시스템",
        "modules_subtitle": "8개의 핵심 모듈로 구성된 강력한 AI 에이전트",
        "modules_count": "개 모듈",
        
        "pricing_title": "가격 플랜",
        "dashboard_title": "대시보드 프리뷰",
        "canvas_title": "캔버스 워크스페이스",
        "login_title": "다시 오신 것을 환영합니다",
    },
    "en": {
        "nav_home": "Home",
        "nav_intro": "About",
        "nav_modules": "Modules",
        "nav_pricing": "Pricing",
        "nav_dashboard": "Dashboard",
        "nav_canvas": "Canvas",
        "nav_login": "Login",
        
        "hero_title": "Your AI Character Assistant<br>That Never Sleeps",
        "hero_subtitle": "Your Always-On AI Character Assistant",
        "hero_tagline": "A Live2D character is always present on your screen, working autonomously<br>but always seeking your approval for important decisions.",
        "hero_input_placeholder": "How can I help you?",
        "hero_voice_button": "🎤 Voice",
        "hero_text_button": "Send",
        "hero_cta_primary": "Start Free",
        "hero_cta_secondary": "Watch Demo",
        
        "value1_title": "Always Visible",
        "value2_title": "Autonomous but Controlled",
        "value3_title": "Korean Native",
        
        "footer_text": "Your AI Character Assistant That Never Sleeps",
        "footer_dev": "Developed by Prof. Nam Hyunwoo, Seokyeong University",
        
        "intro_title": "About NEXUS-ON",
        "intro_subtitle": "Your Trusted AI Partner",
        "intro_vision_title": "Vision",
        "intro_concept_title": "Core Concepts",
        "intro_tech_title": "Tech Stack",
        "intro_developer_title": "About the Developer",
        "intro_developer_name": "Prof. Nam Hyunwoo",
        "intro_developer_website": "Website",
        
        "modules_title": "Module System",
        "modules_subtitle": "8 Core Modules Powering the AI Agent",
        "modules_count": "modules",
    }
}


def t(key: str, lang: str = "ko") -> str:
    """Translation helper."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ko"]).get(key, key)


def render_styles() -> str:
    """Render complete styles."""
    return """
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
      
      :root {
        --bg-primary: #FFFFFF;
        --text-primary: #111111;
        --text-secondary: #3C3C43;
        --text-tertiary: #6B6B73;
        --accent-primary: #2563EB;
        --accent-hover: #1D4ED8;
        --accent-soft: #EFF6FF;
        --border-default: #E6E6EA;
        --gradient-hero: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 30%, #DBEAFE 100%);
        --gradient-accent: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%);
        --status-green: #16A34A;
        --status-yellow: #F59E0B;
        --status-red: #DC2626;
        --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, sans-serif;
        --radius-card: 18px;
        --radius-pill: 999px;
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
        --duration-ui: 180ms;
      }
      
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { font-family: var(--font-sans); color: var(--text-primary); line-height: 1.6; }
      
      @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-20px); } }
      @keyframes pulse-glow { 0%, 100% { box-shadow: 0 0 20px rgba(37, 99, 235, 0.3); } 50% { box-shadow: 0 0 40px rgba(37, 99, 235, 0.6); } }
      
      nav { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-default); padding: 16px 24px; display: flex; align-items: center; gap: 24px; position: sticky; top: 0; z-index: 100; }
      .nav-brand { font-size: 24px; font-weight: 700; background: var(--gradient-accent); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-decoration: none; margin-right: auto; }
      .nav-link { color: var(--text-secondary); text-decoration: none; padding: 8px 16px; border-radius: 12px; transition: all var(--duration-ui); }
      .nav-link:hover { background: var(--accent-soft); color: var(--accent-primary); }
      .nav-link.active { background: var(--gradient-accent); color: white; }
      .lang-toggle { padding: 8px 16px; border: 2px solid var(--accent-primary); background: white; color: var(--accent-primary); border-radius: var(--radius-pill); font-weight: 600; cursor: pointer; transition: all var(--duration-ui); }
      .lang-toggle:hover { background: var(--accent-primary); color: white; }
      
      .hero-world-class { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--gradient-hero); padding: 48px 24px; }
      .hero-content { max-width: 1200px; margin: 0 auto; text-align: center; }
      .hero-character { width: 400px; height: 480px; margin: 0 auto 32px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(239, 246, 255, 0.8) 100%); backdrop-filter: blur(20px); border: 2px solid rgba(255, 255, 255, 0.5); border-radius: var(--radius-card); box-shadow: var(--shadow-xl); display: flex; align-items: center; justify-content: center; animation: float 4s ease-in-out infinite; position: relative; }
      .hero-character::before { content: ''; position: absolute; inset: -2px; border-radius: var(--radius-card); padding: 2px; background: var(--gradient-accent); -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask-composite: exclude; animation: pulse-glow 2s ease-in-out infinite; }
      .character-placeholder { font-size: 120px; opacity: 0.6; }
      .character-state { position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%); background: rgba(37, 99, 235, 0.9); color: white; padding: 8px 16px; border-radius: var(--radius-pill); font-size: 12px; font-weight: 600; }
      
      .hero-input-box { max-width: 600px; margin: 32px auto; background: white; border-radius: var(--radius-pill); padding: 8px; box-shadow: var(--shadow-md); display: flex; align-items: center; gap: 8px; }
      .hero-input { flex: 1; border: none; padding: 12px 20px; font-size: 16px; outline: none; font-family: var(--font-sans); }
      .hero-voice-btn { background: var(--accent-soft); color: var(--accent-primary); border: none; padding: 12px 20px; border-radius: var(--radius-pill); font-weight: 600; cursor: pointer; transition: all var(--duration-ui); }
      .hero-voice-btn:hover { background: var(--accent-primary); color: white; }
      .hero-send-btn { background: var(--gradient-accent); color: white; border: none; padding: 12px 24px; border-radius: var(--radius-pill); font-weight: 600; cursor: pointer; }
      
      .hero-title { font-size: 48px; font-weight: 700; margin-bottom: 16px; line-height: 1.2; }
      .hero-subtitle { font-size: 24px; color: var(--text-secondary); margin-bottom: 32px; font-weight: 500; }
      .hero-cta-group { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 32px; }
      .btn-glass-primary { display: inline-block; padding: 16px 32px; background: var(--gradient-accent); color: white; border-radius: var(--radius-pill); font-size: 18px; font-weight: 600; text-decoration: none; box-shadow: var(--shadow-md); transition: all var(--duration-ui); }
      .btn-glass-primary:hover { transform: translateY(-3px); box-shadow: var(--shadow-xl); }
      
      .core-values { padding: 80px 24px; }
      .core-values-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 32px; max-width: 1200px; margin: 0 auto; }
      .value-card { background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: var(--radius-card); padding: 32px; box-shadow: var(--shadow-md); transition: all var(--duration-ui); }
      .value-card:hover { transform: translateY(-8px); box-shadow: var(--shadow-xl); }
      .value-icon { font-size: 64px; margin-bottom: 16px; }
      .value-title { font-size: 24px; font-weight: 600; margin-bottom: 12px; }
      
      .container { max-width: 1240px; margin: 0 auto; padding: 48px 24px; }
      .section-title { font-size: 32px; font-weight: 700; margin-bottom: 32px; text-align: center; }
      .section-subtitle { font-size: 18px; color: var(--text-secondary); max-width: 700px; margin: 0 auto 48px; text-align: center; line-height: 1.75; }
      
      .developer-card { background: var(--accent-soft); border-radius: var(--radius-card); padding: 40px; margin: 40px 0; }
      .developer-name { font-size: 28px; font-weight: 700; color: var(--accent-primary); margin-bottom: 8px; }
      .developer-link { color: var(--accent-primary); text-decoration: none; font-weight: 600; }
      .developer-link:hover { text-decoration: underline; }
      
      footer { background: #F7F7F8; padding: 48px 24px; text-align: center; border-top: 1px solid var(--border-default); }
      footer p { color: var(--text-tertiary); font-size: 12px; }
      
      @media (max-width: 768px) {
        .hero-character { width: 280px; height: 320px; }
        .character-placeholder { font-size: 80px; }
        .hero-title { font-size: 32px; }
      }
    </style>
    """


def render_navigation(current_page: str = "", lang: str = "ko") -> str:
    """Render navigation."""
    nav_items = [
        (t("nav_home", lang), "/"),
        (t("nav_intro", lang), "/intro"),
        (t("nav_modules", lang), "/modules"),
        (t("nav_pricing", lang), "/pricing"),
        (t("nav_dashboard", lang), "/dashboard-preview"),
        (t("nav_canvas", lang), "/canvas-preview"),
        (t("nav_login", lang), "/login"),
    ]
    
    lang_label = "EN" if lang == "ko" else "한국어"
    nav_html = "<nav><a href='/' class='nav-brand'>NEXUS-ON</a>"
    for label, path in nav_items:
        active = "active" if path == current_page else ""
        nav_html += f"<a href='{path}?lang={lang}' class='nav-link {active}'>{label}</a>"
    nav_html += f"""<button class='lang-toggle' onclick='toggleLanguage()'>{lang_label}</button>
    <script>
    function toggleLanguage() {{
        const url = new URL(window.location.href);
        const currentLang = url.searchParams.get('lang') || 'ko';
        const newLang = currentLang === 'ko' ? 'en' : 'ko';
        url.searchParams.set('lang', newLang);
        window.location.href = url.toString();
    }}
    </script></nav>"""
    return nav_html


def render_footer(lang: str = "ko") -> str:
    """Render footer."""
    return f"""
    <footer>
        <p>&copy; 2026 NEXUS-ON. {t("footer_text", lang)}</p>
        <p>{t("footer_dev", lang)}</p>
    </footer>
    """


def landing_page(lang: str = "ko") -> str:
    """Landing page with Hero input UI."""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS-ON | {t("hero_subtitle", lang)}</title>
    {render_styles()}
</head>
<body>
    {render_navigation("/", lang)}
    
    <section class="hero-world-class">
        <div class="hero-content">
            <div class="hero-character">
                <div class="character-placeholder">🎭</div>
                <div class="character-state">Idle</div>
            </div>
            
            <h1 class="hero-title">{t("hero_title", lang)}</h1>
            <p class="hero-subtitle">{t("hero_subtitle", lang)}</p>
            
            <!-- AI Input Box -->
            <div class="hero-input-box">
                <input type="text" class="hero-input" placeholder="{t("hero_input_placeholder", lang)}">
                <button class="hero-voice-btn">{t("hero_voice_button", lang)}</button>
                <button class="hero-send-btn">{t("hero_text_button", lang)}</button>
            </div>
            
            <div class="hero-cta-group">
                <a href="/signup?lang={lang}" class="btn-glass-primary">{t("hero_cta_primary", lang)}</a>
                <a href="#demo" class="btn-glass-primary" style="background: rgba(255,255,255,0.8); color: var(--accent-primary); border: 2px solid var(--accent-primary);">{t("hero_cta_secondary", lang)}</a>
            </div>
        </div>
    </section>
    
    <section class="core-values">
        <div class="core-values-grid">
            <div class="value-card">
                <div class="value-icon">🎭</div>
                <h3 class="value-title">{t("value1_title", lang)}</h3>
                <p>{t("value1_desc", lang) if lang == "ko" else "Always present Live2D character on screen with 5 visual states."}</p>
            </div>
            <div class="value-card">
                <div class="value-icon">🤖</div>
                <h3 class="value-title">{t("value2_title", lang)}</h3>
                <p>{t("value2_desc", lang) if lang == "ko" else "Autonomous execution with required approval for critical decisions."}</p>
            </div>
            <div class="value-card">
                <div class="value-icon">🇰🇷</div>
                <h3 class="value-title">{t("value3_title", lang)}</h3>
                <p>{t("value3_desc", lang) if lang == "ko" else "Native Korean support with HWP file handling."}</p>
            </div>
        </div>
    </section>
    
    {render_footer(lang)}
</body>
</html>"""


def intro_page(lang: str = "ko") -> str:
    """Enhanced intro page with developer bio."""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t("intro_title", lang)} - NEXUS-ON</title>
    {render_styles()}
</head>
<body>
    {render_navigation("/intro", lang)}
    
    <div class="container">
        <h1 class="section-title">{t("intro_title", lang)}</h1>
        <p class="section-subtitle">{t("intro_subtitle", lang)}</p>
        
        <div style="max-width: 900px; margin: 0 auto;">
            <!-- Vision -->
            <div style="background: var(--accent-soft); padding: 32px; border-radius: var(--radius-card); margin-bottom: 32px;">
                <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 16px; color: var(--accent-primary);">
                    {t("intro_vision_title", lang)}
                </h2>
                <p style="line-height: 1.75; font-size: 16px;">
                    {t("intro_vision_content", lang) if lang == "ko" else "NEXUS-ON is not just an AI tool. It aims to be a 'trusted AI partner' that forms emotional bonds with users through an always-present Live2D character, working autonomously while always seeking user approval at critical moments."}
                </p>
            </div>
            
            <!-- Core Concepts -->
            <h2 style="font-size: 24px; font-weight: 600; margin: 40px 0 24px; text-align: center;">
                {t("intro_concept_title", lang)}
            </h2>
            <div class="core-values-grid" style="margin-bottom: 40px;">
                <div class="value-card" style="text-align: left;">
                    <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 12px;">{t("intro_concept1_title", lang)}</h3>
                    <p style="font-size: 14px; line-height: 1.6;">{t("intro_concept1_desc", lang)}</p>
                </div>
                <div class="value-card" style="text-align: left;">
                    <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 12px;">{t("intro_concept2_title", lang)}</h3>
                    <p style="font-size: 14px; line-height: 1.6;">{t("intro_concept2_desc", lang)}</p>
                </div>
                <div class="value-card" style="text-align: left;">
                    <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 12px;">{t("intro_concept3_title", lang)}</h3>
                    <p style="font-size: 14px; line-height: 1.6;">{t("intro_concept3_desc", lang)}</p>
                </div>
                <div class="value-card" style="text-align: left;">
                    <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 12px;">{t("intro_concept4_title", lang)}</h3>
                    <p style="font-size: 14px; line-height: 1.6;">{t("intro_concept4_desc", lang)}</p>
                </div>
            </div>
            
            <!-- Tech Stack -->
            <div style="background: #F7F7F8; padding: 32px; border-radius: var(--radius-card); margin-bottom: 32px;">
                <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 16px;">
                    {t("intro_tech_title", lang)}
                </h2>
                <ul style="list-style: none; padding: 0; line-height: 2;">
                    <li>✅ {t("intro_tech_frontend", lang)}</li>
                    <li>✅ {t("intro_tech_backend", lang)}</li>
                    <li>✅ {t("intro_tech_live2d", lang)}</li>
                    <li>✅ {t("intro_tech_deployment", lang)}</li>
                </ul>
            </div>
            
            <!-- Developer Bio -->
            <div class="developer-card">
                <h2 style="font-size: 24px; font-weight: 600; margin-bottom: 24px;">
                    {t("intro_developer_title", lang)}
                </h2>
                <div class="developer-name">{t("intro_developer_name", lang)}</div>
                <p style="color: var(--text-secondary); margin-bottom: 8px;">{t("intro_developer_affiliation", lang)}</p>
                <p style="margin-bottom: 16px;">
                    {t("intro_developer_website", lang)}: <a href="https://dxpia.com" target="_blank" class="developer-link">dxpia.com</a>
                </p>
                <p style="line-height: 1.75; margin-bottom: 16px;">
                    {t("intro_developer_bio", lang) if lang == "ko" else "Dedicated to research in AI agent systems and Human-in-the-loop. NEXUS-ON is the result of that research. The goal is to present a new way for autonomous AI to collaborate with humans and develop AI systems that can practically contribute to Korean academic and industrial fields."}
                </p>
                <p style="font-weight: 600; margin-bottom: 8px;">{t("intro_developer_research", lang)}</p>
                <p>{t("intro_developer_research_items", lang) if lang == "ko" else "AI Agents, Human-in-the-loop, RAG, Korean NLP"}</p>
                <p style="margin-top: 16px;">
                    <strong>{t("intro_developer_contact", lang)}:</strong> {t("intro_developer_contact_desc", lang) if lang == "ko" else "Available through dxpia.com"}
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 48px;">
                <a href="/modules?lang={lang}" class="btn-glass-primary">{t("nav_modules", lang)}</a>
            </div>
        </div>
    </div>
    
    {render_footer(lang)}
</body>
</html>"""


def modules_page(lang: str = "ko") -> str:
    """Modules page with Korean translations."""
    modules = load_modules_data()
    
    modules_html = ""
    for module in modules:
        name = module.get('name', 'Unknown Module')
        status_color = {
            "stable": "var(--status-green)",
            "beta": "var(--status-yellow)",
            "alpha": "var(--status-red)"
        }.get(module.get("status", "alpha"), "var(--status-red)")
        
        # 한글 번역 가져오기
        if lang == "ko" and name in MODULE_TRANSLATIONS:
            trans = MODULE_TRANSLATIONS[name]
            display_name = trans.get("name_ko", name)
            tagline = trans.get("tagline_ko", module.get('tagline', ''))
            description = trans.get("description_ko", module.get('description', ''))
        else:
            display_name = name
            tagline = module.get('tagline', '')
            description = module.get('description', '')
        
        modules_html += f"""
        <div class="value-card" style="text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="font-size: 48px;">{module.get('icon', '📦')}</div>
                <div style="background: {status_color}; color: white; padding: 4px 12px; border-radius: var(--radius-pill); font-size: 12px; font-weight: 600;">
                    {module.get('status_label', module.get('status', 'Unknown'))}
                </div>
            </div>
            <h3 style="font-size: 24px; font-weight: 600; margin-bottom: 8px;">
                {display_name}
            </h3>
            <p style="font-size: 12px; color: var(--text-tertiary); margin-bottom: 16px;">
                {tagline}
            </p>
            <p style="font-size: 14px; line-height: 1.6;">
                {description}
            </p>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t("modules_title", lang)} - NEXUS-ON</title>
    {render_styles()}
</head>
<body>
    {render_navigation("/modules", lang)}
    
    <div class="container">
        <h1 class="section-title">{t("modules_title", lang)}</h1>
        <p class="section-subtitle">{t("modules_subtitle", lang)}</p>
        
        <div style="text-align: center; margin-bottom: 48px;">
            <span style="background: var(--gradient-accent); color: white; padding: 8px 24px; border-radius: var(--radius-pill); font-weight: 600;">
                {len(modules)} {t("modules_count", lang)}
            </span>
        </div>
        
        <div class="core-values-grid">
            {modules_html}
        </div>
    </div>
    
    {render_footer(lang)}
</body>
</html>"""


# 나머지 페이지들은 간단한 플레이스홀더
def pricing_page(lang: str = "ko") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{t("pricing_title", lang)}</title>{render_styles()}</head>
<body>{render_navigation("/pricing", lang)}
<div class="container"><h1 class="section-title">{t("pricing_title", lang)}</h1>
<p style="text-align:center; padding:100px 0;">구현 예정...</p></div>
{render_footer(lang)}</body></html>"""


def dashboard_preview_page(lang: str = "ko") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{t("dashboard_title", lang)}</title>{render_styles()}</head>
<body>{render_navigation("/dashboard-preview", lang)}
<div class="container"><h1 class="section-title">{t("dashboard_title", lang)}</h1>
<p style="text-align:center; padding:100px 0;">구현 예정...</p></div>
{render_footer(lang)}</body></html>"""


def canvas_preview_page(lang: str = "ko") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{t("canvas_title", lang)}</title>{render_styles()}</head>
<body>{render_navigation("/canvas-preview", lang)}
<div class="container"><h1 class="section-title">{t("canvas_title", lang)}</h1>
<p style="text-align:center; padding:100px 0;">구현 예정...</p></div>
{render_footer(lang)}</body></html>"""


def login_page(lang: str = "ko") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{t("login_title", lang)}</title>{render_styles()}</head>
<body>{render_navigation("/login", lang)}
<div class="container"><h1 class="section-title">{t("login_title", lang)}</h1>
<p style="text-align:center; padding:100px 0;">구현 예정...</p></div>
{render_footer(lang)}</body></html>"""
