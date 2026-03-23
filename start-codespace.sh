#!/bin/bash
# Lumifren Codespace Start Script

echo "🔆 Starting Lumifren in Codespace..."

# Start Redis
docker start lumifren-redis 2>/dev/null || docker run -d --name lumifren-redis -p 6379:6379 redis:7-alpine
echo "✓ Redis started"

# Start Agents backend
cd /workspaces/lumifren/agents
nohup python main.py > /tmp/agents.log 2>&1 &
echo "✓ Agents backend started (port 8000)"

# Start Flask app  
cd /workspaces/lumifren
echo "✓ Starting Flask app (port 5001)..."
echo "   Access your app at the forwarded URL in the Ports tab"
python lumifren.py
