#!/bin/bash
# OpenClaw Backup Manifest Generator
# Creates detailed manifest of all items included in backup

BACKUP_DIR="${1:-$HOME/.openclaw/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MANIFEST_FILE="$BACKUP_DIR/backup_manifest_$TIMESTAMP.txt"

echo "=== OpenClaw Backup Manifest ===" > "$MANIFEST_FILE"
echo "Generated: $(date)" >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

echo "## CONFIGURATION FILES ##" >> "$MANIFEST_FILE"
echo "-------------------------" >> "$MANIFEST_FILE"
ls -la ~/.openclaw/openclaw.json 2>/dev/null && echo "✓ openclaw.json" >> "$MANIFEST_FILE" || echo "✗ openclaw.json (MISSING)" >> "$MANIFEST_FILE"
ls -la ~/.openclaw/.env 2>/dev/null && echo "✓ .env" >> "$MANIFEST_FILE" || echo "✗ .env (not present)" >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

echo "## WORKSPACE FILES ##" >> "$MANIFEST_FILE"
echo "---------------------" >> "$MANIFEST_FILE"
echo "Location: ~/.openclaw/workspace/" >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

echo "### Core Identity Files ###" >> "$MANIFEST_FILE"
for file in SOUL.md AGENTS.md USER.md TOOLS.md IDENTITY.md BOOTSTRAP.md MEMORY.md HEARTBEAT.md .MODEL_WARNINGS.md; do
    if [ -f ~/.openclaw/workspace/$file ]; then
        size=$(du -h ~/.openclaw/workspace/$file | cut -f1)
        lines=$(wc -l < ~/.openclaw/workspace/$file)
        echo "✓ $file ($size, $lines lines)" >> "$MANIFEST_FILE"
    else
        echo "✗ $file (MISSING)" >> "$MANIFEST_FILE"
    fi
done
echo "" >> "$MANIFEST_FILE"

echo "### Memory Files ###" >> "$MANIFEST_FILE"
if [ -d ~/.openclaw/workspace/memory ]; then
    echo "✓ memory/ directory present" >> "$MANIFEST_FILE"
    find ~/.openclaw/workspace/memory -type f -name "*.md" | while read f; do
        size=$(du -h "$f" | cut -f1)
        echo "  - $(basename $f) ($size)" >> "$MANIFEST_FILE"
    done
else
    echo "✗ memory/ directory (MISSING)" >> "$MANIFEST_FILE"
fi
echo "" >> "$MANIFEST_FILE"

echo "### Learning Files ###" >> "$MANIFEST_FILE"
if [ -d ~/.openclaw/workspace/.learnings ]; then
    echo "✓ .learnings/ directory present" >> "$MANIFEST_FILE"
    find ~/.openclaw/workspace/.learnings -type f | while read f; do
        size=$(du -h "$f" | cut -f1)
        echo "  - $(basename $f) ($size)" >> "$MANIFEST_FILE"
    done
else
    echo "✗ .learnings/ directory (MISSING)" >> "$MANIFEST_FILE"
fi
echo "" >> "$MANIFEST_FILE"

echo "## SKILLS ##" >> "$MANIFEST_FILE"
echo "------------" >> "$MANIFEST_FILE"
if [ -d ~/.openclaw/workspace/skills ]; then
    echo "✓ skills/ directory present" >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"
    echo "Installed Skills:" >> "$MANIFEST_FILE"
    for skill in ~/.openclaw/workspace/skills/*/; do
        if [ -d "$skill" ]; then
            skill_name=$(basename "$skill")
            skill_size=$(du -sh "$skill" | cut -f1)
            has_skill_md=$(find "$skill" -name "SKILL.md" | wc -l)
            if [ $has_skill_md -gt 0 ]; then
                echo "  ✓ $skill_name ($skill_size)" >> "$MANIFEST_FILE"
            else
                echo "  ⚠ $skill_name ($skill_size) - NO SKILL.md" >> "$MANIFEST_FILE"
            fi
        fi
    done
else
    echo "✗ skills/ directory (MISSING)" >> "$MANIFEST_FILE"
fi
echo "" >> "$MANIFEST_FILE"

echo "### Skill Configuration ###" >> "$MANIFEST_FILE"
for skill_config in ~/.openclaw/workspace/skills/*/config.json; do
    if [ -f "$skill_config" ]; then
        echo "  - $(basename $(dirname $skill_config))/config.json" >> "$MANIFEST_FILE"
    fi
done
echo "" >> "$MANIFEST_FILE"

echo "## PROJECTS ##" >> "$MANIFEST_FILE"
echo "--------------" >> "$MANIFEST_FILE"
if [ -d ~/.openclaw/workspace/projects ]; then
    echo "✓ projects/ directory present" >> "$MANIFEST_FILE"
    find ~/.openclaw/workspace/projects -maxdepth 1 -type d | tail -n +2 | while read proj; do
        proj_name=$(basename "$proj")
        proj_size=$(du -sh "$proj" 2>/dev/null | cut -f1)
        echo "  - $proj_name ($proj_size)" >> "$MANIFEST_FILE"
    done
else
    echo "✗ projects/ directory (not present)" >> "$MANIFEST_FILE"
fi
echo "" >> "$MANIFEST_FILE"

echo "## SESSIONS & STATE ##" >> "$MANIFEST_FILE"
echo "----------------------" >> "$MANIFEST_FILE"
ls -la ~/.openclaw/sessions/ 2>/dev/null | head -10 >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

echo "## SIZE SUMMARY ##" >> "$MANIFEST_FILE"
echo "------------------" >> "$MANIFEST_FILE"
du -sh ~/.openclaw/workspace/ 2>/dev/null >> "$MANIFEST_FILE"
du -sh ~/.openclaw/openclaw.json 2>/dev/null >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

echo "=== END OF MANIFEST ===" >> "$MANIFEST_FILE"
echo "Manifest saved to: $MANIFEST_FILE"
cat "$MANIFEST_FILE"