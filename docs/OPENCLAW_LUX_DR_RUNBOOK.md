# OpenClaw Lux Disaster Recovery and Migration Runbook

Document version: 1.0  
Last updated: 2026-02-27 (UTC)  
Primary host this was captured from: `clawnexus`  
Audience: Operators restoring OpenClaw Lux on a new server (VPC or on-prem)

Emergency quickstart companion:
- `docs/OPENCLAW_LUX_EMERGENCY_QUICKSTART.md`
First-time build tutorial:
- `docs/OPENCLAW_LUX_STYLE_FIRST_TIME_SETUP_TUTORIAL.md`

## 1) Purpose and Scope

This runbook is a full technical guide to rebuild and recover your OpenClaw Lux environment on another Linux server without relying on AI assistance.

This guide covers:
- Exact current architecture snapshot
- Backup and export from source host
- Restore on target host
- Service bring-up
- Sandbox/Docker setup
- Validation and troubleshooting
- Cutover checklist for VPC -> on-prem

This guide is written for Ubuntu 24.04 LTS with systemd and Docker.

## 2) Current Production Snapshot (Reference)

### 2.1 OS and Runtime
- OS: Ubuntu 24.04.4 LTS
- Kernel: `6.8.0-101-generic`
- User account: `brewuser` (uid 1000)
- OpenClaw version: `2026.2.24`
- Node: `v22.22.0` via NVM
- npm: `10.9.4`
- Docker engine: system daemon (`dockerd`)

### 2.2 Key Service Topology
- Main gateway service: `openclaw-gateway.service` (user systemd service)
- Health check service: `openclaw-healthcheck.service` (oneshot)
- Health check timer: `openclaw-healthcheck.timer` (every 15 minutes)

Enabled user units:
- `openclaw-gateway.service` -> enabled
- `openclaw-healthcheck.timer` -> enabled

### 2.3 Critical Paths
- OpenClaw config root: `/home/brewuser/.openclaw`
- Main config: `/home/brewuser/.openclaw/openclaw.json`
- Workspace: `/home/brewuser/.openclaw/workspace`
- Backups: `/home/brewuser/.openclaw/backups`
- Logs: `/home/brewuser/.openclaw/logs`
- OpenClaw binary: `/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw`
- Gateway service file: `/home/brewuser/.config/systemd/user/openclaw-gateway.service`
- Gateway override drop-in: `/home/brewuser/.config/systemd/user/openclaw-gateway.service.d/override.conf`
- Healthcheck script: `/home/brewuser/.local/bin/openclaw-healthcheck`
- Healthcheck unit: `/home/brewuser/.config/systemd/user/openclaw-healthcheck.service`
- Healthcheck timer: `/home/brewuser/.config/systemd/user/openclaw-healthcheck.timer`

### 2.4 Homebrew Layout (Important)
Current stable state uses relocated payload plus compatibility symlink:
- Payload dir: `/home/brewuser/.linuxbrew`
- Compatibility path: `/home/linuxbrew/.linuxbrew -> /home/brewuser/.linuxbrew`

Do not remove compatibility path unless doing a full Homebrew prefix rebuild.

### 2.5 OpenClaw Runtime Settings (Non-secret)
- Gateway mode: `local`
- Bind: `loopback`
- Port: `18789`
- Sandbox mode: `all`
- FS policy: `workspaceOnly=true`
- Channels enabled: Telegram + Discord

### 2.6 Docker/Sandbox State
- Required image tag: `openclaw-sandbox:bookworm-slim`
- Current image exists locally
- Example running sandbox container name pattern: `openclaw-sbx-agent-main-*`

## 3) Secrets and Sensitive Material

Treat these as secrets and never commit to git/plain docs:
- `~/.openclaw/openclaw.json` (contains channel tokens, provider keys)
- `~/.config/systemd/user/openclaw-gateway.service` (contains gateway auth token)
- `~/.config/systemd/user/openclaw-gateway.service.d/override.conf` (contains NVIDIA API key)
- `~/.bashrc` if it includes `NVIDIA_API_KEY`
- Any `.env` files

Recommended secret handling:
1. Store values in a password manager / vault.
2. Restore secrets only on target host.
3. Rotate Discord/Telegram/API tokens after migration if needed.

## 4) Recovery Strategy Options

### Option A (Recommended): Lift-and-shift exact clone
Fastest, lowest risk, closest to current behavior.
- Copy `~/.openclaw`
- Copy `~/.linuxbrew`
- Recreate `/home/linuxbrew/.linuxbrew` symlink
- Re-enable systemd user services

### Option B: Clean rebuild
Higher effort/risk, useful if you want to reduce historical baggage.
- Reinstall Node/OpenClaw/Homebrew packages from manifest
- Restore only necessary state/config
- Rebuild sandbox image

## 5) Source Host: Create Recovery Bundle

Run on current host as `brewuser`.

```bash
set -euo pipefail

TS="$(date +%Y%m%d_%H%M%S)"
OUT="/home/brewuser/recovery_bundle_${TS}"
mkdir -p "$OUT"

# 1) Core OpenClaw state
cp -a /home/brewuser/.openclaw "$OUT/openclaw_home"

# 2) Homebrew payload
cp -a /home/brewuser/.linuxbrew "$OUT/linuxbrew_payload"

# 3) User systemd units
mkdir -p "$OUT/systemd_user"
cp -a /home/brewuser/.config/systemd/user/openclaw-gateway.service "$OUT/systemd_user/"
cp -a /home/brewuser/.config/systemd/user/openclaw-gateway.service.d "$OUT/systemd_user/"
cp -a /home/brewuser/.config/systemd/user/openclaw-healthcheck.service "$OUT/systemd_user/"
cp -a /home/brewuser/.config/systemd/user/openclaw-healthcheck.timer "$OUT/systemd_user/"

# 4) Helper scripts
mkdir -p "$OUT/local_bin"
cp -a /home/brewuser/.local/bin/openclaw-healthcheck "$OUT/local_bin/"

# 5) Shell bootstrap files
cp -a /home/brewuser/.bashrc "$OUT/"
cp -a /home/brewuser/.profile "$OUT/"

# 6) Package manifest snapshot
cp -a /home/brewuser/.openclaw/backups/migration_20260227_004254/Brewfile.pre-migration "$OUT/" || true

# 7) Sandbox image export (offline restore support)
sudo -iu brewuser bash -lc 'docker image inspect openclaw-sandbox:bookworm-slim >/dev/null'
sudo -iu brewuser bash -lc 'docker save openclaw-sandbox:bookworm-slim | gzip > "'"$OUT"'"/openclaw-sandbox-bookworm-slim.tar.gz'

# 8) Baseline diagnostics
{
  echo "== date =="; date -Is
  echo "== uname =="; uname -a
  echo "== openclaw =="; /home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw --version
  echo "== node =="; node -v
  echo "== npm =="; npm -v
  echo "== brew prefix =="; brew --prefix
  echo "== docker groups =="; id
  echo "== openclaw units =="; systemctl --user list-unit-files --type=service --type=timer | grep openclaw
} > "$OUT/baseline.txt"

# 9) Archive everything
tar -C "$(dirname "$OUT")" -czf "${OUT}.tar.gz" "$(basename "$OUT")"

echo "Recovery bundle created: ${OUT}.tar.gz"
ls -lh "${OUT}.tar.gz"
```

Transfer this archive to your on-prem target over SCP/rsync.

## 6) Target Host Bootstrap (Ubuntu 24.04)

Run as root or sudo-capable account.

### 6.1 Base packages

```bash
sudo apt update
sudo apt install -y \
  curl git jq ca-certificates build-essential \
  docker.io docker-buildx unzip zip

sudo systemctl enable --now docker
```

### 6.2 Create service user

```bash
id brewuser >/dev/null 2>&1 || sudo useradd -m -s /bin/bash brewuser
sudo usermod -aG docker brewuser
sudo loginctl enable-linger brewuser
```

### 6.3 Install NVM + Node 22 under brewuser

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
node -v
npm -v
'
```

### 6.4 Install OpenClaw CLI

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
npm install -g openclaw@2026.2.24 clawhub mcporter
openclaw --version
'
```

## 7) Restore Bundle on Target

Assume bundle copied to `/tmp/recovery_bundle_*.tar.gz`.

```bash
set -euo pipefail
BUNDLE="/tmp/recovery_bundle_YYYYmmdd_HHMMSS.tar.gz"  # update

sudo -iu brewuser bash -lc '
set -euo pipefail
mkdir -p "$HOME/recovery_import"
'

sudo tar -C /home/brewuser/recovery_import -xzf "$BUNDLE"
```

Find extracted dir:

```bash
sudo -iu brewuser bash -lc 'find "$HOME/recovery_import" -maxdepth 2 -type d -name "recovery_bundle_*"'
```

Set variable:

```bash
RESTORE_DIR="/home/brewuser/recovery_import/recovery_bundle_YYYYmmdd_HHMMSS"  # update
```

### 7.1 Restore OpenClaw home and workspace

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"

rm -rf "$HOME/.openclaw"
cp -a "$RESTORE_DIR/openclaw_home" "$HOME/.openclaw"
'
```

### 7.2 Restore Homebrew payload + compatibility symlink

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"

rm -rf "$HOME/.linuxbrew"
cp -a "$RESTORE_DIR/linuxbrew_payload" "$HOME/.linuxbrew"
'

sudo mkdir -p /home/linuxbrew
sudo rm -rf /home/linuxbrew/.linuxbrew
sudo ln -s /home/brewuser/.linuxbrew /home/linuxbrew/.linuxbrew
sudo chown -h root:root /home/linuxbrew/.linuxbrew
sudo chown -R brewuser:brewuser /home/brewuser/.linuxbrew
```

### 7.3 Restore systemd user unit files and helper script

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"

mkdir -p "$HOME/.config/systemd/user"
cp -a "$RESTORE_DIR/systemd_user/openclaw-gateway.service" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/systemd_user/openclaw-gateway.service.d" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/systemd_user/openclaw-healthcheck.service" "$HOME/.config/systemd/user/"
cp -a "$RESTORE_DIR/systemd_user/openclaw-healthcheck.timer" "$HOME/.config/systemd/user/"

mkdir -p "$HOME/.local/bin"
cp -a "$RESTORE_DIR/local_bin/openclaw-healthcheck" "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/openclaw-healthcheck"
'
```

### 7.4 Restore shell bootstrap files

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
RESTORE_DIR="'"$RESTORE_DIR"'"
cp -a "$RESTORE_DIR/.bashrc" "$HOME/.bashrc"
cp -a "$RESTORE_DIR/.profile" "$HOME/.profile"
'
```

## 8) Secrets Reinjection and Security Check

Before starting gateway, verify and update secret-bearing files.

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail

# Review without printing full secret values in logs
jq -r "
  .gateway.auth.mode,
  (.channels | keys[])
" "$HOME/.openclaw/openclaw.json"

# Optional: rotate/edit secrets
# nano "$HOME/.openclaw/openclaw.json"
# nano "$HOME/.config/systemd/user/openclaw-gateway.service"
# nano "$HOME/.config/systemd/user/openclaw-gateway.service.d/override.conf"
'
```

Recommendation:
- Prefer moving secrets out of `.bashrc`.
- Keep secrets in `openclaw.json` and/or systemd drop-ins with `chmod 600`.

## 9) Sandbox Image Restore/Build

### 9.1 Preferred offline restore from bundle

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

### 9.2 Online rebuild from latest upstream (if needed)

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
mkdir -p "$HOME/.openclaw/sandbox-image-build"
cd "$HOME/.openclaw/sandbox-image-build"

curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw/main/Dockerfile.sandbox -o Dockerfile.sandbox

docker build -t openclaw-sandbox:bookworm-slim -f Dockerfile.sandbox .
docker image inspect openclaw-sandbox:bookworm-slim --format "{{.Id}} {{.Created}}"
'
```

## 10) Bring Services Online

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

systemctl --user status openclaw-gateway.service --no-pager | sed -n "1,40p"
systemctl --user status openclaw-healthcheck.timer --no-pager | sed -n "1,40p"
'
```

## 11) Validation Checklist

Run these in order.

### 11.1 Core binary/path checks

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
command -v node npm openclaw brew docker
node -v
npm -v
openclaw --version
brew --prefix
ls -ld /home/linuxbrew/.linuxbrew /home/brewuser/.linuxbrew
'
```

### 11.2 Docker + sandbox checks

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
id
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
docker image inspect openclaw-sandbox:bookworm-slim >/dev/null && echo "sandbox image present"
openclaw sandbox list
'
```

### 11.3 OpenClaw functional checks

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
openclaw doctor
openclaw logs --limit 50 --timeout 10000 --plain
'
```

### 11.4 Healthcheck verification

```bash
sudo -iu brewuser bash -lc '
set -euo pipefail
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus

systemctl --user start openclaw-healthcheck.service
systemctl --user status openclaw-healthcheck.service --no-pager | sed -n "1,80p"

tail -n 30 /home/brewuser/.openclaw/logs/healthcheck.log
'
```

Success criteria:
- `openclaw-gateway.service` active
- `openclaw-healthcheck.service` exits `status=0/SUCCESS`
- Health log shows `PASS` and no critical failures
- `openclaw doctor` no sandbox-image missing warning

## 12) Network and On-Prem Cutover Notes

### 12.1 Required connectivity
- Outbound TCP 443 for providers (Discord, Telegram, model APIs, package repos)
- Docker daemon local socket access for `brewuser`

Because gateway bind is loopback, inbound internet exposure is not required for normal bot operation.

### 12.2 Cutover steps
1. Freeze source instance (maintenance window).
2. Run final backup bundle creation.
3. Restore on target.
4. Validate target end-to-end.
5. Disable source gateway service.
6. Monitor channels on target for 30-60 minutes.

Disable source:

```bash
sudo -iu brewuser bash -lc '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus
systemctl --user disable --now openclaw-gateway.service
systemctl --user disable --now openclaw-healthcheck.timer
'
```

## 13) Troubleshooting Playbook

### Issue: `permission denied` on Docker socket

```bash
sudo usermod -aG docker brewuser
sudo systemctl restart user@1000.service
sudo -iu brewuser bash -lc 'id; docker ps'
```

### Issue: `openclaw logs` says gateway not reachable
- Ensure user service is running and DBUS vars are set when using `systemctl --user`.

```bash
sudo -iu brewuser bash -lc '
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus
systemctl --user status openclaw-gateway.service --no-pager
openclaw logs --limit 50 --plain
'
```

### Issue: sandbox image missing

```bash
sudo -iu brewuser bash -lc '
docker image inspect openclaw-sandbox:bookworm-slim || true
# load from tar or rebuild (section 9)
'
```

### Issue: user service control fails with bus errors

```bash
sudo systemctl status user@1000.service --no-pager
sudo loginctl enable-linger brewuser
sudo systemctl restart user@1000.service
```

### Issue: OpenClaw command not found in non-interactive shell
Use absolute path:
- `/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw`

## 14) Operational Command Cheat Sheet

```bash
# Gateway status
sudo -iu brewuser bash -lc 'export XDG_RUNTIME_DIR=/run/user/$(id -u); export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus; systemctl --user status openclaw-gateway.service --no-pager'

# Tail OpenClaw logs
sudo -iu brewuser bash -lc '/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw logs --follow --plain'

# Run doctor
sudo -iu brewuser bash -lc '/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw doctor'

# Trigger healthcheck now
sudo -iu brewuser bash -lc 'export XDG_RUNTIME_DIR=/run/user/$(id -u); export DBUS_SESSION_BUS_ADDRESS=unix:path=${XDG_RUNTIME_DIR}/bus; systemctl --user start openclaw-healthcheck.service'

# View healthcheck logs
tail -f /home/brewuser/.openclaw/logs/healthcheck.log

# List sandbox containers
sudo -iu brewuser bash -lc '/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw sandbox list'

# Recreate sandbox containers
sudo -iu brewuser bash -lc '/home/brewuser/.nvm/versions/node/v22.22.0/bin/openclaw sandbox recreate --all'
```

## 14.1 Native Backup Scripts (Current Workspace)

Current workspace includes backup tooling:
- `/home/brewuser/.openclaw/workspace/scripts/backup-manager.sh`
- `/home/brewuser/.openclaw/workspace/scripts/generate-backup-manifest.sh`

Usage examples:

```bash
# List backups
sudo -iu brewuser bash -lc 'cd /home/brewuser/.openclaw/workspace/scripts && ./backup-manager.sh list'

# Create full backup archive
sudo -iu brewuser bash -lc 'cd /home/brewuser/.openclaw/workspace/scripts && ./backup-manager.sh backup'

# Generate manifest only
sudo -iu brewuser bash -lc 'cd /home/brewuser/.openclaw/workspace/scripts && ./backup-manager.sh manifest'

# Interactive restore
sudo -iu brewuser bash -lc 'cd /home/brewuser/.openclaw/workspace/scripts && ./backup-manager.sh restore'
```

## 15) Recovery Artifacts to Keep Safe

Store these in secure off-host storage:
- Recovery bundle tarball from section 5
- `/home/brewuser/.openclaw/backups/*.tar.gz`
- `/home/brewuser/.openclaw/backups/migration_20260227_004254/*`
- Secret inventory in password manager (tokens/keys)

## 16) Recommended Hardening Improvements (Post-Restore)

1. Move `NVIDIA_API_KEY` out of `.bashrc` into a root-readable secret file injected to systemd drop-in only.
2. Periodically rotate gateway token and channel/API tokens.
3. Keep at least 7 daily off-host encrypted backups.
4. Add a weekly restore test to a staging VM.

## 17) Useful Local Reference Files

These files on the source host contain concrete migration history and command outputs from the last successful stabilization:
- `/home/brewuser/.openclaw/backups/migration_20260227_004254/MIGRATION_NOTES.md`
- `/home/brewuser/.openclaw/backups/migration_20260227_004254/brew-baseline.txt`
- `/home/brewuser/.openclaw/backups/migration_20260227_004254/system-baseline.txt`
- `/home/brewuser/.openclaw/backups/migration_20260227_004254/openclaw-doctor.pre-migration.txt`
- `/home/brewuser/.openclaw/backups/migration_20260227_004254/Brewfile.pre-migration`

---

If this runbook is updated, increment document version and capture new service/config snapshots.
