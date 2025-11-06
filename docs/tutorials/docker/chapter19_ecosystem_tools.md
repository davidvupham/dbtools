# Chapter 19: Ecosystem Tools

This chapter rounds out your day‑to‑day toolkit beyond the core `docker` CLI. You’ll learn how to push to different registries, work with remote contexts and builders, harden your daemon with rootless mode, scan for vulnerabilities, and generate SBOMs.

---

## Registries: Docker Hub, GHCR, ECR/GCR/ACR, self‑hosted

- Docker Hub: `docker.io/USERNAME/IMAGE:TAG` (default registry when omitted)
- GitHub Container Registry (GHCR): `ghcr.io/OWNER/IMAGE:TAG`
- AWS ECR, Google GCR/Artifact Registry, Azure ACR: cloud‑hosted, private by default
- Self‑hosted registry: `registry:2` or products like Harbor

Tagging and pushing to GHCR:

```bash
# Authenticate to GHCR (uses your GitHub token with appropriate scopes)
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USER" --password-stdin

# Tag and push
docker tag myapp:1.0 ghcr.io/$GITHUB_USER/myapp:1.0
docker push ghcr.io/$GITHUB_USER/myapp:1.0
```

Pushing to AWS ECR (example):

```bash
# 1) Authenticate the Docker client to ECR (region-specific)
aws ecr get-login-password --region us-east-1 \
	| docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# 2) Tag and push
docker tag myapp:1.0 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
```

Notes
- Prefer immutable digests in deployment manifests. Resolve a tag’s digest with: `docker inspect <image:tag> --format '{{index .RepoDigests 0}}'`.
- Consider retention policies and vulnerability scanning features offered by the registry.

---

## Contexts and remote builders

Docker contexts let you target a remote daemon transparently, and Buildx lets you set up remote builders.

```bash
# List contexts (default is usually 'default')
docker context ls

# Create an SSH-backed context to a remote Docker host
docker context create my-remote --docker "host=ssh://user@my.docker.host"

# Use it for subsequent commands
docker context use my-remote
docker ps  # runs against the remote host

# Switch back
docker context use default
```

Buildx with a dedicated remote builder:

```bash
# Create and use a remote builder over SSH
docker buildx create --name remote-builder --driver docker-container \
	--use ssh://user@my.docker.host

# Inspect builder capabilities
docker buildx inspect --bootstrap

# Build on multiple platforms with the remote builder
docker buildx build --platform linux/amd64,linux/arm64 -t myorg/app:1.0 --push .
```

Why use contexts/builders?
- Offload heavy builds to stronger machines (or ephemeral builders in CI)
- Build once and push multi‑arch images with consistent caching
- Centralize Docker daemon access control

Cross‑links
- See the Buildx example in `docs/tutorials/docker/examples/buildx/`.

---

## Rootless mode and user namespaces

Rootless mode runs the Docker daemon and containers without root privileges on the host, reducing risk.

Benefits
- Smaller attack surface on the host
- Containers map container‑root to an unprivileged host user via user namespaces

Considerations
- Not all features are available (e.g., some storage/network drivers)
- Port binding below 1024 and cgroup interactions differ; read the official docs

Quick start (Linux, high‑level)
- Install `uidmap`, ensure subuid/subgid ranges in `/etc/subuid` and `/etc/subgid`
- Follow Docker’s Rootless guide to run `dockerd-rootless-setuptool.sh install`
- Use `export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock` to target the rootless daemon

Even without full rootless mode, you should:
- Use non‑root `USER` in your images
- Drop capabilities and set `--security-opt no-new-privileges`

---

## Scanners: Trivy, Grype, Snyk, Docker Scout

Scan images locally and in CI to catch known CVEs before release.

Trivy (fast and popular):

```bash
# Scan a local image
trivy image myapp:1.0

# Fail CI on high/critical
trivy image --exit-code 1 --severity HIGH,CRITICAL myorg/app:1.0
```

Grype (Anchore):

```bash
grype myorg/app:1.0
```

Snyk:

```bash
snyk container test myorg/app:1.0
```

Docker Scout (if available):

```bash
docker scout quickview myorg/app:1.0
```

Tips
- Scan both base images and your final images
- Keep base images updated and pin versions (e.g., `python:3.12-slim`)
- Use multi‑stage builds to avoid shipping compilers and package managers

---

## SBOMs: Syft and CycloneDX

An SBOM (Software Bill of Materials) lists the components in your image. Generate and ship SBOMs for compliance and supply‑chain security.

Syft (Anchore) to produce SPDX or CycloneDX:

```bash
# Generate CycloneDX JSON SBOM
syft packages docker:myorg/app:1.0 -o cyclonedx-json > sbom.cdx.json

# Or SPDX JSON
syft packages docker:myorg/app:1.0 -o spdx-json > sbom.spdx.json
```

CycloneDX CLI can validate/transform SBOMs across ecosystems. Some registries support storing SBOMs as OCI artifacts alongside the image.

Pro tips
- Automate SBOM generation during CI build and attach to releases
- Sign SBOMs (see the next chapter for signing/attestation)

---

## Self‑hosted registry (quick start)

For air‑gapped or on‑prem setups, run a local registry:

```bash
docker run -d -p 5000:5000 --name registry registry:2

# Tag and push
docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0

# Pull from another host (replace host/IP as needed)
docker pull your-host:5000/myapp:1.0
```

Secure with TLS and auth in production; evaluate Harbor if you need UI, policies, and replication.

---

## JFrog Artifactory (Enterprise Registry)

For enterprise environments requiring advanced features, **JFrog Artifactory** provides a universal artifact repository that supports Docker alongside other package formats.

**Key features**:
- Universal repository (Docker, Maven, npm, PyPI, etc.)
- Fine-grained access control (RBAC)
- Repository replication and high availability
- Vulnerability scanning with JFrog Xray
- Caching of remote registries (Docker Hub, etc.)
- Build promotion workflows
- Comprehensive audit logs

**Quick setup**:

```bash
# Login to Artifactory
docker login mycompany.jfrog.io

# Pull from Artifactory (caches Docker Hub)
docker pull mycompany.jfrog.io/docker/nginx:alpine

# Push your image
docker tag myapp:1.0 mycompany.jfrog.io/docker-local/myapp:1.0
docker push mycompany.jfrog.io/docker-local/myapp:1.0
```

**Repository types in Artifactory**:
1. **Local**: Your own images (builds)
2. **Remote**: Cache of external registries (Docker Hub, GHCR, etc.)
3. **Virtual**: Aggregates local and remote (single endpoint)

**Example virtual repository setup**:
```
docker-virtual (developers use this)
  ├── docker-local (internal images)
  └── docker-hub-remote (cached external images)
```

**When pulling `mycompany.jfrog.io/docker/nginx:alpine`**:
1. Checks `docker-local` (not found)
2. Checks `docker-hub-remote` (downloads from Docker Hub, caches locally)
3. Returns image
4. Next pull is instant (served from cache)

**For comprehensive JFrog Artifactory guide**: See [Chapter 21: JFrog Artifactory as Docker Registry](./chapter21_jfrog_artifactory.md)

---

## Summary

- Use the right registry for your org (Hub, GHCR, ECR/GCR/ACR, Harbor, Artifactory)
- For enterprises, consider JFrog Artifactory for universal artifact management
- Target remote daemons with contexts and speed up builds with remote builders
- Prefer rootless mode where possible; always run containers as non‑root
- Scan images continuously and generate SBOMs for traceability
- For internal needs, a self‑hosted registry can complement cloud registries

Next: "Beyond the Basics" digs into cache performance, reproducible builds, and supply‑chain integrity.

---

**Related Chapters**:
- [Chapter 21: JFrog Artifactory as Docker Registry](./chapter21_jfrog_artifactory.md) - Comprehensive guide to using Artifactory
