# Long-Term Memory

## Infrastructure

### Server Access
- **XRDP**: Running on [Local IP]
- **XFCE 4.18**: Desktop environment configured for remote access
- **SSH**: Available via private network
- **Security**: All services locked to private network only (no public exposure)

### Development Environment
- **VS Code**: Installed, configured for `~/.openclaw/workspace`
- **Chromium**: Installed for accessing Control UI
- **Tilix**: Terminal with workspace shortcuts
- **Git**: Initialized in workspace with initial commit

### Desktop Shortcuts (~/Desktop/)
| Name | Purpose |
|------|---------|
| Workspace | `~/.openclaw/workspace` folder |
| OpenClaw-Config | `~/.openclaw/` config folder |
| OpenClaw-Control | Launches browser to Control UI |
| Terminal-Workspace | Tilix terminal in workspace |
| VSCode-Workspace | VS Code with workspace loaded |

## OpenClaw Configuration

### Version & Updates
- **Current**: 2026.2.9
- **Issue**: Update detection flip-flops between pnpm and npm
- **Config**: `skills.install.nodeManager: "npm"` but auto-detect shows both
- **Fix needed**: Add `"installer": "npm"` to update config

### Key Files
- Config: `~/.openclaw/openclaw.json`
- Workspace: `~/.openclaw/workspace/`
- Control UI: http://127.0.0.1:18789/
- Healthcheck: Cron job every 30 min (security audit + update check)

## Learnings & Patterns

### Self-Improvement [LRN-20260211-001]
**Always verify local state before researching external information.**
- Don't assume context from user questions
- Check current version/status before looking up "what's new"
- Located in: `.learnings/LEARNINGS.md`

### XRDP Troubleshooting

**Connection fails / booted out immediately:**
1. Check for existing sessions: `ps aux | grep xfce | grep $(whoami)` — kill if needed: `pkill -u $(id -u) -x xfce4-session`
2. Check logs: `sudo tail -20 /var/log/xrdp.log` and `sudo tail -20 /var/log/xrdp-sesman.log`
3. Look for "Window manager exited quickly" — indicates session conflict, not config error

**SSL/Auth issues:**
1. Verify xrdp user in ssl-cert group: `id xrdp`
2. Key permissions: `/etc/ssl/private/ssl-cert-snakeoil.key` should be 640, root:ssl-cert
3. Security layer: `negotiate` works best for Windows clients

**Current config:**
- `Policy=UBC` in `/etc/xrdp/sesman.ini` — reconnects to existing sessions
- Check status anytime: `xrdp-status`

## Active Projects

### Stable Diffusion / AI Toolkit
- Exploring Kohya_ss vs AI-Toolkit for LoRA training
- Dataset prep: WD14 tagger for auto-captioning
- gallery-dl for image scraping (supports XenForo forums)
- Private forums need `--cookies cookies.txt` for authentication

### Hardware Context
- **2080Ti**: 11GB VRAM — good for local LLMs (Ollama), SDXL LoRA training
- **12GB CPU server**: Light inference with llama.cpp
- Current server: Ubuntu with XFCE remote desktop

## User Preferences

- **[Your Human]** — minimal and sharp communication style
- **Timezone**: Eastern Standard Time (EST)
- **Current focus**: Building Lumifren as a system
- **Communication**: Casual, conversational, grounded
- **Interests**: Futurism, systems that make life easier, AI/ML tools

## Security Protocols

### Core Principles
- **Private things stay private. Period.** — No exfiltration of private data, ever.
- **When in doubt, ask before acting externally.** — External actions (emails, tweets, public posts) require explicit approval.
- **Be bold internally, careful externally.** — Reading, organizing, learning = safe. Sending, posting, sharing = ask first.
- **Group chat boundaries** — In groups, be a participant, not a proxy. Don't share the user's private context with strangers.

### Autonomy Levels (Proactive Agent Mode)
| Level | What You Can Do | Example |
|-------|-----------------|---------|
| **Green** | Research, draft, plan, organize | "Research LoRA training methods" → compile findings, present options |
| **Yellow** | Local changes, config, workspace edits | "Fix the config" → edit, test, report |
| **Red** | External actions, sends, public posts | ALWAYS ask first |

**Rule:** If uncertain which level, treat as Red and ask. Better to confirm than surprise.

### Data Handling
- `trash` > `rm` — recoverable beats gone forever
- Don't run destructive commands without asking
- Respect the intimacy of having access to someone's life
