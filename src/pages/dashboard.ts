/**
 * Dashboard Preview Page - Real-time Monitoring
 * NEXUS-ON Dashboard with Ceria status tracking
 */

import { renderNavigation } from '../components/navigation'
import { renderLive2DComponent } from '../components/live2d'
import { renderFooter } from '../components/footer'
import { renderWorldClassStyles } from '../../shared/styles'
import { t } from '../../shared/i18n'
import type { Language } from '../../shared/types'

export function dashboardPreviewPage(lang: Language = 'ko'): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t("nav_dashboard", lang)} - NEXUS-ON</title>
        ${renderWorldClassStyles()}
        <style>
            .dashboard-grid {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: var(--space-6);
                max-width: 1400px;
                margin: 0 auto;
                padding: var(--space-12) var(--space-6);
            }
            
            .dashboard-card {
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                padding: var(--space-8);
                border: 1px solid var(--border-default);
                box-shadow: var(--shadow-lg);
            }
            
            .dashboard-card h3 {
                font-size: var(--text-xl);
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: var(--space-4);
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: var(--space-2);
                animation: pulse-glow 2s infinite;
            }
            
            .status-online { background: var(--status-green); }
            .status-busy { background: var(--status-yellow); }
            .status-idle { background: var(--status-blue); }
            
            @media (max-width: 1024px) {
                .dashboard-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body data-page-state="busy">
        ${renderNavigation("/dashboard-preview", lang)}
        ${renderLive2DComponent("busy")}
        
        <div class="container">
            <h1 class="section-title">${t("dashboard_title", lang)}</h1>
            <p class="section-subtitle">${t("dashboard_subtitle", lang)}</p>
        </div>
        
        <section class="dashboard-grid">
            <article class="dashboard-card">
                <h3>🎭 ${t("dashboard_ceria_status", lang)}</h3>
                <p><span class="status-indicator status-online"></span> Online</p>
                <p style="color: var(--text-secondary); margin-top: var(--space-4);">
                    ${t("dashboard_current_task", lang)}: Idle
                </p>
            </article>
            
            <article class="dashboard-card">
                <h3>⏰ ${t("dashboard_recent_activity", lang)}</h3>
                <ul style="list-style: none; padding: 0; color: var(--text-secondary); font-size: var(--text-sm);">
                    <li style="padding: var(--space-2) 0;">No recent tasks</li>
                </ul>
            </article>
            
            <article class="dashboard-card">
                <h3>📊 ${t("dashboard_system_health", lang)}</h3>
                <p style="color: var(--text-secondary);">
                    Status: <span style="color: var(--status-green); font-weight: 600;">Healthy</span>
                </p>
            </article>
        </section>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
