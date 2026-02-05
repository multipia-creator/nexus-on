/**
 * NEXUS-ON Live2D Integration
 * Simple Cubism SDK 4 Implementation with Canvas
 * 
 * This is a simplified version that works reliably without complex dependencies
 */

class SimpleLive2DManager {
  constructor(canvasId = 'live2d-canvas', modelPath = '/live2d/haru_greeter_t05.model3.json') {
    this.canvas = document.getElementById(canvasId)
    this.modelPath = modelPath
    this.state = 'idle'
    this.isInitialized = false
    
    // Animation state
    this.currentMotion = null
    this.animationFrame = 0
    this.lastTime = Date.now()
    
    // Mouse tracking
    this.mouseX = 0
    this.mouseY = 0
    
    console.log('SimpleLive2DManager created')
  }
  
  async init() {
    if (this.isInitialized) return
    
    try {
      console.log('🎭 Initializing Simple Live2D Manager...')
      
      if (!this.canvas) {
        throw new Error('Canvas element not found')
      }
      
      // Setup canvas
      const ctx = this.canvas.getContext('2d')
      if (!ctx) {
        throw new Error('Could not get canvas 2D context')
      }
      
      this.ctx = ctx
      this.setupCanvas()
      this.setupMouseTracking()
      
      // For now, draw a placeholder character
      // In a full implementation, we would load the Cubism model here
      this.drawPlaceholder()
      this.startAnimation()
      
      this.isInitialized = true
      console.log('✅ Simple Live2D Manager initialized (placeholder mode)')
      
    } catch (error) {
      console.error('❌ Failed to initialize Live2D:', error)
      this.drawError()
    }
  }
  
  setupCanvas() {
    // Set canvas size
    const container = this.canvas.parentElement
    const width = container.clientWidth || 300
    const height = container.clientHeight || 400
    
    this.canvas.width = width
    this.canvas.height = height
    
    console.log(`Canvas setup: ${width}x${height}`)
  }
  
  setupMouseTracking() {
    document.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect()
      this.mouseX = (e.clientX - rect.left) / rect.width * 2 - 1
      this.mouseY = -((e.clientY - rect.top) / rect.height * 2 - 1)
    })
    
    this.canvas.addEventListener('click', () => {
      this.playRandomMotion()
    })
  }
  
  drawPlaceholder() {
    const ctx = this.ctx
    const w = this.canvas.width
    const h = this.canvas.height
    
    // Clear canvas
    ctx.clearRect(0, 0, w, h)
    
    // Draw character silhouette
    ctx.save()
    
    // Body
    const centerX = w / 2
    const centerY = h * 0.6
    const bodyWidth = w * 0.4
    const bodyHeight = h * 0.5
    
    // Gradient fill
    const gradient = ctx.createLinearGradient(centerX - bodyWidth/2, centerY - bodyHeight/2, 
                                               centerX + bodyWidth/2, centerY + bodyHeight/2)
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)')
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.3)')
    
    ctx.fillStyle = gradient
    
    // Draw rounded rectangle for body
    this.roundRect(ctx, centerX - bodyWidth/2, centerY - bodyHeight/2, bodyWidth, bodyHeight, 20)
    ctx.fill()
    
    // Draw head
    const headRadius = w * 0.15
    const headY = centerY - bodyHeight/2 - headRadius * 0.7
    
    ctx.beginPath()
    ctx.arc(centerX, headY, headRadius, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(139, 92, 246, 0.4)'
    ctx.fill()
    
    // Draw eyes (following mouse)
    const eyeY = headY - headRadius * 0.1
    const eyeSpacing = headRadius * 0.5
    const eyeOffsetX = this.mouseX * 5
    const eyeOffsetY = this.mouseY * 5
    
    // Left eye
    ctx.beginPath()
    ctx.arc(centerX - eyeSpacing + eyeOffsetX, eyeY + eyeOffsetY, 5, 0, Math.PI * 2)
    ctx.fillStyle = '#1F2937'
    ctx.fill()
    
    // Right eye
    ctx.beginPath()
    ctx.arc(centerX + eyeSpacing + eyeOffsetX, eyeY + eyeOffsetY, 5, 0, Math.PI * 2)
    ctx.fillStyle = '#1F2937'
    ctx.fill()
    
    // Draw mouth based on state
    this.drawMouth(ctx, centerX, eyeY + headRadius * 0.4)
    
    // Draw state indicator
    this.drawStateIndicator(ctx, 20, 20)
    
    ctx.restore()
  }
  
  drawMouth(ctx, x, y) {
    const states = {
      idle: { curve: 0, width: 20 },
      listening: { curve: 5, width: 25 },
      thinking: { curve: -2, width: 15 },
      speaking: { curve: 10, width: 30 },
      busy: { curve: 3, width: 20 }
    }
    
    const config = states[this.state] || states.idle
    const openAmount = Math.abs(Math.sin(this.animationFrame * 0.1)) * config.curve
    
    ctx.beginPath()
    ctx.moveTo(x - config.width/2, y)
    ctx.quadraticCurveTo(x, y + openAmount, x + config.width/2, y)
    ctx.strokeStyle = '#1F2937'
    ctx.lineWidth = 3
    ctx.lineCap = 'round'
    ctx.stroke()
  }
  
  drawStateIndicator(ctx, x, y) {
    const stateColors = {
      idle: '#10B981',
      listening: '#3B82F6',
      thinking: '#F59E0B',
      speaking: '#8B5CF6',
      busy: '#EF4444'
    }
    
    const stateIcons = {
      idle: '😌',
      listening: '👂',
      thinking: '🤔',
      speaking: '🗣️',
      busy: '⚙️'
    }
    
    // Draw colored circle
    ctx.beginPath()
    ctx.arc(x + 15, y + 15, 12, 0, Math.PI * 2)
    ctx.fillStyle = stateColors[this.state] || stateColors.idle
    ctx.fill()
    
    // Draw icon
    ctx.font = '16px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(stateIcons[this.state] || stateIcons.idle, x + 15, y + 15)
    
    // Draw state label
    ctx.font = 'bold 12px Arial'
    ctx.fillStyle = '#1F2937'
    ctx.textAlign = 'left'
    ctx.fillText(this.state.toUpperCase(), x + 35, y + 15)
  }
  
  roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath()
    ctx.moveTo(x + radius, y)
    ctx.lineTo(x + width - radius, y)
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
    ctx.lineTo(x + width, y + height - radius)
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
    ctx.lineTo(x + radius, y + height)
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
    ctx.lineTo(x, y + radius)
    ctx.quadraticCurveTo(x, y, x + radius, y)
    ctx.closePath()
  }
  
  drawError() {
    const ctx = this.ctx
    const w = this.canvas.width
    const h = this.canvas.height
    
    ctx.clearRect(0, 0, w, h)
    ctx.fillStyle = '#EF4444'
    ctx.font = 'bold 16px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('❌ Live2D Error', w / 2, h / 2)
  }
  
  startAnimation() {
    const animate = () => {
      const now = Date.now()
      const delta = now - this.lastTime
      this.lastTime = now
      
      this.animationFrame += delta / 1000 * 60 // 60 FPS equivalent
      
      this.drawPlaceholder()
      
      requestAnimationFrame(animate)
    }
    
    animate()
  }
  
  setState(newState) {
    const validStates = ['idle', 'listening', 'thinking', 'speaking', 'busy']
    if (!validStates.includes(newState)) {
      console.warn(`Invalid state: ${newState}`)
      return
    }
    
    console.log(`🎭 State changed: ${this.state} → ${newState}`)
    this.state = newState
  }
  
  playRandomMotion() {
    console.log('🎵 Playing random motion')
    // In full implementation, this would trigger a Cubism motion
    const states = ['idle', 'listening', 'thinking', 'speaking', 'busy']
    const randomState = states[Math.floor(Math.random() * states.length)]
    this.setState(randomState)
    
    // Return to idle after 2 seconds
    setTimeout(() => this.setState('idle'), 2000)
  }
  
  show() {
    if (this.canvas) {
      this.canvas.style.display = 'block'
    }
  }
  
  hide() {
    if (this.canvas) {
      this.canvas.style.display = 'none'
    }
  }
}

// Global instance
let live2dManager = null

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLive2D)
} else {
  initLive2D()
}

function initLive2D() {
  // Wait for canvas to be available
  const checkCanvas = setInterval(() => {
    const canvas = document.getElementById('live2d-canvas')
    if (canvas) {
      clearInterval(checkCanvas)
      
      live2dManager = new SimpleLive2DManager()
      live2dManager.init()
      
      // Set initial state from data attribute
      const container = document.getElementById('live2d-container')
      if (container) {
        const initialState = container.dataset.status || 'idle'
        live2dManager.setState(initialState)
        
        // Remove loading class
        container.classList.remove('loading')
      }
      
      // Expose to window for external control
      window.nexusLive2D = live2dManager
    }
  }, 100)
  
  // Timeout after 5 seconds
  setTimeout(() => clearInterval(checkCanvas), 5000)
}

console.log('✅ Simple Live2D loader script loaded')
