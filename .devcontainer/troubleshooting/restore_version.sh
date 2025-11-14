#!/bin/bash
# Restore a specific version from archive
# Usage: ./restore_version.sh <timestamp>
# Example: ./restore_version.sh 20251114_065651

set -e

if [ $# -eq 0 ]; then
    echo "Available backups in archive:"
    echo ""
    ls -lht archive/ | grep -E "Dockerfile|devcontainer.json|postCreate.sh" | head -20
    echo ""
    echo "Usage: $0 <timestamp>"
    echo "Example: $0 20251114_065651"
    exit 1
fi

TIMESTAMP=$1
ARCHIVE_DIR="archive"

echo "Restoring version from timestamp: $TIMESTAMP"
echo ""

# Check if files exist
if [ ! -f "$ARCHIVE_DIR/Dockerfile.$TIMESTAMP" ]; then
    echo "ERROR: Dockerfile.$TIMESTAMP not found in archive/"
    exit 1
fi

if [ ! -f "$ARCHIVE_DIR/devcontainer.json.$TIMESTAMP" ]; then
    echo "ERROR: devcontainer.json.$TIMESTAMP not found in archive/"
    exit 1
fi

# Backup current files before restoring
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "Creating backup of current files with timestamp: $BACKUP_TIMESTAMP"
[ -f Dockerfile ] && cp -p Dockerfile "$ARCHIVE_DIR/Dockerfile.before_restore_$BACKUP_TIMESTAMP"
[ -f devcontainer.json ] && cp -p devcontainer.json "$ARCHIVE_DIR/devcontainer.json.before_restore_$BACKUP_TIMESTAMP"
[ -f postCreate.sh ] && cp -p postCreate.sh "$ARCHIVE_DIR/postCreate.sh.before_restore_$BACKUP_TIMESTAMP"

# Restore files
echo "Restoring Dockerfile..."
cp -p "$ARCHIVE_DIR/Dockerfile.$TIMESTAMP" Dockerfile

echo "Restoring devcontainer.json..."
cp -p "$ARCHIVE_DIR/devcontainer.json.$TIMESTAMP" devcontainer.json

# Restore postCreate.sh if it exists
if [ -f "$ARCHIVE_DIR/postCreate.sh.$TIMESTAMP" ]; then
    echo "Restoring postCreate.sh..."
    cp -p "$ARCHIVE_DIR/postCreate.sh.$TIMESTAMP" postCreate.sh
else
    echo "NOTE: No postCreate.sh.$TIMESTAMP found, skipping"
    [ -f postCreate.sh ] && rm postCreate.sh && echo "Removed current postCreate.sh"
fi

echo ""
echo "✅ Restoration complete!"
echo ""
echo "Restored files:"
ls -lh Dockerfile devcontainer.json 2>/dev/null
[ -f postCreate.sh ] && ls -lh postCreate.sh

echo ""
echo "Now rebuild the dev container in VS Code:"
echo "  F1 → Dev Containers: Rebuild Container"
