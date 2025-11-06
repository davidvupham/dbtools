# Chapter 9: Persistence with Volumes and Mounts

- Named volumes for lifecycle‑managed data.
- Bind mounts to map host folders into containers.

```bash
# Named volume
docker volume create mydata
docker run -d --name pg -v mydata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:16-alpine

# Bind mount current dir
docker run --rm -it -v "$PWD":/work -w /work alpine:3.19 ls -la
```

Backups:
- Use `docker run --rm -v vol:/data -v "$PWD":/backup alpine tar czf /backup/vol_backup.tgz -C /data .`

---

## Choosing between bind mounts and named volumes

- Bind mounts:
  - Pros: Great for local development (live code reload), uses an exact host path
  - Cons: OS-dependent semantics; slower on macOS/WSL2; permission mismatches
- Named volumes:
  - Pros: Managed by Docker; portable; fast on macOS/WSL2; safer for databases
  - Cons: Not directly browsable on host without helper containers

```bash
# Bind mount (host → container)
docker run -d --name web -p 8080:80 \
  -v $(pwd)/site:/usr/share/nginx/html:ro \
  nginx:alpine

# Named volume for Postgres data
docker volume create pgdata
docker run -d --name db \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine

# Inspect volumes
docker volume ls
docker volume inspect pgdata
```

## Backup and restore patterns

```bash
# Backup a named volume to a tarball in the current directory
docker run --rm \
  -v pgdata:/data:ro \
  -v $(pwd):/backup \
  busybox sh -c 'tar czf /backup/pgdata-backup.tgz -C /data .'

# Restore into a new volume
docker volume create pgdata_restored
docker run --rm \
  -v pgdata_restored:/data \
  -v $(pwd):/backup:ro \
  busybox sh -c 'cd /data && tar xzf /backup/pgdata-backup.tgz'
```

Tips:
- Prefer consistent tagging/versioned backups (include date/hash in filename).
- Quiesce apps or use database-native backup tooling for consistency.

## Permissions and ownership

- For bind mounts on Linux, align container user with host UID/GID or set proper ownership on the host path (`chown`).
- Avoid running containers as root just to “fix” permissions—use `USER` and proper ownership instead.
- For macOS/WSL2, prefer named volumes for databases and high I/O workloads.

## Performance notes

- macOS/WSL2: bind mounts cross a VM boundary and can be slow; named volumes perform better.
- Linux: bind mounts are generally fast; still consider named volumes for data integrity and portability.

## Cleaning up and auditing data usage

```bash
docker system df                # High-level disk usage
docker volume ls                # List volumes
docker volume inspect <name>    # Inspect a specific volume
docker volume rm <name>         # Remove (must not be in use)
docker volume prune             # Remove all unused volumes
```
