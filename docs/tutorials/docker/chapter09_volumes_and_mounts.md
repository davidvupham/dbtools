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
