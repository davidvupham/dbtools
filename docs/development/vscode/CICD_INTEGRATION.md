# CI/CD Integration with Dev Containers

This guide explains how to use the same dev container configuration in CI/CD pipelines to ensure consistency between local development and automated builds.

## Table of Contents

- [Why Use Dev Containers in CI/CD?](#why-use-dev-containers-in-cicd)
- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Azure DevOps](#azure-devops)
- [Jenkins](#jenkins)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Best Practices](#best-practices)

## Why Use Dev Containers in CI/CD?

**Benefits:**
- ✅ **Consistency**: Same environment locally and in CI/CD
- ✅ **Reproducibility**: Identical builds every time
- ✅ **Simplified maintenance**: Update Dockerfile, not CI config
- ✅ **Local testing**: Test CI steps locally before pushing
- ✅ **Dependency management**: All dependencies in one place

**Use Cases:**
- Running tests with exact same Python/PowerShell versions
- Linting and code quality checks
- Building and publishing packages
- Database migrations and testing
- Integration tests with databases

## GitHub Actions

### Basic Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build dev container
        uses: devcontainers/ci@v0.3
        with:
          imageName: ghcr.io/${{ github.repository }}/devcontainer
          cacheFrom: ghcr.io/${{ github.repository }}/devcontainer
          push: never
          runCmd: |
            python -m pytest -v --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Advanced Workflow with Multiple Jobs

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/devcontainer

jobs:
  build-container:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
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
            type=sha,prefix={{branch}}-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: .devcontainer/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max
          build-args: |
            PYTHON_VERSION=3.13
            CONDA_ENV_NAME=gds

  lint:
    needs: build-container
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run linting
        uses: devcontainers/ci@v0.3
        with:
          imageName: ${{ needs.build-container.outputs.image-tag }}
          push: never
          runCmd: |
            ruff check . --output-format=github
            ruff format --check .

  test-python:
    needs: build-container
    runs-on: ubuntu-latest

    strategy:
      matrix:
        test-suite:
          - gds_database
          - gds_postgres
          - gds_snowflake
          - gds_vault
          - gds_mongodb
          - gds_mssql

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run tests for ${{ matrix.test-suite }}
        uses: devcontainers/ci@v0.3
        with:
          imageName: ${{ needs.build-container.outputs.image-tag }}
          push: never
          runCmd: |
            cd ${{ matrix.test-suite }}
            pytest -v --cov=. --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./${{ matrix.test-suite }}/coverage.xml
          flags: ${{ matrix.test-suite }}

  test-powershell:
    needs: build-container
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run PowerShell tests
        uses: devcontainers/ci@v0.3
        with:
          imageName: ${{ needs.build-container.outputs.image-tag }}
          push: never
          runCmd: |
            pwsh -NoProfile -Command "Invoke-Pester -Path ./PowerShell/tests -Output Detailed -CI"

  integration-tests:
    needs: build-container
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      mongodb:
        image: mongo:7
        env:
          MONGO_INITDB_ROOT_USERNAME: mongo
          MONGO_INITDB_ROOT_PASSWORD: mongo
        ports:
          - 27017:27017

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run integration tests
        uses: devcontainers/ci@v0.3
        with:
          imageName: ${{ needs.build-container.outputs.image-tag }}
          push: never
          env: |
            POSTGRES_HOST=postgres
            POSTGRES_PORT=5432
            POSTGRES_DB=testdb
            POSTGRES_USER=postgres
            POSTGRES_PASSWORD=postgres
            MONGODB_HOST=mongodb
            MONGODB_PORT=27017
          runCmd: |
            pytest tests/integration -v

  build-packages:
    needs: [lint, test-python, test-powershell]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Build Python packages
        uses: devcontainers/ci@v0.3
        with:
          imageName: ${{ needs.build-container.outputs.image-tag }}
          push: never
          runCmd: |
            for pkg in gds_database gds_postgres gds_snowflake gds_vault gds_mongodb gds_mssql; do
              cd $pkg
              python -m build
              cd ..
            done

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: python-packages
          path: |
            */dist/*.whl
            */dist/*.tar.gz
```

### Caching Strategies

```yaml
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-

- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

### Using Secrets

```yaml
- name: Run tests with secrets
  uses: devcontainers/ci@v0.3
  with:
    imageName: myimage
    push: never
    env: |
      VAULT_TOKEN=${{ secrets.VAULT_TOKEN }}
      SNOWFLAKE_PASSWORD=${{ secrets.SNOWFLAKE_PASSWORD }}
    runCmd: |
      pytest tests/
```

## GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - test
  - package

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  IMAGE_TAG: $CI_REGISTRY_IMAGE/devcontainer:$CI_COMMIT_REF_SLUG

build-container:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -f .devcontainer/Dockerfile -t $IMAGE_TAG
        --build-arg PYTHON_VERSION=3.13
        --build-arg CONDA_ENV_NAME=gds .
    - docker push $IMAGE_TAG
  only:
    - branches
    - tags

lint:
  stage: test
  image: $IMAGE_TAG
  script:
    - ruff check . --output-format=gitlab > ruff-report.json || true
    - ruff format --check .
  artifacts:
    reports:
      codequality: ruff-report.json
  needs:
    - build-container

test:python:
  stage: test
  image: $IMAGE_TAG
  parallel:
    matrix:
      - PACKAGE:
        - gds_database
        - gds_postgres
        - gds_snowflake
        - gds_vault
        - gds_mongodb
        - gds_mssql
  script:
    - cd $PACKAGE
    - pytest -v --cov=. --cov-report=xml --cov-report=term
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: $PACKAGE/coverage.xml
  needs:
    - build-container

test:powershell:
  stage: test
  image: $IMAGE_TAG
  script:
    - pwsh -NoProfile -Command "Invoke-Pester -Path ./PowerShell/tests -Output Detailed -CI"
  needs:
    - build-container

test:integration:
  stage: test
  image: $IMAGE_TAG
  services:
    - name: postgres:15
      alias: postgres
    - name: mongo:7
      alias: mongodb
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    MONGO_INITDB_ROOT_USERNAME: mongo
    MONGO_INITDB_ROOT_PASSWORD: mongo
  script:
    - export POSTGRES_HOST=postgres
    - export MONGODB_HOST=mongodb
    - pytest tests/integration -v
  needs:
    - build-container

build:packages:
  stage: package
  image: $IMAGE_TAG
  script:
    - |
      for pkg in gds_database gds_postgres gds_snowflake gds_vault gds_mongodb gds_mssql; do
        cd $pkg
        python -m build
        cd ..
      done
  artifacts:
    paths:
      - "*/dist/*.whl"
      - "*/dist/*.tar.gz"
    expire_in: 1 week
  only:
    - main
    - tags
  needs:
    - lint
    - test:python
    - test:powershell
```

## Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  containerRegistry: 'myacr.azurecr.io'
  imageName: 'dbtools-devcontainer'
  imageTag: '$(Build.BuildId)'

stages:
  - stage: Build
    jobs:
      - job: BuildContainer
        steps:
          - task: Docker@2
            displayName: Build dev container
            inputs:
              command: build
              repository: $(containerRegistry)/$(imageName)
              dockerfile: .devcontainer/Dockerfile
              tags: |
                $(imageTag)
                latest
              arguments: |
                --build-arg PYTHON_VERSION=3.13
                --build-arg CONDA_ENV_NAME=gds

          - task: Docker@2
            displayName: Push container
            inputs:
              command: push
              repository: $(containerRegistry)/$(imageName)
              tags: |
                $(imageTag)
                latest

  - stage: Test
    dependsOn: Build
    jobs:
      - job: Lint
        container: $(containerRegistry)/$(imageName):$(imageTag)
        steps:
          - script: |
              ruff check .
              ruff format --check .
            displayName: 'Run linting'

      - job: TestPython
        strategy:
          matrix:
            gds_database:
              package: 'gds_database'
            gds_postgres:
              package: 'gds_postgres'
            gds_snowflake:
              package: 'gds_snowflake'
        container: $(containerRegistry)/$(imageName):$(imageTag)
        steps:
          - script: |
              cd $(package)
              pytest -v --cov=. --cov-report=xml --junitxml=test-results.xml
            displayName: 'Run tests for $(package)'

          - task: PublishTestResults@2
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '$(package)/test-results.xml'

          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: 'Cobertura'
              summaryFileLocation: '$(package)/coverage.xml'

      - job: TestPowerShell
        container: $(containerRegistry)/$(imageName):$(imageTag)
        steps:
          - script: |
              pwsh -NoProfile -Command "Invoke-Pester -Path ./PowerShell/tests -Output Detailed -CI"
            displayName: 'Run PowerShell tests'

  - stage: Package
    dependsOn: Test
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - job: BuildPackages
        container: $(containerRegistry)/$(imageName):$(imageTag)
        steps:
          - script: |
              for pkg in gds_database gds_postgres gds_snowflake gds_vault gds_mongodb gds_mssql; do
                cd $pkg
                python -m build
                cd ..
              done
            displayName: 'Build Python packages'

          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '*/dist'
              artifactName: 'python-packages'
```

## Jenkins

Create `Jenkinsfile`:

```groovy
pipeline {
    agent {
        dockerfile {
            filename '.devcontainer/Dockerfile'
            additionalBuildArgs '--build-arg PYTHON_VERSION=3.13 --build-arg CONDA_ENV_NAME=gds'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        PYTHON_VERSION = '3.13'
        CONDA_ENV = 'gds'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                sh 'ruff check .'
                sh 'ruff format --check .'
            }
        }

        stage('Test') {
            parallel {
                stage('Python Tests') {
                    steps {
                        script {
                            def packages = ['gds_database', 'gds_postgres', 'gds_snowflake',
                                          'gds_vault', 'gds_mongodb', 'gds_mssql']
                            packages.each { pkg ->
                                sh """
                                    cd ${pkg}
                                    pytest -v --cov=. --cov-report=xml --junitxml=test-results.xml
                                    cd ..
                                """
                            }
                        }
                    }
                    post {
                        always {
                            junit '*/test-results.xml'
                            publishCoverage adapters: [coberturaAdapter('*/coverage.xml')]
                        }
                    }
                }

                stage('PowerShell Tests') {
                    steps {
                        sh 'pwsh -NoProfile -Command "Invoke-Pester -Path ./PowerShell/tests -Output Detailed -CI"'
                    }
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    docker.image('postgres:15').withRun('-e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=testdb') { postgres ->
                        docker.image('mongo:7').withRun('-e MONGO_INITDB_ROOT_USERNAME=mongo -e MONGO_INITDB_ROOT_PASSWORD=mongo') { mongo ->
                            sh """
                                export POSTGRES_HOST=localhost
                                export MONGODB_HOST=localhost
                                pytest tests/integration -v
                            """
                        }
                    }
                }
            }
        }

        stage('Build Packages') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    for pkg in gds_database gds_postgres gds_snowflake gds_vault gds_mongodb gds_mssql; do
                        cd $pkg
                        python -m build
                        cd ..
                    done
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: '*/dist/*.whl,*/dist/*.tar.gz', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

## Pre-commit Hooks

Integrate pre-commit hooks with the dev container for consistent local validation.

### Setup Pre-commit

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: mixed-line-ending

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]

  - repo: local
    hooks:
      - id: pytest-quick
        name: pytest-quick
        entry: pytest
        language: system
        args: [-v, --tb=short, -x]
        pass_filenames: false
        stages: [commit]
```

### Install Pre-commit in CI

```yaml
# GitHub Actions
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

## Best Practices

### 1. Keep Container Lightweight

- Use multi-stage builds
- Clean up apt cache
- Remove unnecessary files
- Pin dependency versions

### 2. Cache Effectively

```yaml
# Docker layer caching
- uses: docker/build-push-action@v5
  with:
    cache-from: type=registry,ref=myimage:buildcache
    cache-to: type=registry,ref=myimage:buildcache,mode=max
```

### 3. Use Matrix Builds

Test multiple configurations in parallel:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']
    database: ['postgres', 'mysql', 'sqlserver']
```

### 4. Fail Fast

```yaml
strategy:
  fail-fast: true
  matrix:
    ...
```

### 5. Use Secrets Securely

```yaml
# Never log secrets
- name: Test with credentials
  env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: |
    # Don't echo passwords!
    pytest tests/
```

### 6. Tag Images Properly

```
ghcr.io/org/repo:main
ghcr.io/org/repo:v1.2.3
ghcr.io/org/repo:sha-abc123
ghcr.io/org/repo:pr-42
```

### 7. Test Locally Before Pushing

```bash
# Act (run GitHub Actions locally)
brew install act
act -j test

# GitLab Runner locally
gitlab-runner exec docker test
```

### 8. Monitor Build Times

- Track build duration
- Optimize slow steps
- Use build time caching

### 9. Separate Build and Test

Build once, test many times with the same image.

### 10. Version Control Everything

- Dockerfile
- devcontainer.json
- CI configuration
- Requirements files

## Troubleshooting

### Issue: Container Build Timeout

Increase timeout or optimize Dockerfile:

```yaml
- uses: docker/build-push-action@v5
  timeout-minutes: 30
```

### Issue: Out of Disk Space

Clean up after jobs:

```yaml
- name: Clean up Docker
  run: docker system prune -af
```

### Issue: Rate Limiting

Use authenticated registries:

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

## Conclusion

Using dev containers in CI/CD ensures:
- **Consistency** between local and remote environments
- **Reproducibility** of builds and tests
- **Simplified** CI configuration
- **Faster** debugging (test locally first)

Choose your CI/CD platform and adapt the examples above to your needs.
