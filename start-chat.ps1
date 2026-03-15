# Kimi Chat unified start script (Tailscale-enabled)
cd "M:\kimilocal\kimi-proxy"
docker compose up -d
cd "M:\kimilocal"
docker compose -f docker-compose-redis.yml up -d
pip install -r requirements.txt

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Starting Kimi Chat (Tailscale Network Mode)" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "Chat UI: http://portalv2:5001" -ForegroundColor Cyan
Write-Host "Admin UI: http://portalv2:5001/admin/dashboard" -ForegroundColor Cyan
Write-Host "Redis Dashboard: http://portalv2:5000" -ForegroundColor Cyan
Write-Host "`nTailscale IP: 100.95.19.54" -ForegroundColor Yellow
Write-Host "============================================`n" -ForegroundColor Green

python kimi_chat_app.py
