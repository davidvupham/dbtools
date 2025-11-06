# Chapter 16: CI/CD for Containers

- Build on CI: tag with version/commit, push to registry
- Multi‑arch builds with buildx
- Scan images and fail builds on critical CVEs

```bash
# Buildx quick start
docker buildx create --use --name mybuilder
docker buildx build --platform linux/amd64,linux/arm64 -t REPO/app:1.0 --push .
```

---

## GitHub Actions example (Docker Hub)

```yaml
name: ci
on:
  push:
    branches: [ main ]
    tags: [ 'v*.*.*' ]
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/app:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/app:${{ github.sha }}
          cache-from: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/app:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/app:buildcache,mode=max

  scan:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Trivy scan
        uses: aquasecurity/trivy-action@0.24.0
        with:
          image-ref: ${{ secrets.DOCKERHUB_USERNAME }}/app:${{ github.sha }}
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

## GitLab CI example

```yaml
stages: [build, scan]

build:
  stage: build
  image: docker:24
  services: [docker:24-dind]
  variables:
    DOCKER_TLS_CERTDIR: ""
  script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
    - docker buildx create --use || true
    - docker buildx build --platform linux/amd64,linux/arm64 \
        -t $CI_REGISTRY_IMAGE:${CI_COMMIT_SHA} --push .

scan:
  stage: scan
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH $CI_REGISTRY_IMAGE:${CI_COMMIT_SHA}
```

## Tagging and promotion strategy

- Push immutable tags per commit (e.g., SHA) and per release (e.g., 1.2.3).
- Update moving tags (`latest`, major/minor lines) only after promotion.
- Use distinct repos or tags for environments (dev/stage/prod) and promote by retagging.

## Caching for speed

- Export/import BuildKit cache to a registry to reuse across CI runners.
- Keep Dockerfiles cache-friendly: install dependencies before copying source when possible.

## Policy and supply chain

- Scan images in CI and on a schedule; fail on critical vulnerabilities.
- Generate and store SBOMs; consider signing images and enforcing signature policies.
