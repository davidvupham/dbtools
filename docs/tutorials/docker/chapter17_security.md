# Chapter 17: Security Hardening

- Run as non‑root (`USER` directive)
- Read‑only filesystem, writable tmpfs as needed
- Drop capabilities and block privilege escalation
- Minimal bases, multi‑stage to exclude build tools
- Secrets via orchestrator or external vaults, not baked into images
- Scan images regularly (Trivy/Grype/Snyk)

```bash
docker run --rm \
  --cap-drop ALL --security-opt no-new-privileges \
  --read-only -v app-tmp:/tmp \
  myimage:tag
```

---

## Run as a non‑root user

```dockerfile
# Example: Node.js app running as non-root
FROM node:20-alpine AS base
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
USER app
CMD ["node", "server.js"]
```

## Restrict at runtime

```bash
docker run -d --name app -p 3000:3000 \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL --cap-add NET_BIND_SERVICE \
  --security-opt no-new-privileges \
  myorg/app:latest
```

Notes:
- Keep Docker’s default seccomp profile unless you have a documented need.
- Consider AppArmor/SELinux profiles on Linux hosts.

## Managing secrets

- Avoid storing secrets in images or committing them to VCS.
- Prefer orchestrator secrets or mounted files; read them at runtime.

Local dev pattern:
```bash
docker run -d \
  -v $(pwd)/.secrets:/run/secrets:ro \
  myorg/app:latest
```

## Image scanning

```bash
# Trivy (install separately)
trivy image myorg/app:latest

# Docker Scout (Docker 24+)
docker scout cves myorg/app:latest
```

Pin base images and OS packages, and rebuild regularly to pick up security updates.
