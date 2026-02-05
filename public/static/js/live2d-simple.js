/**
 * NEXUS-ON Live2D Simple Manager
 * Direct integration with Live2D Cubism Core and PIXI.js
 */

class Live2DManager {
    constructor(containerId, modelPath) {
        console.log('🎨 Initializing Live2D Manager...');
        this.container = document.getElementById(containerId);
        this.modelPath = modelPath;
        this.model = null;
        this.app = null;
        this.currentState = 'idle';
        
        this.init();
    }

    async init() {
        try {
            // Validate dependencies
            if (typeof PIXI === 'undefined') {
                console.error('❌ PIXI.js not loaded');
                return;
            }

            if (typeof Live2DCubismCore === 'undefined') {
                console.error('❌ Live2D Cubism Core not loaded');
                return;
            }

            console.log('✅ Dependencies validated');

            // Create PIXI Application
            this.app = new PIXI.Application({
                view: document.createElement('canvas'),
                autoStart: true,
                transparent: true,
                width: 300,
                height: 400,
                resolution: window.devicePixelRatio || 1,
                autoDensity: true,
            });

            // Add canvas to container
            this.container.innerHTML = '';
            this.container.appendChild(this.app.view);
            this.container.classList.remove('loading');

            console.log('✅ PIXI Application created');

            // Load Live2D Model
            await this.loadModel();

        } catch (error) {
            console.error('❌ Live2D initialization error:', error);
            this.showFallback();
        }
    }

    async loadModel() {
        try {
            console.log('📦 Loading model from:', this.modelPath);

            // Fetch model3.json
            const response = await fetch(this.modelPath);
            if (!response.ok) {
                throw new Error(`Failed to load model: ${response.status}`);
            }

            const modelData = await response.json();
            console.log('✅ Model data loaded:', modelData);

            // Extract base path
            const basePath = this.modelPath.substring(0, this.modelPath.lastIndexOf('/') + 1);

            // Load .moc3 file
            const mocPath = basePath + modelData.FileReferences.Moc;
            const mocResponse = await fetch(mocPath);
            const mocArrayBuffer = await mocResponse.arrayBuffer();

            // Create Live2D model
            const moc = Live2DCubismCore.Moc.fromArrayBuffer(mocArrayBuffer);
            if (!moc) {
                throw new Error('Failed to create Moc from ArrayBuffer');
            }

            this.model = new Live2DCubismCore.Model(moc);
            console.log('✅ Live2D Model created');

            // Load textures
            await this.loadTextures(basePath, modelData.FileReferences.Textures);

            // Create PIXI sprite
            this.createSprite();

            // Start animation loop
            this.startAnimation();

            console.log('✅ Live2D model fully loaded');

        } catch (error) {
            console.error('❌ Model loading error:', error);
            this.showFallback();
        }
    }

    async loadTextures(basePath, texturePaths) {
        console.log('🎨 Loading textures...');
        
        const texturePromises = texturePaths.map(async (texturePath) => {
            const fullPath = basePath + texturePath;
            console.log('  Loading:', fullPath);
            
            const texture = await PIXI.Texture.fromURL(fullPath);
            return texture;
        });

        this.textures = await Promise.all(texturePromises);
        console.log('✅ Textures loaded:', this.textures.length);
    }

    createSprite() {
        // Create a simple sprite container
        this.sprite = new PIXI.Container();
        
        // Add textures as sprites
        this.textures.forEach((texture, index) => {
            const sprite = new PIXI.Sprite(texture);
            sprite.anchor.set(0.5);
            this.sprite.addChild(sprite);
        });

        // Center the sprite
        this.sprite.x = this.app.screen.width / 2;
        this.sprite.y = this.app.screen.height / 2;
        this.sprite.scale.set(0.5); // Scale down to fit

        this.app.stage.addChild(this.sprite);
        console.log('✅ Sprite created and added to stage');
    }

    startAnimation() {
        let elapsed = 0;
        
        this.app.ticker.add((delta) => {
            elapsed += delta * 0.01;
            
            // Simple breathing animation
            if (this.sprite) {
                this.sprite.scale.set(0.5 + Math.sin(elapsed) * 0.02);
            }

            // Update model parameters if available
            if (this.model) {
                // Simulate idle breathing
                const breathParam = this.model.parameters.ids.find(id => 
                    id.includes('Breath') || id.includes('breath')
                );
                if (breathParam) {
                    const paramIndex = this.model.parameters.ids.indexOf(breathParam);
                    this.model.parameters.values[paramIndex] = Math.sin(elapsed) * 0.5;
                }

                this.model.update();
            }
        });

        console.log('✅ Animation loop started');
    }

    setState(state) {
        console.log(`🎭 State change: ${this.currentState} → ${state}`);
        this.currentState = state;
        
        // Update container data attribute
        if (this.container) {
            this.container.setAttribute('data-status', state);
        }

        // Apply state-specific animations
        this.applyStateAnimation(state);
    }

    applyStateAnimation(state) {
        if (!this.sprite) return;

        // State-specific animations
        switch (state) {
            case 'idle':
                // Gentle breathing
                break;
            case 'listening':
                // Slight scale pulse
                this.sprite.scale.set(0.52);
                break;
            case 'thinking':
                // Slow rotation
                this.sprite.rotation = Math.PI / 180 * 5;
                break;
            case 'speaking':
                // Bounce animation
                this.sprite.y -= 10;
                setTimeout(() => {
                    if (this.sprite) this.sprite.y += 10;
                }, 200);
                break;
            case 'busy':
                // Faster breathing
                break;
        }
    }

    showFallback() {
        console.log('🎭 Showing fallback character');
        this.container.classList.remove('loading');
        this.container.innerHTML = `
            <div style="
                width: 300px;
                height: 400px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            ">
                <div style="font-size: 80px; margin-bottom: 16px;">🎭</div>
                <div style="font-size: 18px; font-weight: 600;">세리아</div>
                <div style="font-size: 14px; opacity: 0.8; margin-top: 8px;">NEXUS AI Assistant</div>
                <div style="font-size: 12px; opacity: 0.6; margin-top: 16px; text-align: center; padding: 0 20px;">
                    Live2D 모델을 불러오는 중...
                </div>
            </div>
        `;
    }

    destroy() {
        if (this.app) {
            this.app.destroy(true, { children: true, texture: true, baseTexture: true });
        }
        this.model = null;
        this.sprite = null;
    }
}

// Export to global scope
window.Live2DManager = Live2DManager;

console.log('✅ Live2D Simple Manager loaded');
