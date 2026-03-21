import os
import shutil
import datetime
import json

# Configuration
WORKSPACE_ROOT = r"M:\lumifren_app"
SNAPSHOT_DIR = os.path.join(WORKSPACE_ROOT, "snapshots")
CORE_FILES = [
    "lumifren.py",
    "templates/index.html",
    ".env",
    "requirements.txt",
    "README.md",
    "TOOLS.md",
    "AGENTS.md",
    "SOUL.md",
    "IDENTITY.md",
    "config.json",
    "model_client.py"
]

def create_snapshot(label="manual"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"snapshot_{timestamp}_{label}"
    target_path = os.path.join(SNAPSHOT_DIR, snapshot_name)
    
    print(f"[*] Creating snapshot: {snapshot_name}...")
    
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    
    manifest = {
        "timestamp": timestamp,
        "label": label,
        "files": []
    }
    
    for rel_path in CORE_FILES:
        src = os.path.join(WORKSPACE_ROOT, rel_path)
        if os.path.exists(src):
            # Maintain directory structure in snapshot
            dst = os.path.join(target_path, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            
            manifest["files"].append(rel_path)
            print(f"  [+] Copied: {rel_path}")
        else:
            print(f"  [!] Missing: {rel_path}")

    # Save manifest
    with open(os.path.join(target_path, "snapshot_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"[SUCCESS] Snapshot saved to: {target_path}")
    return snapshot_name

def list_snapshots():
    if not os.path.exists(SNAPSHOT_DIR):
        print("[!] No snapshots directory found.")
        return
    
    print("\n--- Available Snapshots ---")
    snapshots = [d for d in os.listdir(SNAPSHOT_DIR) if os.path.isdir(os.path.join(SNAPSHOT_DIR, d))]
    for i, s in enumerate(sorted(snapshots, reverse=True)):
        print(f"{i+1}. {s}")
    print("---------------------------\n")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "create"
    label = sys.argv[2] if len(sys.argv) > 2 else "milestone"
    
    if cmd == "create":
        create_snapshot(label)
    elif cmd == "list":
        list_snapshots()
    else:
        print("Usage: python snapshot_manager.py [create|list] [label]")
