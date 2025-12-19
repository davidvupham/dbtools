# How to Use UV in CI/CD Pipelines

This guide covers integrating UV into various CI/CD platforms for testing, building, and deploying Python applications.

## GitHub Actions

### Basic Setup

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        uses: astral-sh/setup-uv@v4
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests
        run: uv run pytest
```

### With Python Version Matrix

```yaml
name: Test Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests
        run: uv run pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### With Caching (Faster Builds)

```yaml
name: CI with Cache

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests
        run: uv run pytest
```

### Full CI/CD Pipeline

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ========================================
  # Linting and Type Checking
  # ========================================
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - run: uv sync
      - name: Lint with Ruff
        run: uv run ruff check .
      - name: Format check
        run: uv run ruff format --check .
      - name: Type check with mypy
        run: uv run mypy src

  # ========================================
  # Testing
  # ========================================
  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          python-version: ${{ matrix.python-version }}
          enable-cache: true
      - run: uv sync
      - name: Run tests
        run: uv run pytest -v --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4

  # ========================================
  # Build Docker Image
  # ========================================
  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ========================================
  # Deploy
  # ========================================
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Your deployment commands here
          echo "Deploying..."
```

---

## GitLab CI

### Basic Pipeline

```yaml
# .gitlab-ci.yml
image: python:3.12-slim

stages:
  - test
  - build
  - deploy

variables:
  UV_CACHE_DIR: .uv-cache

cache:
  key: uv-cache
  paths:
    - .uv-cache
    - .venv

before_script:
  - curl -LsSf https://astral.sh/uv/install.sh | sh
  - export PATH="$HOME/.local/bin:$PATH"

test:
  stage: test
  script:
    - uv sync
    - uv run pytest --cov

lint:
  stage: test
  script:
    - uv sync
    - uv run ruff check .
    - uv run ruff format --check .

build:
  stage: build
  image: docker:24.0
  services:
    - docker:24.0-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main
```

### With Python Version Matrix

```yaml
# .gitlab-ci.yml
test:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.10", "3.11", "3.12"]
  image: python:${PYTHON_VERSION}-slim
  script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.local/bin:$PATH"
    - uv sync
    - uv run pytest
```

---

## Azure DevOps

### Basic Pipeline

```yaml
# azure-pipelines.yml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Test
    jobs:
      - job: Test
        strategy:
          matrix:
            Python311:
              python.version: '3.11'
            Python312:
              python.version: '3.12'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(python.version)'

          - script: |
              curl -LsSf https://astral.sh/uv/install.sh | sh
              echo "##vso[task.prependpath]$HOME/.local/bin"
            displayName: 'Install UV'

          - script: uv sync
            displayName: 'Install dependencies'

          - script: uv run pytest --junitxml=junit.xml
            displayName: 'Run tests'

          - task: PublishTestResults@2
            inputs:
              testResultsFiles: 'junit.xml'
              testRunTitle: 'Python $(python.version)'

  - stage: Build
    dependsOn: Test
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - job: Docker
        steps:
          - task: Docker@2
            inputs:
              command: buildAndPush
              repository: myapp
              dockerfile: Dockerfile
              tags: |
                $(Build.BuildId)
                latest
```

---

## CircleCI

### Basic Configuration

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run:
          name: Install UV
          command: curl -LsSf https://astral.sh/uv/install.sh | sh
      - run:
          name: Install dependencies
          command: ~/.local/bin/uv sync
      - run:
          name: Run tests
          command: ~/.local/bin/uv run pytest
      - store_test_results:
          path: test-results

  lint:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run:
          name: Install UV
          command: curl -LsSf https://astral.sh/uv/install.sh | sh
      - run:
          name: Lint
          command: |
            ~/.local/bin/uv sync
            ~/.local/bin/uv run ruff check .

workflows:
  main:
    jobs:
      - lint
      - test:
          requires:
            - lint
```

---

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
        }
    }
    
    environment {
        PATH = "${env.HOME}/.local/bin:${env.PATH}"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                sh 'uv sync'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'uv run ruff check .'
                sh 'uv run ruff format --check .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'uv run pytest --junitxml=results.xml'
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }
        
        stage('Build') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker build -t myapp:${BUILD_NUMBER} .'
            }
        }
    }
}
```

---

## Common Patterns

### Dependency Caching

All CI platforms benefit from caching the UV cache directory:

```bash
# Default cache locations
# Linux: ~/.cache/uv
# macOS: ~/Library/Caches/uv
# Windows: %LOCALAPPDATA%\uv\cache

# Or set custom location
export UV_CACHE_DIR=/path/to/cache
```

### Lock File Verification

Ensure the lock file is up to date:

```yaml
- name: Verify lock file
  run: |
    uv lock --check
    if [ $? -ne 0 ]; then
      echo "Lock file is outdated. Run 'uv lock' locally."
      exit 1
    fi
```

### Publishing to PyPI

```yaml
- name: Build and publish
  run: |
    uv build
    uv publish --token ${{ secrets.PYPI_TOKEN }}
```

### Running Specific Dependency Groups

```yaml
# Install only production deps
- run: uv sync --no-dev

# Install with specific group
- run: uv sync --group test

# Install all groups
- run: uv sync --all-groups
```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `UV_CACHE_DIR` | Cache location | `~/.cache/uv` |
| `UV_FROZEN` | Always use --frozen | `1` |
| `UV_NO_CACHE` | Disable caching | `1` |
| `UV_PYTHON` | Python to use | `3.12` |
| `UV_SYSTEM_PYTHON` | Use system Python | `1` |

---

## Production Deployment

### Building Wheels for Deployment

Build Python packages as wheels for deployment to production environments:

```yaml
name: Build and Deploy

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      
      # Build wheels for all packages
      - name: Build packages
        run: |
          for pkg in gds-database gds-mssql gds-postgres gds-snowflake; do
            uv build --package "$pkg" --out-dir dist/
          done
      
      - uses: actions/upload-artifact@v4
        with:
          name: wheels
          path: dist/*.whl
```

### Publishing to Private PyPI

```yaml
  publish:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: wheels
          path: dist/
      
      - uses: astral-sh/setup-uv@v4
      
      - name: Publish to private PyPI
        run: uv publish dist/*.whl
        env:
          UV_PUBLISH_URL: ${{ secrets.PYPI_URL }}
          UV_PUBLISH_USERNAME: ${{ secrets.PYPI_USER }}
          UV_PUBLISH_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

### Deploying with pip (Traditional)

If your production environment requires pip:

```yaml
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      # Download built wheels
      - uses: actions/download-artifact@v4
        with:
          name: wheels
          path: dist/
      
      # Deploy to server
      - name: Deploy
        run: |
          scp dist/*.whl user@server:/tmp/
          ssh user@server "pip install /tmp/*.whl"
```

### Where Packages Are Installed

| Environment | Package Location |
|-------------|------------------|
| UV with venv | `.venv/lib/python3.x/site-packages/` |
| pip (system) | `/usr/local/lib/python3.x/site-packages/` |
| pip (user) | `~/.local/lib/python3.x/site-packages/` |
| Docker with UV | `/app/.venv/lib/python3.x/site-packages/` |

> [!TIP]
> UV is primarily a development and build tool. For production, you can either:
>
> 1. Use `uv sync --frozen` in containers (consistent with development)
> 2. Build wheels with `uv build` and deploy with pip (traditional approach)

---

## Troubleshooting

### "Lock file is out of date"

```yaml
# Option 1: Fail and require update
- run: uv lock --check

# Option 2: Auto-update (not recommended for CI)
- run: uv lock
```

### Slow CI builds

1. Enable caching (platform-specific)
2. Use `--frozen` to skip resolution
3. Use `--no-dev` for production builds

### Permission errors

```yaml
# Run UV with proper permissions
- run: |
    mkdir -p ~/.local/bin
    curl -LsSf https://astral.sh/uv/install.sh | sh
    chmod +x ~/.local/bin/uv
```

---

## Related Guides

- [UV Getting Started](../../../tutorials/python/uv/uv-getting-started.md)
- [UV Docker Integration](./uv-docker-integration.md)
- [GitHub Actions Tutorial](../../../tutorials/github-actions/README.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
