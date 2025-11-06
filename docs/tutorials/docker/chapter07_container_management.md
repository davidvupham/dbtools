# Chapter 7: Container Management

- Logs and exec:

```bash
docker logs -f <name>
docker exec -it <name> sh
```

- Inspect, stats, health:

```bash
docker inspect <name>
docker stats
```

- Restart policies:

```bash
docker run --restart=on-failure:3 myimage:tag
```

---

## Health checks

Define a health check in your Dockerfile or at run-time so orchestrators/Compose can react to failures.

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
```

Check health:
```bash
docker inspect --format '{{.State.Health.Status}}' <name>
```

## Resource limits

Constrain CPU and memory to protect the host and shape performance.

```bash
docker run -d --name svc \
  --cpus=2 \
  --memory=2g --memory-reservation=1g \
  myorg/app:latest
```

## Cleanup helpers

```bash
docker ps -a
docker stop <name> && docker rm <name>
docker container prune    # remove stopped containers
```
