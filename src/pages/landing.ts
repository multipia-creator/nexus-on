/**
 * NEXUS-ON - Landing Page
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 * World-class landing page with Live2D character, AI chat input, and core values
 */

import { Language, t } from '../../shared/i18n'
import { renderWorldClassStyles } from '../../shared/styles'
import { renderLive2DComponent } from '../components/live2d'
import { renderNavigation } from '../components/navigation'
import { renderFooter } from '../components/footer'

export function landingPage(lang: Language = 'ko'): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS-ON | ${t('hero_subtitle', lang)}</title>
        ${renderWorldClassStyles()}
    </head>
    <body data-page-state="idle">
        ${renderNavigation('/', lang)}
        
        <!-- Live2D Character (Idle state for landing) -->
        ${renderLive2DComponent('idle')}
        
        <!-- HERO SECTION -->
        <section class="hero-world-class">
            <div class="hero-content">
                <h1 class="hero-title">${t('hero_title', lang)}</h1>
                <p class="hero-subtitle">${t('hero_subtitle', lang)}</p>
                <p class="hero-tagline">${t('hero_tagline', lang)}</p>
                
                <!-- AI Chat Input UI (Below Live2D Character) -->
                <div class="hero-input-container">
                    <div class="hero-input-wrapper">
                        <input 
                            type="text" 
                            class="hero-input" 
                            placeholder="${t('hero_input_placeholder', lang)}"
                            id="hero-chat-input"
                        />
                        <button class="hero-voice-btn" id="voice-input-btn" title="${t('hero_voice_button', lang)}">
                            🎤
                        </button>
                        <button class="hero-send-btn" id="send-btn" title="${t('hero_text_button', lang)}">
                            →
                        </button>
                    </div>
                </div>
                
                <div class="hero-cta-group">
                    <a href="/signup?lang=${lang}" class="btn-glass-primary">${t('hero_cta_primary', lang)}</a>
                    <a href="#demo" class="btn-glass-secondary">${t('hero_cta_secondary', lang)}</a>
                </div>
            </div>
        </section>
        
        <!-- 3 CORE VALUES -->
        <section class="core-values">
            <div class="core-values-grid">
                <div class="value-card">
                    <div class="value-icon">🎭</div>
                    <h3 class="value-title">${t('value1_title', lang)}</h3>
                    <p class="value-desc">${t('value1_desc', lang)}</p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🤖</div>
                    <h3 class="value-title">${t('value2_title', lang)}</h3>
                    <p class="value-desc">${t('value2_desc', lang)}</p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🇰🇷</div>
                    <h3 class="value-title">${t('value3_title', lang)}</h3>
                    <p class="value-desc">${t('value3_desc', lang)}</p>
                </div>
            </div>
        </section>
        
        <!-- WINDOWS 11 ENGINE DOWNLOAD SECTION -->
        <section class="download-section">
            <div class="container">
                <h2 class="section-title">${t('download_title', lang)}</h2>
                <p class="section-subtitle">${t('download_subtitle', lang)}</p>
                
                <div class="download-container">
                    <div class="download-main">
                        <div class="download-icon">💻</div>
                        <a href="/downloads/windows" class="btn-glass-primary btn-lg">
                            ${t('download_cta', lang)}
                        </a>
                        <p class="download-info">${t('download_install_time', lang)}</p>
                    </div>
                    
                    <div class="download-requirements">
                        <h3>${t('download_requirements', lang)}</h3>
                        <ul class="requirements-list">
                            <li>✅ ${t('download_req_os', lang)}</li>
                            <li>✅ ${t('download_req_ram', lang)}</li>
                            <li>✅ ${t('download_req_disk', lang)}</li>
                            <li>✅ ${t('download_req_python', lang)}</li>
                        </ul>
                        <a href="/docs/windows-installation" class="download-guide-link">
                            📖 ${t('download_guide', lang)}
                        </a>
                    </div>
                </div>
            </div>
        </section>
        
        <style>
            .download-section {
                padding: var(--space-20) var(--space-6);
                background: linear-gradient(135deg, #f5f7fa 0%, #e3e7ed 100%);
            }
            
            .download-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--space-8);
                max-width: 1000px;
                margin: var(--space-12) auto 0;
            }
            
            .download-main {
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                padding: var(--space-12);
                text-align: center;
                border: 1px solid var(--border-default);
                box-shadow: var(--shadow-xl);
            }
            
            .download-icon {
                font-size: 80px;
                margin-bottom: var(--space-6);
                animation: float 3s ease-in-out infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            .btn-lg {
                font-size: var(--text-lg);
                padding: var(--space-6) var(--space-12);
            }
            
            .download-info {
                margin-top: var(--space-4);
                color: var(--text-secondary);
                font-size: var(--text-sm);
            }
            
            .download-requirements {
                background: white;
                border-radius: var(--radius-xl);
                padding: var(--space-8);
                border: 1px solid var(--border-default);
            }
            
            .download-requirements h3 {
                font-size: var(--text-xl);
                font-weight: 700;
                margin-bottom: var(--space-6);
                color: var(--text-primary);
            }
            
            .requirements-list {
                list-style: none;
                padding: 0;
                margin: 0 0 var(--space-6) 0;
            }
            
            .requirements-list li {
                padding: var(--space-3) 0;
                color: var(--text-secondary);
                font-size: var(--text-base);
                line-height: 1.6;
            }
            
            .download-guide-link {
                display: inline-block;
                color: var(--accent-primary);
                text-decoration: none;
                font-weight: 600;
                transition: all var(--duration-ui) var(--ease-out);
            }
            
            .download-guide-link:hover {
                color: var(--accent-secondary);
                transform: translateX(4px);
            }
            
            @media (max-width: 768px) {
                .download-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        
        ${renderFooter(lang)}
        
        <!-- Chat Input & Voice Interaction -->
        <script>
            // Chat input handler
            const chatInput = document.getElementById('hero-chat-input');
            const sendBtn = document.getElementById('send-btn');
            const voiceBtn = document.getElementById('voice-input-btn');
            const character = window.nexusCharacter();
            
            // Send message
            function sendMessage() {
                const message = chatInput.value.trim();
                if (!message) return;
                
                console.log('Sending message:', message);
                if (character) character.setState('thinking');
                
                // Simulate response
                setTimeout(() => {
                    if (character) character.setState('speaking');
                    setTimeout(() => {
                        if (character) character.setState('idle');
                    }, 2000);
                }, 1000);
                
                chatInput.value = '';
            }
            
            sendBtn.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            // Voice input
            voiceBtn.addEventListener('click', () => {
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    const recognition = new SpeechRecognition();
                    recognition.lang = '${lang}';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    
                    recognition.onstart = () => {
                        if (character) character.setState('listening');
                        voiceBtn.style.background = 'var(--accent-primary)';
                        voiceBtn.style.color = 'white';
                    };
                    
                    recognition.onresult = (event) => {
                        const transcript = event.results[0][0].transcript;
                        chatInput.value = transcript;
                        if (character) character.setState('thinking');
                    };
                    
                    recognition.onend = () => {
                        voiceBtn.style.background = '';
                        voiceBtn.style.color = '';
                        if (character) character.setState('idle');
                    };
                    
                    recognition.onerror = (event) => {
                        console.error('Speech recognition error:', event.error);
                        voiceBtn.style.background = '';
                        voiceBtn.style.color = '';
                        if (character) character.setState('idle');
                    };
                    
                    recognition.start();
                } else {
                    alert('${t('voice_not_supported', lang)}');
                }
            });
        </script>
        
        <!-- Scroll-based state changes -->
        <script>
            window.addEventListener('scroll', function() {
                const scrollY = window.scrollY;
                const character = window.nexusCharacter();
                if (!character) return;
                
                if (scrollY < 300) {
                    character.setState('idle');
                } else if (scrollY < 600) {
                    character.setState('listening');
                } else {
                    character.setState('thinking');
                }
            });
        </script>
    </body>
    </html>
  `
}
