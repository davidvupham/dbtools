# Advanced Volume Operations

> **Module:** Storage Deep Dive | **Level:** Intermediate | **Time:** 35 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Backup and restore Docker/Podman volumes
- Copy data between volumes
- Share volumes between containers
- Manage volume lifecycle and cleanup
- Implement volume backup strategies

---

## Volume Backup Strategies

### Method 1: Tar Archive (Simple)

```bash
# Create backup from running or stopped container
docker run --rm \
    -v myvolume:/data \
    -v $(pwd):/backup \
    alpine tar czf /backup/myvolume-backup.tar.gz -C /data .

# Restore to new volume
docker volume create myvolume-restored
docker run --rm \
    -v myvolume-restored:/data \
    -v $(pwd):/backup \
    alpine tar xzf /backup/myvolume-backup.tar.gz -C /data
```

### Method 2: Direct Copy with rsync

```bash
# Backup using rsync (preserves more metadata)
docker run --rm \
    -v myvolume:/source:ro \
    -v $(pwd)/backup:/backup \
    alpine sh -c "apk add --no-cache rsync && rsync -av /source/ /backup/"

# Restore
docker volume create myvolume-restored
docker run --rm \
    -v myvolume-restored:/target \
    -v $(pwd)/backup:/source:ro \
    alpine sh -c "apk add --no-cache rsync && rsync -av /source/ /target/"
```

### Method 3: Using Docker/Podman cp

```bash
# Create a temporary container to access the volume
docker create --name temp-backup -v myvolume:/data alpine

# Copy out
docker cp temp-backup:/data ./backup/

# Copy in (restore)
docker cp ./backup/. temp-backup:/data/

# Cleanup
docker rm temp-backup
```

---

## Automated Backup Script

Create a reusable backup script:

```bash
#!/bin/bash
# backup-volume.sh

VOLUME_NAME=$1
BACKUP_DIR=${2:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${VOLUME_NAME}_${TIMESTAMP}.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if volume exists
if ! docker volume inspect "$VOLUME_NAME" &>/dev/null; then
    echo "Error: Volume $VOLUME_NAME does not exist"
    exit 1
fi

# Create backup
echo "Backing up volume: $VOLUME_NAME"
docker run --rm \
    -v "$VOLUME_NAME":/data:ro \
    -v "$BACKUP_DIR":/backup \
    alpine tar czf "/backup/${VOLUME_NAME}_${TIMESTAMP}.tar.gz" -C /data .

if [ $? -eq 0 ]; then
    echo "Backup created: $BACKUP_FILE"
    echo "Size: $(ls -lh "$BACKUP_FILE" | awk '{print $5}')"
else
    echo "Backup failed!"
    exit 1
fi
```

```bash
# Usage
chmod +x backup-volume.sh
./backup-volume.sh pgdata ./backups
```

---

## Database Volume Backups

### PostgreSQL

```bash
# Consistent backup using pg_dump
docker exec postgres pg_dump -U postgres mydb > backup.sql

# Or backup the entire cluster
docker exec postgres pg_dumpall -U postgres > full-backup.sql

# Restore
docker exec -i postgres psql -U postgres < backup.sql
```

For volume-level backup (requires stopping writes):

```bash
# Stop the database container
docker stop postgres

# Backup the volume
docker run --rm \
    -v pgdata:/data:ro \
    -v $(pwd):/backup \
    alpine tar czf /backup/pgdata-$(date +%Y%m%d).tar.gz -C /data .

# Start the database
docker start postgres
```

### MySQL/MariaDB

```bash
# Logical backup
docker exec mysql mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --all-databases > backup.sql

# Restore
docker exec -i mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" < backup.sql
```

### MongoDB

```bash
# Backup
docker exec mongodb mongodump --out /backup

# Copy backup out
docker cp mongodb:/backup ./mongodb-backup

# Restore
docker cp ./mongodb-backup mongodb:/backup
docker exec mongodb mongorestore /backup
```

---

## Volume Copy Operations

### Copy Volume to Volume

```bash
# Create destination volume
docker volume create vol-copy

# Copy data
docker run --rm \
    -v source-vol:/source:ro \
    -v vol-copy:/dest \
    alpine sh -c "cp -av /source/. /dest/"
```

### Clone Volume with Different Name

```bash
#!/bin/bash
# clone-volume.sh

SOURCE=$1
DEST=$2

docker volume create "$DEST"
docker run --rm \
    -v "$SOURCE":/source:ro \
    -v "$DEST":/dest \
    alpine sh -c "cp -av /source/. /dest/"

echo "Cloned $SOURCE to $DEST"
```

### Sync Volumes (Incremental)

```bash
# Initial sync
docker run --rm \
    -v source:/source:ro \
    -v dest:/dest \
    instrumentisto/rsync-ssh \
    rsync -av --delete /source/ /dest/

# Subsequent syncs (only changes)
# Same command - rsync handles incremental updates
```

---

## Volume Sharing Patterns

### Read-Only Sharing

```bash
# One writer, multiple readers
docker run -d --name writer -v shared-data:/data mywriter
docker run -d --name reader1 -v shared-data:/data:ro myreader
docker run -d --name reader2 -v shared-data:/data:ro myreader
```

### Shared Config Volume

```bash
# Create config volume
docker volume create app-config

# Populate with config
docker run --rm -v app-config:/config -v $(pwd)/config:/src alpine \
    cp -r /src/. /config/

# Multiple containers use same config
docker run -d --name app1 -v app-config:/app/config:ro myapp
docker run -d --name app2 -v app-config:/app/config:ro myapp
docker run -d --name app3 -v app-config:/app/config:ro myapp
```

### Data Processing Pipeline

```bash
# Stage 1: Ingest
docker run -d --name ingest \
    -v raw-data:/output \
    ingest-image

# Stage 2: Process
docker run -d --name process \
    -v raw-data:/input:ro \
    -v processed-data:/output \
    process-image

# Stage 3: Analyze
docker run -d --name analyze \
    -v processed-data:/input:ro \
    -v results:/output \
    analyze-image
```

---

## Volume Lifecycle Management

### List and Inspect

```bash
# List all volumes
docker volume ls

# Filter volumes
docker volume ls --filter name=pg
docker volume ls --filter dangling=true

# Inspect volume
docker volume inspect myvolume

# Get specific field
docker volume inspect --format '{{.Mountpoint}}' myvolume
```

### Identify Unused Volumes

```bash
# List dangling (unused) volumes
docker volume ls -f dangling=true

# List volumes not used by any container
docker volume ls -f dangling=true -q

# Get size of unused volumes (requires checking each)
for vol in $(docker volume ls -f dangling=true -q); do
    size=$(docker run --rm -v "$vol":/data alpine du -sh /data 2>/dev/null | cut -f1)
    echo "$vol: $size"
done
```

### Cleanup Strategies

```bash
# Remove specific volume
docker volume rm myvolume

# Remove all unused volumes
docker volume prune

# Force remove without prompt
docker volume prune -f

# Remove volumes matching pattern
docker volume ls --filter name=test -q | xargs docker volume rm

# Remove volumes older than N days (requires labels or naming convention)
# Example: volumes named with timestamp
for vol in $(docker volume ls -q); do
    created=$(docker volume inspect --format '{{.CreatedAt}}' "$vol")
    # Add date comparison logic here
done
```

---

## Volume Labels and Metadata

### Creating Labeled Volumes

```bash
# Create volume with labels
docker volume create \
    --label project=myapp \
    --label environment=production \
    --label backup=daily \
    myapp-data

# Filter by label
docker volume ls --filter label=project=myapp
docker volume ls --filter label=backup=daily
```

### Label-Based Backup Script

```bash
#!/bin/bash
# backup-labeled-volumes.sh

BACKUP_LABEL="backup=daily"
BACKUP_DIR="./backups/$(date +%Y%m%d)"

mkdir -p "$BACKUP_DIR"

for volume in $(docker volume ls --filter label=$BACKUP_LABEL -q); do
    echo "Backing up: $volume"
    docker run --rm \
        -v "$volume":/data:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/${volume}.tar.gz" -C /data .
done

echo "Backups saved to: $BACKUP_DIR"
```

---

## Volume Drivers

### Local Driver Options

```bash
# Create volume with specific options
docker volume create \
    --driver local \
    --opt type=tmpfs \
    --opt device=tmpfs \
    --opt o=size=100m \
    tmpfs-vol

# NFS volume
docker volume create \
    --driver local \
    --opt type=nfs \
    --opt o=addr=192.168.1.100,rw \
    --opt device=:/path/on/nfs \
    nfs-vol

# Bind mount style volume
docker volume create \
    --driver local \
    --opt type=none \
    --opt device=/mnt/data/myapp \
    --opt o=bind \
    bind-vol
```

### Third-Party Volume Drivers

| Driver | Use Case |
|--------|----------|
| **Portworx** | Multi-cloud persistent storage |
| **REX-Ray** | Dell EMC storage |
| **Azure File** | Azure cloud storage |
| **convoy** | Snapshot and backup |
| **flocker** | Multi-host volumes |

---

## Monitoring Volume Usage

### Disk Usage Report

```bash
#!/bin/bash
# volume-usage-report.sh

echo "Docker Volume Usage Report"
echo "=========================="
echo ""

total_size=0
for volume in $(docker volume ls -q); do
    size=$(docker run --rm -v "$volume":/data alpine du -sb /data 2>/dev/null | cut -f1)
    size_human=$(docker run --rm -v "$volume":/data alpine du -sh /data 2>/dev/null | cut -f1)

    if [ -n "$size" ]; then
        total_size=$((total_size + size))
        echo "$volume: $size_human"
    fi
done

echo ""
echo "Total: $(numfmt --to=iec-i $total_size)"
```

### Prometheus Metrics (Advanced)

```bash
# Use docker_volume_exporter or similar
# Exposes metrics like:
# docker_volume_size_bytes{name="myvolume"} 1234567890
```

---

## Key Takeaways

1. **Backup volumes regularly** using tar or rsync methods
2. **Use database-specific tools** for consistent DB backups
3. **Label volumes** for organization and automated management
4. **Clean up unused volumes** to reclaim disk space
5. **Share volumes read-only** when write access isn't needed
6. **Monitor volume usage** to prevent disk full issues

---

## What's Next

Learn about storage drivers and how to optimize container I/O performance.

Continue to: [04-storage-drivers.md](04-storage-drivers.md)

---

## Quick Quiz

1. What is the safest way to backup a database volume?
   - [ ] Copy the volume directory directly
   - [x] Use database-specific tools like pg_dump
   - [ ] Snapshot the entire disk
   - [ ] Export the container

2. How do you mount a volume as read-only?
   - [ ] `-v myvolume:/data --readonly`
   - [x] `-v myvolume:/data:ro`
   - [ ] `-v myvolume:/data:r`
   - [ ] `--volume-readonly myvolume:/data`

3. What command removes all unused volumes?
   - [ ] `docker volume clean`
   - [ ] `docker volume rm --all`
   - [x] `docker volume prune`
   - [ ] `docker volume delete unused`

4. How can you identify volumes not attached to any container?
   - [ ] `docker volume ls --unused`
   - [x] `docker volume ls -f dangling=true`
   - [ ] `docker volume ls --orphan`
   - [ ] `docker volume inspect --no-container`

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Custom Storage Locations](02-custom-storage-locations.md) | [Course Overview](../course_overview.md) | [Networking Fundamentals](../networking/01-networking-fundamentals.md) |
