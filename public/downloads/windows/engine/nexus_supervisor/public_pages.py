"""
Public pages HTML rendering for NEXUS-ON marketing site.
WORLD-CLASS AI Character Assistant Service.

Design System: NEXUS UI v2.0 (World-Class Edition)
- Gradient Backgrounds
- Glassmorphism
- Micro Animations
- Live2D Character Integration (Large Scale)
- Premium Interactive Elements
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


def render_world_class_styles() -> str:
    """NEXUS UI v2.0 - World-Class Design System."""
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
        
        /* Gradients (World-Class) */
        --gradient-hero: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 30%, #DBEAFE 100%);
        --gradient-accent: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%);
        --gradient-card-hover: linear-gradient(135deg, 
          rgba(37, 99, 235, 0.05) 0%, 
          rgba(59, 130, 246, 0.1) 100%);
        --gradient-premium: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        
        /* Status Colors */
        --status-green: #16A34A;
        --status-green-bg: #F0FDF4;
        --status-yellow: #F59E0B;
        --status-yellow-bg: #FFFBEB;
        --status-red: #DC2626;
        --status-red-bg: #FEF2F2;
        
        /* Typography */
        --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, 
                     "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
        --text-3xl: 48px;
        --text-2xl: 32px;
        --text-xl: 24px;
        --text-lg: 18px;
        --text-base: 14px;
        --text-sm: 12px;
        
        /* Spacing (8pt Grid) */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;
        --space-16: 64px;
        --space-20: 80px;
        --space-24: 96px;
        
        /* Radius */
        --radius-card: 18px;
        --radius-control: 12px;
        --radius-pill: 999px;
        
        /* Shadow */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
        
        /* Motion */
        --duration-micro: 120ms;
        --duration-ui: 180ms;
        --duration-modal: 240ms;
        --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
        --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
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
      
      /* ============================================
         WORLD-CLASS ANIMATIONS
         ============================================ */
      
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
      }
      
      @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(37, 99, 235, 0.3); }
        50% { box-shadow: 0 0 40px rgba(37, 99, 235, 0.6); }
      }
      
      @keyframes slide-in-up {
        from {
          opacity: 0;
          transform: translateY(30px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      @keyframes scale-in {
        from {
          opacity: 0;
          transform: scale(0.9);
        }
        to {
          opacity: 1;
          transform: scale(1);
        }
      }
      
      @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
      }
      
      /* ============================================
         NAVIGATION (Premium)
         ============================================ */
      
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
      
      /* ============================================
         HERO SECTION (Full Screen, Character-Focused)
         ============================================ */
      
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
      
      .hero-world-class::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(37, 99, 235, 0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
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
        background: linear-gradient(135deg, 
          rgba(255, 255, 255, 0.9) 0%, 
          rgba(239, 246, 255, 0.8) 100%);
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
      
      .hero-cta-group {
        display: flex;
        gap: var(--space-4);
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
      }
      
      /* ============================================
         GLASSMORPHISM BUTTONS
         ============================================ */
      
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
      
      /* ============================================
         3 CORE VALUES (Glassmorphism Cards)
         ============================================ */
      
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
        animation: scale-in 0.6s var(--ease-out);
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
      
      /* ============================================
         CONTAINER & UTILITIES
         ============================================ */
      
      .container {
        max-width: 1240px;
        margin: 0 auto;
        padding: var(--space-12) var(--space-6);
      }
      
      .container-narrow {
        max-width: 768px;
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
      
      /* ============================================
         FOOTER
         ============================================ */
      
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
      
      /* ============================================
         RESPONSIVE
         ============================================ */
      
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
        
        .hero-tagline {
          font-size: var(--text-base);
        }
        
        .btn-glass-primary,
        .btn-glass-secondary {
          font-size: var(--text-base);
          padding: var(--space-3) var(--space-6);
        }
      }
      
      /* Reduced Motion */
      @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }
      }
    </style>
    """


def render_navigation(current_page: str = "") -> str:
    """Render navigation bar."""
    nav_items = [
        ("Home", "/"),
        ("Pricing", "/pricing"),
        ("Dashboard", "/dashboard-preview"),
        ("Canvas", "/canvas-preview"),
        ("Login", "/login"),
    ]
    
    nav_html = "<nav>"
    nav_html += '<a href="/" class="nav-brand">NEXUS-ON</a>'
    for label, path in nav_items:
        active_class = "active" if path == current_page else ""
        nav_html += f'<a href="{path}" class="nav-link {active_class}">{label}</a>'
    nav_html += "</nav>"
    return nav_html


def render_footer() -> str:
    """Render footer."""
    return """
    <footer>
        <p>&copy; 2026 NEXUS-ON. Your AI Character Assistant That Never Sleeps.</p>
        <p>Developed by Prof. Nam Hyunwoo, Seokyeong University.</p>
    </footer>
    """


def landing_page() -> str:
    """Render world-class landing page with huge Live2D character."""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS-ON | Your AI Character Assistant That Never Sleeps</title>
        {render_world_class_styles()}
    </head>
    <body>
        {render_navigation("/")}
        
        <!-- HERO SECTION (Full Screen, Character-Focused) -->
        <section class="hero-world-class">
            <div class="hero-content">
                <!-- HUGE Live2D Character -->
                <div class="hero-character">
                    <div class="character-placeholder">🎭</div>
                    <div class="character-state">Idle</div>
                </div>
                
                <h1 class="hero-title">Your AI Character Assistant<br>That Never Sleeps</h1>
                <p class="hero-subtitle">항상 깨어있는 당신만의 AI 캐릭터 비서</p>
                <p class="hero-tagline">
                    Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만<br>
                    중요한 결정은 항상 당신의 승인을 받습니다.
                </p>
                
                <div class="hero-cta-group">
                    <a href="/signup" class="btn-glass-primary">무료로 시작하기</a>
                    <a href="#demo" class="btn-glass-secondary">데모 보기</a>
                </div>
            </div>
        </section>
        
        <!-- 3 CORE VALUES -->
        <section class="core-values">
            <div class="core-values-grid">
                <div class="value-card">
                    <div class="value-icon">🎭</div>
                    <h3 class="value-title">Always Visible</h3>
                    <p class="value-desc">
                        화면에 항상 존재하는 Live2D 캐릭터 비서.<br>
                        5가지 상태로 현재 작업을 시각적으로 표현합니다.
                    </p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🤖</div>
                    <h3 class="value-title">Autonomous but Controlled</h3>
                    <p class="value-desc">
                        자율적으로 작업을 수행하지만,<br>
                        중요한 결정은 항상 당신의 승인을 받습니다.
                    </p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🇰🇷</div>
                    <h3 class="value-title">Korean Native</h3>
                    <p class="value-desc">
                        한국어 네이티브 지원.<br>
                        HWP 파일을 완벽하게 처리합니다.
                    </p>
                </div>
            </div>
        </section>
        
        {render_footer()}
    </body>
    </html>
    """


def pricing_page() -> str:
    """Render pricing page."""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pricing - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body>
        {render_navigation("/pricing")}
        
        <div class="container">
            <h1 class="section-title">가격 플랜</h1>
            <p class="section-subtitle">
                당신의 필요에 맞는 플랜을 선택하세요.<br>
                언제든지 업그레이드 가능합니다.
            </p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">💳</div>
                <p style="font-size: 18px;">가격 플랜 페이지 구현 중...</p>
                <p>FREE / PRO / ENTERPRISE 플랜 제공 예정</p>
            </div>
        </div>
        
        {render_footer()}
    </body>
    </html>
    """


def dashboard_preview_page() -> str:
    """Render dashboard preview page."""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Preview - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body>
        {render_navigation("/dashboard-preview")}
        
        <div class="container">
            <h1 class="section-title">대시보드 프리뷰</h1>
            <p class="section-subtitle">
                실시간으로 업데이트되는 AI 비서의 작업 현황을 확인하세요.
            </p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">📊</div>
                <p style="font-size: 18px;">대시보드 프리뷰 페이지 구현 중...</p>
                <p>3-Column Layout | 실시간 SSE 업데이트 | Live2D 상태 변화</p>
            </div>
        </div>
        
        {render_footer()}
    </body>
    </html>
    """


def canvas_preview_page() -> str:
    """Render canvas workspace preview page."""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Canvas Preview - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body>
        {render_navigation("/canvas-preview")}
        
        <div class="container">
            <h1 class="section-title">캔버스 워크스페이스</h1>
            <p class="section-subtitle">
                AI 비서와 함께 문서를 작성하고 편집하세요.
            </p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">📝</div>
                <p style="font-size: 18px;">캔버스 워크스페이스 페이지 구현 중...</p>
                <p>Markdown Editor | AI 제안 | Multi-format Export</p>
            </div>
        </div>
        
        {render_footer()}
    </body>
    </html>
    """


def login_page() -> str:
    """Render login page."""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body>
        {render_navigation("/login")}
        
        <div class="container-narrow">
            <div style="text-align: center; padding: 100px 0;">
                <div style="font-size: 64px; margin-bottom: 24px;">🔐</div>
                <h1 class="section-title">Welcome Back</h1>
                <p class="section-subtitle">다시 만나서 반가워요!</p>
                
                <div style="max-width: 400px; margin: 48px auto; text-align: left;">
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">Email</label>
                        <input type="email" placeholder="your@email.com" 
                               style="width: 100%; padding: 12px 16px; border: 1px solid var(--border-default); 
                                      border-radius: var(--radius-control); font-size: var(--text-base);">
                    </div>
                    
                    <div style="margin-bottom: 24px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">Password</label>
                        <input type="password" placeholder="••••••••" 
                               style="width: 100%; padding: 12px 16px; border: 1px solid var(--border-default); 
                                      border-radius: var(--radius-control); font-size: var(--text-base);">
                    </div>
                    
                    <button class="btn-glass-primary" style="width: 100%; margin-bottom: 16px;">Sign In</button>
                    
                    <div style="text-align: center; color: var(--text-tertiary); font-size: var(--text-sm);">
                        Don't have an account? <a href="/signup" style="color: var(--accent-primary);">Sign Up</a>
                    </div>
                </div>
            </div>
        </div>
        
        {render_footer()}
    </body>
    </html>
    """
