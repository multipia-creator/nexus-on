/**
 * Canvas Preview Page - Markdown Editor Workspace
 * NEXUS-ON Canvas with AI-powered editing tools
 */

import { renderNavigation } from '../components/navigation'
import { renderLive2DComponent } from '../components/live2d'
import { renderFooter } from '../components/footer'
import { renderWorldClassStyles } from '../../shared/styles'
import { t } from '../../shared/i18n'
import type { Language } from '../../shared/types'

export function canvasPreviewPage(lang: Language = 'ko'): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${t("nav_canvas", lang)} - NEXUS-ON</title>
        ${renderWorldClassStyles()}
        <style>
            .canvas-workspace {
                max-width: 1200px;
                margin: var(--space-12) auto;
                padding: var(--space-6);
            }
            
            .canvas-editor {
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                border: 1px solid var(--border-default);
                box-shadow: var(--shadow-lg);
                overflow: hidden;
            }
            
            .canvas-toolbar {
                background: rgba(0,0,0,0.03);
                padding: var(--space-4) var(--space-6);
                border-bottom: 1px solid var(--border-default);
                display: flex;
                gap: var(--space-2);
            }
            
            .canvas-toolbar button {
                padding: var(--space-2) var(--space-4);
                background: white;
                border: 1px solid var(--border-default);
                border-radius: var(--radius-md);
                cursor: pointer;
                font-size: var(--text-sm);
                transition: all var(--duration-ui) var(--ease-out);
            }
            
            .canvas-toolbar button:hover {
                background: var(--accent-soft);
                border-color: var(--accent-primary);
            }
            
            .canvas-textarea {
                width: 100%;
                min-height: 500px;
                padding: var(--space-8);
                border: none;
                font-family: var(--font-mono);
                font-size: var(--text-base);
                line-height: 1.8;
                resize: vertical;
            }
        </style>
    </head>
    <body data-page-state="thinking">
        ${renderNavigation("/canvas-preview", lang)}
        ${renderLive2DComponent("thinking")}
        
        <div class="container">
            <h1 class="section-title">${t("canvas_title", lang)}</h1>
            <p class="section-subtitle">${t("canvas_subtitle", lang)}</p>
        </div>
        
        <section class="canvas-workspace">
            <div class="canvas-editor">
                <div class="canvas-toolbar">
                    <button>💾 ${t("canvas_save_draft", lang)}</button>
                    <button>📤 ${t("canvas_export", lang)}</button>
                    <button>🤖 ${t("canvas_ai_assist", lang)}</button>
                </div>
                <textarea class="canvas-textarea" placeholder="${t("canvas_placeholder", lang)}"></textarea>
            </div>
        </section>
        
        ${renderFooter(lang)}
    </body>
    </html>
  `
}
