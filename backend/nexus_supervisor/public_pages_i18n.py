"""
Public pages with i18n support (Korean/English toggle).
WORLD-CLASS AI Character Assistant Service.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("nexus_supervisor")

# Path to data directory
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


# i18n Translations
TRANSLATIONS = {
    "ko": {
        "nav_home": "홈",
        "hero_input_placeholder": "무엇을 도와드릴까요?",
        "hero_voice_button": "음성 입력",
        "hero_text_button": "전송",
        "voice_not_supported": "이 브라우저는 음성 인식을 지원하지 않습니다.",
        
        "nav_intro": "소개",
        "nav_modules": "모듈",
        "nav_pricing": "가격",
        "nav_dashboard": "대시보드",
        "nav_canvas": "캔버스",
        "nav_login": "로그인",
        
        "hero_title": "잠들지 않는<br>당신만의 AI 캐릭터 비서",
        "hero_subtitle": "항상 깨어있는 당신만의 AI 캐릭터 비서",
        "hero_tagline": "Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만<br>중요한 결정은 항상 당신의 승인을 받습니다.",
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
        
        "pricing_title": "가격 플랜",
        "pricing_subtitle": "당신의 필요에 맞는 플랜을 선택하세요.<br>언제든지 업그레이드 가능합니다.",
        "pricing_coming": "가격 플랜 페이지 구현 중...",
        "pricing_plans": "FREE / PRO / ENTERPRISE 플랜 제공 예정",
        
        "dashboard_title": "대시보드 프리뷰",
        "dashboard_subtitle": "실시간으로 업데이트되는 AI 비서의 작업 현황을 확인하세요.",
        "dashboard_coming": "대시보드 프리뷰 페이지 구현 중...",
        "dashboard_features": "3-Column Layout | 실시간 SSE 업데이트 | Live2D 상태 변화",
        
        "canvas_title": "캔버스 워크스페이스",
        "canvas_subtitle": "AI 비서와 함께 문서를 작성하고 편집하세요.",
        "canvas_coming": "캔버스 워크스페이스 페이지 구현 중...",
        "canvas_features": "Markdown Editor | AI 제안 | Multi-format Export",
        
        "login_title": "다시 오신 것을 환영합니다",
        "login_subtitle": "다시 만나서 반가워요!",
        "login_email": "이메일",
        "login_password": "비밀번호",
        "login_button": "로그인",
        "login_no_account": "계정이 없으신가요?",
        "login_signup": "회원가입",
        
        "intro_title": "NEXUS-ON 소개",
        "intro_subtitle": "Live2D 캐릭터 비서 기반의 자율 AI 에이전트 시스템",
        "intro_section1_title": "핵심 개념",
        "intro_section1_content": "NEXUS-ON은 Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만 중요한 결정은 항상 사용자의 승인을 받는 혁신적인 AI 비서 시스템입니다.",
        "intro_section2_title": "차별화 포인트",
        "intro_diff1": "시각적 존재감: 항상 화면에 존재하는 Live2D 캐릭터",
        "intro_diff2": "통제된 자율성: 자율적이지만 중요 결정은 승인 필요",
        "intro_diff3": "한국어 최적화: HWP 파일 네이티브 지원",
        "intro_diff4": "로컬 우선: 클라우드 업로드 없는 안전한 데이터 처리",
        
        "modules_title": "모듈 시스템",
        "modules_subtitle": "8개의 핵심 모듈로 구성된 강력한 AI 에이전트",
        "modules_count": "개 모듈",
        
        # Developer Profile Section
        "developer_title": "개발자 소개",
        "developer_name": "남현우 교수",
        "developer_affiliation": "서경대학교 컴퓨터공학과",
        "developer_research_title": "연구 분야",
        "developer_research_1": "AI 에이전트 시스템 및 멀티 에이전트 오케스트레이션",
        "developer_research_2": "Human-in-the-loop AI 인터페이스 설계",
        "developer_research_3": "자율 시스템의 안전성 및 신뢰성",
        "developer_research_4": "소프트웨어 공학과 AI 융합",
        "developer_research_5": "한국어 문서 처리 및 RAG 시스템",
        "developer_vision_title": "프로젝트 비전",
        "developer_vision_content": "NEXUS-ON은 인간-AI 협업의 새로운 패러다임을 제시합니다. Local-first 아키텍처로 데이터 안전을 보장하고, HWP를 포함한 한국어 문서를 완벽하게 처리하며, 항상 사용자의 통제 하에서 작동하는 투명하고 신뢰할 수 있는 AI 비서를 목표로 합니다.",
        "developer_philosophy_title": "개발 철학",
        "developer_philosophy_1": "Local-first: 클라우드 업로드 없는 안전한 데이터 처리",
        "developer_philosophy_2": "Human oversight: 중요한 결정은 항상 사용자 승인",
        "developer_philosophy_3": "Fail-safe: 오류 발생 시 안전한 기본 상태로 복귀",
        "developer_philosophy_4": "Open by design: 교육 및 연구를 위한 오픈소스 프로젝트",
        "developer_contact_title": "연락처",
        "developer_contact_dept": "서경대학교 컴퓨터공학과",
        "developer_contact_project": "NEXUS-ON 오픈소스 프로젝트",
    },
    "en": {
        "nav_home": "Home",
        "nav_intro": "About",
        "nav_modules": "Modules",
        "nav_pricing": "Pricing",
        "nav_dashboard": "Dashboard",
        "nav_canvas": "Canvas",
        "nav_login": "Login",
        
        "hero_input_placeholder": "What can I help you with?",
        "hero_voice_button": "Voice Input",
        "hero_text_button": "Send",
        "voice_not_supported": "Your browser does not support speech recognition.",
        
        "hero_title": "Your AI Character Assistant<br>That Never Sleeps",
        "hero_subtitle": "Your Always-On AI Character Assistant",
        "hero_tagline": "A Live2D character is always present on your screen, working autonomously<br>but always seeking your approval for important decisions.",
        "hero_cta_primary": "Start Free",
        "hero_cta_secondary": "Watch Demo",
        
        "value1_title": "Always Visible",
        "value1_desc": "A Live2D character assistant always present on screen.<br>5 states visually represent current tasks.",
        "value2_title": "Autonomous but Controlled",
        "value2_desc": "Works autonomously,<br>but always requires your approval for critical decisions.",
        "value3_title": "Korean Native",
        "value3_desc": "Native Korean language support.<br>Handles HWP files perfectly.",
        
        "footer_text": "Your AI Character Assistant That Never Sleeps",
        "footer_dev": "Developed by Prof. Nam Hyunwoo, Seokyeong University",
        
        "pricing_title": "Pricing Plans",
        "pricing_subtitle": "Choose the plan that fits your needs.<br>Upgrade anytime.",
        "pricing_coming": "Pricing page under construction...",
        "pricing_plans": "FREE / PRO / ENTERPRISE plans coming soon",
        
        "dashboard_title": "Dashboard Preview",
        "dashboard_subtitle": "Monitor your AI assistant's real-time activity.",
        "dashboard_coming": "Dashboard preview page under construction...",
        "dashboard_features": "3-Column Layout | Real-time SSE Updates | Live2D State Changes",
        
        "canvas_title": "Canvas Workspace",
        "canvas_subtitle": "Create and edit documents with your AI assistant.",
        "canvas_coming": "Canvas workspace page under construction...",
        "canvas_features": "Markdown Editor | AI Suggestions | Multi-format Export",
        
        "login_title": "Welcome Back",
        "login_subtitle": "Good to see you again!",
        "login_email": "Email",
        "login_password": "Password",
        "login_button": "Sign In",
        "login_no_account": "Don't have an account?",
        "login_signup": "Sign Up",
        
        # Developer Profile Section
        "developer_title": "About Developer",
        "developer_name": "Prof. Nam Hyunwoo",
        "developer_affiliation": "Seokyeong University, Computer Science Dept.",
        "developer_research_title": "Research Interests",
        "developer_research_1": "AI Agent Systems & Multi-agent Orchestration",
        "developer_research_2": "Human-in-the-loop AI Interface Design",
        "developer_research_3": "Safety and Reliability of Autonomous Systems",
        "developer_research_4": "Software Engineering & AI Integration",
        "developer_research_5": "Korean Document Processing & RAG Systems",
        "developer_vision_title": "Project Vision",
        "developer_vision_content": "NEXUS-ON presents a new paradigm of human-AI collaboration. With a local-first architecture ensuring data safety, perfect processing of Korean documents including HWP, and transparent operation always under user control, we aim to create a trustworthy AI assistant.",
        "developer_philosophy_title": "Development Philosophy",
        "developer_philosophy_1": "Local-first: Secure data processing without cloud uploads",
        "developer_philosophy_2": "Human oversight: Critical decisions always require user approval",
        "developer_philosophy_3": "Fail-safe: Return to safe default state on errors",
        "developer_philosophy_4": "Open by design: Open-source project for education and research",
        "developer_contact_title": "Contact",
        "developer_contact_dept": "Seokyeong University, Computer Science Dept.",
        "developer_contact_project": "NEXUS-ON Open Source Project",
    }
}


def t(key: str, lang: str = "ko") -> str:
    """Translation helper."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ko"]).get(key, key)


def render_live2d_component(page_state: str = 'idle') -> str:
    """
    Render Live2D character component with real Live2D SDK.
    
    Args:
        page_state: Initial character state (idle/listening/thinking/speaking/busy)
    
    Returns:
        HTML string for Live2D component
    """
    return f'''
    <!-- Live2D Character Container -->
    <div id="live2d-container" class="live2d-container loading" data-status="{page_state}">
        <!-- Live2D canvas will be injected here -->
    </div>

    <!-- Live2D Styles -->
    <link rel="stylesheet" href="/static/css/live2d.css">

    <!-- PIXI.js v7.x (Required for Live2D) -->
    <script src="https://cdn.jsdelivr.net/npm/pixi.js@7.3.2/dist/pixi.min.js"></script>
    
    <!-- Live2D Cubism Core -->
    <script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
    
    <!-- pixi-live2d-display (LOCAL) -->
    <script src="/static/js/pixi-live2d-display.min.js"></script>

    <!-- Live2D Manager -->
    <script src="/static/js/live2d-loader.js"></script>

    <!-- TTS Manager -->
    <script src="/static/js/tts-manager.js"></script>

    <!-- Initialize Live2D -->
    <script>
        let live2dManager = null;
        
        window.addEventListener('DOMContentLoaded', () => {{
            try {{
                const container = document.getElementById('live2d-container');
                if (!container) {{
                    console.error('❌ Live2D container not found');
                    return;
                }}

                // Show loading state
                container.classList.add('loading');

                // Initialize Live2D Manager
                setTimeout(() => {{
                    try {{
                        live2dManager = new Live2DManager(
                            'live2d-container',
                            '/live2d/haru_greeter_t05.model3.json'
                        );
                        
                        // Set initial state
                        setTimeout(() => {{
                            if (live2dManager && live2dManager.model) {{
                                live2dManager.setState('{page_state}');
                                container.classList.remove('loading');
                                console.log('✅ Live2D initialized with state: {page_state}');
                            }}
                        }}, 1000);
                        
                    }} catch (error) {{
                        console.error('❌ Live2D initialization error:', error);
                        container.classList.remove('loading');
                        container.classList.add('error');
                    }}
                }}, 500);
                
            }} catch (error) {{
                console.error('❌ Live2D setup error:', error);
            }}
        }});
        
        // Make globally available for state changes
        window.nexusCharacter = function() {{
            return {{
                setState: (state) => {{
                    if (live2dManager) {{
                        live2dManager.setState(state);
                    }}
                }},
                hide: () => {{
                    const container = document.getElementById('live2d-container');
                    if (container) container.style.display = 'none';
                }},
                show: () => {{
                    const container = document.getElementById('live2d-container');
                    if (container) container.style.display = 'block';
                }}
            }};
        }};
    </script>
    '''



def render_world_class_styles() -> str:
    """NEXUS UI v2.0 - World-Class Design System with i18n support."""
    return """
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
      
      :root {
        /* Colors */
        --bg-primary: #FFFFFF;
        --bg-secondary: #F7F7F8;
        --text-primary: #111111;
        --text-secondary: #3C3C43;
        --text-tertiary: #6B6B73;
        --accent-primary: #2563EB;
        --accent-hover: #1D4ED8;
        --accent-soft: #EFF6FF;
        --border-default: #E6E6EA;
        --border-strong: #D1D1D6;
        
        /* Gradients */
        --gradient-hero: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 30%, #DBEAFE 100%);
        --gradient-accent: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%);
        --gradient-card-hover: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(59, 130, 246, 0.1) 100%);
        
        /* Status Colors */
        --status-green: #16A34A;
        --status-yellow: #F59E0B;
        --status-red: #DC2626;
        
        /* Typography */
        --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
        --text-3xl: 48px;
        --text-2xl: 32px;
        --text-xl: 24px;
        --text-lg: 18px;
        --text-base: 14px;
        --text-sm: 12px;
        
        /* Spacing */
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-6: 24px;
        --space-8: 32px;
        --space-12: 48px;
        --space-16: 64px;
        --space-20: 80px;
        
        /* Radius */
        --radius-card: 18px;
        --radius-control: 12px;
        --radius-pill: 999px;
        
        /* Shadow */
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
        
        /* Motion */
        --duration-ui: 180ms;
        --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
      }
      
      * { box-sizing: border-box; margin: 0; padding: 0; }
      
      body {
        font-family: var(--font-sans);
        font-size: var(--text-base);
        color: var(--text-primary);
        background: var(--bg-primary);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
      }
      
      /* Animations */
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
      }
      
      @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(37, 99, 235, 0.3); }
        50% { box-shadow: 0 0 40px rgba(37, 99, 235, 0.6); }
      }
      
      @keyframes slide-in-up {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      /* Navigation */
      nav {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-default);
        padding: var(--space-4) var(--space-6);
        display: flex;
        align-items: center;
        gap: var(--space-6);
        position: sticky;
        top: 0;
        z-index: 100;
      }
      
      .nav-brand {
        font-size: var(--text-xl);
        font-weight: 700;
        background: var(--gradient-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-decoration: none;
        margin-right: auto;
      }
      
      .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: var(--text-base);
        font-weight: 500;
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-control);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .nav-link:hover {
        background: var(--accent-soft);
        color: var(--accent-primary);
        transform: translateY(-2px);
      }
      
      .nav-link.active {
        background: var(--gradient-accent);
        color: #FFFFFF;
      }
      
      /* Language Toggle Button */
      .lang-toggle {
        padding: var(--space-2) var(--space-4);
        border: 2px solid var(--accent-primary);
        background: white;
        color: var(--accent-primary);
        border-radius: var(--radius-pill);
        font-size: var(--text-sm);
        font-weight: 600;
        cursor: pointer;
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .lang-toggle:hover {
        background: var(--accent-primary);
        color: white;
        transform: scale(1.05);
      }
      
      /* Hero Section */
      .hero-world-class {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--gradient-hero);
        position: relative;
        overflow: hidden;
        padding: var(--space-12) var(--space-6);
      }
      
      .hero-content {
        max-width: 1200px;
        margin: 0 auto;
        text-align: center;
        position: relative;
        z-index: 2;
        animation: slide-in-up 0.8s var(--ease-out);
      }
      
      .hero-character {
        width: 400px;
        height: 480px;
        margin: 0 auto var(--space-8);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(239, 246, 255, 0.8) 100%);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.5);
        border-radius: var(--radius-card);
        box-shadow: var(--shadow-xl);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: float 4s ease-in-out infinite;
        position: relative;
      }
      
      .hero-character::before {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: var(--radius-card);
        padding: 2px;
        background: var(--gradient-accent);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        animation: pulse-glow 2s ease-in-out infinite;
      }
      
      .character-placeholder {
        font-size: 120px;
        opacity: 0.6;
      }
      
      .character-state {
        position: absolute;
        bottom: var(--space-4);
        left: 50%;
        transform: translateX(-50%);
        background: rgba(37, 99, 235, 0.9);
        color: white;
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-pill);
        font-size: var(--text-sm);
        font-weight: 600;
      }
      
      .hero-title {
        font-size: var(--text-3xl);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-4);
        line-height: 1.2;
      }
      
      .hero-subtitle {
        font-size: var(--text-xl);
        color: var(--text-secondary);
        margin-bottom: var(--space-8);
        font-weight: 500;
      }
      
      .hero-tagline {
        font-size: var(--text-lg);
        color: var(--text-tertiary);
        max-width: 700px;
        margin: 0 auto var(--space-8);
        line-height: 1.75;
      }
      
      /* Hero Input Container (AI Chat) */
      .hero-input-container {
        max-width: 700px;
        margin: 0 auto var(--space-8);
        padding: 0 var(--space-4);
      }
      
      .hero-input-wrapper {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(37, 99, 235, 0.15);
        border-radius: var(--radius-control);
        padding: var(--space-2);
        box-shadow: var(--shadow-lg);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .hero-input-wrapper:focus-within {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), var(--shadow-lg);
      }
      
      .hero-input {
        flex: 1;
        border: none;
        background: transparent;
        font-size: var(--text-base);
        color: var(--text-primary);
        padding: var(--space-3) var(--space-4);
        outline: none;
        font-family: var(--font-sans);
      }
      
      .hero-input::placeholder {
        color: var(--text-tertiary);
      }
      
      .hero-voice-btn,
      .hero-send-btn {
        width: 44px;
        height: 44px;
        border: none;
        border-radius: var(--radius-control);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all var(--duration-ui) var(--ease-out);
        font-size: 20px;
      }
      
      .hero-voice-btn {
        background: var(--bg-secondary);
        color: var(--text-primary);
      }
      
      .hero-voice-btn:hover {
        background: var(--accent-soft);
        transform: scale(1.05);
      }
      
      .hero-voice-btn:active {
        transform: scale(0.95);
      }
      
      .hero-send-btn {
        background: var(--gradient-accent);
        color: white;
        font-weight: 600;
      }
      
      .hero-send-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
      }
      
      .hero-send-btn:active {
        transform: scale(0.95);
      }
      
      .hero-cta-group {
        display: flex;
        gap: var(--space-4);
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
      }
      
      /* Glassmorphism Buttons */
      .btn-glass-primary {
        display: inline-block;
        padding: var(--space-4) var(--space-8);
        background: var(--gradient-accent);
        color: white;
        border-radius: var(--radius-pill);
        font-size: var(--text-lg);
        font-weight: 600;
        text-decoration: none;
        box-shadow: var(--shadow-lg);
        transition: all var(--duration-ui) var(--ease-out);
        border: none;
        cursor: pointer;
      }
      
      .btn-glass-primary:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
      }
      
      .btn-glass-secondary {
        display: inline-block;
        padding: var(--space-4) var(--space-8);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        color: var(--accent-primary);
        border: 2px solid var(--accent-primary);
        border-radius: var(--radius-pill);
        font-size: var(--text-lg);
        font-weight: 600;
        text-decoration: none;
        box-shadow: var(--shadow-md);
        transition: all var(--duration-ui) var(--ease-out);
        cursor: pointer;
      }
      
      .btn-glass-secondary:hover {
        background: var(--accent-soft);
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
      }
      
      /* Core Values */
      .core-values {
        padding: var(--space-20) var(--space-6);
        background: var(--bg-primary);
      }
      
      .core-values-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: var(--space-8);
        max-width: 1200px;
        margin: 0 auto;
      }
      
      .value-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: var(--radius-card);
        padding: var(--space-8);
        box-shadow: var(--shadow-md);
        transition: all var(--duration-ui) var(--ease-out);
        text-align: center;
      }
      
      .value-card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-xl);
        background: var(--gradient-card-hover);
      }
      
      .value-icon {
        font-size: 64px;
        margin-bottom: var(--space-4);
      }
      
      .value-title {
        font-size: var(--text-xl);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-3);
      }
      
      .value-desc {
        font-size: var(--text-base);
        color: var(--text-secondary);
        line-height: 1.75;
      }
      
      /* Container */
      .container {
        max-width: 1240px;
        margin: 0 auto;
        padding: var(--space-12) var(--space-6);
      }
      
      .section-title {
        font-size: var(--text-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-8);
        text-align: center;
      }
      
      .section-subtitle {
        font-size: var(--text-lg);
        color: var(--text-secondary);
        max-width: 700px;
        margin: 0 auto var(--space-12);
        text-align: center;
        line-height: 1.75;
      }
      
      /* Footer */
      footer {
        background: var(--bg-secondary);
        padding: var(--space-12) var(--space-6);
        text-align: center;
        border-top: 1px solid var(--border-default);
      }
      
      footer p {
        color: var(--text-tertiary);
        font-size: var(--text-sm);
      }
      
      /* Responsive */
      @media (max-width: 768px) {
        .hero-character {
          width: 280px;
          height: 320px;
        }
        
        .character-placeholder {
          font-size: 80px;
        }
        
        .hero-title {
          font-size: var(--text-2xl);
        }
        
        .hero-subtitle {
          font-size: var(--text-lg);
        }
        
        .hero-input-container {
          padding: 0 var(--space-2);
        }
        
        .hero-input-wrapper {
          flex-wrap: nowrap;
        }
        
        .hero-voice-btn,
        .hero-send-btn {
          width: 40px;
          height: 40px;
          font-size: 18px;
        }
        
        .hero-cta-group {
          flex-direction: column;
          gap: var(--space-3);
        }
        
        .btn-glass-primary,
        .btn-glass-secondary {
          font-size: var(--text-base);
          padding: var(--space-3) var(--space-6);
          width: 100%;
          max-width: 300px;
        }
      }
    </style>
    """


def render_navigation(current_page: str = "", lang: str = "ko") -> str:
    """Render navigation with language toggle."""
    nav_items = [
        (t("nav_home", lang), "/"),
        (t("nav_intro", lang), "/intro"),
        (t("nav_modules", lang), "/modules"),
        (t("nav_pricing", lang), "/pricing"),
        (t("nav_dashboard", lang), "/dashboard-preview"),
        (t("nav_canvas", lang), "/canvas-preview"),
        (t("nav_login", lang), "/login"),
    ]
    
    other_lang = "en" if lang == "ko" else "ko"
    lang_label = "EN" if lang == "ko" else "한국어"
    
    nav_html = "<nav>"
    nav_html += '<a href="/" class="nav-brand">NEXUS-ON</a>'
    for label, path in nav_items:
        active_class = "active" if path == current_page else ""
        nav_html += f'<a href="{path}?lang={lang}" class="nav-link {active_class}">{label}</a>'
    nav_html += f'<button class="lang-toggle" onclick="toggleLanguage()">{lang_label}</button>'
    nav_html += """
    <script>
    function toggleLanguage() {
        const url = new URL(window.location.href);
        const currentLang = url.searchParams.get('lang') || 'ko';
        const newLang = currentLang === 'ko' ? 'en' : 'ko';
        url.searchParams.set('lang', newLang);
        window.location.href = url.toString();
    }
    </script>
    """
    nav_html += "</nav>"
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
    """Render world-class landing page with i18n support and Live2D character."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS-ON | {t("hero_subtitle", lang)}</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="idle">
        {render_navigation("/", lang)}
        
        <!-- Live2D Character (Idle state for landing) -->
        {render_live2d_component("idle")}
        
        <!-- HERO SECTION -->
        <section class="hero-world-class">
            <div class="hero-content">
                <h1 class="hero-title">{t("hero_title", lang)}</h1>
                <p class="hero-subtitle">{t("hero_subtitle", lang)}</p>
                <p class="hero-tagline">{t("hero_tagline", lang)}</p>
                
                <!-- AI Chat Input UI (Below Live2D Character) -->
                <div class="hero-input-container">
                    <div class="hero-input-wrapper">
                        <input 
                            type="text" 
                            class="hero-input" 
                            placeholder="{t('hero_input_placeholder', lang)}"
                            id="hero-chat-input"
                        />
                        <button class="hero-voice-btn" id="voice-input-btn" title="{t('hero_voice_button', lang)}">
                            🎤
                        </button>
                        <button class="hero-send-btn" id="send-btn" title="{t('hero_text_button', lang)}">
                            →
                        </button>
                    </div>
                </div>
                
                <div class="hero-cta-group">
                    <a href="/signup?lang={lang}" class="btn-glass-primary">{t("hero_cta_primary", lang)}</a>
                    <a href="#demo" class="btn-glass-secondary">{t("hero_cta_secondary", lang)}</a>
                </div>
            </div>
        </section>
        
        <!-- 3 CORE VALUES -->
        <section class="core-values">
            <div class="core-values-grid">
                <div class="value-card">
                    <div class="value-icon">🎭</div>
                    <h3 class="value-title">{t("value1_title", lang)}</h3>
                    <p class="value-desc">{t("value1_desc", lang)}</p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🤖</div>
                    <h3 class="value-title">{t("value2_title", lang)}</h3>
                    <p class="value-desc">{t("value2_desc", lang)}</p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🇰🇷</div>
                    <h3 class="value-title">{t("value3_title", lang)}</h3>
                    <p class="value-desc">{t("value3_desc", lang)}</p>
                </div>
            </div>
        </section>
        
        {render_footer(lang)}
        
        <!-- Chat Input & Voice Interaction -->
        <script>
            // Chat input handler
            const chatInput = document.getElementById('hero-chat-input');
            const sendBtn = document.getElementById('send-btn');
            const voiceBtn = document.getElementById('voice-input-btn');
            const character = window.nexusCharacter();
            
            // Send message
            function sendMessage() {{
                const message = chatInput.value.trim();
                if (!message) return;
                
                console.log('Sending message:', message);
                if (character) character.setState('thinking');
                
                // Simulate response
                setTimeout(() => {{
                    if (character) character.setState('speaking');
                    setTimeout(() => {{
                        if (character) character.setState('idle');
                    }}, 2000);
                }}, 1000);
                
                chatInput.value = '';
            }}
            
            sendBtn.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});
            
            // Voice input
            voiceBtn.addEventListener('click', () => {{
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    const recognition = new SpeechRecognition();
                    recognition.lang = '{lang}';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    
                    recognition.onstart = () => {{
                        if (character) character.setState('listening');
                        voiceBtn.style.background = 'var(--accent-primary)';
                        voiceBtn.style.color = 'white';
                    }};
                    
                    recognition.onresult = (event) => {{
                        const transcript = event.results[0][0].transcript;
                        chatInput.value = transcript;
                        if (character) character.setState('thinking');
                    }};
                    
                    recognition.onend = () => {{
                        voiceBtn.style.background = '';
                        voiceBtn.style.color = '';
                        if (character) character.setState('idle');
                    }};
                    
                    recognition.onerror = (event) => {{
                        console.error('Speech recognition error:', event.error);
                        voiceBtn.style.background = '';
                        voiceBtn.style.color = '';
                        if (character) character.setState('idle');
                    }};
                    
                    recognition.start();
                }} else {{
                    alert('{t("voice_not_supported", lang)}');
                }}
            }});
        </script>
        
        <!-- Scroll-based state changes -->
        <script>
            window.addEventListener('scroll', function() {{
                const scrollY = window.scrollY;
                const character = window.nexusCharacter();
                if (!character) return;
                
                if (scrollY < 300) {{
                    character.setState('idle');
                }} else if (scrollY < 600) {{
                    character.setState('listening');
                }} else {{
                    character.setState('thinking');
                }}
            }});
        </script>
    </body>
    </html>
    """


def pricing_page(lang: str = "ko") -> str:
    """Render pricing page with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_pricing", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="thinking">
        {render_navigation("/pricing", lang)}
        
        <!-- Live2D Character (Thinking state for pricing) -->
        {render_live2d_component("thinking")}
        
        <div class="container">
            <h1 class="section-title">{t("pricing_title", lang)}</h1>
            <p class="section-subtitle">{t("pricing_subtitle", lang)}</p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">💳</div>
                <p style="font-size: 18px;">{t("pricing_coming", lang)}</p>
                <p>{t("pricing_plans", lang)}</p>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def dashboard_preview_page(lang: str = "ko") -> str:
    """Render dashboard preview with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_dashboard", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="busy">
        {render_navigation("/dashboard-preview", lang)}
        
        <!-- Live2D Character (Busy state for dashboard) -->
        {render_live2d_component("busy")}
        
        <div class="container">
            <h1 class="section-title">{t("dashboard_title", lang)}</h1>
            <p class="section-subtitle">{t("dashboard_subtitle", lang)}</p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">📊</div>
                <p style="font-size: 18px;">{t("dashboard_coming", lang)}</p>
                <p>{t("dashboard_features", lang)}</p>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def canvas_preview_page(lang: str = "ko") -> str:
    """Render canvas workspace with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_canvas", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="thinking">
        {render_navigation("/canvas-preview", lang)}
        
        <!-- Live2D Character (Thinking state for canvas) -->
        {render_live2d_component("thinking")}
        
        <div class="container">
            <h1 class="section-title">{t("canvas_title", lang)}</h1>
            <p class="section-subtitle">{t("canvas_subtitle", lang)}</p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">📝</div>
                <p style="font-size: 18px;">{t("canvas_coming", lang)}</p>
                <p>{t("canvas_features", lang)}</p>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def login_page(lang: str = "ko") -> str:
    """Render login page with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_login", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="idle">
        {render_navigation("/login", lang)}
        
        <!-- Live2D Character (Idle state for login) -->
        {render_live2d_component("idle")}
        
        <div class="container">
            <div style="text-align: center; padding: 100px 0;">
                <div style="font-size: 64px; margin-bottom: 24px;">🔐</div>
                <h1 class="section-title">{t("login_title", lang)}</h1>
                <p class="section-subtitle">{t("login_subtitle", lang)}</p>
                
                <div style="max-width: 400px; margin: 48px auto; text-align: left;">
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">{t("login_email", lang)}</label>
                        <input type="email" placeholder="your@email.com" 
                               style="width: 100%; padding: 12px 16px; border: 1px solid var(--border-default); 
                                      border-radius: var(--radius-control); font-size: var(--text-base);">
                    </div>
                    
                    <div style="margin-bottom: 24px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">{t("login_password", lang)}</label>
                        <input type="password" placeholder="••••••••" 
                               style="width: 100%; padding: 12px 16px; border: 1px solid var(--border-default); 
                                      border-radius: var(--radius-control); font-size: var(--text-base);">
                    </div>
                    
                    <button class="btn-glass-primary" style="width: 100%; margin-bottom: 16px;">{t("login_button", lang)}</button>
                    
                    <div style="text-align: center; color: var(--text-tertiary); font-size: var(--text-sm);">
                        {t("login_no_account", lang)} <a href="/signup?lang={lang}" style="color: var(--accent-primary);">{t("login_signup", lang)}</a>
                    </div>
                </div>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def intro_page(lang: str = "ko") -> str:
    """Render introduction page with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_intro", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="listening">
        {render_navigation("/intro", lang)}
        
        <!-- Live2D Character (Listening state for intro) -->
        {render_live2d_component("listening")}
        
        <div class="container">
            <h1 class="section-title">{t("intro_title", lang)}</h1>
            <p class="section-subtitle">{t("intro_subtitle", lang)}</p>
            
            <div style="max-width: 900px; margin: 0 auto;">
                <div style="background: var(--bg-secondary); padding: var(--space-8); border-radius: var(--radius-card); margin-bottom: var(--space-8);">
                    <h2 style="font-size: var(--text-xl); font-weight: 600; margin-bottom: var(--space-4); color: var(--text-primary);">
                        {t("intro_section1_title", lang)}
                    </h2>
                    <p style="color: var(--text-secondary); line-height: 1.75; font-size: var(--text-base);">
                        {t("intro_section1_content", lang)}
                    </p>
                </div>
                
                <div style="background: var(--bg-secondary); padding: var(--space-8); border-radius: var(--radius-card);">
                    <h2 style="font-size: var(--text-xl); font-weight: 600; margin-bottom: var(--space-4); color: var(--text-primary);">
                        {t("intro_section2_title", lang)}
                    </h2>
                    <ul style="color: var(--text-secondary); line-height: 2; font-size: var(--text-base); list-style: none; padding: 0;">
                        <li>✅ {t("intro_diff1", lang)}</li>
                        <li>✅ {t("intro_diff2", lang)}</li>
                        <li>✅ {t("intro_diff3", lang)}</li>
                        <li>✅ {t("intro_diff4", lang)}</li>
                    </ul>
                </div>
                
                <!-- Developer Profile Section -->
                <div style="background: var(--gradient-card); padding: var(--space-10); border-radius: var(--radius-card); margin-top: var(--space-8); border: 2px solid var(--accent-soft);">
                    <h2 style="font-size: var(--text-2xl); font-weight: 700; margin-bottom: var(--space-6); color: var(--text-primary); text-align: center;">
                        👨‍💻 {t("developer_title", lang)}
                    </h2>
                    
                    <div style="text-align: center; margin-bottom: var(--space-8);">
                        <h3 style="font-size: var(--text-xl); font-weight: 600; color: var(--accent-primary); margin-bottom: var(--space-2);">
                            {t("developer_name", lang)}
                        </h3>
                        <p style="font-size: var(--text-base); color: var(--text-tertiary);">
                            {t("developer_affiliation", lang)}
                        </p>
                    </div>
                    
                    <div style="margin-bottom: var(--space-8);">
                        <h4 style="font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-3); color: var(--text-primary);">
                            🔬 {t("developer_research_title", lang)}
                        </h4>
                        <ul style="color: var(--text-secondary); line-height: 2; font-size: var(--text-sm); list-style: none; padding: 0;">
                            <li>• {t("developer_research_1", lang)}</li>
                            <li>• {t("developer_research_2", lang)}</li>
                            <li>• {t("developer_research_3", lang)}</li>
                            <li>• {t("developer_research_4", lang)}</li>
                            <li>• {t("developer_research_5", lang)}</li>
                        </ul>
                    </div>
                    
                    <div style="margin-bottom: var(--space-8);">
                        <h4 style="font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-3); color: var(--text-primary);">
                            🎯 {t("developer_vision_title", lang)}
                        </h4>
                        <p style="color: var(--text-secondary); line-height: 1.75; font-size: var(--text-sm);">
                            {t("developer_vision_content", lang)}
                        </p>
                    </div>
                    
                    <div style="margin-bottom: var(--space-6);">
                        <h4 style="font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-3); color: var(--text-primary);">
                            💡 {t("developer_philosophy_title", lang)}
                        </h4>
                        <ul style="color: var(--text-secondary); line-height: 2; font-size: var(--text-sm); list-style: none; padding: 0;">
                            <li>✅ {t("developer_philosophy_1", lang)}</li>
                            <li>✅ {t("developer_philosophy_2", lang)}</li>
                            <li>✅ {t("developer_philosophy_3", lang)}</li>
                            <li>✅ {t("developer_philosophy_4", lang)}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; padding-top: var(--space-6); border-top: 1px solid rgba(0,0,0,0.1);">
                        <h4 style="font-size: var(--text-base); font-weight: 600; margin-bottom: var(--space-2); color: var(--text-primary);">
                            📧 {t("developer_contact_title", lang)}
                        </h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary); margin-bottom: var(--space-2);">
                            {t("developer_contact_dept", lang)}
                        </p>
                        <p style="font-size: var(--text-sm); color: var(--accent-primary);">
                            <a href="https://github.com/multipia-creator/nexus-on" target="_blank" style="color: var(--accent-primary); text-decoration: none;">
                                🔗 {t("developer_contact_project", lang)}
                            </a>
                        </p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: var(--space-12);">
                    <a href="/modules?lang={lang}" class="btn-glass-primary">{t("nav_modules", lang)}</a>
                </div>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def developer_page(lang: str = "ko") -> str:
    """
    Render dedicated developer profile page with 2-column layout.
    
    Layout:
    - Left: Profile image placeholder
    - Right: Detailed profile information
    """
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("developer_title", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
        <style>
            .developer-profile {{
                max-width: 1200px;
                margin: var(--space-20) auto;
                padding: var(--space-6);
            }}
            
            .profile-container {{
                display: grid;
                grid-template-columns: 320px 1fr;
                gap: var(--space-10);
                background: var(--gradient-card);
                border-radius: var(--radius-card);
                padding: var(--space-10);
                box-shadow: var(--shadow-xl);
                border: 2px solid var(--accent-soft);
            }}
            
            @media (max-width: 768px) {{
                .profile-container {{
                    grid-template-columns: 1fr;
                    gap: var(--space-6);
                }}
            }}
            
            .profile-image-section {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: var(--space-4);
            }}
            
            .profile-image-placeholder {{
                width: 280px;
                height: 280px;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                border-radius: var(--radius-card);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 120px;
                box-shadow: var(--shadow-lg);
            }}
            
            .profile-name {{
                font-size: var(--text-2xl);
                font-weight: 700;
                color: var(--accent-primary);
                text-align: center;
                margin-top: var(--space-2);
            }}
            
            .profile-affiliation {{
                font-size: var(--text-base);
                color: var(--text-tertiary);
                text-align: center;
            }}
            
            .profile-info-section {{
                display: flex;
                flex-direction: column;
                gap: var(--space-8);
            }}
            
            .info-block {{
                background: rgba(255, 255, 255, 0.5);
                padding: var(--space-6);
                border-radius: var(--radius-md);
                border-left: 4px solid var(--accent-primary);
            }}
            
            .info-block h3 {{
                font-size: var(--text-xl);
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: var(--space-4);
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }}
            
            .info-block ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .info-block li {{
                color: var(--text-secondary);
                line-height: 1.8;
                font-size: var(--text-sm);
                padding: var(--space-1) 0;
            }}
            
            .info-block li::before {{
                content: "▸";
                color: var(--accent-primary);
                font-weight: bold;
                display: inline-block;
                width: 1em;
                margin-right: var(--space-2);
            }}
            
            .info-block p {{
                color: var(--text-secondary);
                line-height: 1.75;
                font-size: var(--text-sm);
                margin: 0;
            }}
            
            .contact-links {{
                display: flex;
                flex-direction: column;
                gap: var(--space-2);
            }}
            
            .contact-link {{
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--accent-primary);
                text-decoration: none;
                font-size: var(--text-sm);
                transition: all var(--duration-ui) var(--ease-out);
            }}
            
            .contact-link:hover {{
                transform: translateX(4px);
                color: var(--accent-secondary);
            }}
            
            .back-button {{
                text-align: center;
                margin-top: var(--space-10);
            }}
        </style>
    </head>
    <body data-page-state="friendly">
        {render_navigation("/developer", lang)}
        
        <!-- Live2D Character (Friendly state) -->
        {render_live2d_component("friendly")}
        
        <div class="developer-profile">
            <div class="profile-container">
                <!-- Left Column: Profile Image -->
                <div class="profile-image-section">
                    <div class="profile-image-placeholder">
                        👨‍💻
                    </div>
                    <h2 class="profile-name">{t("developer_name", lang)}</h2>
                    <p class="profile-affiliation">{t("developer_affiliation", lang)}</p>
                </div>
                
                <!-- Right Column: Profile Information -->
                <div class="profile-info-section">
                    <!-- Research Interests -->
                    <div class="info-block">
                        <h3>🔬 {t("developer_research_title", lang)}</h3>
                        <ul>
                            <li>{t("developer_research_1", lang)}</li>
                            <li>{t("developer_research_2", lang)}</li>
                            <li>{t("developer_research_3", lang)}</li>
                            <li>{t("developer_research_4", lang)}</li>
                            <li>{t("developer_research_5", lang)}</li>
                        </ul>
                    </div>
                    
                    <!-- Project Vision -->
                    <div class="info-block">
                        <h3>🎯 {t("developer_vision_title", lang)}</h3>
                        <p>{t("developer_vision_content", lang)}</p>
                    </div>
                    
                    <!-- Development Philosophy -->
                    <div class="info-block">
                        <h3>💡 {t("developer_philosophy_title", lang)}</h3>
                        <ul>
                            <li>{t("developer_philosophy_1", lang)}</li>
                            <li>{t("developer_philosophy_2", lang)}</li>
                            <li>{t("developer_philosophy_3", lang)}</li>
                            <li>{t("developer_philosophy_4", lang)}</li>
                        </ul>
                    </div>
                    
                    <!-- Contact Information -->
                    <div class="info-block">
                        <h3>📧 {t("developer_contact_title", lang)}</h3>
                        <div class="contact-links">
                            <div class="contact-link">
                                🏫 {t("developer_contact_dept", lang)}
                            </div>
                            <a href="https://github.com/multipia-creator/nexus-on" target="_blank" class="contact-link">
                                🔗 {t("developer_contact_project", lang)}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="back-button">
                <a href="/?lang={lang}" class="btn-glass-primary">← {t("nav_home", lang)}</a>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def modules_page(lang: str = "ko") -> str:
    """Render modules page with module cards."""
    modules = load_modules_data()
    
    modules_html = ""
    for module in modules:
        status_color = {
            "stable": "var(--status-green)",
            "beta": "var(--status-yellow)",
            "alpha": "var(--status-red)"
        }.get(module.get("status", "alpha"), "var(--status-red)")
        
        modules_html += f"""
        <div class="value-card" style="text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4);">
                <div style="font-size: 48px;">{module.get('icon', '📦')}</div>
                <div style="background: {status_color}; color: white; padding: 4px 12px; border-radius: var(--radius-pill); font-size: 12px; font-weight: 600;">
                    {module.get('status_label', module.get('status', 'Unknown'))}
                </div>
            </div>
            <h3 style="font-size: var(--text-xl); font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">
                {module.get('name', 'Unknown Module')}
            </h3>
            <p style="font-size: var(--text-sm); color: var(--text-tertiary); margin-bottom: var(--space-4);">
                {module.get('tagline', '')}
            </p>
            <p style="font-size: var(--text-base); color: var(--text-secondary); line-height: 1.6;">
                {module.get('description', '')}
            </p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_modules", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="speaking">
        {render_navigation("/modules", lang)}
        
        <!-- Live2D Character (Speaking state for modules) -->
        {render_live2d_component("speaking")}
        
        <div class="container">
            <h1 class="section-title">{t("modules_title", lang)}</h1>
            <p class="section-subtitle">{t("modules_subtitle", lang)}</p>
            
            <div style="text-align: center; margin-bottom: var(--space-12);">
                <span style="background: var(--gradient-accent); color: white; padding: var(--space-2) var(--space-6); border-radius: var(--radius-pill); font-weight: 600;">
                    {len(modules)} {t("modules_count", lang)}
                </span>
            </div>
            
            <div class="core-values-grid">
                {modules_html}
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """
