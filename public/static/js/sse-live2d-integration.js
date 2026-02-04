/**
 * NEXUS-ON SSE + Live2D Integration
 * Connects to Backend SSE stream and syncs agent_status with Live2D character states
 * 
 * Features:
 * - EventSource SSE connection with auto-reconnect
 * - agent_status → Live2D setState mapping
 * - TTS event handling for lip-sync
 * - Worklog/Asks UI updates
 */

class NexusSSEClient {
    constructor(apiKey, orgId = 'default', projectId = 'default') {
        this.apiKey = apiKey;
        this.orgId = orgId;
        this.projectId = projectId;
        this.eventSource = null;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.currentDelay = this.reconnectDelay;
        this.cursor = 0;
        this.isConnecting = false;
        
        // Callbacks
        this.onAgentStatus = null;  // (status, context) => void
        this.onTTSStart = null;     // (data) => void
        this.onTTSChunk = null;     // (data) => void
        this.onTTSEnd = null;       // (data) => void
        this.onReport = null;       // (report) => void
        this.onSnapshot = null;     // (snapshot) => void
        this.onWorklog = null;      // (worklog) => void
        this.onAsk = null;          // (ask) => void
    }

    connect() {
        if (this.isConnecting || this.eventSource) {
            console.log('[SSE] Already connecting or connected');
            return;
        }

        this.isConnecting = true;
        const url = `/agent/reports/stream?api_key=${encodeURIComponent(this.apiKey)}&org_id=${encodeURIComponent(this.orgId)}&project_id=${encodeURIComponent(this.projectId)}&cursor=${this.cursor}`;
        
        console.log('[SSE] Connecting to:', url);
        
        this.eventSource = new EventSource(url);

        this.eventSource.onopen = () => {
            console.log('[SSE] Connected successfully');
            this.isConnecting = false;
            this.currentDelay = this.reconnectDelay; // Reset delay on successful connection
        };

        // Handle agent_status events
        this.eventSource.addEventListener('agent_status', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] agent_status:', data);
                
                if (this.onAgentStatus) {
                    this.onAgentStatus(data.status, data.context);
                }
                
                // Update cursor
                if (e.lastEventId) {
                    this.cursor = parseInt(e.lastEventId);
                }
            } catch (err) {
                console.error('[SSE] Error parsing agent_status:', err);
            }
        });

        // Handle TTS events
        this.eventSource.addEventListener('tts_start', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] tts_start:', data);
                
                if (this.onTTSStart) {
                    this.onTTSStart(data);
                }
                
                if (e.lastEventId) {
                    this.cursor = parseInt(e.lastEventId);
                }
            } catch (err) {
                console.error('[SSE] Error parsing tts_start:', err);
            }
        });

        this.eventSource.addEventListener('tts_chunk', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] tts_chunk');
                
                if (this.onTTSChunk) {
                    this.onTTSChunk(data);
                }
                
                if (e.lastEventId) {
                    this.cursor = parseInt(e.lastEventId);
                }
            } catch (err) {
                console.error('[SSE] Error parsing tts_chunk:', err);
            }
        });

        this.eventSource.addEventListener('tts_end', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] tts_end:', data);
                
                if (this.onTTSEnd) {
                    this.onTTSEnd(data);
                }
                
                if (e.lastEventId) {
                    this.cursor = parseInt(e.lastEventId);
                }
            } catch (err) {
                console.error('[SSE] Error parsing tts_end:', err);
            }
        });

        // Handle report events
        this.eventSource.addEventListener('report', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] report:', data.status, data.summary);
                
                if (this.onReport) {
                    this.onReport(data);
                }
                
                if (e.lastEventId) {
                    this.cursor = parseInt(e.lastEventId);
                }
            } catch (err) {
                console.error('[SSE] Error parsing report:', err);
            }
        });

        // Handle snapshot events
        this.eventSource.addEventListener('snapshot', (e) => {
            try {
                const data = JSON.parse(e.data);
                console.log('[SSE] snapshot received');
                
                if (this.onSnapshot) {
                    this.onSnapshot(data);
                }
                
                if (e.lastEventId) {
                    this.cursor = parseInt(e.lastEventId);
                }
            } catch (err) {
                console.error('[SSE] Error parsing snapshot:', err);
            }
        });

        // Handle ping events
        this.eventSource.addEventListener('ping', (e) => {
            console.log('[SSE] ping');
        });

        this.eventSource.onerror = (err) => {
            console.error('[SSE] Connection error:', err);
            this.disconnect();
            this.scheduleReconnect();
        };
    }

    disconnect() {
        if (this.eventSource) {
            console.log('[SSE] Disconnecting');
            this.eventSource.close();
            this.eventSource = null;
        }
        this.isConnecting = false;
    }

    scheduleReconnect() {
        console.log(`[SSE] Reconnecting in ${this.currentDelay}ms...`);
        setTimeout(() => {
            this.connect();
        }, this.currentDelay);

        // Exponential backoff
        this.currentDelay = Math.min(this.currentDelay * 2, this.maxReconnectDelay);
    }
}


/**
 * Live2D + SSE Integration Manager
 * Connects SSE agent_status events to Live2D character states
 */
class Live2DAgentIntegration {
    constructor(apiKey, orgId = 'default', projectId = 'default') {
        this.sseClient = new NexusSSEClient(apiKey, orgId, projectId);
        this.live2dManager = window.live2dManager; // Assumes Live2DManager is already loaded
        this.isSpeaking = false;
        this.speakingTimeout = null;
        
        this.setupHandlers();
    }

    setupHandlers() {
        // agent_status → Live2D setState mapping
        this.sseClient.onAgentStatus = (status, context) => {
            console.log(`[Live2D Agent] Status change: ${status}`, context);
            
            if (this.live2dManager) {
                // Map agent_status to Live2D states
                switch (status) {
                    case 'idle':
                        this.live2dManager.setState('idle');
                        this.isSpeaking = false;
                        break;
                    case 'listening':
                        this.live2dManager.setState('listening');
                        break;
                    case 'thinking':
                        this.live2dManager.setState('thinking');
                        break;
                    case 'speaking':
                        this.live2dManager.setState('speaking');
                        this.isSpeaking = true;
                        break;
                    case 'busy':
                        this.live2dManager.setState('busy');
                        break;
                    case 'waiting_approval':
                        // Special visual effect for waiting approval
                        this.live2dManager.setState('busy'); // Use busy state with visual indicator
                        break;
                    default:
                        console.warn(`[Live2D Agent] Unknown status: ${status}`);
                        this.live2dManager.setState('idle');
                }
            } else {
                console.warn('[Live2D Agent] Live2DManager not available');
            }
        };

        // TTS event handlers (for future lip-sync integration)
        this.sseClient.onTTSStart = (data) => {
            console.log('[Live2D Agent] TTS started:', data.text);
            // Future: Start lip-sync animation
            if (this.live2dManager) {
                this.live2dManager.setState('speaking');
            }
        };

        this.sseClient.onTTSEnd = (data) => {
            console.log('[Live2D Agent] TTS ended, duration:', data.duration_ms);
            // Future: Stop lip-sync animation
            // Wait a bit before returning to idle
            if (this.speakingTimeout) {
                clearTimeout(this.speakingTimeout);
            }
            this.speakingTimeout = setTimeout(() => {
                if (this.live2dManager) {
                    this.live2dManager.setState('idle');
                }
                this.isSpeaking = false;
            }, 500); // 500ms buffer after TTS ends
        };

        // Report handler (for UI updates)
        this.sseClient.onReport = (report) => {
            console.log('[Live2D Agent] Report received:', report);
            // Future: Update UI with report data
            // e.g., worklog updates, chat messages, etc.
        };

        // Snapshot handler (initial state)
        this.sseClient.onSnapshot = (snapshot) => {
            console.log('[Live2D Agent] Snapshot received:', snapshot);
            // Future: Initialize UI with snapshot data
            // e.g., load existing asks, worklog, autopilot state
        };
    }

    connect() {
        console.log('[Live2D Agent] Connecting to SSE stream...');
        this.sseClient.connect();
    }

    disconnect() {
        console.log('[Live2D Agent] Disconnecting from SSE stream...');
        this.sseClient.disconnect();
    }
}


// Global initialization
window.NexusSSEClient = NexusSSEClient;
window.Live2DAgentIntegration = Live2DAgentIntegration;

console.log('✅ SSE + Live2D Integration loaded');
