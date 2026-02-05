/**
 * NEXUS-ON - Navigation Component
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 */

import { Language, t } from '../../shared/i18n'

export function renderNavigation(currentPage: string = '', lang: Language = 'ko'): string {
  const navItems: Array<[string, string]> = [
    [t('nav_home', lang), '/'],
    [t('nav_intro', lang), '/intro'],
    [t('nav_modules', lang), '/modules'],
    [t('nav_pricing', lang), '/pricing'],
    [t('nav_dashboard', lang), '/dashboard-preview'],
    [t('nav_canvas', lang), '/canvas-preview'],
    [t('nav_login', lang), '/login'],
  ]
  
  const otherLang = lang === 'ko' ? 'en' : 'ko'
  const langLabel = lang === 'ko' ? 'EN' : '한국어'
  
  let navHTML = '<nav>'
  
  // Brand with logo
  navHTML += `
    <a href="/" class="nav-brand">
        <div class="nav-logo">
            <img src="/static/images/nexus-on-logo.png" alt="NEXUS-ON" />
        </div>
        <span>NEXUS-ON</span>
    </a>
  `
  
  // Navigation links
  navHTML += '<div class="nav-links">'
  for (const [label, path] of navItems) {
    const activeClass = path === currentPage ? 'active' : ''
    navHTML += `<a href="${path}?lang=${lang}" class="nav-link ${activeClass}">${label}</a>`
  }
  navHTML += '</div>'
  
  // Language toggle
  navHTML += `<button class="lang-toggle" onclick="toggleLanguage()">${langLabel}</button>`
  
  // Language toggle script
  navHTML += `
    <script>
    function toggleLanguage() {
        const url = new URL(window.location.href);
        const currentLang = url.searchParams.get('lang') || 'ko';
        const newLang = currentLang === 'ko' ? 'en' : 'ko';
        url.searchParams.set('lang', newLang);
        window.location.href = url.toString();
    }
    </script>
  `
  
  navHTML += '</nav>'
  return navHTML
}
