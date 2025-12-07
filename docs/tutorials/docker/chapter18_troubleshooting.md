# Chapter 18: Troubleshooting & Debugging

When containers misbehave, here's how to diagnose and fix common issues.

## Debugging Tools Overview

| Tool | Purpose |
| :--- | :--- |
| `docker logs` | View container output |
| `docker exec` | Run commands inside container |
| `docker inspect` | Get container/image metadata |
| `docker stats` | Monitor resource usage |
| `docker events` | Watch Docker daemon events |
| `docker system df` | Check disk usage |

---

## Problem: Container Exits Immediately

### Symptoms

```bash
docker run myapp
# Container exits with no output

docker ps -a
# STATUS: Exited (1) 5 seconds ago
```

### Diagnosis

```bash
# Check exit code
docker inspect myapp --format '{{.State.ExitCode}}'

# View logs
docker logs myapp

# Run interactively to see what happens
docker run -it myapp sh
```

### Common Causes

1. **Missing command**: No `CMD` or `ENTRYPOINT` in Dockerfile
2. **Application crash**: App throws error on startup
3. **Missing dependencies**: File or library not found
4. **Permission denied**: Can't read/write required files

---

## Problem: "Port Already in Use"

### Symptom

```
Error: Bind for 0.0.0.0:8080 failed: port is already allocated
```

### Solution

```bash
# Find what's using the port
sudo lsof -i :8080
# or
sudo netstat -tlnp | grep 8080

# Kill the process or use a different port
docker run -p 8081:80 myapp
```

---

## Problem: Container Can't Reach Internet

### Diagnosis

```bash
# Test from inside container
docker exec myapp ping google.com
docker exec myapp curl -I https://google.com

# Check DNS
docker exec myapp cat /etc/resolv.conf
```

### Common Causes

1. **Firewall blocking**: Check host firewall rules
2. **DNS issues**: Try `--dns 8.8.8.8`
3. **Network mode**: `--network none` disables networking

### Solution

```bash
# Specify DNS
docker run --dns 8.8.8.8 myapp

# Check Docker's default bridge
docker network inspect bridge
```

---

## Problem: Container Can't Connect to Another Container

### Diagnosis

```bash
# Check both containers are on the same network
docker inspect web --format '{{.NetworkSettings.Networks}}'
docker inspect db --format '{{.NetworkSettings.Networks}}'
```

### Solution

Use a user-defined network:

```bash
docker network create app-net
docker run -d --name db --network app-net postgres
docker run -d --name web --network app-net myapp

# Now web can reach db at hostname "db"
docker exec web ping db
```

---

## Problem: "No Space Left on Device"

### Diagnosis

```bash
# Check Docker disk usage
docker system df

# Detailed breakdown
docker system df -v
```

### Solution

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes (CAREFUL: data loss!)
docker volume prune

# Nuclear option: remove everything unused
docker system prune -a --volumes
```

---

## Problem: Container Is Slow

### Diagnosis

```bash
# Check resource usage
docker stats myapp

# Check if hitting limits
docker inspect myapp --format '{{.HostConfig.Memory}}'
```

### Common Causes

1. **CPU/Memory limits too low**: Increase limits
2. **Slow volume mounts** (especially on Mac): Use named volumes
3. **Application issue**: Profile the app itself

### Solution

```bash
# Increase resources
docker run --memory 2g --cpus 2 myapp
```

---

## Problem: Build Fails

### Common Errors

#### "COPY failed: file not found"

```dockerfile
COPY myfile.txt /app/  # File not in build context
```

**Solution**: Ensure file exists and isn't in `.dockerignore`.

#### "RUN command failed"

```bash
# View build output
docker build --progress=plain .

# Build without cache to see full output
docker build --no-cache .
```

#### "Could not resolve 'archive.ubuntu.com'"

DNS issue during build. Solution:

```bash
docker build --network host .
```

---

## Useful Debug Commands

### View Everything About a Container

```bash
docker inspect myapp | jq .
```

### Follow All Container Events

```bash
docker events
```

### Get Container IP Address

```bash
docker inspect myapp --format '{{.NetworkSettings.IPAddress}}'
```

### Check If App Is Responding

```bash
docker exec myapp curl -s localhost:8080/health
```

### View Container Filesystem

```bash
# Create a temporary container to browse an image
docker run -it --rm myapp sh

# Export filesystem to tar
docker export myapp > container.tar
```

### Debug a Crashing Container

```bash
# Override the entrypoint to get a shell
docker run -it --entrypoint sh myapp
```

---

## Logging Best Practices

### View Logs with Context

```bash
# Last 100 lines with timestamps
docker logs --tail 100 -t myapp

# Logs from the last hour
docker logs --since 1h myapp

# Follow logs in real-time
docker logs -f myapp
```

### Redirect Logs to Files

```bash
docker logs myapp > container.log 2>&1
```

### Configure Log Rotation (daemon.json)

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## Summary Checklist

When things go wrong:

1. [ ] Check container status: `docker ps -a`
2. [ ] Check logs: `docker logs <container>`
3. [ ] Check exit code: `docker inspect --format '{{.State.ExitCode}}'`
4. [ ] Check resources: `docker stats`
5. [ ] Check network: `docker network inspect`
6. [ ] Check disk: `docker system df`
7. [ ] Get a shell: `docker exec -it <container> sh`

**Next Chapter:** Explore the Docker ecosystem in **Chapter 19: Ecosystem Tools**.
