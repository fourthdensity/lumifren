/**
 * Toast Notification System for Lumifren
 * Lightweight notification manager with animations
 */

class ToastManager {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.style.cssText = `
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 12px;
        pointer-events: none;
      `;
      document.body.appendChild(this.container);
    }
  }

  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const colors = {
      info: 'var(--accent-primary)',
      success: 'var(--accent-tertiary)',
      error: 'var(--accent-secondary)',
      warning: '#ff9500'
    };
    
    const icons = {
      info: 'ℹ️',
      success: '✓',
      error: '✕',
      warning: '⚠'
    };
    
    toast.style.cssText = `
      background: rgba(18, 18, 22, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid ${colors[type] || colors.info};
      border-radius: 12px;
      padding: 14px 20px;
      color: white;
      font-size: 14px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      pointer-events: auto;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
    `;
    
    toast.innerHTML = `
      <span style="font-size: 16px;">${icons[type] || icons.info}</span>
      <span>${message}</span>
    `;
    
    this.container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto remove
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, duration);
    
    // Click to dismiss
    toast.addEventListener('click', () => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    });
    
    return toast;
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }

  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }
}

// Create global instance
const toast = new ToastManager();
