#!/bin/bash
# OpenClaw Backup Manager with Confirmation
# Usage: ./backup-manager.sh [backup|restore|list]

set -e

BACKUP_DIR="${BACKUP_DIR:-$HOME/.openclaw/backups}"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

generate_manifest() {
    local target_dir="$1"
    local manifest_file="$target_dir/MANIFEST.txt"
    
    log_info "Generating backup manifest..."
    
    cat > "$manifest_file" << EOF
================================================================================
                    OPENCLAW BACKUP MANIFEST
================================================================================
Generated: $(date)
Backup Type: Full System Backup
Backup Location: $target_dir

================================================================================
                              CONTENTS
================================================================================

## 1. CONFIGURATION FILES
--------------------------------------------------------------------------------
EOF
    
    # Config files
    echo "✓ openclaw.json (Main configuration)" >> "$manifest_file"
    [ -f "$HOME/.openclaw/.env" ] && echo "✓ .env (Environment variables)" >> "$manifest_file" || echo "  .env (not present)" >> "$manifest_file"
    echo "" >> "$manifest_file"
    
    # Workspace files
    echo "## 2. WORKSPACE CORE FILES" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    for file in SOUL.md AGENTS.md USER.md TOOLS.md IDENTITY.md BOOTSTRAP.md MEMORY.md HEARTBEAT.md .MODEL_WARNINGS.md SELF_IMPROVEMENT_REMINDER.md; do
        if [ -f "$WORKSPACE_DIR/$file" ]; then
            size=$(du -h "$WORKSPACE_DIR/$file" | cut -f1)
            lines=$(wc -l < "$WORKSPACE_DIR/$file")
            echo "✓ $file ($size, $lines lines)" >> "$manifest_file"
        else
            echo "✗ $file (MISSING)" >> "$manifest_file"
        fi
    done
    echo "" >> "$manifest_file"
    
    # Memory files
    echo "## 3. MEMORY FILES" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    if [ -d "$WORKSPACE_DIR/memory" ]; then
        count=$(find "$WORKSPACE_DIR/memory" -type f -name "*.md" | wc -l)
        total_size=$(du -sh "$WORKSPACE_DIR/memory" | cut -f1)
        echo "✓ memory/ directory ($count files, $total_size total)" >> "$manifest_file"
        find "$WORKSPACE_DIR/memory" -type f -name "*.md" | sort | head -20 | while read f; do
            size=$(du -h "$f" | cut -f1)
            echo "    - $(basename $f) ($size)" >> "$manifest_file"
        done
        [ $count -gt 20 ] && echo "    ... and $((count - 20)) more files" >> "$manifest_file"
    else
        echo "✗ memory/ directory (MISSING)" >> "$manifest_file"
    fi
    echo "" >> "$manifest_file"
    
    # Learnings
    echo "## 4. LEARNINGS" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    if [ -d "$WORKSPACE_DIR/.learnings" ]; then
        for f in "$WORKSPACE_DIR/.learnings"/*; do
            [ -f "$f" ] && echo "✓ $(basename $f)" >> "$manifest_file"
        done
    else
        echo "  No .learnings directory" >> "$manifest_file"
    fi
    echo "" >> "$manifest_file"
    
    # Skills - THIS IS THE IMPORTANT PART
    echo "## 5. SKILLS (★ CRITICAL - Check carefully!)" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    if [ -d "$WORKSPACE_DIR/skills" ]; then
        skill_count=$(find "$WORKSPACE_DIR/skills" -mindepth 1 -maxdepth 1 -type d | wc -l)
        echo "✓ skills/ directory ($skill_count skills installed)" >> "$manifest_file"
        echo "" >> "$manifest_file"
        echo "Installed Skills:" >> "$manifest_file"
        for skill_dir in "$WORKSPACE_DIR/skills"/*/; do
            if [ -d "$skill_dir" ]; then
                skill_name=$(basename "$skill_dir")
                skill_size=$(du -sh "$skill_dir" 2>/dev/null | cut -f1)
                has_skill_md=$(find "$skill_dir" -name "SKILL.md" | wc -l)
                has_config=$(find "$skill_dir" -name "config.json" | wc -l)
                
                if [ $has_skill_md -gt 0 ]; then
                    echo "  ✓ $skill_name ($skill_size) [SKILL.md present]" >> "$manifest_file"
                else
                    echo "  ⚠ $skill_name ($skill_size) [NO SKILL.md - may be incomplete]" >> "$manifest_file"
                fi
            fi
        done
    else
        echo "✗ skills/ directory (MISSING - CRITICAL!)" >> "$manifest_file"
    fi
    echo "" >> "$manifest_file"
    
    # Projects
    echo "## 6. PROJECTS" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    if [ -d "$WORKSPACE_DIR/projects" ]; then
        for proj in "$WORKSPACE_DIR/projects"/*/; do
            [ -d "$proj" ] || continue
            proj_name=$(basename "$proj")
            proj_size=$(du -sh "$proj" 2>/dev/null | cut -f1)
            echo "✓ $proj_name ($proj_size)" >> "$manifest_file"
        done
    else
        echo "  No projects directory" >> "$manifest_file"
    fi
    echo "" >> "$manifest_file"
    
    # Scripts
    echo "## 7. CUSTOM SCRIPTS" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    if [ -d "$WORKSPACE_DIR/scripts" ]; then
        for script in "$WORKSPACE_DIR/scripts"/*; do
            [ -f "$script" ] || continue
            script_name=$(basename "$script")
            script_size=$(du -h "$script" | cut -f1)
            echo "✓ $script_name ($script_size)" >> "$manifest_file"
        done
    else
        echo "  No scripts directory" >> "$manifest_file"
    fi
    echo "" >> "$manifest_file"
    
    # Size summary
    echo "## 8. SIZE SUMMARY" >> "$manifest_file"
    echo "--------------------------------------------------------------------------------" >> "$manifest_file"
    echo "Workspace: $(du -sh "$WORKSPACE_DIR" | cut -f1)" >> "$manifest_file"
    echo "Config: $(du -sh "$CONFIG_FILE" | cut -f1)" >> "$manifest_file"
    echo "Total backup size: $(du -sh "$target_dir" | cut -f1)" >> "$manifest_file"
    echo "" >> "$manifest_file"
    
    echo "================================================================================" >> "$manifest_file"
    echo "                         END OF MANIFEST" >> "$manifest_file"
    echo "================================================================================" >> "$manifest_file"
    
    log_success "Manifest generated: $manifest_file"
    cat "$manifest_file"
}

create_backup() {
    log_info "Starting backup process..."
    
    # Create backup directory
    backup_name="openclaw-backup-$TIMESTAMP"
    backup_path="$BACKUP_DIR/$backup_name"
    mkdir -p "$backup_path"
    
    # Copy configuration
    log_info "Backing up configuration..."
    cp "$CONFIG_FILE" "$backup_path/"
    [ -f "$HOME/.openclaw/.env" ] && cp "$HOME/.openclaw/.env" "$backup_path/"
    
    # Copy workspace
    log_info "Backing up workspace (this may take a while)..."
    cp -r "$WORKSPACE_DIR" "$backup_path/"
    
    # Generate manifest
    generate_manifest "$backup_path"
    
    # Create tar.gz
    log_info "Creating compressed archive..."
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "$backup_name"
    
    # Clean up temp directory
    rm -rf "$backup_path"
    
    log_success "Backup created: $backup_path.tar.gz"
    log_info "Manifest included in archive as MANIFEST.txt"
    
    # List the backup
    ls -lh "$backup_path.tar.gz"
}

list_backups() {
    log_info "Available backups:"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/*.tar.gz 2>/dev/null)" ]; then
        log_warn "No backups found in $BACKUP_DIR"
        return 1
    fi
    
    printf "%-40s %-15s %-20s\n" "BACKUP FILE" "SIZE" "DATE"
    echo "--------------------------------------------------------------------------------"
    
    for backup in "$BACKUP_DIR"/*.tar.gz; do
        [ -f "$backup" ] || continue
        filename=$(basename "$backup")
        size=$(du -h "$backup" | cut -f1)
        date=$(stat -c %y "$backup" 2>/dev/null | cut -d' ' -f1)
        printf "%-40s %-15s %-20s\n" "$filename" "$size" "$date"
    done
}

restore_backup() {
    log_info "Available backups:"
    list_backups
    
    echo ""
    read -p "Enter backup filename to restore (or 'cancel' to abort): " backup_file
    
    if [ "$backup_file" = "cancel" ]; then
        log_info "Restore cancelled"
        return 0
    fi
    
    # Add extension if not present
    [[ "$backup_file" != *.tar.gz ]] && backup_file="$backup_file.tar.gz"
    
    backup_path="$BACKUP_DIR/$backup_file"
    
    if [ ! -f "$backup_path" ]; then
        log_error "Backup not found: $backup_path"
        return 1
    fi
    
    # Extract manifest first
    log_info "Reading backup manifest..."
    manifest=$(tar -xzf "$backup_path" -O */MANIFEST.txt 2>/dev/null || echo "No manifest found")
    
    echo ""
    echo "================================================================================"
    echo "                          BACKUP CONTENTS"
    echo "================================================================================"
    echo "$manifest"
    echo "================================================================================"
    echo ""
    
    log_warn "⚠️  RESTORE WILL OVERWRITE CURRENT CONFIGURATION AND WORKSPACE!"
    echo ""
    
    # Show what's different
    log_info "Checking for differences..."
    
    # Check skills
    current_skills=$(find "$WORKSPACE_DIR/skills" -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "Current skills: $current_skills"
    
    # Extract to temp to count
    temp_dir=$(mktemp -d)
    tar -xzf "$backup_path" -C "$temp_dir" >/devdev/null 2>&1
    backup_skills=$(find "$temp_dir"/*/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    rm -rf "$temp_dir"
    echo "Backup skills: $backup_skills"
    
    if [ "$current_skills" -ne "$backup_skills" ]; then
        log_warn "SKILL COUNT MISMATCH! Current: $current_skills, Backup: $backup_skills"
        log_warn "You may lose skills if you proceed with restore!"
    fi
    
    echo ""
    read -p "Are you SURE you want to restore? Type 'RESTORE' to confirm: " confirm
    
    if [ "$confirm" != "RESTORE" ]; then
        log_info "Restore cancelled"
        return 0
    fi
    
    # Create pre-restore backup
    log_info "Creating safety backup of current state..."
    create_backup > /dev/null 2>&1
    
    # Extract backup
    log_info "Restoring from backup..."
    tar -xzf "$backup_path" -C "$BACKUP_DIR"
    
    # Find extracted directory
    extracted_dir=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "openclaw-backup-*" | grep -v ".tar.gz" | head -1)
    
    # Restore config
    cp "$extracted_dir/openclaw.json" "$CONFIG_FILE"
    [ -f "$extracted_dir/.env" ] && cp "$extracted_dir/.env" "$HOME/.openclaw/"
    
    # Restore workspace
    rm -rf "$WORKSPACE_DIR"
    cp -r "$extracted_dir/workspace" "$WORKSPACE_DIR"
    
    # Clean up
    rm -rf "$extracted_dir"
    
    log_success "Restore complete!"
    log_info "Please restart OpenClaw to apply changes"
}

# Main
case "${1:-backup}" in
    backup)
        create_backup
        ;;
    restore)
        restore_backup
        ;;
    list)
        list_backups
        ;;
    manifest)
        temp_dir=$(mktemp -d)
        generate_manifest "$temp_dir"
        rm -rf "$temp_dir"
        ;;
    *)
        echo "Usage: $0 [backup|restore|list|manifest]"
        echo ""
        echo "Commands:"
        echo "  backup   - Create a new backup with manifest"
        echo "  restore  - Restore from a backup (requires confirmation)"
        echo "  list     - List available backups"
        echo "  manifest - Generate manifest of current state without backing up"
        exit 1
        ;;
esac