/**
 * NEXUS-ON - Modules Page
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 * 8 modules detailed grid with status badges
 */

import { Language, t } from '../../shared/i18n'
import { renderWorldClassStyles } from '../../shared/styles'
import { renderLive2DComponent } from '../components/live2d'
import { renderNavigation } from '../components/navigation'
import { renderFooter } from '../components/footer'

export function modulesPage(lang: Language = 'ko'): string {
  // Define 8 modules
  const modules = [
    { key: 'bot', icon: '🤖', status: 'production', color: '#10B981' },
    { key: 'shield', icon: '🛡️', status: 'production', color: '#10B981' },
    { key: 'filesearch', icon: '📚', status: 'beta', color: '#F59E0B' },
    { key: 'youtube', icon: '▶️', status: 'production', color: '#10B981' },
    { key: 'fileedit', icon: '✏️', status: 'beta', color: '#F59E0B' },
    { key: 'users', icon: '👥', status: 'production', color: '#10B981' },
    { key: 'monitor', icon: '🖥️', status: 'beta', color: '#F59E0B' },
    { key: 'activity', icon: '📊', status: 'alpha', color: '#EF4444' }
  ]

  const modulesHTML = modules.map((module, idx) => {
    const delay = (idx + 1) * 0.1
    return `
      <article class="module-card" style="animation: scale-in 0.5s var(--ease-out) ${delay}s both;">
        <div class="module-header">
          <span class="module-icon">${module.icon}</span>
          <span class="module-status" style="background: ${module.color};">
            ${t(`module_${module.key}_status`, lang)}
          </span>
        </div>
        <h3 class="module-title">${t(`module_${module.key}_title`, lang)}</h3>
        <p class="module-subtitle">${t(`module_${module.key}_subtitle`, lang)}</p>
        <p class="module-desc">${t(`module_${module.key}_desc`, lang)}</p>
      </article>
    `
  }).join('')

  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('nav_modules', lang)} - NEXUS-ON</title>
        ${renderWorldClassStyles()}
        <style>
            .modules-hero {
                background: var(--gradient-hero);
                padding: var(--space-20) var(--space-6) var(--space-12);
                text-align: center;
            }
            
            .modules-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
                gap: var(--space-6);
                max-width: 1400px;
                margin: 0 auto;
                padding: var(--space-12) var(--space-6) var(--space-20);
            }
            
            .module-card {
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                padding: var(--space-8);
                border: 1px solid var(--border-default);
                box-shadow: var(--shadow-lg);
                transition: all var(--duration-slow) var(--ease-out);
                position: relative;
                overflow: hidden;
            }
            
            .module-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: var(--gradient-accent);
                transform: scaleX(0);
                transform-origin: left;
                transition: transform var(--duration-slow) var(--ease-out);
            }
            
            .module-card:hover {
                transform: translateY(-8px);
                box-shadow: var(--shadow-2xl);
                border-color: var(--accent-primary);
            }
            
            .module-card:hover::before {
                transform: scaleX(1);
            }
            
            .module-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--space-6);
            }
            
            .module-icon {
                font-size: 56px;
                display: block;
            }
            
            .module-status {
                color: white;
                padding: 6px 16px;
                border-radius: var(--radius-pill);
                font-size: var(--text-xs);
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                box-shadow: var(--shadow-sm);
            }
            
            .module-title {
                font-size: var(--text-2xl);
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: var(--space-2);
            }
            
            .module-subtitle {
                font-size: var(--text-base);
                color: var(--text-tertiary);
                font-weight: 500;
                margin-bottom: var(--space-4);
            }
            
            .module-desc {
                font-size: var(--text-sm);
                color: var(--text-secondary);
                line-height: 1.7;
            }
            
            @media (max-width: 768px) {
                .modules-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body data-page-state="speaking">
        ${renderNavigation('/modules', lang)}
        
        <!-- Live2D Character (Speaking state for modules) -->
        ${renderLive2DComponent('speaking')}
        
        <!-- Hero Section -->
        <section class="modules-hero">
            <h1 class="section-title">${t('modules_title', lang)}</h1>
            <p class="section-subtitle">${t('modules_subtitle', lang)}</p>
            <div style="margin-top: var(--space-6);">
                <span style="background: var(--gradient-accent); color: white; padding: var(--space-3) var(--space-8); border-radius: var(--radius-pill); font-weight: 700; font-size: var(--text-lg); box-shadow: var(--shadow-lg);">
                    8 ${t('modules_count', lang)}
                </span>
            </div>
        </section>
        
        <!-- Modules Grid -->
        <section class="modules-grid">
            ${modulesHTML}
        </section>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
