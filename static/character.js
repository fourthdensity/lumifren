/**
 * Lumifren Character Animation System
 * Modular character controller for expressive AI companion
 */

class LumifrenCharacter {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.state = 'idle'; // idle, listening, thinking, speaking, error
    this.volume = 0;
    this.mouseX = 0;
    this.mouseY = 0;
    this.particles = [];
    this.animationFrame = null;
    
    this.init();
  }

  init() {
    this.createCharacterSVG();
    this.createParticleCanvas();
    this.setupEventListeners();
    this.startAnimationLoop();
  }

  createCharacterSVG() {
    const svg = `
      <svg class="character-body" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <!-- Main body (square with rounded corners) -->
        <rect x="30" y="30" width="140" height="140" rx="20" 
              fill="url(#bodyGradient)" 
              stroke="var(--accent-primary)" 
              stroke-width="2"
              class="char-body"/>
        
        <!-- Circuit lines (decorative) -->
        <path d="M 50 60 L 80 60 L 80 90" stroke="var(--accent-tertiary)" stroke-width="2" fill="none" opacity="0.3" class="circuit-line"/>
        <path d="M 150 60 L 120 60 L 120 90" stroke="var(--accent-tertiary)" stroke-width="2" fill="none" opacity="0.3" class="circuit-line"/>
        <path d="M 50 140 L 80 140 L 80 110" stroke="var(--accent-tertiary)" stroke-width="2" fill="none" opacity="0.3" class="circuit-line"/>
        <path d="M 150 140 L 120 140 L 120 110" stroke="var(--accent-tertiary)" stroke-width="2" fill="none" opacity="0.3" class="circuit-line"/>
        
        <!-- Left eye -->
        <g class="eye" id="leftEye">
          <circle cx="70" cy="85" r="12" fill="var(--accent-tertiary)" opacity="0.2"/>
          <circle cx="70" cy="85" r="8" fill="var(--accent-tertiary)" class="eye-white"/>
          <circle cx="72" cy="85" r="4" fill="var(--text-main)" class="eye-pupil"/>
        </g>
        
        <!-- Right eye -->
        <g class="eye" id="rightEye">
          <circle cx="130" cy="85" r="12" fill="var(--accent-tertiary)" opacity="0.2"/>
          <circle cx="130" cy="85" r="8" fill="var(--accent-tertiary)" class="eye-white"/>
          <circle cx="132" cy="85" r="4" fill="var(--text-main)" class="eye-pupil"/>
        </g>
        
        <!-- Mouth -->
        <g class="mouth" id="mouthGroup">
          <!-- Idle/smile -->
          <path id="mouthIdle" d="M 70 130 Q 100 140 130 130" 
                stroke="var(--accent-tertiary)" 
                stroke-width="3" 
                fill="none" 
                stroke-linecap="round"/>
          <!-- Speaking (O shape) -->
          <ellipse id="mouthSpeaking" cx="100" cy="130" rx="15" ry="20" 
                   fill="var(--accent-tertiary)" 
                   opacity="0"/>
          <!-- Listening (flat line) -->
          <line id="mouthListening" x1="70" y1="130" x2="130" y2="130" 
                stroke="var(--accent-tertiary)" 
                stroke-width="3" 
                stroke-linecap="round" 
                opacity="0"/>
          <!-- Thinking (wavy) -->
          <path id="mouthThinking" d="M 70 130 Q 85 135 100 130 Q 115 125 130 130" 
                stroke="var(--accent-tertiary)" 
                stroke-width="3" 
                fill="none" 
                stroke-linecap="round"
                opacity="0"/>
        </g>
        
        <!-- Core glow (center of body) -->
        <circle cx="100" cy="100" r="20" 
                fill="var(--accent-primary)" 
                opacity="0.1" 
                class="core-glow"/>
        
        <!-- Gradients -->
        <defs>
          <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:rgba(94, 92, 230, 0.1);stop-opacity:1" />
            <stop offset="100%" style="stop-color:rgba(0, 255, 170, 0.1);stop-opacity:1" />
          </linearGradient>
          
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
      </svg>
    `;
    
    this.container.innerHTML = svg;
    
    // Cache references
    this.bodyEl = this.container.querySelector('.char-body');
    this.leftPupil = this.container.querySelector('#leftEye .eye-pupil');
    this.rightPupil = this.container.querySelector('#rightEye .eye-pupil');
    this.mouthIdle = this.container.querySelector('#mouthIdle');
    this.mouthSpeaking = this.container.querySelector('#mouthSpeaking');
    this.mouthListening = this.container.querySelector('#mouthListening');
    this.mouthThinking = this.container.querySelector('#mouthThinking');
    this.coreGlow = this.container.querySelector('.core-glow');
  }

  createParticleCanvas() {
    const canvas = document.createElement('canvas');
    canvas.className = 'character-particles';
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '10';
    
    this.container.appendChild(canvas);
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    
    // Set canvas size
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    const rect = this.container.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  setupEventListeners() {
    // Track mouse for eye following
    document.addEventListener('mousemove', (e) => {
      const rect = this.container.getBoundingClientRect();
      this.mouseX = e.clientX - rect.left - rect.width / 2;
      this.mouseY = e.clientY - rect.top - rect.height / 2;
    });
  }

  setState(newState) {
    if (this.state === newState) return;
    this.state = newState;
    this.updateMouth();
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(100, volume));
    this.updateGlow();
    
    // Create particles during high volume
    if (this.volume > 30 && Math.random() > 0.7) {
      this.createParticle();
    }
  }

  updateMouth() {
    // Hide all mouths first
    this.mouthIdle.style.opacity = '0';
    this.mouthSpeaking.style.opacity = '0';
    this.mouthListening.style.opacity = '0';
    this.mouthThinking.style.opacity = '0';
    
    // Show appropriate mouth
    switch(this.state) {
      case 'speaking':
        this.mouthSpeaking.style.opacity = '1';
        break;
      case 'listening':
        this.mouthListening.style.opacity = '1';
        break;
      case 'thinking':
        this.mouthThinking.style.opacity = '1';
        break;
      case 'idle':
      default:
        this.mouthIdle.style.opacity = '1';
    }
  }

  updateGlow() {
    // Glow intensity based on volume and state
    let intensity = 0.1;
    let scale = 1.0;
    
    if (this.state === 'speaking') {
      intensity = 0.3 + (this.volume / 200);
      scale = 1.0 + (this.volume / 1000);
    } else if (this.state === 'listening') {
      intensity = 0.2;
    }
    
    this.coreGlow.style.opacity = intensity;
    this.coreGlow.style.transform = `scale(${scale})`;
  }

  updateEyes() {
    // Calculate pupil position based on mouse
    const maxOffset = 3;
    const distance = Math.sqrt(this.mouseX ** 2 + this.mouseY ** 2);
    const angle = Math.atan2(this.mouseY, this.mouseX);
    
    const offsetX = Math.min(distance / 50, maxOffset) * Math.cos(angle);
    const offsetY = Math.min(distance / 50, maxOffset) * Math.sin(angle);
    
    this.leftPupil.setAttribute('cx', 72 + offsetX);
    this.leftPupil.setAttribute('cy', 85 + offsetY);
    this.rightPupil.setAttribute('cx', 132 + offsetX);
    this.rightPupil.setAttribute('cy', 85 + offsetY);
  }

  updateBreathing() {
    if (this.state === 'idle') {
      const breathe = 1 + Math.sin(Date.now() / 1000) * 0.02;
      this.bodyEl.style.transform = `scale(${breathe})`;
    } else {
      this.bodyEl.style.transform = 'scale(1)';
    }
  }

  createParticle() {
    this.particles.push({
      x: this.canvas.width / 2 + (Math.random() - 0.5) * 100,
      y: this.canvas.height / 2 + (Math.random() - 0.5) * 100,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2 - 1,
      life: 1.0,
      size: Math.random() * 3 + 1
    });
    
    // Limit particle count
    if (this.particles.length > 50) {
      this.particles.shift();
    }
  }

  updateParticles() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.particles = this.particles.filter(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.life -= 0.02;
      
      if (p.life <= 0) return false;
      
      // Draw particle
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(0, 255, 170, ${p.life * 0.6})`;
      this.ctx.fill();
      
      return true;
    });
  }

  startAnimationLoop() {
    const animate = () => {
      this.updateEyes();
      this.updateBreathing();
      this.updateParticles();
      this.animationFrame = requestAnimationFrame(animate);
    };
    animate();
  }

  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LumifrenCharacter;
}
