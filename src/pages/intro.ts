/**
 * NEXUS-ON - Intro Page
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 * World-class introduction page with 6 differentiators
 */

import { Language, t } from '../../shared/i18n'
import { renderWorldClassStyles } from '../../shared/styles'
import { renderLive2DComponent } from '../components/live2d'
import { renderNavigation } from '../components/navigation'
import { renderFooter } from '../components/footer'

export function introPage(lang: Language = 'ko'): string {
  // Helper function to split emoji from title
  const splitTitle = (title: string): { icon: string; text: string } => {
    const parts = title.split(' ')
    return {
      icon: parts[0],
      text: parts.slice(1).join(' ')
    }
  }

  const feature1 = splitTitle(t('intro_feature1_title', lang))
  const feature2 = splitTitle(t('intro_feature2_title', lang))
  const feature3 = splitTitle(t('intro_feature3_title', lang))
  const feature4 = splitTitle(t('intro_feature4_title', lang))
  const feature5 = splitTitle(t('intro_feature5_title', lang))
  const feature6 = splitTitle(t('intro_feature6_title', lang))

  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('nav_intro', lang)} - NEXUS-ON</title>
        ${renderWorldClassStyles()}
        <style>
            .intro-hero {
                background: var(--gradient-hero);
                padding: var(--space-20) var(--space-6);
                text-align: center;
            }
            
            .intro-hero h1 {
                font-size: var(--text-4xl);
                font-weight: 800;
                color: var(--text-primary);
                margin-bottom: var(--space-6);
                background: var(--gradient-accent);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .intro-hero p {
                font-size: var(--text-xl);
                color: var(--text-secondary);
                max-width: 800px;
                margin: 0 auto var(--space-12);
                line-height: 1.8;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
                gap: var(--space-8);
                max-width: 1400px;
                margin: 0 auto;
                padding: var(--space-12) var(--space-6);
            }
            
            .feature-card {
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                padding: var(--space-10);
                box-shadow: var(--shadow-lg);
                border: 1px solid var(--border-default);
                transition: all var(--duration-slow) var(--ease-out);
                position: relative;
                overflow: hidden;
            }
            
            .feature-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--gradient-accent);
                transform: scaleX(0);
                transform-origin: left;
                transition: transform var(--duration-slow) var(--ease-out);
            }
            
            .feature-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: var(--shadow-2xl);
                border-color: var(--accent-primary);
            }
            
            .feature-card:hover::before {
                transform: scaleX(1);
            }
            
            .feature-icon {
                font-size: 48px;
                margin-bottom: var(--space-4);
                display: block;
            }
            
            .feature-title {
                font-size: var(--text-2xl);
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: var(--space-4);
            }
            
            .feature-content {
                font-size: var(--text-base);
                color: var(--text-secondary);
                line-height: 1.8;
            }
            
            @media (max-width: 768px) {
                .features-grid {
                    grid-template-columns: 1fr;
                }
                
                .intro-hero h1 {
                    font-size: var(--text-3xl);
                }
            }
        </style>
    </head>
    <body data-page-state="listening">
        ${renderNavigation('/intro', lang)}
        
        <!-- Live2D Character (Listening state for intro) -->
        ${renderLive2DComponent('listening')}
        
        <!-- Hero Section -->
        <section class="intro-hero">
            <h1>${t('intro_worldclass_title', lang)}</h1>
            <p>${t('intro_worldclass_subtitle', lang)}</p>
        </section>
        
        <!-- Features Grid -->
        <section class="features-grid">
            <!-- Feature 1: Live2D Character -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.1s both;">
                <span class="feature-icon">${feature1.icon}</span>
                <h2 class="feature-title">${feature1.text}</h2>
                <p class="feature-content">${t('intro_feature1_content', lang)}</p>
            </article>
            
            <!-- Feature 2: ShieldCheck -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.2s both;">
                <span class="feature-icon">${feature2.icon}</span>
                <h2 class="feature-title">${feature2.text}</h2>
                <p class="feature-content">${t('intro_feature2_content', lang)}</p>
            </article>
            
            <!-- Feature 3: Korean Native -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.3s both;">
                <span class="feature-icon">${feature3.icon}</span>
                <h2 class="feature-title">${feature3.text}</h2>
                <p class="feature-content">${t('intro_feature3_content', lang)}</p>
            </article>
            
            <!-- Feature 4: Multi-Agent -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.4s both;">
                <span class="feature-icon">${feature4.icon}</span>
                <h2 class="feature-title">${feature4.text}</h2>
                <p class="feature-content">${t('intro_feature4_content', lang)}</p>
            </article>
            
            <!-- Feature 5: Local-first -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.5s both;">
                <span class="feature-icon">${feature5.icon}</span>
                <h2 class="feature-title">${feature5.text}</h2>
                <p class="feature-content">${t('intro_feature5_content', lang)}</p>
            </article>
            
            <!-- Feature 6: Real-time Monitoring -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.6s both;">
                <span class="feature-icon">${feature6.icon}</span>
                <h2 class="feature-title">${feature6.text}</h2>
                <p class="feature-content">${t('intro_feature6_content', lang)}</p>
            </article>
        </section>
        
        <!-- Product Philosophy Section -->
        <div class="container" style="margin-top: var(--space-20);">
            <div class="intro-hero" style="padding: var(--space-12) var(--space-6);">
                <h2 style="font-size: var(--text-3xl); font-weight: 700; margin-bottom: var(--space-4);">
                    💡 ${t('intro_philosophy_title', lang)}
                </h2>
                <p style="font-size: var(--text-lg); color: var(--text-secondary); margin-bottom: var(--space-10);">
                    ${t('intro_philosophy_subtitle', lang)}
                </p>
                
                <div class="features-grid" style="grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: var(--space-6);">
                    <div class="feature-card">
                        <h3 class="feature-title">🤝 ${t('intro_philosophy_hitl', lang)}</h3>
                        <p class="feature-content">${t('intro_philosophy_hitl_desc', lang)}</p>
                    </div>
                    <div class="feature-card">
                        <h3 class="feature-title">✅ ${t('intro_philosophy_approvals', lang)}</h3>
                        <p class="feature-content">${t('intro_philosophy_approvals_desc', lang)}</p>
                    </div>
                    <div class="feature-card">
                        <h3 class="feature-title">💰 ${t('intro_philosophy_cost', lang)}</h3>
                        <p class="feature-content">${t('intro_philosophy_cost_desc', lang)}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Ceria System States Section -->
        <div class="container" style="margin-top: var(--space-16);">
            <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%); padding: var(--space-12); border-radius: var(--radius-2xl); border: 2px solid var(--accent-soft);">
                <h2 style="font-size: var(--text-3xl); font-weight: 700; text-align: center; margin-bottom: var(--space-4); color: var(--text-primary);">
                    🎭 ${t('intro_ceria_title', lang)}
                </h2>
                <p style="font-size: var(--text-lg); color: var(--text-secondary); text-align: center; margin-bottom: var(--space-10);">
                    ${t('intro_ceria_subtitle', lang)}
                </p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4);">
                    <div style="background: white; padding: var(--space-6); border-radius: var(--radius-lg); text-align: center; border: 1px solid var(--border-default);">
                        <div style="font-size: 36px; margin-bottom: var(--space-2);">😌</div>
                        <h4 style="font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">${t('intro_ceria_idle', lang)}</h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary);">${t('intro_ceria_idle_desc', lang)}</p>
                    </div>
                    <div style="background: white; padding: var(--space-6); border-radius: var(--radius-lg); text-align: center; border: 1px solid var(--border-default);">
                        <div style="font-size: 36px; margin-bottom: var(--space-2);">👂</div>
                        <h4 style="font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">${t('intro_ceria_listening', lang)}</h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary);">${t('intro_ceria_listening_desc', lang)}</p>
                    </div>
                    <div style="background: white; padding: var(--space-6); border-radius: var(--radius-lg); text-align: center; border: 1px solid var(--border-default);">
                        <div style="font-size: 36px; margin-bottom: var(--space-2);">🤔</div>
                        <h4 style="font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">${t('intro_ceria_thinking', lang)}</h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary);">${t('intro_ceria_thinking_desc', lang)}</p>
                    </div>
                    <div style="background: white; padding: var(--space-6); border-radius: var(--radius-lg); text-align: center; border: 1px solid var(--border-default);">
                        <div style="font-size: 36px; margin-bottom: var(--space-2);">🗣️</div>
                        <h4 style="font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">${t('intro_ceria_speaking', lang)}</h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary);">${t('intro_ceria_speaking_desc', lang)}</p>
                    </div>
                    <div style="background: white; padding: var(--space-6); border-radius: var(--radius-lg); text-align: center; border: 1px solid var(--border-default);">
                        <div style="font-size: 36px; margin-bottom: var(--space-2);">⚙️</div>
                        <h4 style="font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">${t('intro_ceria_busy', lang)}</h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary);">${t('intro_ceria_busy_desc', lang)}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Developer Profile Section (Compact version) -->
        <div class="container">
            <div style="background: var(--gradient-card); padding: var(--space-10); border-radius: var(--radius-xl); margin-top: var(--space-20); border: 2px solid var(--accent-soft); box-shadow: var(--shadow-xl);">
                <h2 style="font-size: var(--text-2xl); font-weight: 700; margin-bottom: var(--space-6); color: var(--text-primary); text-align: center;">
                    👨‍💻 ${t('developer_title', lang)}
                </h2>
                
                <div style="text-align: center; margin-bottom: var(--space-4);">
                    <h3 style="font-size: var(--text-xl); font-weight: 600; color: var(--accent-primary); margin-bottom: var(--space-2);">
                        ${t('developer_name', lang)}
                    </h3>
                    <p style="font-size: var(--text-base); color: var(--text-tertiary); margin-bottom: var(--space-6);">
                        ${t('developer_affiliation', lang)}
                    </p>
                    <a href="/developer?lang=${lang}" style="display: inline-block; padding: var(--space-3) var(--space-8); background: var(--gradient-accent); color: white; border-radius: var(--radius-pill); text-decoration: none; font-weight: 600; font-size: var(--text-sm); transition: all var(--duration-ui) var(--ease-out); box-shadow: var(--shadow-md);">
                        View Full Profile →
                    </a>
                </div>
            </div>
            
            <!-- CTA Section -->
            <div style="text-align: center; margin-top: var(--space-20); margin-bottom: var(--space-12);">
                <a href="/modules?lang=${lang}" class="btn-glass-primary" style="font-size: var(--text-lg); padding: var(--space-5) var(--space-12);">
                    ${t('nav_modules', lang)} →
                </a>
            </div>
        </div>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
