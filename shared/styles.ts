/**
 * NEXUS-ON - World-Class Design System (NEXUS UI v2.0)
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 * Complete CSS design system with animations and responsive design
 */

export function renderWorldClassStyles(): string {
  return `
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
      
      :root {
        /* Dark Navigation Colors */
        --nav-bg: #1A1A1A;
        --nav-text: #FFFFFF;
        --nav-text-dim: #B4B4B4;
        --nav-border: rgba(255, 255, 255, 0.1);
        
        /* Colors */
        --bg-primary: #FFFFFF;
        --bg-secondary: #F7F7F8;
        --bg-dark: #0A0A0A;
        --text-primary: #111111;
        --text-secondary: #3C3C43;
        --text-tertiary: #6B6B73;
        --accent-primary: #3B82F6;
        --accent-hover: #2563EB;
        --accent-soft: #EFF6FF;
        --accent-gold: #F59E0B;
        --border-default: #E6E6EA;
        --border-strong: #D1D1D6;
        
        /* Gradients */
        --gradient-hero: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 30%, #DBEAFE 100%);
        --gradient-accent: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        --gradient-gold: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        --gradient-card: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.95) 100%);
        --gradient-card-hover: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(37, 99, 235, 0.12) 100%);
        --gradient-dark: linear-gradient(135deg, #1A1A1A 0%, #0A0A0A 100%);
        
        /* Status Colors */
        --status-green: #10B981;
        --status-yellow: #F59E0B;
        --status-red: #EF4444;
        --status-blue: #3B82F6;
        
        /* Typography */
        --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
        --font-mono: "SF Mono", "Consolas", "Monaco", monospace;
        --text-4xl: 56px;
        --text-3xl: 48px;
        --text-2xl: 36px;
        --text-xl: 24px;
        --text-lg: 18px;
        --text-base: 16px;
        --text-sm: 14px;
        --text-xs: 12px;
        
        /* Spacing */
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
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-card: 24px;
        --radius-pill: 999px;
        --radius-control: 12px;
        
        /* Shadow */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
        --shadow-2xl: 0 24px 64px rgba(0, 0, 0, 0.20);
        
        /* Motion */
        --duration-fast: 120ms;
        --duration-ui: 180ms;
        --duration-slow: 280ms;
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
      
      /* Animations */
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
      }
      
      @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
        50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.6); }
      }
      
      @keyframes slide-in-up {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      @keyframes slide-in-left {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
      }
      
      @keyframes slide-in-right {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
      }
      
      @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      
      @keyframes scale-in {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
      }
      
      @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
      }
      
      /* Navigation - Dark Premium Theme */
      nav {
        background: var(--nav-bg);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--nav-border);
        padding: var(--space-4) var(--space-8);
        display: flex;
        align-items: center;
        gap: var(--space-6);
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5);
      }
      
      .nav-brand {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        font-size: var(--text-xl);
        font-weight: 700;
        color: var(--nav-text);
        text-decoration: none;
        margin-right: auto;
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .nav-brand:hover {
        transform: translateY(-2px);
        filter: brightness(1.2);
      }
      
      .nav-logo {
        width: 40px;
        height: 40px;
        border-radius: var(--radius-md);
        background: var(--gradient-accent);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .nav-brand:hover .nav-logo {
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.6);
        transform: rotate(5deg) scale(1.05);
      }
      
      .nav-logo img {
        width: 28px;
        height: 28px;
        object-fit: contain;
      }
      
      .nav-links {
        display: flex;
        align-items: center;
        gap: var(--space-2);
      }
      
      .nav-link {
        color: var(--nav-text-dim);
        text-decoration: none;
        font-size: var(--text-sm);
        font-weight: 500;
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-md);
        transition: all var(--duration-ui) var(--ease-out);
        position: relative;
      }
      
      .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--nav-text);
        transform: translateY(-2px);
      }
      
      .nav-link.active {
        background: var(--gradient-accent);
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
      }
      
      .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: -16px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--accent-primary);
        box-shadow: 0 0 8px var(--accent-primary);
      }
      
      /* Language Toggle Button */
      .lang-toggle {
        padding: var(--space-2) var(--space-4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.05);
        color: var(--nav-text);
        border-radius: var(--radius-pill);
        font-size: var(--text-xs);
        font-weight: 600;
        cursor: pointer;
        transition: all var(--duration-ui) var(--ease-out);
        backdrop-filter: blur(10px);
      }
      
      .lang-toggle:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        transform: scale(1.05);
      }
      
      @media (max-width: 768px) {
        nav {
          padding: var(--space-3) var(--space-4);
          gap: var(--space-3);
        }
        
        .nav-links {
          display: none;
        }
        
        .nav-logo {
          width: 32px;
          height: 32px;
        }
        
        .nav-logo img {
          width: 20px;
          height: 20px;
        }
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
  `
}
