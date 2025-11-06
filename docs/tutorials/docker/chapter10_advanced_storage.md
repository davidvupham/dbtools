# Chapter 10: Advanced Data & Storage

- Drivers and platforms (local, NFS, cloud drivers)
- tmpfs for ephemeral data
- Strategies for migrations and backups

```bash
# tmpfs example
docker run --rm --read-only --tmpfs /tmp:size=64m myimage:tag
```

---

## Storage drivers overview (high level)

- overlay2 (Linux default): copy-on-write performance, recommended.
- btrfs/zfs: snapshotting features; niche setups.
- windowsfilter: Windows containers.

Tip: You rarely need to change the storage driver; prefer the OS default (overlay2 on modern Linux).

## tmpfs and read-only filesystems

Use a read-only root with tmpfs mounts for writable paths.

```bash
docker run --read-only --tmpfs /tmp:rw,size=64m myorg/app
```

## Data migration and backups

Prefer database-native tooling for consistency. For generic data volumes, see Chapter 9 for tar‑based backup/restore patterns.

```bash
# PostgreSQL logical backup (example)
docker exec -t db pg_dump -U postgres mydb | gzip > mydb_$(date +%F).sql.gz

# Restore
gunzip -c mydb_2025-01-01.sql.gz | docker exec -i db psql -U postgres mydb
```

## Remote and cloud-backed volumes

Use volume plugins/drivers to mount NFS/EFS or cloud volumes when needed; evaluate throughput/latency and failure modes. Keep network partitions in mind.
