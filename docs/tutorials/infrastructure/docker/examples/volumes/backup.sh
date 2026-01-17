#!/bin/bash
# Docker Volume Backup Script
# Usage: ./backup.sh <volume_name> [backup_dir]

set -e

VOLUME_NAME="${1:?Usage: ./backup.sh <volume_name> [backup_dir]}"
BACKUP_DIR="${2:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${VOLUME_NAME}_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Backing up volume: $VOLUME_NAME"
echo "Destination: $BACKUP_FILE"

docker run --rm \
  -v "${VOLUME_NAME}:/data:ro" \
  -v "${BACKUP_DIR}:/backup" \
  alpine \
  tar czf "/backup/${VOLUME_NAME}_${TIMESTAMP}.tar.gz" -C /data .

echo "Backup complete: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"
