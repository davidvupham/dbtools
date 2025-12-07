# Volume Backup and Restore Examples

This directory contains scripts for backing up and restoring Docker volumes.

## Files

- `backup.sh` - Backup a Docker volume to a tar.gz file
- `restore.sh` - Restore a Docker volume from a tar.gz backup

## Usage

### Backup a Volume

```bash
chmod +x backup.sh
./backup.sh my-db-data ./backups

# Creates: ./backups/my-db-data_20241207_103000.tar.gz
```

### Restore a Volume

```bash
chmod +x restore.sh
./restore.sh ./backups/my-db-data_20241207_103000.tar.gz my-db-data-restored
```

## How It Works

The scripts use a temporary Alpine container to:

1. Mount the volume (read-only for backup)
2. Create/extract the tar.gz archive
3. Clean up automatically (`--rm`)

This approach works without stopping your running containers, though for databases you may want to stop writes during backup for consistency.
