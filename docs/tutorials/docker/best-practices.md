# Docker Best Practices

This guide covers essential instructions and best practices to take your Dockerfiles from "functional" to **production-grade**.

> [!NOTE]
> This guide incorporates advanced "dos and don'ts" often overlooked by beginners.

## 1. Production Healthchecks (`HEALTHCHECK`)

Kubernetes and Docker Swarm know if your container is *running*, but they don't know if it's *working*. A container stuck in a deadlock is technically "running".

Use `HEALTHCHECK` to tell Docker how to test your application.

```dockerfile
# Check every 30s, timeout after 5s, fail after 3 retries
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

If the command fails (exit code 1), the container status becomes `unhealthy`, allowing orchestrators to restart it.

---

## 2. Shell Handling (`SHELL`)

The default shell on Linux is `/bin/sh -c`. This can be limiting or annoying if you want to use bashisms (like pipefail) or are on Windows.

**Stop fighting your shell.** Change it.

```dockerfile
# Use bash with pipefail enabled (fails if any part of a pipe fails)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Now this will actually fail build if wget fails, unlike standard sh
RUN wget -O - https://some.site | wc -l
```

---

## 3. Graceful Shutdowns (`STOPSIGNAL`)

When you run `docker stop`, Docker sends `SIGTERM`. If your app (like Nginx) expects `SIGQUIT` or another signal to shut down gracefully, you might be killing active connections forcefully after the timeout (usually 10s).

Tell Docker what signal your app needs:

```dockerfile
# Nginx uses SIGQUIT for graceful shutdown
STOPSIGNAL SIGQUIT
```

This prevents zombie processes and broken requests during deployments.

---

## 4. Metadata is Mandatory (`LABEL`)

Labels are not just comments; they are metadata used by tools, CI/CD pipelines, and auditors.

```dockerfile
LABEL org.opencontainers.image.title="My App"
LABEL org.opencontainers.image.description="Production Web Server"
LABEL org.opencontainers.image.version="1.2.3"
LABEL org.opencontainers.image.authors="ops@example.com"
LABEL com.example.release-date="2023-10-31"
```

Your future self (and your Ops team) will thank you when they can identify an image's purpose without guessing.

---

## 5. Build-time vs Runtime (`ARG` vs `ENV`)

Confusing these is a common source of bugs.

| Instruction | Scope | Usage |
| :--- | :--- | :--- |
| **`ARG`** | **Build-time only**. Disappears in final image. | Build versions, compiler flags. |
| **`ENV`** | **Runtime + Build-time**. Persists in container. | App config, paths, defaults. |

**Example:**

```dockerfile
# ARG: Available only during build
ARG BUILD_VERSION=1.0

# ENV: Available to the running app
ENV APP_HOME=/app
```

> [!WARNING]
> Do NOT use `ARG` or `ENV` for secrets (API keys, passwords). Both are visible in `docker history`. Use Secret Mounts instead (see [Chapter 17: Security](chapter17_security.md)).

---

## 6. The "Magic" Trigger (`ONBUILD`)

`ONBUILD` executes instructions commands *only when the image is used as a base for another build*.

Useful for creating reusable frameworks (e.g., a standard Python wrapper), but dangerous if used unexpectedly.

```dockerfile
# In "my-python-base" image:
ONBUILD COPY requirements.txt .
ONBUILD RUN pip install -r requirements.txt
```

When someone else writes `FROM my-python-base`, those lines run immediately. Use with caution—it can break downstream builds silently.

---

## 7. General Dos and Don'ts

| Category | Do ✅ | Don't ❌ |
| :--- | :--- | :--- |
| **Tags** | Pin versions (`node:18.1-alpine`) | Use `node:latest` (unpredictable) |
| **User** | create and use a non-root user | Run as `root` (default) |
| **Files** | Use `.dockerignore` for local junk | Copy `.git`, `node_modules`, `secrets` |
| **Layers** | Combine related `RUN` commands | Run `apt-get update` on its own line |
| **Secrets** | Mount secrets at runtime | Bake secrets into `ENV` vars |

### Optimize Layer Caching

Order matters! Place frequently changing files (source code) **after** rarely changing files (dependency manifests).

**✅ Correct Order:**

1. `COPY package.json .`
2. `RUN npm install` (Cached unless package.json changes)
3. `COPY . .` (Source code changes often, invalidating cache only from here down)

---

## Summary

Dockerfiles are **production code**. They define the system you ship. Don't treat them like messy shell scripts.

1. **`HEALTHCHECK`**:Define what "healthy" means.
2. **`SHELL`**: Use strict modes (pipefail).
3. **`STOPSIGNAL`**: Handle shutdowns gracefully.
4. **`LABEL`**: Add metadata.
5. **`ARG` vs `ENV`**: Know the difference.
6. **`ONBUILD`**: Use sparingly for base images.

For deeper security practices, see [Chapter 17: Security Hardening](chapter17_security.md).
