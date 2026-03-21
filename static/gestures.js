/**
 * Gesture Handler for Touch Devices
 * Swipe, pull-to-refresh, and haptic feedback
 */

class GestureHandler {
  constructor() {
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.touchEndX = 0;
    this.touchEndY = 0;
    this.minSwipeDistance = 50;
    this.callbacks = {
      swipeUp: [],
      swipeDown: [],
      swipeLeft: [],
      swipeRight: []
    };
    
    this.init();
  }

  init() {
    document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
    document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
    document.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
  }

  handleTouchStart(e) {
    this.touchStartX = e.changedTouches[0].screenX;
    this.touchStartY = e.changedTouches[0].screenY;
  }

  handleTouchMove(e) {
    this.touchEndX = e.changedTouches[0].screenX;
    this.touchEndY = e.changedTouches[0].screenY;
  }

  handleTouchEnd(e) {
    const deltaX = this.touchEndX - this.touchStartX;
    const deltaY = this.touchEndY - this.touchStartY;
    
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);
    
    // Determine primary direction
    if (Math.max(absDeltaX, absDeltaY) < this.minSwipeDistance) {
      return; // Not a swipe
    }
    
    if (absDeltaX > absDeltaY) {
      // Horizontal swipe
      if (deltaX > 0) {
        this.trigger('swipeRight', { deltaX, deltaY, target: e.target });
      } else {
        this.trigger('swipeLeft', { deltaX, deltaY, target: e.target });
      }
    } else {
      // Vertical swipe
      if (deltaY > 0) {
        this.trigger('swipeDown', { deltaX, deltaY, target: e.target });
      } else {
        this.trigger('swipeUp', { deltaX, deltaY, target: e.target });
      }
    }
  }

  on(gesture, callback) {
    if (this.callbacks[gesture]) {
      this.callbacks[gesture].push(callback);
    }
  }

  off(gesture, callback) {
    if (this.callbacks[gesture]) {
      this.callbacks[gesture] = this.callbacks[gesture].filter(cb => cb !== callback);
    }
  }

  trigger(gesture, data) {
    if (this.callbacks[gesture]) {
      this.callbacks[gesture].forEach(callback => callback(data));
    }
  }

  vibrate(pattern = 10) {
    if ('vibrate' in navigator) {
      navigator.vibrate(pattern);
    }
  }
}

// Pull-to-refresh implementation
class PullToRefresh {
  constructor(element, callback) {
    this.element = element;
    this.callback = callback;
    this.pullStartY = 0;
    this.pullDistance = 0;
    this.threshold = 80;
    this.isRefreshing = false;
    this.indicator = null;
    
    this.init();
  }

  init() {
    this.createIndicator();
    
    this.element.addEventListener('touchstart', (e) => {
      if (this.element.scrollTop === 0 && !this.isRefreshing) {
        this.pullStartY = e.touches[0].clientY;
      }
    }, { passive: true });
    
    this.element.addEventListener('touchmove', (e) => {
      if (this.pullStartY > 0 && !this.isRefreshing) {
        this.pullDistance = e.touches[0].clientY - this.pullStartY;
        
        if (this.pullDistance > 0) {
          e.preventDefault();
          this.updateIndicator();
        }
      }
    }, { passive: false });
    
    this.element.addEventListener('touchend', () => {
      if (this.pullDistance >= this.threshold && !this.isRefreshing) {
        this.triggerRefresh();
      } else {
        this.resetIndicator();
      }
      
      this.pullStartY = 0;
      this.pullDistance = 0;
    }, { passive: true });
  }

  createIndicator() {
    this.indicator = document.createElement('div');
    this.indicator.style.cssText = `
      position: absolute;
      top: -60px;
      left: 50%;
      transform: translateX(-50%);
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      transition: all 0.3s ease;
      z-index: 100;
    `;
    this.indicator.innerHTML = '↓';
    this.element.style.position = 'relative';
    this.element.appendChild(this.indicator);
  }

  updateIndicator() {
    const progress = Math.min(this.pullDistance / this.threshold, 1);
    const rotation = progress * 180;
    
    this.indicator.style.top = `${-60 + this.pullDistance * 0.5}px`;
    this.indicator.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
    this.indicator.style.opacity = progress;
  }

  async triggerRefresh() {
    this.isRefreshing = true;
    this.indicator.innerHTML = '⟳';
    this.indicator.style.animation = 'spin 1s linear infinite';
    this.indicator.style.top = '10px';
    
    // Haptic feedback
    if ('vibrate' in navigator) {
      navigator.vibrate(50);
    }
    
    try {
      await this.callback();
    } finally {
      this.resetIndicator();
      this.isRefreshing = false;
    }
  }

  resetIndicator() {
    this.indicator.style.top = '-60px';
    this.indicator.style.transform = 'translateX(-50%) rotate(0deg)';
    this.indicator.style.opacity = '0';
    this.indicator.style.animation = 'none';
    this.indicator.innerHTML = '↓';
  }
}

// Add spin animation to document
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: translateX(-50%) rotate(0deg); }
    to { transform: translateX(-50%) rotate(360deg); }
  }
`;
document.head.appendChild(style);

// Export
window.GestureHandler = GestureHandler;
window.PullToRefresh = PullToRefresh;
