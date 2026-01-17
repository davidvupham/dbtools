# Buildx Multi-Arch Demo

A tiny Go web server built with a multi-stage Dockerfile and published for linux/amd64 and linux/arm64.

## Build locally (single arch)

```bash
cd docs/tutorials/docker/examples/buildx
# Single-arch local build & run
docker build -t buildx-demo:dev .
docker run --rm -p 8080:8080 buildx-demo:dev
```

## Multi-arch with Buildx

```bash
# One-time: create and select a builder
docker buildx create --use --name mybuilder

# Build for multiple platforms and push to a registry (replace REPO)
# Requires 'docker login' to your registry
export REPO=your-registry/yourname/buildx-demo

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t $REPO:1.0 \
  -t $REPO:latest \
  --push .
```

## Notes

- Cache mounts (`--mount=type=cache`) speed up repeat builds.
- The final image uses `distroless:nonroot` and exposes 8080.
- For CI, pair with Trivy/Grype to scan the resulting image tags.
