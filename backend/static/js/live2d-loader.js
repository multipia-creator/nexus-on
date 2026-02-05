/**
 * NEXUS-ON Live2D Loader
 * Uses pixi-live2d-display for Live2D Cubism 4.0 support
 */

class Live2DManager {
    constructor(containerId, modelPath) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('❌ Live2D container not found:', containerId);
            return;
        }

        this.modelPath = modelPath;
        this.app = null;
        this.model = null;
        this.currentMotion = null;
        
        // Motion mapping for NEXUS-ON states
        this.motionMapping = {
            'idle': 'haru_g_idle',           // Idle state - default
            'listening': 'haru_g_m01',       // Listening - nodding
            'thinking': 'haru_g_m02',        // Thinking - looking around
            'speaking': 'haru_g_m03',        // Speaking - talking
            'busy': 'haru_g_m04'             // Busy - working
        };

        this.init();
    }

    async init() {
        try {
            console.log('🎭 Initializing Live2D Manager...');
            
            // Wait for PIXI to be loaded
            if (typeof PIXI === 'undefined') {
                console.error('❌ PIXI.js not loaded');
                return;
            }

            // Wait for Live2D to be loaded
            if (typeof PIXI.live2d === 'undefined') {
                console.error('❌ pixi-live2d-display not loaded');
                return;
            }

            // Get container dimensions
            const rect = this.container.getBoundingClientRect();
            const width = rect.width || 280;
            const height = rect.height || 320;

            // Create PIXI Application
            this.app = new PIXI.Application({
                width: width,
                height: height,
                transparent: true,
                backgroundAlpha: 0,
                antialias: true,
                resolution: window.devicePixelRatio || 1,
                autoDensity: true
            });

            // Add canvas to container
            this.container.appendChild(this.app.view);

            // Load Live2D model
            await this.loadModel();

            console.log('✅ Live2D Manager initialized');
        } catch (error) {
            console.error('❌ Live2D initialization error:', error);
        }
    }

    async loadModel() {
        try {
            console.log('📦 Loading Live2D model from:', this.modelPath);

            // Load the model
            this.model = await PIXI.live2d.Live2DModel.from(this.modelPath);

            // Scale and position the model
            const scale = Math.min(
                this.app.screen.width / this.model.width,
                this.app.screen.height / this.model.height
            ) * 0.8;

            this.model.scale.set(scale);
            this.model.x = this.app.screen.width / 2;
            this.model.y = this.app.screen.height / 2;
            this.model.anchor.set(0.5, 0.5);

            // Add model to stage
            this.app.stage.addChild(this.model);

            // Enable interaction
            this.model.buttonMode = true;
            this.model.on('pointerdown', () => {
                console.log('🎭 Live2D model clicked');
                this.playRandomMotion();
            });

            // Start idle motion
            this.setState('idle');

            // Enable eye tracking (follow mouse)
            this.enableMouseTracking();

            console.log('✅ Live2D model loaded successfully');
        } catch (error) {
            console.error('❌ Failed to load Live2D model:', error);
            throw error;
        }
    }

    setState(state) {
        if (!this.model) {
            console.warn('⚠️ Model not loaded yet');
            return;
        }

        const motionFile = this.motionMapping[state] || this.motionMapping['idle'];
        console.log(`🎭 Changing state to: ${state} (motion: ${motionFile})`);

        // Update container data attribute
        this.container.setAttribute('data-status', state);

        // Play motion
        this.playMotion(motionFile);
    }

    playMotion(motionName) {
        if (!this.model || !this.model.internalModel) {
            console.warn('⚠️ Model not ready for motion playback');
            return;
        }

        try {
            // Find motion index by name
            const motions = this.model.internalModel.motionManager.definitions;
            let motionIndex = -1;

            for (let i = 0; i < motions.length; i++) {
                const motionFile = motions[i].File || motions[i].file;
                if (motionFile && motionFile.includes(motionName)) {
                    motionIndex = i;
                    break;
                }
            }

            if (motionIndex >= 0) {
                this.model.motion(motionIndex, 0, PIXI.live2d.MotionPriority.FORCE);
                console.log(`✅ Playing motion: ${motionName} (index: ${motionIndex})`);
            } else {
                console.warn(`⚠️ Motion not found: ${motionName}`);
            }
        } catch (error) {
            console.error('❌ Error playing motion:', error);
        }
    }

    playRandomMotion() {
        if (!this.model || !this.model.internalModel) return;

        const motions = this.model.internalModel.motionManager.definitions;
        const randomIndex = Math.floor(Math.random() * motions.length);
        this.model.motion(randomIndex, 0, PIXI.live2d.MotionPriority.FORCE);
    }

    enableMouseTracking() {
        if (!this.model) return;

        // Mouse tracking for eye following
        document.addEventListener('mousemove', (event) => {
            if (!this.model || !this.model.internalModel) return;

            const rect = this.container.getBoundingClientRect();
            const x = (event.clientX - rect.left - rect.width / 2) / rect.width * 2;
            const y = (event.clientY - rect.top - rect.height / 2) / rect.height * 2;

            // Update eye tracking parameters
            try {
                this.model.internalModel.coreModel.setParameterValueById('ParamAngleX', x * 30);
                this.model.internalModel.coreModel.setParameterValueById('ParamAngleY', -y * 30);
                this.model.internalModel.coreModel.setParameterValueById('ParamBodyAngleX', x * 10);
            } catch (error) {
                // Silently fail if parameters don't exist
            }
        });

        console.log('✅ Mouse tracking enabled');
    }

    destroy() {
        if (this.app) {
            this.app.destroy(true);
            this.app = null;
        }
        this.model = null;
    }
}

// Make globally available
window.Live2DManager = Live2DManager;
