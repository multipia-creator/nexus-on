/**
 * NEXUS-ON - Developer Page
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 * Dedicated developer profile page with 2-column layout
 */

import { Language, t } from '../../shared/i18n'
import { renderWorldClassStyles } from '../../shared/styles'
import { renderLive2DComponent } from '../components/live2d'
import { renderNavigation } from '../components/navigation'
import { renderFooter } from '../components/footer'

export function developerPage(lang: Language = 'ko'): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('developer_title', lang)} - NEXUS-ON</title>
        ${renderWorldClassStyles()}
        <style>
            .developer-profile {
                max-width: 1200px;
                margin: var(--space-20) auto;
                padding: var(--space-6);
            }
            
            .profile-container {
                display: grid;
                grid-template-columns: 320px 1fr;
                gap: var(--space-10);
                background: var(--gradient-card);
                border-radius: var(--radius-card);
                padding: var(--space-10);
                box-shadow: var(--shadow-xl);
                border: 2px solid var(--accent-soft);
            }
            
            @media (max-width: 768px) {
                .profile-container {
                    grid-template-columns: 1fr;
                    gap: var(--space-6);
                }
            }
            
            .profile-image-section {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: var(--space-4);
            }
            
            .profile-image-placeholder {
                width: 280px;
                height: 280px;
                background: linear-gradient(135deg, var(--accent-primary), #2563EB);
                border-radius: var(--radius-card);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 120px;
                box-shadow: var(--shadow-lg);
            }
            
            .profile-name {
                font-size: var(--text-2xl);
                font-weight: 700;
                color: var(--accent-primary);
                text-align: center;
                margin-top: var(--space-2);
            }
            
            .profile-affiliation {
                font-size: var(--text-base);
                color: var(--text-tertiary);
                text-align: center;
                line-height: 1.6;
            }
            
            .profile-specialty {
                font-size: var(--text-sm);
                color: var(--accent-primary);
                font-weight: 600;
                text-align: center;
                margin-top: var(--space-2);
                padding: var(--space-1) var(--space-3);
                background: var(--accent-soft);
                border-radius: var(--radius-pill);
                display: inline-block;
            }
            
            .profile-website {
                font-size: var(--text-sm);
                color: var(--accent-primary);
                text-align: center;
                margin-top: var(--space-2);
            }
            
            .profile-website a {
                color: var(--accent-primary);
                text-decoration: none;
                font-weight: 600;
                transition: all var(--duration-ui) var(--ease-out);
            }
            
            .profile-website a:hover {
                color: #2563EB;
                text-decoration: underline;
            }
            
            .profile-info-section {
                display: flex;
                flex-direction: column;
                gap: var(--space-8);
            }
            
            .info-block {
                background: rgba(255, 255, 255, 0.5);
                padding: var(--space-6);
                border-radius: var(--radius-md);
                border-left: 4px solid var(--accent-primary);
            }
            
            .info-block h3 {
                font-size: var(--text-xl);
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: var(--space-4);
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }
            
            .info-block ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .info-block li {
                color: var(--text-secondary);
                line-height: 1.8;
                font-size: var(--text-sm);
                padding: var(--space-1) 0;
            }
            
            .info-block li::before {
                content: "▸";
                color: var(--accent-primary);
                font-weight: bold;
                display: inline-block;
                width: 1em;
                margin-right: var(--space-2);
            }
            
            .info-block p {
                color: var(--text-secondary);
                line-height: 1.75;
                font-size: var(--text-sm);
                margin: 0;
            }
            
            .contact-links {
                display: flex;
                flex-direction: column;
                gap: var(--space-2);
            }
            
            .contact-link {
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--accent-primary);
                text-decoration: none;
                font-size: var(--text-sm);
                transition: all var(--duration-ui) var(--ease-out);
            }
            
            .contact-link:hover {
                transform: translateX(4px);
                color: #2563EB;
            }
            
            .back-button {
                text-align: center;
                margin-top: var(--space-10);
            }
        </style>
    </head>
    <body data-page-state="friendly">
        ${renderNavigation('/developer', lang)}
        
        <!-- Live2D Character (Idle state) -->
        ${renderLive2DComponent('idle')}
        
        <div class="developer-profile">
            <div class="profile-container">
                <!-- Left Column: Profile Image -->
                <div class="profile-image-section">
                    <div class="profile-image-placeholder">
                        👨‍💻
                    </div>
                    <h2 class="profile-name">${t('developer_name', lang)}</h2>
                    <p class="profile-affiliation">${t('developer_affiliation', lang)}</p>
                    <div class="profile-specialty">
                        ${t('developer_specialty', lang)}
                    </div>
                    <div class="profile-website">
                        🌐 <a href="https://dxpia.com" target="_blank">${t('developer_website', lang)}</a>
                    </div>
                </div>
                
                <!-- Right Column: Profile Information -->
                <div class="profile-info-section">
                    <!-- Research Interests -->
                    <div class="info-block">
                        <h3>🔬 ${t('developer_research_title', lang)}</h3>
                        <ul>
                            <li>${t('developer_research_1', lang)}</li>
                            <li>${t('developer_research_2', lang)}</li>
                            <li>${t('developer_research_3', lang)}</li>
                            <li>${t('developer_research_4', lang)}</li>
                            <li>${t('developer_research_5', lang)}</li>
                        </ul>
                    </div>
                    
                    <!-- Project Vision -->
                    <div class="info-block">
                        <h3>🎯 ${t('developer_vision_title', lang)}</h3>
                        <p>${t('developer_vision_content', lang)}</p>
                    </div>
                    
                    <!-- Development Philosophy -->
                    <div class="info-block">
                        <h3>💡 ${t('developer_philosophy_title', lang)}</h3>
                        <ul>
                            <li>${t('developer_philosophy_1', lang)}</li>
                            <li>${t('developer_philosophy_2', lang)}</li>
                            <li>${t('developer_philosophy_3', lang)}</li>
                            <li>${t('developer_philosophy_4', lang)}</li>
                        </ul>
                    </div>
                    
                    <!-- Contact Information -->
                    <div class="info-block">
                        <h3>📧 ${t('developer_contact_title', lang)}</h3>
                        <div class="contact-links">
                            <div class="contact-link">
                                🏫 ${t('developer_contact_dept', lang)}
                            </div>
                            <div class="contact-link">
                                🔬 ${t('developer_contact_lab', lang)}
                            </div>
                            <a href="https://dxpia.com" target="_blank" class="contact-link">
                                🌐 ${t('developer_contact_website', lang)}
                            </a>
                            <a href="https://github.com/multipia-creator/nexus-on" target="_blank" class="contact-link">
                                🔗 ${t('developer_contact_project', lang)}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="back-button">
                <a href="/?lang=${lang}" class="btn-glass-primary">← ${t('nav_home', lang)}</a>
            </div>
        </div>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
