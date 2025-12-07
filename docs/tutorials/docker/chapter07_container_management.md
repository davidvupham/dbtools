# Chapter 7: Container Management

Containers are the running instances of your images. This chapter covers how to monitor, interact with, and manage their lifecycle.

## Listing Containers

```bash
# List running containers
docker ps

# List ALL containers (including stopped)
docker ps -a

# Show only container IDs
docker ps -q

# Filter by status
docker ps -f "status=exited"

# Custom output format
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## Viewing Logs

Logs are your primary debugging tool.

```bash
# View all logs from a container
docker logs my-container

# Follow logs in real-time (like tail -f)
docker logs -f my-container

# Show timestamps
docker logs -t my-container

# Show only the last 100 lines
docker logs --tail 100 my-container

# Combine: follow last 50 lines with timestamps
docker logs -f --tail 50 -t my-container
```

---

## Executing Commands Inside Containers

Use `docker exec` to run commands in a **running** container.

```bash
# Open an interactive shell
docker exec -it my-container sh

# Run a single command
docker exec my-container cat /etc/hostname

# Run as a different user
docker exec -u root my-container whoami

# Set environment variables for the command
docker exec -e MY_VAR=hello my-container printenv MY_VAR
```

> [!NOTE]
> `docker exec` only works on **running** containers. Use `docker start` first if the container is stopped.

---

## Inspecting Containers

Get detailed information about a container's configuration and state.

```bash
# Full JSON output
docker inspect my-container

# Get IP address
docker inspect my-container --format '{{.NetworkSettings.IPAddress}}'

# Get environment variables
docker inspect my-container --format '{{json .Config.Env}}' | jq .

# Get mounted volumes
docker inspect my-container --format '{{json .Mounts}}' | jq .
```

---

## Resource Monitoring

### Real-Time Stats

```bash
# Stream resource usage for all containers
docker stats

# Stats for specific containers
docker stats web db cache

# Single snapshot (no streaming)
docker stats --no-stream
```

**Output columns:**

- **CPU %**: CPU usage
- **MEM USAGE / LIMIT**: Current memory / allowed limit
- **NET I/O**: Network traffic in/out
- **BLOCK I/O**: Disk read/write

### View Processes Inside Container

```bash
docker top my-container
```

---

## Health Checks

Health checks tell Docker whether your application inside the container is working.

### Define in Dockerfile

```dockerfile
FROM nginx:alpine
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

### Check Health Status

```bash
docker ps
# Look at the STATUS column: "Up 5 minutes (healthy)"

docker inspect my-container --format '{{.State.Health.Status}}'
# Output: healthy, unhealthy, or starting
```

---

## Restart Policies

Control what happens when a container stops.

```bash
# Never restart (default)
docker run --restart=no myapp

# Always restart (even after host reboot)
docker run --restart=always myapp

# Restart only on failure (non-zero exit code)
docker run --restart=on-failure myapp

# Restart on failure, max 5 attempts
docker run --restart=on-failure:5 myapp

# Restart unless explicitly stopped
docker run --restart=unless-stopped myapp
```

| Policy | Use Case |
| :--- | :--- |
| `no` | Development, testing |
| `always` | Production services |
| `on-failure` | Services with potential startup issues |
| `unless-stopped` | Services that should survive reboot but respect manual stops |

---

## Copying Files To/From Containers

```bash
# Copy from host to container
docker cp myfile.txt my-container:/app/

# Copy from container to host
docker cp my-container:/app/config.yml ./backup/

# Copy entire directory
docker cp my-container:/var/log ./container-logs/
```

---

## Stopping and Removing Containers

```bash
# Graceful stop (sends SIGTERM, waits, then SIGKILL)
docker stop my-container

# Force stop immediately (SIGKILL)
docker kill my-container

# Remove a stopped container
docker rm my-container

# Force remove a running container
docker rm -f my-container

# Remove all stopped containers
docker container prune
```

---

## Summary

| Task | Command |
| :--- | :--- |
| List running | `docker ps` |
| List all | `docker ps -a` |
| View logs | `docker logs -f <container>` |
| Run command inside | `docker exec -it <container> sh` |
| Get details | `docker inspect <container>` |
| Monitor resources | `docker stats` |
| View processes | `docker top <container>` |
| Copy files | `docker cp src dest` |
| Stop | `docker stop <container>` |
| Remove | `docker rm <container>` |

**Next Chapter:** Learn how to persist data with **Chapter 9: Persistence with Volumes and Mounts**.
