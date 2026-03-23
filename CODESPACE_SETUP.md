# Lumifren Codespace Sync Workflow

## Services Running

✅ **Flask App**: Port 5001 (Lumifren main UI)  
✅ **Foundry Agents**: Port 8000 (Memory Curator, Tone Detector, Dev Assistant)  
✅ **Redis**: Port 6379 (Docker container for long-term memory)

## Architecture

```
GitHub Codespace (Cloud)
├── lumifren.py (Flask - Port 5001)
├── agents/main.py (FastAPI - Port 8000)  
└── Redis (Docker - Port 6379)
       ↓
    Firebase (Cloud)
    FOUNDRY Backend (Azure AI)
```

## Git Sync Workflow

### From Codespace → Local

When you make changes in Codespace:

```bash
# 1. Check what changed
git status

# 2. Stage changes
git add .

# 3. Commit with message
git commit -m "Description of changes"

# 4. Push to GitHub
git push origin main
```

Then on your local machine:
```bash
git pull origin main
```

### From Local → Codespace

When you make changes on local machine:

```bash
# On local machine
git add .
git commit -m "Description of changes"
git push origin main
```

Then in Codespace, the changes will auto-sync, or manually:
```bash
git pull origin main
```

## Starting Services (After Restart)

Codespaces may shut down when idle. To restart everything:

```bash
# 1. Start Redis
docker start lumifren-redis || docker run -d --name lumifren-redis -p 6379:6379 redis:7-alpine

# 2. Start Agents (in background)
cd /workspaces/lumifren/agents && python main.py &

# 3. Start Flask app
cd /workspaces/lumifren && python lumifren.py
```

Or use the convenience script:
```bash
./start-codespace.sh
```

## Accessing the App

In Codespace, ports are automatically forwarded. Click the "Ports" tab in VS Code to get public URLs for:
- **Port 5001** - Main Lumifren UI
- **Port 8000** - Agents API (admin/debugging)

## Important Notes

- ✅ `.env` is git-ignored (safe, won't sync secrets)
- ✅ Changes to code files sync via git
- ✅ Firebase/FOUNDRY connections work from Codespace (cloud → cloud)
- ⚠️ Redis data is ephemeral (reset when container is removed)
- ⚠️ For production, use persistent Redis or cloud Redis

## Quick Commands

```bash
# Check service status
ps aux | grep -E '(lumifren|main.py)'
docker ps

# View logs
tail -f /tmp/lumifren.log  # if logging to file
docker logs lumifren-redis

# Stop services
pkill -f lumifren.py
pkill -f agents/main.py
docker stop lumifren-redis

# Git status
git status
git log --oneline -5
```
