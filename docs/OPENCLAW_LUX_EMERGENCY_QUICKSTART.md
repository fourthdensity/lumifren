# OpenClaw Lumifren Emergency Quickstart (15-30 Minute Restore)

Last updated: 2026-02-27 (UTC)  
Primary target: Ubuntu 24.04 + systemd + Docker  
Use this for rapid recovery only. Full guide: `docs/OPENCLAW_LUX_DR_RUNBOOK.md`
First-time tutorial: `docs/OPENCLAW_LUX_STYLE_FIRST_TIME_SETUP_TUTORIAL.md`

## 0) Inputs You Need Before Starting

- Recovery bundle file:
  - `recovery_bundle_YYYYmmdd_HHMMSS.tar.gz`
- A sudo-capable shell on target host.
- Internet access (unless all dependencies/images are bundled).

## 1) Fast Preflight (Target Host)

```bash
sudo apt update
sudo apt install -y docker.io docker-buildx curl git jq ca-certificates
sudo systemctl enable --now docker

id brewuser >/dev/null 2>&1 || sudo useradd -m -s /bin/bash brewuser
sudo usermod -aG docker brewuser
sudo loginctl enable-linger brewuser
```

## 2) Install Node 22 + OpenClaw CLI

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] || curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
. "$NVM_DIR/nvm.sh"
nvm install 22
nvm alias default 22
nvm use 22
npm install -g openclaw@2026.2.24 clawhub mcporter
node -v
openclaw --version
'
```

## 3) Unpack Recovery Bundle

Update bundle path before running:

```bash
set -euo pipefail
BUNDLE="/tmp/recovery_bundle_YYYYmmdd_HHMMSS.tar.gz"

sudo -iu brewuser bash -lc 'mkdir -p "$HOME/recovery_import"'
sudo tar -C /home/brewuser/recovery_import -xzf "$BUNDLE"

sudo -iu brewuser bash -lc 'find "$HOME/recovery_import" -maxdepth 2 -type d -name "recovery_bundle_*"'
```

Set restore dir:

```bash
RESTORE_DIR="/home/brewuser/recovery_import/recovery_bundle_YYYYmmdd_HHMMSS"
```

## 4) Restore OpenClaw State + Homebrew Payload

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"

rm -rf "$HOME/.openclaw"
cp -a "$RESTORE_DIR/openclaw_home" "$HOME/.openclaw"

rm -rf "$HOME/.linuxbrew"
cp -a "$RESTORE_DIR/linuxbrew_payload" "$HOME/.linuxbrew"
'

sudo mkdir -p /home/linuxbrew
sudo rm -rf /home/linuxbrew/.linuxbrew
sudo ln -s /home/brewuser/.linuxbrew /home/linuxbrew/.linuxbrew
sudo chown -h root:root /home/linuxbrew/.linuxbrew
sudo chown -R brewuser:brewuser /home/brewuser/.linuxbrew
```

## 5) Restore Units + Healthcheck Script

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"

mkdir -p "$HOME/.config/systemd/user" "$HOME/.local/bin"
cp -a "$RESTORE_DIR/systemd_user/openclaw-gateway.service" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/systemd_user/openclaw-gateway.service.d" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/systemd_user/openclaw-healthcheck.service" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/systemd_user/openclaw-healthcheck.timer" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/local_bin/openclaw-healthcheck" "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/openclaw-healthcheck"

cp -a "$RESTORE_DIR/.bashrc" "$HOME/.bashrc"
cp -a "$RESTORE_DIR/.profile" "$HOME/.profile"
'
```

## 6) Restore Sandbox Image (Preferred: Offline Load)

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"
if [ -f "$RESTORE_DIR/openclaw-sandbox-bookworm-slim.tar.gz" ]; then
  gunzip -c "$RESTORE_DIR/openclaw-sandbox-bookworm-slim.tar.gz" | docker load
fi
docker image inspect openclaw-sandbox:bookworm-slim --format "{{.Id}} {{.Created}}"
'
```

If missing, rebuild online:

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
mkdir -p "$HOME/.openclaw/sandbox-image-build"
cd "$HOME/.openclaw/sandbox-image-build"
curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw/main/Dockerfile.sandbox -o Dockerfile.sandbox
docker build -t openclaw-sandbox:bookworm-slim -f Dockerfile.sandbox .
'
```

## 7) Start Services

```bash
sudo systemctl restart user@1000.service
sleep 2

sudo -iu brewuser bash -lc '
set -euo pipefail
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus

systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway.service
systemctl --user enable --now openclaw-healthcheck.timer
'
```

## 8) 60-Second Validation

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus

id
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
systemctl --user status openclaw-gateway.service --no-pager | sed -n "1,25p"
/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw doctor
/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw logs --limit 30 --timeout 10000 --plain
systemctl --user start openclaw-healthcheck.service
tail -n 20 /home/brewuser/.openclaw/logs/healthcheck.log
'
```

Success indicators:
- `openclaw-gateway.service` is `active (running)`.
- `openclaw doctor` has no sandbox-image-missing error.
- `healthcheck.log` ends with `PASS`.

## 9) Common Fast Fixes

### Docker permission denied

```bash
sudo usermod -aG docker brewuser
sudo systemctl restart user@1000.service
sudo -iu brewuser bash -lc 'id; docker ps'
```

### Gateway not reachable

```bash
sudo -iu brewuser bash -lc '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus
systemctl --user restart openclaw-gateway.service
/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw logs --limit 50 --plain
'
```

### OpenClaw not found

Use full path:

```bash
/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw --version
```

## 10) Immediate Post-Cutover

1. Confirm Telegram/Discord message flow.
2. Monitor:
   - `/home/brewuser/.openclaw/logs/healthcheck.log`
   - `/home/brewuser/.openclaw/logs/commands.log`
3. Keep source host online but passive for 30-60 minutes.
4. After stable cutover, disable source gateway services.
