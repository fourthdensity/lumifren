# Lumifren Chat unified start script
cd "M:\lumifren_app"
docker compose up -d
pip install -r requirements.txt
python lumifren.py
