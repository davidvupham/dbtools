# Chapter 3: CLI Essentials and First Run

Key commands:

```bash
# Images
docker pull alpine:3.19
docker images

# Containers
docker run --rm -it alpine:3.19 sh
docker ps -a

# Ports
docker run --rm -d --name web -p 8080:80 nginx:alpine
curl -I http://localhost:8080

# Stop/remove
docker stop web && docker rm web 2>/dev/null || true
```

Tips:
- `--rm` cleans up after exit.
- Use `--name` to reference containers easily.
- `docker logs -f <name>` to tail.
