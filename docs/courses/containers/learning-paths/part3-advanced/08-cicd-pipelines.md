# CI/CD pipelines for containers

> **Module:** Part 3 - Advanced | **Level:** Advanced | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Build container images in CI/CD
- Implement testing strategies
- Set up automated deployments
- Implement security scanning

---

## CI/CD pipeline overview

```mermaid
graph LR
    A[Code Push] --> B[Build Image]
    B --> C[Run Tests]
    C --> D[Security Scan]
    D --> E[Push to Registry]
    E --> F[Deploy]
```

---

## GitHub Actions

### Basic build and push

```yaml
# .github/workflows/docker.yaml
name: Build and Push

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Multi-stage with testing

```yaml
name: Build, Test, Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Build test image
        run: docker build --target test -t app:test .

      - name: Run tests
        run: |
          docker run --network host \
            -e DATABASE_URL=postgres://postgres:testpass@localhost:5432/testdb \
            app:test npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy:
    needs: [build, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Deploy to production
        run: |
          # Update deployment with new image
          echo "Deploying ghcr.io/${{ github.repository }}:${{ github.sha }}"
```

---

## GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - scan
  - deploy

variables:
  DOCKER_TLS_CERTDIR: "/certs"
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build --cache-from $CI_REGISTRY_IMAGE:latest -t $IMAGE_TAG -t $CI_REGISTRY_IMAGE:latest .
    - docker push $IMAGE_TAG
    - docker push $CI_REGISTRY_IMAGE:latest

test:
  stage: test
  image: docker:24
  services:
    - docker:24-dind
    - postgres:15-alpine
  variables:
    POSTGRES_PASSWORD: testpass
    POSTGRES_DB: testdb
    DATABASE_URL: postgres://postgres:testpass@postgres:5432/testdb
  script:
    - docker pull $IMAGE_TAG
    - docker run --network host -e DATABASE_URL=$DATABASE_URL $IMAGE_TAG npm test

scan:
  stage: scan
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE_TAG
  allow_failure: true

deploy:
  stage: deploy
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker stack deploy -c docker-stack.yml myapp
  environment:
    name: production
  only:
    - main
  when: manual
```

---

## Jenkins pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        REGISTRY = 'registry.example.com'
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${REGISTRY}/${IMAGE_NAME}:${BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("${IMAGE_TAG}")
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    docker.image("${IMAGE_TAG}").inside {
                        sh 'npm test'
                    }
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh "trivy image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_TAG}"
            }
        }

        stage('Push') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'registry-credentials') {
                        docker.image("${IMAGE_TAG}").push()
                        docker.image("${IMAGE_TAG}").push('latest')
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    docker stack deploy -c docker-stack.yml myapp
                """
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f'
        }
    }
}
```

---

## Testing strategies

### Unit tests in Docker

```dockerfile
# Multi-stage with test stage
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS test
COPY . .
CMD ["npm", "test"]

FROM base AS production
COPY . .
RUN npm prune --production
CMD ["node", "index.js"]
```

### Integration tests with compose

```yaml
# compose.test.yaml
services:
  test:
    build:
      context: .
      target: test
    environment:
      - DATABASE_URL=postgres://test:test@db:5432/testdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: npm run test:integration

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=testdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
```

```bash
# Run integration tests
docker compose -f compose.test.yaml run --rm test
```

### End-to-end tests

```yaml
# compose.e2e.yaml
services:
  e2e:
    image: cypress/included:latest
    environment:
      - CYPRESS_BASE_URL=http://frontend
    volumes:
      - ./cypress:/app/cypress
      - ./cypress.config.js:/app/cypress.config.js
    depends_on:
      - frontend
      - api

  frontend:
    build: ./frontend
    depends_on:
      - api

  api:
    build: ./api
    environment:
      - DATABASE_URL=postgres://test:test@db:5432/testdb
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=testdb
```

---

## Security scanning

### Image scanning in CI

```yaml
# Trivy scan
- name: Trivy vulnerability scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
    format: 'table'
    exit-code: '1'
    ignore-unfixed: true
    vuln-type: 'os,library'
    severity: 'CRITICAL,HIGH'

# Snyk scan
- name: Snyk Container scan
  uses: snyk/actions/docker@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    image: ${{ env.IMAGE }}
    args: --severity-threshold=high

# Docker Scout
- name: Docker Scout scan
  uses: docker/scout-action@v1
  with:
    command: cves
    image: ${{ env.IMAGE }}
    sarif-file: scout-results.sarif
```

### SBOM generation

```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE }}
    artifact-name: sbom.spdx.json
    output-file: sbom.spdx.json
```

---

## Deployment strategies

### Rolling deployment

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy with rolling update
      run: |
        docker service update \
          --image ${{ env.IMAGE }}:${{ github.sha }} \
          --update-parallelism 1 \
          --update-delay 30s \
          --update-failure-action rollback \
          myapp_api
```

### Blue-green deployment

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy green
      run: |
        # Deploy new version as green
        VERSION=${{ github.sha }} docker stack deploy -c stack-green.yaml myapp-green

    - name: Health check green
      run: |
        # Wait for health
        for i in {1..30}; do
          if curl -sf http://green.internal/health; then
            echo "Green is healthy"
            exit 0
          fi
          sleep 10
        done
        exit 1

    - name: Switch traffic
      run: |
        # Update load balancer to point to green
        ./scripts/switch-to-green.sh

    - name: Remove blue
      run: |
        # Clean up old version
        docker stack rm myapp-blue
```

### Canary deployment

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy canary (10%)
      run: |
        docker service update --replicas 1 myapp_api-canary --image ${{ env.IMAGE }}
        docker service scale myapp_api=9 myapp_api-canary=1

    - name: Monitor canary
      run: |
        ./scripts/monitor-canary.sh --duration 15m --threshold 0.01

    - name: Promote or rollback
      run: |
        if [ "$CANARY_SUCCESS" == "true" ]; then
          docker service scale myapp_api=0
          docker service update --replicas 10 myapp_api-canary
        else
          docker service scale myapp_api-canary=0
        fi
```

---

## Best practices

### Caching

```yaml
# GitHub Actions cache
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ env.IMAGE }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Parallel builds

```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [api, worker, frontend]
    steps:
      - name: Build ${{ matrix.service }}
        run: docker build -t myapp/${{ matrix.service }} ./${{ matrix.service }}
```

### Environment promotion

```yaml
environments:
  - name: staging
    deploy_on: main branch
  - name: production
    deploy_on: tag (v*)
    requires: staging success
```

---

## Key takeaways

1. **Automate everything** - Build, test, scan, deploy
2. **Test in containers** - Same environment as production
3. **Scan for vulnerabilities** - Fail fast on security issues
4. **Use caching** - Speed up builds significantly
5. **Progressive deployment** - Canary/blue-green for safety

---

## What's next

Learn about monitoring and observability in production.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Storage Deep Dive](07-storage-deep-dive.md) | [Part 3 Overview](../../course_overview.md#part-3-advanced) | [Monitoring and Observability](09-monitoring-observability.md) |
