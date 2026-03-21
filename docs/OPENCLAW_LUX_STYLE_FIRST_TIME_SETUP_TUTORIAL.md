# OpenClaw Lumifren-Style First-Time Setup Tutorial

Document version: 1.0  
Last updated: 2026-02-27 (UTC)  
Target: Operators building a new OpenClaw system from zero (non-Lux deployment)

## 1) What You Are Building

This tutorial builds a production-style OpenClaw setup with the same architecture pattern as Lux:
- Dedicated Linux user (`brewuser`) running OpenClaw
- Node 22 via NVM
- OpenClaw CLI installed globally under that user
- Gateway running as `systemd --user` service
- Docker sandbox mode enabled (`agents.defaults.sandbox.mode=all`)
- Local sandbox image tag: `openclaw-sandbox:bookworm-slim`
- Periodic health checks via `systemd` timer

This guide is optimized for Ubuntu 24.04 LTS.

## 2) Prerequisites

### 2.1 Minimum host requirements
- CPU: 4+ cores (8 preferred)
- RAM: 16 GB minimum (32 GB preferred)
- Disk: 80+ GB free (more if storing models/media)
- OS: Ubuntu 24.04 LTS with systemd
- Network: outbound HTTPS (443) to provider APIs, package repos, Discord/Telegram

### 2.2 Required access
- A sudo-capable account on the server
- Ability to open SSH sessions
- API tokens/keys you plan to use (Telegram, Discord, model providers)

## 3) Phase A: Base Host Setup

Run as your sudo-capable user.

```bash
sudo apt update
sudo apt install -y \
  curl git jq ca-certificates build-essential \
  docker.io docker-buildx unzip zip

sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

### Likely output
- Docker should show `active (running)`.

### If Docker is not active
```bash
sudo journalctl -u docker -n 100 --no-pager
sudo systemctl restart docker
```

## 4) Phase B: Create Runtime User and Session Model

```bash
id brewuser >/dev/null 2>&1 || sudo useradd -m -s /bin/bash brewuser
sudo usermod -aG docker brewuser
sudo loginctl enable-linger brewuser

getent passwd brewuser
sudo loginctl show-user brewuser -p Linger -p State -p RuntimePath
```

### Why this matters
- `docker` group allows non-root Docker access.
- `linger=yes` allows user services to run after reboot/login transitions.

## 5) Phase C: Install Node 22 + OpenClaw CLI

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail

export NVM_DIR="$HOME/.nvm"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi

. "$NVM_DIR/nvm.sh"
nvm install 22
nvm use 22
nvm alias default 22

npm install -g openclaw@2026.2.24 clawhub mcporter

node -v
npm -v
openclaw --version
'
```

### Expected
- Node prints `v22.x`
- OpenClaw prints `2026.2.24` (or newer if you intentionally changed version)

### If `openclaw` not found
```bash
sudo -iu brewuser bash -lc 'echo $PATH; npm root -g; ls -la ~/.nvm/versions/node/*/bin/openclaw'
```

Use absolute path in scripts/services if needed.

## 6) Phase D: Install Homebrew + Core Tooling

This tutorial uses lumifren-style compatibility:
- Payload at `/home/brewuser/.linuxbrew`
- Compatibility symlink `/home/linuxbrew/.linuxbrew -> /home/brewuser/.linuxbrew`

### 6.1 Install Homebrew (official script)

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
'
```

### 6.2 Move to lumifren-style payload path and create compat symlink

```bash
sudo bash -lc '
set -euo pipefail

if [ -d /home/linuxbrew/.linuxbrew ] && [ ! -e /home/brewuser/.linuxbrew ]; then
  mv /home/linuxbrew/.linuxbrew /home/brewuser/.linuxbrew
fi

mkdir -p /home/linuxbrew
rm -rf /home/linuxbrew/.linuxbrew
ln -s /home/brewuser/.linuxbrew /home/linuxbrew/.linuxbrew

chown -R brewuser:brewuser /home/brewuser/.linuxbrew
chown -h root:root /home/linuxbrew/.linuxbrew
'
```

### 6.3 Add shell bootstrap for brew + nvm

```bash
sudo -iu brewuser bash -lc 'cat >> ~/.bashrc <<"BASHRC_BLOCK"

# lumifren-style Homebrew bootstrap
if [ -x "$HOME/.linuxbrew/bin/brew" ]; then
    eval "$("$HOME/.linuxbrew/bin/brew" shellenv bash)"
elif [ -x "/home/linuxbrew/.linuxbrew/bin/brew" ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"
fi

# NVM bootstrap
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"
BASHRC_BLOCK'
```

### 6.4 Install common packages used in lumifren-style workflows

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
source ~/.bashrc
brew update
brew install ffmpeg openai-whisper uv gcc ripgrep
brew list --formula | grep -E "ffmpeg|openai-whisper|uv|gcc|ripgrep"
'
```

## 7) Phase E: Initialize OpenClaw Configuration

### 7.1 Run initial configure flow

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
openclaw configure
'
```

### 7.2 Apply baseline lumifren-style operational config

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail

openclaw config set agents.defaults.workspace /home/brewuser/.openclaw/workspace
openclaw config set agents.defaults.sandbox.mode all
openclaw config set tools.fs.workspaceOnly true
openclaw config set gateway.mode local
openclaw config set gateway.bind loopback
openclaw config set gateway.port 18789

TOKEN="$(openssl rand -hex 24)"
openclaw config set gateway.auth.mode token
openclaw config set gateway.auth.token "$TOKEN"

echo "Generated gateway token (store securely): $TOKEN"
'
```

### 7.3 Optional channels

Enable only what you need.

Telegram example:
```bash
sudo -iu brewuser bash -lc '
openclaw config set channels.telegram.enabled true
openclaw config set channels.telegram.botToken "<YOUR_TELEGRAM_BOT_TOKEN>"
'
```

Discord example:
```bash
sudo -iu brewuser bash -lc '
openclaw config set channels.discord.enabled true
openclaw config set channels.discord.token "<YOUR_DISCORD_BOT_TOKEN>"
'
```

## 8) Phase F: Create Gateway Service (systemd --user)

Generate a service file dynamically based on installed Node/OpenClaw paths:

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail

NODE_BIN="$(command -v node)"
OPENCLAW_DIST="$(npm root -g)/openclaw/dist/index.js"
GATEWAY_TOKEN="$(jq -r ".gateway.auth.token" ~/.openclaw/openclaw.json)"

mkdir -p ~/.config/systemd/user ~/.config/systemd/user/openclaw-gateway.service.d

cat > ~/.config/systemd/user/openclaw-gateway.service <<UNIT_BLOCK
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=${NODE_BIN} ${OPENCLAW_DIST} gateway --port 18789
Restart=always
RestartSec=5
KillMode=process
Environment=HOME=/home/brewuser
Environment=TMPDIR=/tmp
Environment=PATH=/home/brewuser/.nvm/current/bin:/home/brewuser/.local/bin:/home/brewuser/.linuxbrew/bin:/home/brewuser/.linuxbrew/sbin:/usr/local/bin:/usr/bin:/bin
Environment=OPENCLAW_GATEWAY_PORT=18789
Environment=OPENCLAW_GATEWAY_TOKEN=${GATEWAY_TOKEN}
Environment=OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service
Environment=OPENCLAW_SERVICE_MARKER=openclaw
Environment=OPENCLAW_SERVICE_KIND=gateway

[Install]
WantedBy=default.target
UNIT_BLOCK
'
```

If you use an API key as environment variable (example NVIDIA), create drop-in:

```bash
sudo -iu brewuser bash -lc '
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d
cat > ~/.config/systemd/user/openclaw-gateway.service.d/override.conf <<OVERRIDE_BLOCK
[Service]
Environment=NVIDIA_API_KEY=<YOUR_NVIDIA_API_KEY>
OVERRIDE_BLOCK
'
```

## 9) Phase G: Build Sandbox Image

OpenClaw expects tag `openclaw-sandbox:bookworm-slim` for default sandboxing.

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
mkdir -p ~/.openclaw/sandbox-image-build
cd ~/.openclaw/sandbox-image-build

curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw/main/Dockerfile.sandbox -o Dockerfile.sandbox

docker build -t openclaw-sandbox:bookworm-slim -f Dockerfile.sandbox .
docker image inspect openclaw-sandbox:bookworm-slim --format "ID={{.Id}} Created={{.Created}}"
'
```

## 10) Phase H: Enable and Start Services

```bash
sudo systemctl restart user@1000.service
sleep 2

sudo -iu brewuser bash -lc '
set -euo pipefail
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus

systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway.service

systemctl --user status openclaw-gateway.service --no-pager | sed -n "1,60p"
'
```

## 11) Phase I: Add Lumifren-Style Healthcheck Automation

### 11.1 Install healthcheck script

```bash
sudo -iu brewuser bash -lc '
cat > ~/.local/bin/openclaw-healthcheck <<HEALTH_BLOCK
#!/usr/bin/env bash
set -u

LOG_FILE="${HEALTHCHECK_LOG_FILE:-/home/brewuser/.openclaw/logs/healthcheck.log}"
OPENCLAW_BIN="${OPENCLAW_BIN:-/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw}"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  printf "%s %s\\n" "$(date -Is)" "$1" | tee -a "$LOG_FILE"
}

FAIL=0

docker info >/dev/null 2>&1 || { log "FAIL docker unreachable"; FAIL=1; }
systemctl --user is-active --quiet openclaw-gateway.service || { log "FAIL gateway inactive"; FAIL=1; }
"$OPENCLAW_BIN" logs --limit 1 --timeout 6000 --plain >/dev/null 2>&1 || { log "FAIL openclaw logs unreachable"; FAIL=1; }
docker image inspect openclaw-sandbox:bookworm-slim >/dev/null 2>&1 || log "WARN sandbox image missing"

if [ "$FAIL" -eq 0 ]; then
  log "PASS healthcheck"
  exit 0
fi

log "FAIL healthcheck"
exit 1
HEALTH_BLOCK

chmod +x ~/.local/bin/openclaw-healthcheck
'
```

### 11.2 Create service and timer

```bash
sudo -iu brewuser bash -lc '
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/openclaw-healthcheck.service <<HEALTH_SERVICE
[Unit]
Description=OpenClaw periodic health check
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/home/brewuser/.local/bin/openclaw-healthcheck
Environment=HOME=/home/brewuser
Environment=PATH=/home/brewuser/.nvm/current/bin:/home/brewuser/.local/bin:/home/brewuser/.linuxbrew/bin:/home/brewuser/.linuxbrew/sbin:/usr/local/bin:/usr/bin:/bin
HEALTH_SERVICE

cat > ~/.config/systemd/user/openclaw-healthcheck.timer <<HEALTH_TIMER
[Unit]
Description=Run OpenClaw health check every 15 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=15min
AccuracySec=30s
Unit=openclaw-healthcheck.service
Persistent=true

[Install]
WantedBy=timers.target
HEALTH_TIMER
'
```

### 11.3 Enable timer

```bash
sudo -iu brewuser bash -lc '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus

systemctl --user daemon-reload
systemctl --user enable --now openclaw-healthcheck.timer
systemctl --user start openclaw-healthcheck.service
systemctl --user list-timers --all --no-pager | grep openclaw-healthcheck
'
```

## 12) Phase J: Validation Checklist

Run all checks:

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus

echo "== versions =="
node -v
npm -v
openclaw --version

echo "== core commands =="
command -v brew node npm openclaw docker

echo "== services =="
systemctl --user status openclaw-gateway.service --no-pager | sed -n "1,30p"
systemctl --user status openclaw-healthcheck.timer --no-pager | sed -n "1,30p"

echo "== openclaw doctor =="
openclaw doctor

echo "== openclaw logs =="
openclaw logs --limit 50 --timeout 10000 --plain

echo "== sandbox =="
openclaw sandbox list

echo "== healthcheck log =="
tail -n 20 /home/brewuser/.openclaw/logs/healthcheck.log
'
```

Success means:
- Gateway service running
- Doctor has no Docker permission issues
- Sandbox image found
- Healthcheck ends with PASS

## 13) Common Errors and Exact Fixes

### 13.1 Docker socket permission denied

Symptom:
- `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`

Fix:
```bash
sudo usermod -aG docker brewuser
sudo systemctl restart user@1000.service
sudo -iu brewuser bash -lc 'id; docker ps'
```

### 13.2 `systemctl --user` fails (`Failed to connect to bus`)

Fix:
```bash
sudo systemctl restart user@1000.service
sudo -iu brewuser bash -lc '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus
systemctl --user status openclaw-gateway.service --no-pager
'
```

### 13.3 OpenClaw logs says gateway not reachable

Fix:
```bash
sudo -iu brewuser bash -lc '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus
systemctl --user restart openclaw-gateway.service
openclaw logs --limit 50 --timeout 10000 --plain
'
```

### 13.4 Sandbox image missing

Fix:
```bash
sudo -iu brewuser bash -lc '
docker image inspect openclaw-sandbox:bookworm-slim || true
cd ~/.openclaw/sandbox-image-build
[ -f Dockerfile.sandbox ] || curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw/main/Dockerfile.sandbox -o Dockerfile.sandbox
docker build -t openclaw-sandbox:bookworm-slim -f Dockerfile.sandbox .
'
```

### 13.5 `openclaw` command not found

Fix:
```bash
sudo -iu brewuser bash -lc '
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
command -v openclaw || npm install -g openclaw@2026.2.24
/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw --version
'
```

## 14) Daily Operations Cheat Sheet

```bash
# Gateway status
sudo -iu brewuser bash -lc 'export XDG_RUNTIME_DIR=/run/user/$(id -u); export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus; systemctl --user status openclaw-gateway.service --no-pager'

# Tail logs
sudo -iu brewuser bash -lc '/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw logs --follow --plain'

# Run doctor
sudo -iu brewuser bash -lc '/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw doctor'

# Run immediate healthcheck
sudo -iu brewuser bash -lc 'export XDG_RUNTIME_DIR=/run/user/$(id -u); export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus; systemctl --user start openclaw-healthcheck.service'

# Healthcheck history
tail -f /home/brewuser/.openclaw/logs/healthcheck.log
```

## 15) Backup Basics

Quick periodic backup command (no custom script required):

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
TS="$(date +%Y%m%d_%H%M%S)"
OUT="$HOME/.openclaw/backups/openclaw-backup-${TS}.tar.gz"
tar -C "$HOME" -czf "$OUT" .openclaw
ls -lh "$OUT"
'
```

If you adopt Lux backup scripts, keep them in:
- `~/.openclaw/workspace/scripts/backup-manager.sh`
- `~/.openclaw/workspace/scripts/generate-backup-manifest.sh`

## 16) Security Checklist (Do This)

1. Do not keep long-lived API keys in shell history.
2. Restrict permissions:
   - `chmod 700 ~/.openclaw`
   - `chmod 600 ~/.openclaw/openclaw.json`
3. Keep gateway bound to loopback unless you intentionally expose it.
4. Rotate tokens periodically.
5. Keep off-host encrypted backups.

---

You now have a lumifren-style OpenClaw platform blueprint that can be replicated in any new environment (VPC or on-prem).
