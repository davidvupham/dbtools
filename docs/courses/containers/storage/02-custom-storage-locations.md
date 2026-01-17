# Configuring Custom Storage Locations

> **Module:** Storage Deep Dive | **Level:** Intermediate | **Time:** 35 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Configure Docker to store images in a custom directory
- Configure Podman to use different storage paths
- Move existing data to a new location
- Set up storage on mounted drives or partitions
- Configure per-user storage in rootless mode

---

## Why Change Storage Location?

Common reasons to customize storage location:

| Reason | Solution |
|--------|----------|
| **Root disk full** | Move to larger partition |
| **SSD vs HDD** | Put active data on SSD |
| **Separate mount point** | Use dedicated storage |
| **Network storage** | Use NFS/shared storage |
| **Rootless user directory** | Custom user paths |

---

## Docker: Changing the Data Root

### Method 1: daemon.json Configuration

```bash
# 1. Stop Docker
sudo systemctl stop docker
sudo systemctl stop docker.socket

# 2. Create new directory
sudo mkdir -p /mnt/docker-data
sudo chown root:root /mnt/docker-data

# 3. Edit or create daemon.json
sudo nano /etc/docker/daemon.json
```

```json
{
  "data-root": "/mnt/docker-data"
}
```

```bash
# 4. (Optional) Move existing data
sudo rsync -aP /var/lib/docker/ /mnt/docker-data/

# 5. Start Docker
sudo systemctl start docker

# 6. Verify
docker info | grep "Docker Root Dir"
# Docker Root Dir: /mnt/docker-data
```

### Method 2: Symbolic Link

```bash
# 1. Stop Docker
sudo systemctl stop docker
sudo systemctl stop docker.socket

# 2. Move existing data
sudo mv /var/lib/docker /mnt/docker-data

# 3. Create symlink
sudo ln -s /mnt/docker-data /var/lib/docker

# 4. Start Docker
sudo systemctl start docker

# 5. Verify
ls -la /var/lib/docker
# /var/lib/docker -> /mnt/docker-data
```

### Example: Using a Mounted Drive

```bash
# 1. Identify the drive
lsblk
# NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
# sdb      8:16   0  500G  0 disk

# 2. Create filesystem (if new drive)
sudo mkfs.ext4 /dev/sdb

# 3. Create mount point
sudo mkdir -p /mnt/docker-storage

# 4. Mount the drive
sudo mount /dev/sdb /mnt/docker-storage

# 5. Add to fstab for persistence
echo '/dev/sdb /mnt/docker-storage ext4 defaults 0 2' | sudo tee -a /etc/fstab

# 6. Create Docker directory
sudo mkdir -p /mnt/docker-storage/docker
sudo chown root:root /mnt/docker-storage/docker

# 7. Configure Docker
sudo nano /etc/docker/daemon.json
```

```json
{
  "data-root": "/mnt/docker-storage/docker"
}
```

```bash
# 8. Restart Docker
sudo systemctl restart docker

# 9. Verify
df -h /mnt/docker-storage
docker info | grep "Docker Root Dir"
```

---

## Podman: Changing Storage Location

### Rootful Podman

```bash
# 1. Stop any running containers
sudo podman stop --all

# 2. Edit storage configuration
sudo nano /etc/containers/storage.conf
```

```toml
[storage]
driver = "overlay"
runroot = "/run/containers/storage"
graphroot = "/mnt/podman-storage"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
```

```bash
# 3. Create the directory
sudo mkdir -p /mnt/podman-storage
sudo chown root:root /mnt/podman-storage

# 4. Reset storage (WARNING: removes existing data!)
sudo podman system reset

# 5. Verify
sudo podman info | grep graphRoot
# graphRoot: /mnt/podman-storage
```

### Rootless Podman

Each user can have their own storage configuration:

```bash
# 1. Create user config directory
mkdir -p ~/.config/containers

# 2. Create storage.conf
nano ~/.config/containers/storage.conf
```

```toml
[storage]
driver = "overlay"
runroot = "/run/user/1000/containers"
graphroot = "/home/username/containers-storage"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
```

```bash
# 3. Create the directory
mkdir -p ~/containers-storage

# 4. Reset storage
podman system reset

# 5. Verify
podman info | grep graphRoot
# graphRoot: /home/username/containers-storage
```

### Using External Drive for Rootless Podman

```bash
# 1. Mount drive with user permissions
sudo mount /dev/sdb /mnt/external -o uid=$(id -u),gid=$(id -g)

# 2. Or use fstab with user mount option
echo '/dev/sdb /mnt/external ext4 defaults,uid=1000,gid=1000 0 2' | sudo tee -a /etc/fstab

# 3. Create user storage config
cat > ~/.config/containers/storage.conf << 'EOF'
[storage]
driver = "overlay"
graphroot = "/mnt/external/podman"

[storage.options]
mount_program = "/usr/bin/fuse-overlayfs"
EOF

# 4. Create directory and reset
mkdir -p /mnt/external/podman
podman system reset
```

---

## Migrating Existing Data

### Docker Migration

```bash
# 1. Stop Docker completely
sudo systemctl stop docker
sudo systemctl stop docker.socket

# 2. Verify no Docker processes
ps aux | grep docker

# 3. Copy data to new location
sudo rsync -aP --info=progress2 /var/lib/docker/ /mnt/new-location/docker/

# 4. Update configuration
sudo nano /etc/docker/daemon.json
# Add: "data-root": "/mnt/new-location/docker"

# 5. Start Docker
sudo systemctl start docker

# 6. Verify everything works
docker images
docker ps -a
docker volume ls

# 7. (Optional) Remove old data after verification
sudo rm -rf /var/lib/docker
```

### Podman Migration

```bash
# 1. Export important containers (optional)
podman save -o images-backup.tar $(podman images -q)

# 2. Note volume locations
podman volume ls
podman volume inspect --all

# 3. Stop all containers
podman stop --all

# 4. Copy storage
sudo rsync -aP ~/.local/share/containers/storage/ /mnt/new-location/

# 5. Update storage.conf
nano ~/.config/containers/storage.conf
# Update graphroot to new location

# 6. Reset and verify
podman system reset
podman load -i images-backup.tar  # If you exported
```

---

## Volume-Specific Storage

### Docker: Custom Volume Location

```bash
# Create volume with specific driver options
docker volume create --driver local \
    --opt type=none \
    --opt device=/mnt/data/myvolume \
    --opt o=bind \
    myvolume

# Use the volume
docker run -v myvolume:/data myimage
```

### Docker: NFS Volume

```bash
# Create NFS-backed volume
docker volume create --driver local \
    --opt type=nfs \
    --opt o=addr=192.168.1.100,rw \
    --opt device=:/path/to/share \
    nfs-volume
```

### Podman: Volume Configuration

```bash
# Create volume in specific location
podman volume create --opt device=/mnt/data/myvolume \
    --opt type=none \
    --opt o=bind \
    myvolume

# Inspect volume
podman volume inspect myvolume
```

---

## Docker Desktop: Changing Disk Location

### macOS

1. Open Docker Desktop
2. Go to Preferences (gear icon)
3. Resources → Advanced
4. Change "Disk image location"
5. Apply and restart

Or via settings file:
```bash
# ~/Library/Group Containers/group.com.docker/settings.json
{
  "diskPath": "/path/to/docker.raw"
}
```

### Windows

1. Open Docker Desktop
2. Go to Settings (gear icon)
3. Resources → Advanced
4. Change "Disk image location"
5. Apply and restart

Default location: `%LOCALAPPDATA%\Docker\wsl`

---

## Podman Desktop: Storage Configuration

For Podman on macOS/Windows (using Podman machine):

```bash
# View current machine config
podman machine inspect

# Create machine with custom disk size
podman machine init --disk-size 100 --memory 4096

# The virtual disk is stored in:
# macOS: ~/.local/share/containers/podman/machine/
# Windows: %APPDATA%\containers\podman\machine\
```

---

## Verification and Testing

### Verify Storage Location

```bash
# Docker
docker info | grep -E "(Root Dir|Storage Driver)"
ls -la /path/to/docker-data

# Podman
podman info | grep -E "(graphRoot|GraphDriverName)"
ls -la /path/to/podman-data
```

### Test Write Performance

```bash
# Docker
docker run --rm -v testvolume:/data alpine sh -c \
    "dd if=/dev/zero of=/data/testfile bs=1M count=100 && rm /data/testfile"

# Compare different locations
time docker run --rm -v fastvolume:/data alpine sh -c \
    "dd if=/dev/zero of=/data/test bs=1M count=500"
```

### Check Disk Usage

```bash
# Overall usage
docker system df
podman system df

# Specific directory
du -sh /mnt/docker-data/*
du -sh ~/.local/share/containers/*
```

---

## Troubleshooting

### Permission Denied

```bash
# Docker: Check ownership
ls -la /mnt/docker-data
# Should be root:root

# Podman rootless: Check user ownership
ls -la ~/containers-storage
# Should be your user

# Fix permissions
sudo chown -R root:root /mnt/docker-data          # Docker
chown -R $(id -u):$(id -g) ~/containers-storage   # Podman rootless
```

### SELinux Issues

```bash
# If using SELinux, set proper context
sudo semanage fcontext -a -t container_var_lib_t "/mnt/docker-data(/.*)?"
sudo restorecon -Rv /mnt/docker-data
```

### Storage Not Changing

```bash
# Ensure Docker/Podman is fully stopped
sudo systemctl stop docker docker.socket
pgrep -a docker  # Should return nothing

# Verify config file syntax
cat /etc/docker/daemon.json | python3 -m json.tool

# Check for typos in path
ls -la /mnt/docker-data  # Verify directory exists
```

---

## Key Takeaways

1. **Docker uses `data-root`** in daemon.json to configure storage location
2. **Podman uses `graphroot`** in storage.conf
3. **Always stop the service** before migrating data
4. **Use rsync with -a flag** to preserve permissions during migration
5. **Verify after migration** that all images and volumes are accessible
6. **Consider performance** when choosing storage location (SSD vs HDD)
7. **Rootless storage** is per-user and separately configurable

---

## What's Next

Learn about advanced volume operations including backup and restore strategies.

Continue to: [03-volume-operations.md](03-volume-operations.md)

---

## Quick Quiz

1. Which Docker configuration option changes the storage location?
   - [ ] `storage-path`
   - [ ] `root-directory`
   - [x] `data-root`
   - [ ] `image-location`

2. What must you do before moving Docker data to a new location?
   - [ ] Delete all containers
   - [x] Stop Docker completely
   - [ ] Create a backup
   - [ ] Update the kernel

3. What is the correct Podman configuration option for storage location?
   - [ ] `data-root`
   - [ ] `storage-path`
   - [x] `graphroot`
   - [ ] `containerdir`

4. Which tool is recommended for copying Docker data to preserve permissions?
   - [ ] cp
   - [ ] mv
   - [x] rsync with -a flag
   - [ ] tar
