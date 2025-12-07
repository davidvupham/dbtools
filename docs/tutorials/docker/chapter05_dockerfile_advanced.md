# Chapter 5: Advanced Dockerfile Techniques

Now that you can build functional images, it's time to build **better** images. Production images should be fast to build, small in size, and secure.

## 1. Layer Caching

Docker caches the result of each instruction. If an instruction and the files it touches haven't changed, Docker reuses the cached layer. This speeds up builds significantly.

### Order Matters

Put instructions that change frequently (like your source code) **after** instructions that change rarely (like installing dependencies).

**❌ Bad Optimization:**

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .                  # <--- Code changes often breaks cache here
RUN pip install -r requirements.txt  # <--- Re-runs every time code changes!
CMD ["python", "app.py"]
```

**✅ Good Optimization:**

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .   # <--- Only changes when deps change
RUN pip install -r requirements.txt  # <--- Cached until deps change!
COPY . .                  # <--- Code changes; only this layer rebuilds
CMD ["python", "app.py"]
```

---

## 2. Multi-Stage Builds

One of the most powerful features in Docker is **multi-stage builds**. This allows you to use a heavy image with all the build tools (compilers, headers) to build your app, and then copy *only the binary* to a tiny runtime image.

**Example: Go Application**
(See runnable code in `examples/basics/multi-stage/`)

```dockerfile
# --- Stage 1: Builder ---
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY main.go .

# Build the binary
RUN go build -o myapp main.go

# --- Stage 2: Runtime ---
FROM alpine:latest

WORKDIR /root/

# Copy ONLY the binary from the builder stage
COPY --from=builder /app/myapp .

EXPOSE 8080
CMD ["./myapp"]
```

**Why is this better?**

- **Size:** The `golang` image is ~800MB. The `alpine` image is ~5MB. Your final image is tiny!
- **Security:** The build tools (compiler, etc.) are left behind, reducing the attack surface.

---

## 3. Build Arguments (ARG)

Sometimes you need to pass variables at build time (e.g., version numbers) that shouldn't persist as environment variables in the final container.

```dockerfile
FROM python:3.9-slim
ARG VERSION=1.0.0
RUN echo "Building version $VERSION" > version.txt
```

Build with:

```bash
docker build --build-arg VERSION=2.0.0 -t myapp .
```

---

## 4. Running as Non-Root User

By default, Docker containers run as `root`. This is a security risk. If an attacker escapes the container, they could have root access to your host. Best practice is to create a dedicated user and switch to it.

### Step-by-Step Configuration

To run as non-root, you need to handle three things: **User Creation**, **Permissions**, and **Ports**.

#### 1. Create the User

Use `adduser` (Alpine/Debian) or `useradd` (RedHat/CentOS) to create a system user with no password.

```dockerfile
# Alpine example
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
```

#### 2. Set Ownership (Permissions)

The new user cannot write to files owned by `root`. You must change ownership of your working directory.

```dockerfile
WORKDIR /app
COPY . .

# Change ownership of the application files to the new user
RUN chown -R appuser:appgroup /app
```

> [!TIP]
> You can also use `COPY --chown=appuser:appgroup . .` to copy and set permissions in one step!

#### 3. Switch User

Tell Docker to run subsequent commands (and the final app) as this user.

```dockerfile
USER appuser
CMD ["node", "index.js"]
```

#### Important Restrictions

- **Ports:** Non-root users cannot bind to ports below 1024 (like 80 or 443) by default.
  - *Solution:* Use high ports (e.g., `8080`, `3000`).
- **Volumes:** If you mount a volume from the host, the permissions must match the non-root user (UID/GID), or the container won't be able to write to it.
- **Installs:** You cannot run `apt-get` or `apk install` *after* switching users. Do all your setup as root first, then switch to the non-root user at the very end.

### Complete Example

```dockerfile
FROM node:18-alpine

# 1. Setup environment
ENV NODE_ENV=production
WORKDIR /app

# 2. Install dependencies (as root)
COPY package*.json ./
RUN npm ci --only=production

# 3. Create user and fix permissions
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --chown=appuser:appgroup . .

# 4. Switch to non-root privileges
USER appuser

# 5. Run app on a high port
EXPOSE 8080
CMD ["node", "index.js"]
```

---

## 5. Summary Checklist for Production Images

1. **Use specific tags** (`python:3.9-slim`), never just `latest`.
2. **Optimize caching** by copying dependency files first.
3. **Use Multi-Stage Builds** for compiled languages or frontend builds.
4. **Add `.dockerignore`** to keep junk out.
5. **Run as non-root** for security.
6. **Scan your images** for vulnerabilities (Chapter 17).

**Next Chapter:** Learn how to manage the images you've built in **Chapter 6: Managing Images**.
