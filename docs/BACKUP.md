# Backup Management

## Quick Reference

### Create a Backup
```bash
~/.openclaw/workspace/scripts/backup-manager.sh backup
```

### List Available Backups
```bash
~/.openclaw/workspace/scripts/backup-manager.sh list
```

### Restore from Backup
```bash
~/.openclaw/workspace/scripts/backup-manager.sh restore
```
⚠️ **Restore requires confirmation and will show you exactly what's in the backup before proceeding.**

### Check Current State
```bash
~/.openclaw/workspace/scripts/backup-manager.sh manifest
```

## What's Included in Backups?

### ✅ Included
- **Configuration**: `openclaw.json`, `.env`
- **Core Files**: SOUL.md, AGENTS.md, USER.md, TOOLS.md, IDENTITY.md, etc.
- **Memory**: All files in `memory/` directory
- **Learnings**: All files in `.learnings/` directory
- **Skills**: All installed skills with SKILL.md files
- **Projects**: All projects in `projects/` directory
- **Scripts**: Custom scripts in `scripts/` directory

### ⚠️ Critical: Skills Check

**ALWAYS verify skills are included!** The manifest shows:
- ✓ = Skill present with SKILL.md
- ⚠ = Skill directory exists but no SKILL.md (may be incomplete)
- ✗ = Skill missing entirely

**Current Skills (as of last backup):**
- algorithmic-art
- csm-voice
- frontend-design
- game-art
- godot-gdscript-patterns
- proactive-agent-3.1.0
- sam-tts
- self-improving-agent
- sonoscli
- telegram-context
- ux-researcher-designer

## Restore Process

1. **List backups** to see available options
2. **Select backup** - enter filename when prompted
3. **Review manifest** - shows exactly what's included
4. **Check differences** - warns if skill counts don't match
5. **Type 'RESTORE'** to confirm (must be uppercase)
6. **Safety backup created** of current state before restore
7. **Files restored** from backup archive

## Important Notes

- **Manifest is generated automatically** with every backup
- **Manifest is human-readable** - check it before restoring
- **Safety backup created** before any restore operation
- **Skill count mismatch warning** if backup differs from current
- **Confirmation required** for all restore operations

## Troubleshooting Missing Skills

If skills are missing after restore:
1. Check the backup manifest to see what was included
2. Compare with `ls ~/.openclaw/workspace/skills/`
3. If backup was incomplete, restore from an older backup
4. Reinstall missing skills via ClawHub if needed