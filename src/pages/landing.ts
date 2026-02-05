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
