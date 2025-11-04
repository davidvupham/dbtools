# Chapter 2: Setting Up Your Docker Environment

- Linux: install the Docker Engine; add your user to the `docker` group.
- macOS/Windows: install Docker Desktop (bundles engine, UI, Kubernetes optional).
- Verify and basics:

```bash
docker version
docker info
```

- Optional: enable experimental features (BuildKit, buildx), set up credential helpers for private registries.
- Registries: Docker Hub (default), GHCR, ECR/GCR/ACR. Authenticate where needed.
