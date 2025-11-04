# Chapter 20: Beyond the Basics

Level up your builds with BuildKit features, advanced multi‑stage patterns, minimal bases, and supply‑chain security (provenance, attestations, and signing).

---

## BuildKit cache export/import and cache mounts

BuildKit drastically speeds up builds with richer caching and parallelism.

Export/import cache between machines (e.g., CI → developer):

```bash
# Export cache to a registry
docker buildx build \
	--cache-to type=registry,ref=myorg/app:buildcache,mode=max \
	--cache-from type=registry,ref=myorg/app:buildcache \
	-t myorg/app:1.0 --push .
```

Use cache mounts to persist dependencies between layers (example: Node):

```dockerfile
# syntax=docker/dockerfile:1.6
FROM node:20-alpine AS build
WORKDIR /src

# Leverage cache mount for npm cache
RUN --mount=type=cache,target=/root/.npm npm config set fund false

COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --prefer-offline

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /src/dist /usr/share/nginx/html
```

Similar patterns exist for Go (GOMODCACHE), pip/pipenv, Maven, and others.

Cross‑link: See `docs/tutorials/docker/examples/buildx/` for a runnable multi‑arch demo.

---

## Advanced multi‑stage patterns

Targeted stages and conditional builds:

```dockerfile
# syntax=docker/dockerfile:1.6
FROM golang:1.22-alpine AS unit-tests
WORKDIR /src
COPY . .
RUN go test ./...

FROM golang:1.22-alpine AS build
WORKDIR /src
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
		--mount=type=cache,target=/root/.cache/go-build \
		go build -ldflags='-s -w' -o app ./cmd/app

FROM gcr.io/distroless/base-debian12
WORKDIR /app
COPY --from=build /src/app ./app
USER 65532:65532  # non-root
ENTRYPOINT ["/app/app"]
```

Build only a specific target during CI (faster pipelines):

```bash
docker buildx build --target unit-tests .
```

Parameterize builds with `--build-arg` and keep secrets out of layers using `RUN --mount=type=secret` where supported.

---

## Minimal bases: Distroless, Wolfi, Alpine, Slim variants

Trade‑offs:
- Distroless: smallest runtime surface, no shell; great for static apps
- Alpine: tiny but musl libc can reveal edge‑case bugs in some libs
- Slim variants (Debian/Ubuntu slim): larger than Alpine, but glibc‑compatible
- Wolfi/Chainguard: hardened, frequently rebuilt to minimize CVE windows

Example swapping alpine → distroless for final stage (as above). Always test your app and observability (logs, certs) under the chosen base.

---

## Reproducible builds, provenance, and attestations

Reproducible builds aim to produce identical artifacts from the same sources.

Tips
- Pin versions for OS packages and language deps
- Avoid `apt-get upgrade`; install only needed packages in one `RUN` layer
- Bake metadata deterministically (labels, timestamps) where possible

Provenance and attestations with Buildx:

```bash
# Build and attach provenance (SLSA-style) attestations
docker buildx build \
	--provenance=true \
	--attest type=provenance,mode=max \
	-t myorg/app:1.0 --push .

# Inspect provenance (if your tooling supports it)
docker buildx imagetools inspect myorg/app:1.0
```

Some registries and tooling surface these attestations in UI or via APIs. Align with your org’s SLSA level targets.

---

## Supply chain integrity: signing and OCI artifacts

Sign images and attach extra artifacts (SBOMs, attestations) to strengthen trust.

Cosign (Sigstore):

```bash
# Generate a key pair (or use keyless via OIDC in CI)
cosign generate-key-pair

# Sign an image tag
cosign sign myorg/app:1.0

# Verify the signature
cosign verify myorg/app:1.0
```

Attach SBOMs/attestations as OCI artifacts:

```bash
# Attach an SBOM (cyclonedx)
cosign attach sbom --sbom sbom.cdx.json myorg/app:1.0

# List attached artifacts
cosign verify-attestation --type cyclonedx myorg/app:1.0 || true
```

Notation (CNCF project) is another signing option that integrates with some registries and policies.

Policy engines (preview your platform’s support):
- Enforce “only signed images”
- Require attestations (provenance, SBOM, vulnerability thresholds)

---

## Performance tips and next steps

- Reuse Buildx cache across CI jobs and environments
- Prefer multi‑stage builds that copy only final artifacts
- Split monolith Dockerfiles into independent contexts to maximize cache reuse
- Keep secrets out of layers and avoid copying entire repos unnecessarily
- Continuously scan images and dependencies; regenerate SBOMs on each release

Where to go next
- Orchestration at scale (Kubernetes, GitOps)
- Image lifecycle management (retention, promotions, provenance dashboards)
- Supply chain policy and admission control
