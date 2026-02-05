/**
 * Simple Live2D Loader using Cubism Core 4 + PIXI.js
 * No pixi-live2d-display dependency
 */

class SimpleLive2DManager {
    constructor(containerId, modelPath) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('❌ Container not found:', containerId);
            return;
        }

        this.modelPath = modelPath;
        this.app = null;
        this.model = null;
        
        console.log('🎭 SimpleLive2DManager initialized');
        this.init();
    }

    async init() {
        try {
            // Check PIXI
            if (typeof PIXI === 'undefined') {
                console.error('❌ PIXI not loaded');
                return;
            }
            console.log('✅ PIXI loaded:', PIXI.VERSION);

            // Check Cubism Core
            if (typeof Live2DCubismCore === 'undefined') {
                console.error('❌ Live2DCubismCore not loaded');
                return;
            }
            console.log('✅ Cubism Core loaded:', Live2DCubismCore.Version);

            // Create PIXI app
            const rect = this.container.getBoundingClientRect();
            this.app = new PIXI.Application({
                width: rect.width || 280,
                height: rect.height || 320,
                transparent: true,
                backgroundAlpha: 0,
                antialias: true,
                resolution: window.devicePixelRatio || 1,
                autoDensity: true
            });

            this.container.appendChild(this.app.view);
            console.log('✅ PIXI app created');

            // Show placeholder
            this.showPlaceholder();

        } catch (error) {
            console.error('❌ Init error:', error);
        }
    }

    showPlaceholder() {
        // Create a simple animated placeholder
        const graphics = new PIXI.Graphics();
        graphics.beginFill(0x3B82F6, 0.3);
        graphics.drawCircle(0, 0, 50);
        graphics.endFill();
        
        graphics.x = this.app.screen.width / 2;
        graphics.y = this.app.screen.height / 2;
        
        this.app.stage.addChild(graphics);

        // Animate
        let scale = 1;
        let growing = true;
        
        this.app.ticker.add(() => {
            if (growing) {
                scale += 0.01;
                if (scale >= 1.2) growing = false;
            } else {
                scale -= 0.01;
                if (scale <= 0.8) growing = true;
            }
            graphics.scale.set(scale);
        });

        // Add text
        const text = new PIXI.Text('🎭', {
            fontSize: 64,
            fill: 0x3B82F6
        });
        text.anchor.set(0.5);
        text.x = this.app.screen.width / 2;
        text.y = this.app.screen.height / 2;
        this.app.stage.addChild(text);

        console.log('✅ Placeholder shown (Live2D model loading not yet implemented)');
    }

    setState(state) {
        console.log('🎭 State change:', state);
        // Placeholder for state changes
    }

    destroy() {
        if (this.app) {
            this.app.destroy(true);
            this.app = null;
        }
    }
}

// Make globally available
window.SimpleLive2DManager = SimpleLive2DManager;
window.Live2DManager = SimpleLive2DManager; // Alias for compatibility
