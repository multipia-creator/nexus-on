/**
 * Page rendering functions for NEXUS-ON Marketing Pages
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 */

import { t, Language } from './i18n'

/**
 * Render common CSS styles (world-class design system)
 */
export function renderStyles(): string {
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
        
        /* Typography */
        --font-display: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-base: 14px;
        
        /* Spacing (8pt grid) */
        --space-1: 8px;
        --space-2: 16px;
        --space-3: 24px;
        --space-4: 32px;
        --space-5: 40px;
        --space-6: 48px;
        --space-8: 64px;
        --space-10: 80px;
        --space-12: 96px;
        
        /* Border Radius */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        
        /* Shadows */
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        
        /* Transitions */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      
      body {
        font-family: var(--font-display);
        font-size: var(--font-base);
        color: var(--text-primary);
        background: var(--bg-primary);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }
      
      /* Dark Navigation Bar */
      .nav {
        background: var(--nav-bg);
        border-bottom: 1px solid var(--nav-border);
        padding: var(--space-2) var(--space-3);
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(10px);
      }
      
      .nav-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .nav-logo {
        font-size: 20px;
        font-weight: 700;
        color: var(--nav-text);
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: var(--space-1);
      }
      
      .nav-links {
        display: flex;
        gap: var(--space-3);
        align-items: center;
      }
      
      .nav-link {
        color: var(--nav-text-dim);
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: color var(--transition-base);
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
      }
      
      .nav-link:hover {
        color: var(--nav-text);
        background: rgba(255, 255, 255, 0.05);
      }
      
      .lang-switch {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--nav-border);
        color: var(--nav-text);
        padding: 6px 12px;
        border-radius: var(--radius-sm);
        font-size: 13px;
        cursor: pointer;
        transition: all var(--transition-base);
      }
      
      .lang-switch:hover {
        background: rgba(255, 255, 255, 0.15);
      }
      
      /* Hero Section */
      .hero {
        background: var(--gradient-hero);
        padding: var(--space-10) var(--space-3);
        text-align: center;
      }
      
      .hero-content {
        max-width: 900px;
        margin: 0 auto;
      }
      
      .hero-title {
        font-size: 56px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: var(--space-3);
        background: var(--gradient-accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      .hero-subtitle {
        font-size: 20px;
        color: var(--text-secondary);
        margin-bottom: var(--space-2);
        font-weight: 600;
      }
      
      .hero-tagline {
        font-size: 16px;
        color: var(--text-tertiary);
        margin-bottom: var(--space-6);
        line-height: 1.8;
      }
      
      .hero-cta {
        display: flex;
        gap: var(--space-2);
        justify-content: center;
        margin-bottom: var(--space-8);
      }
      
      .btn {
        padding: 14px 32px;
        border-radius: var(--radius-md);
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        transition: all var(--transition-base);
        border: none;
        cursor: pointer;
      }
      
      .btn-primary {
        background: var(--gradient-accent);
        color: white;
        box-shadow: var(--shadow-md);
      }
      
      .btn-primary:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
      }
      
      .btn-secondary {
        background: white;
        color: var(--accent-primary);
        border: 2px solid var(--accent-primary);
      }
      
      .btn-secondary:hover {
        background: var(--accent-soft);
      }
      
      /* Chat Input (Hero) */
      .hero-chat {
        max-width: 700px;
        margin: 0 auto var(--space-8);
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-2);
        box-shadow: var(--shadow-xl);
        display: flex;
        gap: var(--space-2);
        align-items: center;
      }
      
      .hero-chat input {
        flex: 1;
        border: none;
        outline: none;
        font-size: 16px;
        padding: var(--space-2);
        font-family: var(--font-display);
      }
      
      .hero-chat button {
        background: var(--gradient-accent);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: var(--radius-md);
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all var(--transition-base);
      }
      
      .hero-chat button:hover {
        opacity: 0.9;
      }
      
      /* Values Section */
      .values {
        max-width: 1200px;
        margin: 0 auto;
        padding: var(--space-10) var(--space-3);
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--space-4);
      }
      
      .value-card {
        background: white;
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        transition: all var(--transition-base);
      }
      
      .value-card:hover {
        box-shadow: var(--shadow-xl);
        transform: translateY(-4px);
      }
      
      .value-icon {
        font-size: 40px;
        margin-bottom: var(--space-2);
      }
      
      .value-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: var(--space-2);
        color: var(--text-primary);
      }
      
      .value-desc {
        font-size: 15px;
        color: var(--text-tertiary);
        line-height: 1.7;
      }
      
      /* Footer */
      .footer {
        background: var(--gradient-dark);
        color: var(--nav-text-dim);
        padding: var(--space-6) var(--space-3);
        text-align: center;
        margin-top: var(--space-10);
      }
      
      .footer-text {
        font-size: 16px;
        margin-bottom: var(--space-2);
        color: var(--nav-text);
        font-weight: 600;
      }
      
      .footer-dev {
        font-size: 14px;
        color: var(--nav-text-dim);
      }
      
      /* Section Title */
      .section {
        max-width: 1200px;
        margin: 0 auto;
        padding: var(--space-10) var(--space-3);
      }
      
      .section-header {
        text-align: center;
        margin-bottom: var(--space-8);
      }
      
      .section-title {
        font-size: 40px;
        font-weight: 800;
        margin-bottom: var(--space-2);
        color: var(--text-primary);
      }
      
      .section-subtitle {
        font-size: 18px;
        color: var(--text-tertiary);
        line-height: 1.7;
      }
      
      /* Feature Cards */
      .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: var(--space-4);
      }
      
      .feature-card {
        background: var(--gradient-card);
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-default);
        transition: all var(--transition-base);
      }
      
      .feature-card:hover {
        background: var(--gradient-card-hover);
        border-color: var(--accent-primary);
        transform: translateY(-4px);
      }
      
      .feature-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: var(--space-2);
        color: var(--text-primary);
      }
      
      .feature-content {
        font-size: 15px;
        color: var(--text-secondary);
        line-height: 1.8;
      }
      
      /* Responsive */
      @media (max-width: 768px) {
        .hero-title {
          font-size: 36px;
        }
        
        .hero-subtitle {
          font-size: 18px;
        }
        
        .hero-cta {
          flex-direction: column;
        }
        
        .nav-links {
          flex-wrap: wrap;
          gap: var(--space-1);
        }
        
        .section-title {
          font-size: 32px;
        }
        
        .features-grid {
          grid-template-columns: 1fr;
        }
      }
    </style>
  `
}

/**
 * Render navigation bar
 */
export function renderNavigation(lang: Language): string {
  const otherLang = lang === 'ko' ? 'en' : 'ko'
  const langLabel = lang === 'ko' ? 'EN' : 'KO'
  
  return `
    <nav class="nav">
      <div class="nav-container">
        <a href="/?lang=${lang}" class="nav-logo">
          🔷 NEXUS-ON
        </a>
        <div class="nav-links">
          <a href="/?lang=${lang}" class="nav-link">${t('nav_home', lang)}</a>
          <a href="/intro?lang=${lang}" class="nav-link">${t('nav_intro', lang)}</a>
          <a href="/developer?lang=${lang}" class="nav-link">개발자</a>
          <a href="/modules?lang=${lang}" class="nav-link">${t('nav_modules', lang)}</a>
          <button onclick="location.href='?lang=${otherLang}'" class="lang-switch">${langLabel}</button>
        </div>
      </div>
    </nav>
  `
}

/**
 * Render footer
 */
export function renderFooter(lang: Language): string {
  return `
    <footer class="footer">
      <div class="footer-text">${t('footer_text', lang)}</div>
      <div class="footer-dev">${t('footer_dev', lang)}</div>
    </footer>
  `
}

/**
 * Render Landing Page
 */
export function renderLandingPage(lang: Language): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS-ON | ${t('hero_subtitle', lang)}</title>
        ${renderStyles()}
    </head>
    <body>
        ${renderNavigation(lang)}
        
        <section class="hero">
            <div class="hero-content">
                <h1 class="hero-title">${t('hero_title', lang)}</h1>
                <p class="hero-subtitle">${t('hero_subtitle', lang)}</p>
                <p class="hero-tagline">${t('hero_tagline', lang)}</p>
                
                <div class="hero-chat">
                    <input 
                        type="text" 
                        id="hero-chat-input" 
                        placeholder="${t('hero_input_placeholder', lang)}"
                    />
                    <button id="send-btn">${t('hero_text_button', lang)}</button>
                </div>
                
                <div class="hero-cta">
                    <a href="/signup?lang=${lang}" class="btn btn-primary">${t('hero_cta_primary', lang)}</a>
                    <a href="#demo" class="btn btn-secondary">${t('hero_cta_secondary', lang)}</a>
                </div>
            </div>
        </section>
        
        <section class="values">
            <div class="value-card">
                <div class="value-icon">👁️</div>
                <h3 class="value-title">${t('value1_title', lang)}</h3>
                <p class="value-desc">${t('value1_desc', lang)}</p>
            </div>
            <div class="value-card">
                <div class="value-icon">🎯</div>
                <h3 class="value-title">${t('value2_title', lang)}</h3>
                <p class="value-desc">${t('value2_desc', lang)}</p>
            </div>
            <div class="value-card">
                <div class="value-icon">🇰🇷</div>
                <h3 class="value-title">${t('value3_title', lang)}</h3>
                <p class="value-desc">${t('value3_desc', lang)}</p>
            </div>
        </section>
        
        ${renderFooter(lang)}
        
        <script>
          // Simple chat input handler
          document.getElementById('send-btn')?.addEventListener('click', () => {
            const input = document.getElementById('hero-chat-input');
            const message = input.value.trim();
            if (message) {
              console.log('User message:', message);
              // TODO: Integrate with Backend API
              alert('Chat integration coming soon!');
            }
          });
        </script>
    </body>
    </html>
  `
}

/**
 * Render Intro Page
 */
export function renderIntroPage(lang: Language): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('intro_title', lang)} - NEXUS-ON</title>
        ${renderStyles()}
    </head>
    <body>
        ${renderNavigation(lang)}
        
        <section class="section">
            <div class="section-header">
                <h1 class="section-title">${t('intro_worldclass_title', lang)}</h1>
                <p class="section-subtitle">${t('intro_worldclass_subtitle', lang)}</p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <h3 class="feature-title">${t('intro_feature1_title', lang)}</h3>
                    <p class="feature-content">${t('intro_feature1_content', lang)}</p>
                </div>
                <div class="feature-card">
                    <h3 class="feature-title">${t('intro_feature2_title', lang)}</h3>
                    <p class="feature-content">${t('intro_feature2_content', lang)}</p>
                </div>
                <div class="feature-card">
                    <h3 class="feature-title">${t('intro_feature3_title', lang)}</h3>
                    <p class="feature-content">${t('intro_feature3_content', lang)}</p>
                </div>
                <div class="feature-card">
                    <h3 class="feature-title">${t('intro_feature4_title', lang)}</h3>
                    <p class="feature-content">${t('intro_feature4_content', lang)}</p>
                </div>
                <div class="feature-card">
                    <h3 class="feature-title">${t('intro_feature5_title', lang)}</h3>
                    <p class="feature-content">${t('intro_feature5_content', lang)}</p>
                </div>
                <div class="feature-card">
                    <h3 class="feature-title">${t('intro_feature6_title', lang)}</h3>
                    <p class="feature-content">${t('intro_feature6_content', lang)}</p>
                </div>
            </div>
        </section>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}

/**
 * Render Developer Page
 */
export function renderDeveloperPage(lang: Language): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('developer_title', lang)} - NEXUS-ON</title>
        ${renderStyles()}
        <style>
          .developer-profile {
            max-width: 900px;
            margin: 0 auto;
            padding: var(--space-10) var(--space-3);
          }
          
          .profile-header {
            text-align: center;
            margin-bottom: var(--space-8);
          }
          
          .profile-image {
            width: 280px;
            height: 280px;
            margin: 0 auto var(--space-4);
            border-radius: var(--radius-xl);
            background: var(--gradient-accent);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 120px;
          }
          
          .profile-name {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: var(--space-1);
          }
          
          .profile-affiliation {
            font-size: 16px;
            color: var(--text-secondary);
            margin-bottom: var(--space-1);
          }
          
          .profile-specialty {
            font-size: 14px;
            color: var(--text-tertiary);
          }
          
          .profile-section {
            background: white;
            padding: var(--space-5);
            border-radius: var(--radius-lg);
            margin-bottom: var(--space-4);
            box-shadow: var(--shadow-md);
          }
          
          .profile-section h3 {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: var(--space-3);
            color: var(--accent-primary);
          }
          
          .research-list, .philosophy-list {
            list-style: none;
            padding-left: var(--space-3);
          }
          
          .research-list li, .philosophy-list li {
            position: relative;
            padding-left: var(--space-3);
            margin-bottom: var(--space-2);
            line-height: 1.7;
            color: var(--text-secondary);
          }
          
          .research-list li::before, .philosophy-list li::before {
            content: "▸";
            position: absolute;
            left: 0;
            color: var(--accent-primary);
            font-weight: 700;
          }
        </style>
    </head>
    <body>
        ${renderNavigation(lang)}
        
        <div class="developer-profile">
            <div class="profile-header">
                <div class="profile-image">👨‍🏫</div>
                <h1 class="profile-name">${t('developer_name', lang)}</h1>
                <p class="profile-affiliation">${t('developer_affiliation', lang)}</p>
                <p class="profile-specialty">${t('developer_specialty', lang)}</p>
            </div>
            
            <div class="profile-section">
                <h3>${t('developer_research_title', lang)}</h3>
                <ul class="research-list">
                    <li>${t('developer_research_1', lang)}</li>
                    <li>${t('developer_research_2', lang)}</li>
                    <li>${t('developer_research_3', lang)}</li>
                    <li>${t('developer_research_4', lang)}</li>
                    <li>${t('developer_research_5', lang)}</li>
                </ul>
            </div>
            
            <div class="profile-section">
                <h3>${t('developer_vision_title', lang)}</h3>
                <p style="line-height: 1.8; color: var(--text-secondary);">
                    ${t('developer_vision_content', lang)}
                </p>
            </div>
            
            <div class="profile-section">
                <h3>${t('developer_philosophy_title', lang)}</h3>
                <ul class="philosophy-list">
                    <li>${t('developer_philosophy_1', lang)}</li>
                    <li>${t('developer_philosophy_2', lang)}</li>
                    <li>${t('developer_philosophy_3', lang)}</li>
                    <li>${t('developer_philosophy_4', lang)}</li>
                </ul>
            </div>
            
            <div class="profile-section">
                <h3>${t('developer_contact_title', lang)}</h3>
                <p style="line-height: 2; color: var(--text-secondary);">
                    📧 ${t('developer_contact_dept', lang)}<br>
                    🏢 ${t('developer_contact_lab', lang)}<br>
                    🌐 ${t('developer_contact_website', lang)}<br>
                    💻 <a href="https://github.com/multipia-creator/nexus-on" style="color: var(--accent-primary);">${t('developer_contact_project', lang)}</a>
                </p>
            </div>
        </div>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}

/**
 * Render Modules Page
 */
export function renderModulesPage(lang: Language): string {
  const modules = [
    { key: 'bot', icon: '🤖', status: 'production' },
    { key: 'shield', icon: '🛡️', status: 'production' },
    { key: 'filesearch', icon: '📚', status: 'beta' },
    { key: 'youtube', icon: '📺', status: 'production' },
    { key: 'fileedit', icon: '📝', status: 'beta' },
    { key: 'users', icon: '👥', status: 'production' },
    { key: 'monitor', icon: '📊', status: 'beta' },
    { key: 'activity', icon: '📈', status: 'alpha' },
  ]
  
  const statusColors: Record<string, string> = {
    production: '#10B981',
    beta: '#F59E0B',
    alpha: '#6B7280'
  }
  
  const modulesHTML = modules.map(module => `
    <div class="feature-card">
      <div style="font-size: 40px; margin-bottom: var(--space-2);">${module.icon}</div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2);">
        <h3 class="feature-title">${t(`module_${module.key}_title`, lang)}</h3>
        <span style="
          background: ${statusColors[module.status]};
          color: white;
          padding: 4px 12px;
          border-radius: var(--radius-sm);
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
        ">${t(`module_${module.key}_status`, lang)}</span>
      </div>
      <p style="font-size: 13px; color: var(--text-tertiary); margin-bottom: var(--space-1); font-weight: 600;">
        ${t(`module_${module.key}_subtitle`, lang)}
      </p>
      <p class="feature-content">${t(`module_${module.key}_desc`, lang)}</p>
    </div>
  `).join('')
  
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('modules_title', lang)} - NEXUS-ON</title>
        ${renderStyles()}
    </head>
    <body>
        ${renderNavigation(lang)}
        
        <section class="section">
            <div class="section-header">
                <h1 class="section-title">${t('modules_title', lang)}</h1>
                <p class="section-subtitle">${t('modules_subtitle', lang)}</p>
                <p style="font-size: 24px; font-weight: 700; color: var(--accent-primary); margin-top: var(--space-2);">
                    ${modules.length}${t('modules_count', lang)}
                </p>
            </div>
            
            <div class="features-grid">
                ${modulesHTML}
            </div>
        </section>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
