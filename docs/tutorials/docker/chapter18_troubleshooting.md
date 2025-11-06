# Chapter 18: Troubleshooting & Debugging

- Logs/events/stats: `docker logs -f`, `docker events`, `docker stats`
- Exec into containers: `docker exec -it <name> sh`
- Inspect everything: `docker inspect <name-or-id>`
- Port issues: verify `-p host:container` and app binds to `0.0.0.0`
- Mount issues: check user IDs, SELinux/AppArmor labels

Cleanup helpers:

```bash
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker image prune -f
```

---

## Common issues and quick fixes

### Cannot connect to the Docker daemon
```bash
# Linux
sudo systemctl status docker
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker "$USER"
newgrp docker

# macOS/Windows: ensure Docker Desktop is running
```

### Permission denied on bind mounts (Linux)
- Ensure the host path exists and has correct ownership.
- Align container user with host UID/GID or `chown` the directory.

### Port already in use
```bash
docker ps --filter 'publish=8080'
sudo lsof -i :8080 || sudo ss -lntp | grep 8080
```

### Container exits immediately
```bash
docker logs <container>
docker inspect <container> --format '{{.State.ExitCode}}'
docker run -it --entrypoint sh <image>    # start a shell to debug
```

### DNS/Networking issues
```bash
docker network ls
docker network inspect <net>
docker run --rm --network <net> nicolaka/netshoot dig google.com
```

### OOMKilled / Out of memory
- Check: `docker inspect <container> | jq .[].State.OOMKilled`
- Set `--memory` limits or reduce app memory usage.

### WSL2 (Windows) tips
- Enable WSL integration in Docker Desktop (Settings → Resources → WSL Integration).
- Restart WSL: `wsl --shutdown`, then restart Docker Desktop.
- Prefer Linux paths inside WSL (e.g., `/home/you/project`) for faster I/O.

---

## Diagnostics toolbox

```bash
# Logs and events
docker logs -f <name>
docker events --since 10m

# Resource usage
docker stats
docker inspect <name> | jq '.[0].HostConfig.Resources'

# Network checks
docker port <name>
docker exec <name> sh -c 'ip a; ip route; getent hosts peer'

# Disk space and cleanup
docker system df
docker system prune
```
