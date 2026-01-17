# Chapter 10: Advanced Data & Storage

This chapter covers advanced storage concepts: tmpfs mounts, storage drivers, and performance considerations.

## tmpfs Mounts (In-Memory Storage)

`tmpfs` mounts store data **in memory**. Data is never written to disk and disappears when the container stops.

### When to Use tmpfs

- Sensitive data (secrets, tokens) that shouldn't persist
- High-speed scratch space for temporary files
- Data that should never survive a restart

### Usage

```bash
docker run -d \
  --name app \
  --tmpfs /tmp:rw,size=100m,mode=1777 \
  myapp
```

**Options:**

- `size=100m`: Limit to 100MB
- `mode=1777`: Set permissions (sticky bit for `/tmp`)
- `rw`: Read-write (default)

### In Docker Compose

```yaml
services:
  app:
    image: myapp
    tmpfs:
      - /tmp:size=100m,mode=1777
```

---

## Storage Drivers

Docker uses **storage drivers** to manage how image layers and container filesystems are stored on disk.

### Common Storage Drivers

| Driver | Description | Best For |
| :--- | :--- | :--- |
| **overlay2** | Default on modern Linux | Most use cases |
| **btrfs** | Copy-on-write filesystem | Btrfs-based hosts |
| **zfs** | ZFS integration | ZFS-based hosts |
| **devicemapper** | Legacy, block-level | Older RHEL/CentOS |

### Check Your Storage Driver

```bash
docker info | grep "Storage Driver"
# Output: Storage Driver: overlay2
```

> [!NOTE]
> For most users, `overlay2` (the default) is the best choice. Only change this if you have specific requirements.

---

## Performance Considerations

### 1. Avoid Writing to the Container Layer

Writes to the container's filesystem (not a volume) go through the storage driver, which is slower.

**❌ Bad:**

```dockerfile
RUN echo "data" > /app/cache.txt  # Writes to container layer
```

**✅ Good:**

```bash
docker run -v cache:/app/cache myapp  # Writes to volume
```

### 2. Use Named Volumes for I/O-Heavy Workloads

Named volumes bypass the storage driver and write directly to the host filesystem.

```bash
# Fast: Direct I/O to volume
docker run -v db-data:/var/lib/mysql mysql

# Slow: I/O goes through overlay2
docker run mysql  # Data stored in container layer
```

### 3. Consider Volume Drivers for Cloud Storage

For production, you can use volume drivers to store data on cloud storage or network filesystems.

```bash
# Example: Create a volume backed by a driver
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/dir \
  nfs-volume
```

---

## Choosing the Right Storage Type

| Scenario | Recommendation |
| :--- | :--- |
| Database files | Named volume |
| Application logs (centralized) | Bind mount or logging driver |
| Temporary build artifacts | tmpfs |
| Secrets at runtime | tmpfs or Docker secrets |
| Development source code | Bind mount |
| Config files | Bind mount (read-only) |

---

## Docker Context and Remote Storage

When working with remote Docker hosts (Docker Context), volumes are created on the remote machine, not locally.

```bash
# Check current context
docker context ls

# Switch context
docker context use remote-server

# Volumes now create on remote-server
docker volume create mydata
```

---

## Summary

| Storage Type | Persistence | Speed | Use Case |
| :--- | :--- | :--- | :--- |
| Container layer | Container lifetime | Slow | Avoid for data |
| Named volume | Beyond container | Fast | Databases, uploads |
| Bind mount | Host filesystem | Fast | Development, configs |
| tmpfs | Container lifetime (memory) | Very Fast | Secrets, temp files |

**Next Chapter:** Learn how to connect multiple services with **Chapter 12: Advanced Compose**.
