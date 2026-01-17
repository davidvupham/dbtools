#!/bin/bash
# Docker Volume Restore Script
# Usage: ./restore.sh <backup_file> <volume_name>

set -e

BACKUP_FILE="${1:?Usage: ./restore.sh <backup_file> <volume_name>}"
VOLUME_NAME="${2:?Usage: ./restore.sh <backup_file> <volume_name>}"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring to volume: $VOLUME_NAME"
echo "From backup: $BACKUP_FILE"

# Create volume if it doesn't exist
docker volume create "$VOLUME_NAME" 2>/dev/null || true

docker run --rm \
  -v "${VOLUME_NAME}:/data" \
  -v "$(dirname "$BACKUP_FILE"):/backup:ro" \
  alpine \
  sh -c "rm -rf /data/* && tar xzf /backup/$(basename "$BACKUP_FILE") -C /data"

echo "Restore complete!"
