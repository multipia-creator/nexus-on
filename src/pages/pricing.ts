/**
 * NEXUS-ON - Pricing Page
 * 3-tier pricing with features list
 */

import { Language, t } from '../../shared/i18n'
import { renderWorldClassStyles } from '../../shared/styles'
import { renderLive2DComponent } from '../components/live2d'
import { renderNavigation } from '../components/navigation'
import { renderFooter } from '../components/footer'

export function pricingPage(lang: Language = 'ko'): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t('nav_pricing', lang)} - NEXUS-ON</title>
        ${renderWorldClassStyles()}
        <style>
            .pricing-hero {
                background: var(--gradient-hero);
                padding: var(--space-20) var(--space-6) var(--space-12);
                text-align: center;
            }
            
            .pricing-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: var(--space-8);
                max-width: 1200px;
                margin: 0 auto;
                padding: var(--space-12) var(--space-6) var(--space-20);
            }
            
            .pricing-card {
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                padding: var(--space-10);
                border: 2px solid var(--border-default);
                box-shadow: var(--shadow-lg);
                transition: all var(--duration-slow) var(--ease-out);
                position: relative;
            }
            
            .pricing-card.featured {
                border-color: var(--accent-primary);
                transform: scale(1.05);
                box-shadow: var(--shadow-2xl);
            }
            
            .pricing-card:hover {
                transform: translateY(-12px) scale(1.02);
                box-shadow: var(--shadow-2xl);
            }
            
            .pricing-badge {
                position: absolute;
                top: -12px;
                left: 50%;
                transform: translateX(-50%);
                background: var(--gradient-gold);
                color: white;
                padding: 6px 24px;
                border-radius: var(--radius-pill);
                font-size: var(--text-xs);
                font-weight: 700;
                letter-spacing: 1px;
                box-shadow: var(--shadow-lg);
            }
            
            .pricing-tier {
                font-size: var(--text-sm);
                font-weight: 700;
                color: var(--text-tertiary);
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-bottom: var(--space-2);
            }
            
            .pricing-price {
                font-size: var(--text-4xl);
                font-weight: 800;
                color: var(--accent-primary);
                margin-bottom: var(--space-2);
            }
            
            .pricing-period {
                font-size: var(--text-base);
                color: var(--text-tertiary);
                margin-bottom: var(--space-6);
            }
            
            .pricing-desc {
                font-size: var(--text-sm);
                color: var(--text-secondary);
                margin-bottom: var(--space-8);
                min-height: 40px;
            }
            
            .pricing-features {
                list-style: none;
                padding: 0;
                margin: 0 0 var(--space-8) 0;
            }
            
            .pricing-features li {
                font-size: var(--text-sm);
                color: var(--text-secondary);
                padding: var(--space-2) 0;
                line-height: 1.6;
            }
            
            .pricing-cta {
                display: block;
                width: 100%;
                padding: var(--space-4);
                background: var(--gradient-accent);
                color: white;
                border-radius: var(--radius-md);
                font-size: var(--text-base);
                font-weight: 600;
                text-align: center;
                text-decoration: none;
                border: none;
                cursor: pointer;
                transition: all var(--duration-ui) var(--ease-out);
                box-shadow: var(--shadow-md);
            }
            
            .pricing-cta:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }
            
            @media (max-width: 768px) {
                .pricing-grid {
                    grid-template-columns: 1fr;
                }
                
                .pricing-card.featured {
                    transform: scale(1);
                }
            }
        </style>
    </head>
    <body data-page-state="thinking">
        ${renderNavigation('/pricing', lang)}
        ${renderLive2DComponent('thinking')}
        
        <section class="pricing-hero">
            <h1 class="section-title">${t('pricing_title', lang)}</h1>
            <p class="section-subtitle">${t('pricing_subtitle', lang)}</p>
        </section>
        
        <section class="pricing-grid">
            <article class="pricing-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.1s both;">
                <div class="pricing-tier">${t('pricing_free_title', lang)}</div>
                <div class="pricing-price">${t('pricing_free_price', lang)}</div>
                <div class="pricing-period">${t('pricing_free_period', lang)}</div>
                <div class="pricing-desc">${t('pricing_free_desc', lang)}</div>
                <ul class="pricing-features">
                    <li>${t('pricing_free_feature1', lang)}</li>
                    <li>${t('pricing_free_feature2', lang)}</li>
                    <li>${t('pricing_free_feature3', lang)}</li>
                    <li>${t('pricing_free_feature4', lang)}</li>
                    <li>${t('pricing_free_feature5', lang)}</li>
                    <li>${t('pricing_free_feature6', lang)}</li>
                    <li>${t('pricing_free_feature7', lang)}</li>
                    <li>${t('pricing_free_feature8', lang)}</li>
                </ul>
                <button class="pricing-cta">${t('hero_cta_primary', lang)}</button>
            </article>
            
            <article class="pricing-card featured" style="animation: slide-in-up 0.6s var(--ease-out) 0.2s both;">
                <div class="pricing-badge">${t('pricing_plus_badge', lang)}</div>
                <div class="pricing-tier">${t('pricing_plus_title', lang)}</div>
                <div class="pricing-price">${t('pricing_plus_price', lang)}</div>
                <div class="pricing-period">${t('pricing_plus_period', lang)}</div>
                <div class="pricing-desc">${t('pricing_plus_desc', lang)}</div>
                <ul class="pricing-features">
                    <li>${t('pricing_plus_feature1', lang)}</li>
                    <li>${t('pricing_plus_feature2', lang)}</li>
                    <li>${t('pricing_plus_feature3', lang)}</li>
                    <li>${t('pricing_plus_feature4', lang)}</li>
                    <li>${t('pricing_plus_feature5', lang)}</li>
                    <li>${t('pricing_plus_feature6', lang)}</li>
                    <li>${t('pricing_plus_feature7', lang)}</li>
                    <li>${t('pricing_plus_feature8', lang)}</li>
                </ul>
                <button class="pricing-cta">${t('hero_cta_primary', lang)}</button>
            </article>
            
            <article class="pricing-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.3s both;">
                <div class="pricing-badge" style="background: var(--gradient-accent);">${t('pricing_pro_badge', lang)}</div>
                <div class="pricing-tier">${t('pricing_pro_title', lang)}</div>
                <div class="pricing-price">${t('pricing_pro_price', lang)}</div>
                <div class="pricing-period">${t('pricing_pro_period', lang)}</div>
                <div class="pricing-desc">${t('pricing_pro_desc', lang)}</div>
                <ul class="pricing-features">
                    <li>${t('pricing_pro_feature1', lang)}</li>
                    <li>${t('pricing_pro_feature2', lang)}</li>
                    <li>${t('pricing_pro_feature3', lang)}</li>
                    <li>${t('pricing_pro_feature4', lang)}</li>
                    <li>${t('pricing_pro_feature5', lang)}</li>
                    <li>${t('pricing_pro_feature6', lang)}</li>
                    <li>${t('pricing_pro_feature7', lang)}</li>
                    <li>${t('pricing_pro_feature8', lang)}</li>
                </ul>
                <button class="pricing-cta">${t('hero_cta_primary', lang)}</button>
            </article>
        </section>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
