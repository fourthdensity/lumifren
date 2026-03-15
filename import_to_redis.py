import redis
import os
import glob
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def import_memories():
    print("Importing memories...")
    memory_files = glob.glob("memory/*.md")
    for file_path in memory_files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            key = f"memory:imported:{filename}"
            r.set(key, content)
            print(f"Stored {filename}")

def import_config():
    print("\nImporting configs...")
    config_files = ["SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md", "AGENTS.md", "HEARTBEAT.md", "SESSION-STATE.md"]
    for filename in config_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                key = f"config:{filename.replace('.md', '').lower()}"
                r.set(key, content)
                print(f"Stored {filename}")

if __name__ == "__main__":
    import_memories()
    import_config()
    print("\n[OK] Import completed.")
