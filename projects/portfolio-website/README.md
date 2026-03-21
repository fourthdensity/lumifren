# LUX Portfolio Website

A futuristic, cyberpunk-inspired portfolio showcasing AI systems architecture, creative development, and technical capabilities.

## 🎨 Design Philosophy

**"Neon Noir Cyberpunk"** - Dark, masculine aesthetics with electric neon accents creating a future-forward impression.

### Color Palette
- **Background**: Deep black (#050508)
- **Primary**: Electric cyan (#00f5ff)
- **Secondary**: Hot magenta (#ff006e)
- **Accent**: Electric blue (#0066ff)
- **Text**: White with subtle gray hierarchy

## ✨ Features

### Visual Effects
- **Particle Network Background**: Animated particles with connection lines
- **Custom Cursor**: Glowing cyan ring (desktop only)
- **Gradient Animations**: Shifting text gradients
- **Neon Glows**: Box shadows and text shadows throughout
- **Scroll Animations**: Reveal animations as you scroll

### Sections
1. **Hero**: Eye-catching intro with animated stats
2. **Projects**: 6 project cards with hover effects
3. **Skills**: 12 technical skills with animated progress bars
4. **Timeline**: Development journey with 6 milestones
5. **Contact**: Call-to-action section
6. **Footer**: Branded sign-off

## 📱 Mobile Optimization

### Mobile-First Enhancements
- ✅ **Hamburger Menu**: Touch-friendly mobile navigation overlay
- ✅ **Reduced Particle Count**: 20 particles on mobile vs 50 on desktop
- ✅ **Touch Targets**: Minimum 44px for all interactive elements
- ✅ **Optimized Layout**: Single column grids on mobile
- ✅ **Performance**: Connection lines disabled on mobile
- ✅ **Custom Cursor**: Hidden on touch devices
- ✅ **Responsive Typography**: Fluid font scaling
- ✅ **Safe Areas**: Proper padding for notched devices

### Breakpoints
- **Desktop**: 769px+
- **Tablet/Mobile**: 768px and below
- **Small Mobile**: 480px and below

## 🚀 Usage

### Local Development
```bash
cd ~/.openclaw/workspace/projects/portfolio-website
python3 -m http.server 8000
# Visit: http://localhost:8000
```

### File Structure
```
portfolio-website/
├── index.html          # Main portfolio file
└── README.md           # This file
```

## 🎯 Projects Showcased

1. **Warpcast Game** - Social gaming platform with blockchain
2. **CSM Voice Pipeline** - Complete voice AI system
3. **Algorithmic Art Engine** - Generative art with p5.js
4. **AI Agent Framework** - Proactive agent system
5. **FL Studio MIDI Bridge** - Music production AI
6. **Nano Banana Image Gen** - Image generation integration

## 🛠️ Technical Stack

- **Pure HTML5/CSS3/JavaScript** - No frameworks
- **Google Fonts**: Orbitron, Rajdhani, Inter
- **CSS Animations**: Keyframes and transitions
- **Canvas API**: Particle system
- **Intersection Observer**: Scroll animations

## 📊 Performance

- **No external dependencies** (except fonts)
- **Optimized particle system** for mobile
- **CSS-only animations** where possible
- **Lazy loading ready** structure

## 🔧 Customization

### Adding Projects
Edit the `.project-card` sections in `index.html`:
```html
<div class="project-card reveal">
    <div class="project-content">
        <div class="project-icon">🎮</div>
        <h3 class="project-title">Your Project</h3>
        <p class="project-description">Description here...</p>
        <div class="project-tags">
            <span class="project-tag">Tag1</span>
            <span class="project-tag">Tag2</span>
        </div>
    </div>
</div>
```

### Changing Colors
Update CSS variables in the `:root` selector:
```css
:root {
    --neon-cyan: #00f5ff;
    --neon-magenta: #ff006e;
    --neon-blue: #0066ff;
}
```

## 📱 Tested On

- iPhone 12/13/14 (iOS Safari)
- Samsung Galaxy S21 (Chrome)
- iPad Pro (iOS Safari)
- Desktop Chrome, Firefox, Safari, Edge

## 🎓 For Schools/Employers/Clients

This portfolio demonstrates:
- **Frontend Development**: Custom animations, responsive design
- **AI Integration**: Voice, vision, generative systems
- **System Architecture**: Backend design, API development
- **Creative Coding**: Generative art, interactive experiences
- **Project Management**: Multiple concurrent projects

## 📞 Contact

To update contact information, edit the Contact section in `index.html`:
```html
<a href="mailto:your@email.com" class="btn btn-primary">Start a Project</a>
```

---

**Crafted by LUX** // AI Systems Architect
