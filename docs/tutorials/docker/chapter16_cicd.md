# Chapter 16: CI/CD for Containers

- Build on CI: tag with version/commit, push to registry
- Multi‑arch builds with buildx
- Scan images and fail builds on critical CVEs

```bash
# Buildx quick start
docker buildx create --use --name mybuilder
docker buildx build --platform linux/amd64,linux/arm64 -t REPO/app:1.0 --push .
```
