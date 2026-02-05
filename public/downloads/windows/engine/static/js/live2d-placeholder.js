/**
 * Live2D Character Placeholder
 * Manages SVG-based character animations before real Live2D integration
 */

export type Live2DState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'busy';

export class Live2DPlaceholder {
  private container: HTMLElement;
  private imageElement: HTMLImageElement;
  private currentState: Live2DState = 'idle';
  
  constructor(containerId: string) {
    this.container = document.getElementById(containerId);
    
    if (!this.container) {
      console.error(`Container #${containerId} not found`);
      return;
    }
    
    // Create image element
    this.imageElement = document.createElement('img');
    this.imageElement.className = 'live2d-character-image';
    this.imageElement.alt = 'NEXUS AI Character';
    this.imageElement.style.width = '100%';
    this.imageElement.style.height = '100%';
    this.imageElement.style.objectFit = 'contain';
    
    this.container.appendChild(this.imageElement);
    
    // Set initial state
    this.setState('idle');
    
    console.log('Live2D Placeholder initialized');
  }
  
  /**
   * Change character state
   */
  setState(state: Live2DState): void {
    if (this.currentState === state) return;
    
    this.currentState = state;
    const imagePath = `/images/character/${state}.svg`;
    
    // Update image source
    this.imageElement.src = imagePath;
    
    // Update container data attribute for CSS styling
    this.container.setAttribute('data-status', state);
    
    console.log(`Live2D state changed: ${state}`);
  }
  
  /**
   * Get current state
   */
  getState(): Live2DState {
    return this.currentState;
  }
  
  /**
   * Hide character
   */
  hide(): void {
    this.container.style.display = 'none';
  }
  
  /**
   * Show character
   */
  show(): void {
    this.container.style.display = 'block';
  }
  
  /**
   * Cleanup
   */
  destroy(): void {
    if (this.imageElement && this.imageElement.parentNode) {
      this.imageElement.parentNode.removeChild(this.imageElement);
    }
    this.container.removeAttribute('data-status');
  }
}

/**
 * Auto-initialize on DOMContentLoaded
 */
if (typeof window !== 'undefined') {
  // Make Live2DPlaceholder globally available
  window.Live2DPlaceholder = Live2DPlaceholder;
}
