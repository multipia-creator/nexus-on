/**
 * NEXUS-ON - Live2D Character Component
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 */

import { Live2DState } from '../shared/types'

export function renderLive2DComponent(pageState: Live2DState = 'idle'): string {
  return `
    <!-- Live2D Character Container -->
    <div id="live2d-container" class="live2d-container loading" data-status="${pageState}">
        <!-- Live2D canvas will be injected here -->
    </div>

    <!-- Live2D Styles -->
    <link rel="stylesheet" href="/static/css/live2d.css">

    <!-- PIXI.js v7.x (Required for Live2D) -->
    <script src="https://cdn.jsdelivr.net/npm/pixi.js@7.3.2/dist/pixi.min.js"></script>
    
    <!-- Live2D Cubism Core -->
    <script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
    
    <!-- pixi-live2d-display (LOCAL) -->
    <script src="/static/js/pixi-live2d-display.min.js"></script>

    <!-- Live2D Manager -->
    <script src="/static/js/live2d-loader.js"></script>

    <!-- TTS Manager -->
    <script src="/static/js/tts-manager.js"></script>

    <!-- Initialize Live2D -->
    <script>
        let live2dManager = null;
        
        window.addEventListener('DOMContentLoaded', () => {
            try {
                const container = document.getElementById('live2d-container');
                if (!container) {
                    console.error('❌ Live2D container not found');
                    return;
                }

                // Show loading state
                container.classList.add('loading');

                // Initialize Live2D Manager
                setTimeout(() => {
                    try {
                        live2dManager = new Live2DManager(
                            'live2d-container',
                            '/live2d/haru_greeter_t05.model3.json'
                        );
                        
                        // Set initial state
                        setTimeout(() => {
                            if (live2dManager && live2dManager.model) {
                                live2dManager.setState('${pageState}');
                                container.classList.remove('loading');
                                console.log('✅ Live2D initialized with state: ${pageState}');
                            }
                        }, 1000);
                        
                    } catch (error) {
                        console.error('❌ Live2D initialization error:', error);
                        container.classList.remove('loading');
                        container.classList.add('error');
                    }
                }, 500);
                
            } catch (error) {
                console.error('❌ Live2D setup error:', error);
            }
        });
        
        // Make globally available for state changes
        window.nexusCharacter = function() {
            return {
                setState: (state) => {
                    if (live2dManager) {
                        live2dManager.setState(state);
                    }
                },
                hide: () => {
                    const container = document.getElementById('live2d-container');
                    if (container) container.style.display = 'none';
                },
                show: () => {
                    const container = document.getElementById('live2d-container');
                    if (container) container.style.display = 'block';
                }
            };
        };
    </script>
  `
}
