# Chapter 17: Security Hardening

Security is critical for production containers. This chapter provides a comprehensive guide to securing your Docker workloads.

## 1. Run as Non-Root User

By default, containers run as `root`. This is dangerous if an attacker escapes the container.

### In Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Change ownership
COPY --chown=appuser:appgroup . .

# Switch to non-root
USER appuser

EXPOSE 8080
CMD ["node", "server.js"]
```

### At Runtime

```bash
docker run --user 1000:1000 myapp
```

> [!WARNING]
> Non-root users cannot bind to ports below 1024 (like 80 or 443). Use high ports (8080, 3000) or a reverse proxy.

---

## 2. Advanced: User Namespace Remapping (`userns-remap`)

While running as a non-root user in the Dockerfile is best practice, you can adds an extra layer of security by configuring the Docker Daemon to use **User Namespaces**.

This maps the `root` user *inside* the container to a non-privileged user *outside* the container. Even if an attacker breaks out of the container as root, they are a nobody on the host.

### Enable Remapping

Edit `/etc/docker/daemon.json`:

```json
{
  "userns-remap": "default"
}
```

Restart Docker. It will create a user `dockremap` and map container IDs to high-range host IDs (e.g., container UID 0 maps to host UID 165536).

> [!NOTE]
> This applies to **all** containers on the daemon and can complicate volume permissions (files created by containers will be owned by high UIDs on the host).

---

## 3. Use Read-Only Filesystems

Prevent malicious writes by making the container filesystem read-only.

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /var/run \
  myapp
```

In Compose:

```yaml
services:
  web:
    image: myapp
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
```

---

## 4. Drop Capabilities

Linux capabilities grant fine-grained root-like powers. Drop all and add back only what you need.

```bash
docker run -d \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  myapp
```

### Common Capabilities

| Capability | Description |
| :--- | :--- |
| `NET_BIND_SERVICE` | Bind to ports < 1024 |
| `CHOWN` | Change file ownership |
| `SETUID` / `SETGID` | Change user/group IDs |
| `SYS_ADMIN` | **Dangerous:** broad admin access |

> [!CAUTION]
> Never run with `--privileged` in production. It grants ALL capabilities.

---

## 5. Prevent Privilege Escalation

Block processes from gaining additional privileges:

```bash
docker run -d \
  --security-opt no-new-privileges \
  myapp
```

This prevents setuid binaries and other privilege escalation techniques.

---

## 6. Secrets Management

**Never bake secrets into images.** They end up in layers and are visible with `docker history`.

### Bad ❌

```dockerfile
ENV API_KEY=supersecret  # Visible in image history!
```

### Good ✅ (Runtime Mount)

```bash
docker run -d \
  -v ./secrets:/run/secrets:ro \
  myapp

# In your app, read from /run/secrets/api_key
```

### Good ✅ (Docker Secrets with Swarm/Compose)

```yaml
services:
  web:
    image: myapp
    secrets:
      - api_key

secrets:
  api_key:
    file: ./secrets/api_key.txt
```

---

## 7. Use Minimal Base Images

Fewer packages = smaller attack surface.

| Base Image | Size | Shell | Use Case |
| :--- | :--- | :--- | :--- |
| `alpine` | ~5MB | Yes | General purpose |
| `distroless` | ~2MB | No | Production apps |
| `scratch` | 0B | No | Static binaries (Go, Rust) |
| `debian-slim` | ~25MB | Yes | When glibc is needed |

```dockerfile
# Multi-stage: Build in fat image, run in minimal
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o myapp

FROM gcr.io/distroless/static
COPY --from=builder /app/myapp /myapp
CMD ["/myapp"]
```

---

## 8. Scan Images for Vulnerabilities

Regularly scan your images for known CVEs.

### With Trivy

```bash
# Install: https://aquasecurity.github.io/trivy/
trivy image myapp:latest
```

### With Docker Scout (Docker 24+)

```bash
docker scout cves myapp:latest
```

### In CI/CD

```yaml
# GitHub Actions example
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:latest'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

---

## 9. Network Isolation

- Don't expose ports unless necessary.
- Use user-defined networks to isolate services.
- Never run with `--network host` in production unless absolutely required.

```yaml
services:
  db:
    image: postgres
    networks:
      - backend  # Only backend services can reach db

  web:
    image: myapp
    networks:
      - frontend
      - backend
    ports:
      - "8080:80"

networks:
  frontend:
  backend:
```

---

## 10. Resource Limits

Prevent denial-of-service by limiting CPU and memory.

```bash
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  myapp
```

In Compose:

```yaml
services:
  web:
    image: myapp
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

---

## Security Checklist for Production

Before deploying, verify:

- [ ] **User:** Container runs as a non-root user?
- [ ] **Image:** Using a minimal base image (Alpine/Distroless)?
- [ ] **Scan:** Has the image been scanned for CVEs recently?
- [ ] **Secrets:** Are secrets mounted at runtime (not ENV/build-time)?
- [ ] **Filesystem:** Is the root filesystem read-only?
- [ ] **Privilege:** Is `--privileged` disabled and unnecessary capabilities dropped?
- [ ] **Resources:** Are CPU/Memory limits set?
- [ ] **Network:** Are only necessary ports exposed?
- [ ] **Logging:** Are logs sent to a central system (not just container stdout)?

---

## Summary

| Practice | Command/Config |
| :--- | :--- |
| Non-root user | `USER appuser` in Dockerfile |
| Read-only FS | `--read-only` |
| Drop capabilities | `--cap-drop ALL` |
| No privilege escalation | `--security-opt no-new-privileges` |
| Secrets at runtime | `-v ./secrets:/run/secrets:ro` |
| Minimal base | `FROM alpine` or `distroless` |
| Scan images | `trivy image` or `docker scout cves` |
| Resource limits | `--memory`, `--cpus` |

---

## Exercises

### Exercise 1: Run the Security Demo

1. Navigate to `examples/security/`
2. Run `docker compose up -d`
3. Verify security options: `docker inspect security-demo-web-1 | jq '.[0].HostConfig.SecurityOpt'`
4. Verify non-root user: `docker compose exec web whoami`
5. Try writing to root fs: `docker compose exec web touch /test.txt` (should fail)
6. Clean up: `docker compose down`

### Exercise 2: Scan Your Own Image

1. Install Trivy: `brew install trivy` or `apt install trivy`
2. Scan an image: `trivy image nginx:alpine`
3. Review the CVE report
4. Try scanning with severity filter: `trivy image --severity HIGH,CRITICAL nginx`

### Exercise 3: Add Non-Root User to Existing Image

1. Take any Dockerfile you've created
2. Add user creation and switch to non-root
3. Rebuild and verify: `docker run --rm myimage whoami`

---

**Next Chapter:** Learn how to debug issues in **Chapter 18: Troubleshooting & Debugging**.
