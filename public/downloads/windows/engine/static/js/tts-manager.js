/**
 * NEXUS-ON TTS Manager
 * Text-to-Speech using Web Speech API
 * Integrates with Live2D for lip-sync
 */

class TTSManager {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voices = [];
        this.currentUtterance = null;
        this.isSpeaking = false;
        this.defaultVoice = null;
        
        // Callbacks
        this.onStart = null;      // () => void
        this.onEnd = null;        // () => void
        this.onBoundary = null;   // (charIndex) => void
        
        this.init();
    }

    init() {
        if (!this.synth) {
            console.error('❌ Web Speech API not supported');
            return;
        }

        // Load voices
        this.loadVoices();
        
        // Voices might load asynchronously
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = () => this.loadVoices();
        }
        
        console.log('✅ TTS Manager initialized');
    }

    loadVoices() {
        this.voices = this.synth.getVoices();
        
        // Prefer Korean voices
        this.defaultVoice = this.voices.find(voice => 
            voice.lang.startsWith('ko-')
        ) || this.voices.find(voice => 
            voice.lang.startsWith('en-')
        ) || this.voices[0];
        
        console.log(`🗣️ Loaded ${this.voices.length} voices`);
        if (this.defaultVoice) {
            console.log(`🎤 Default voice: ${this.defaultVoice.name} (${this.defaultVoice.lang})`);
        }
    }

    /**
     * Speak text with TTS
     * @param {string} text - Text to speak
     * @param {object} options - TTS options
     * @returns {Promise<void>}
     */
    speak(text, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.synth) {
                reject(new Error('TTS not supported'));
                return;
            }

            // Stop current speech
            if (this.isSpeaking) {
                this.stop();
            }

            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);
            this.currentUtterance = utterance;

            // Set voice
            const voice = options.voice || this.defaultVoice;
            if (voice) {
                utterance.voice = voice;
            }

            // Set parameters
            utterance.lang = options.lang || 'ko-KR';
            utterance.rate = options.rate || 1.0;      // 0.1 to 10
            utterance.pitch = options.pitch || 1.0;    // 0 to 2
            utterance.volume = options.volume || 1.0;  // 0 to 1

            // Event handlers
            utterance.onstart = () => {
                this.isSpeaking = true;
                console.log('🎤 TTS started:', text.substring(0, 50));
                if (this.onStart) this.onStart();
            };

            utterance.onend = () => {
                this.isSpeaking = false;
                this.currentUtterance = null;
                console.log('🎤 TTS ended');
                if (this.onEnd) this.onEnd();
                resolve();
            };

            utterance.onerror = (event) => {
                this.isSpeaking = false;
                this.currentUtterance = null;
                console.error('❌ TTS error:', event.error);
                reject(new Error(event.error));
            };

            utterance.onboundary = (event) => {
                // Called at word boundaries (for lip-sync)
                if (this.onBoundary) {
                    this.onBoundary(event.charIndex);
                }
            };

            // Start speaking
            this.synth.speak(utterance);
        });
    }

    /**
     * Stop current speech
     */
    stop() {
        if (this.synth) {
            this.synth.cancel();
            this.isSpeaking = false;
            this.currentUtterance = null;
            console.log('🛑 TTS stopped');
        }
    }

    /**
     * Pause current speech
     */
    pause() {
        if (this.synth && this.isSpeaking) {
            this.synth.pause();
            console.log('⏸️ TTS paused');
        }
    }

    /**
     * Resume paused speech
     */
    resume() {
        if (this.synth) {
            this.synth.resume();
            console.log('▶️ TTS resumed');
        }
    }

    /**
     * Get available voices
     * @param {string} lang - Filter by language (optional)
     * @returns {Array}
     */
    getVoices(lang = null) {
        if (!lang) return this.voices;
        return this.voices.filter(voice => voice.lang.startsWith(lang));
    }

    /**
     * Set default voice
     * @param {string} voiceName - Voice name
     */
    setDefaultVoice(voiceName) {
        const voice = this.voices.find(v => v.name === voiceName);
        if (voice) {
            this.defaultVoice = voice;
            console.log(`🎤 Default voice set to: ${voice.name}`);
        } else {
            console.warn(`⚠️ Voice not found: ${voiceName}`);
        }
    }
}

// Global instance
window.ttsManager = new TTSManager();

console.log('✅ TTS Manager loaded');
