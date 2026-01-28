# How to Build and Publish Packages with UV

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Publishing-blue)

> [!IMPORTANT]
> **Related Docs:** [Workspaces](./uv-workspaces.md) | [CI/CD Integration](./uv-ci-cd-integration.md)

This guide covers building Python packages and publishing them to PyPI or private package indexes using UV.

## Table of contents

- [Prerequisites](#prerequisites)
- [Building Packages](#building-packages)
  - [Build Wheel and Source Distribution](#build-wheel-and-source-distribution)
  - [Build Options](#build-options)
  - [Building Workspace Packages](#building-workspace-packages)
- [Publishing to PyPI](#publishing-to-pypi)
  - [Set Up PyPI Credentials](#set-up-pypi-credentials)
  - [Publish Your Package](#publish-your-package)
  - [Publishing to TestPyPI](#publishing-to-testpypi)
- [Publishing to Private Indexes](#publishing-to-private-indexes)
  - [Artifactory](#artifactory)
  - [AWS CodeArtifact](#aws-codeartifact)
  - [Azure Artifacts](#azure-artifacts)
  - [Google Artifact Registry](#google-artifact-registry)
- [CI/CD Publishing](#cicd-publishing)
  - [GitHub Actions with Trusted Publishing](#github-actions-with-trusted-publishing)
  - [GitHub Actions with API Token](#github-actions-with-api-token)
  - [GitLab CI](#gitlab-ci)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Related Guides](#related-guides)

---

## Prerequisites

Before publishing, ensure your `pyproject.toml` has the required metadata:

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "A short description of your package"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["python", "example"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "requests>=2.28",
]

[project.urls]
Homepage = "https://github.com/you/my-package"
Documentation = "https://my-package.readthedocs.io"
Repository = "https://github.com/you/my-package"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Building Packages

### Build Wheel and Source Distribution

```bash
# Build both wheel (.whl) and source distribution (.tar.gz)
uv build
```

Output goes to `dist/`:

```
dist/
├── my_package-0.1.0-py3-none-any.whl
└── my_package-0.1.0.tar.gz
```

### Build Options

```bash
# Build only wheel
uv build --wheel

# Build only source distribution
uv build --sdist

# Custom output directory
uv build --out-dir ./packages

# Verify build without publishing
uv build && ls -la dist/
```

### Building Workspace Packages

In a monorepo with multiple packages:

```bash
# Build a specific package
uv build --package my-core

# Build all packages
for pkg in packages/*/; do
    name=$(basename "$pkg")
    uv build --package "$name"
done
```

---

## Publishing to PyPI

### Set Up PyPI Credentials

**Option 1: API Token (Recommended)**

1. Create an API token at https://pypi.org/manage/account/token/
2. Use the token when publishing:

```bash
uv publish --token pypi-AgEIcH...
```

**Option 2: Environment Variable**

```bash
export UV_PUBLISH_TOKEN="pypi-AgEIcH..."
uv publish
```

**Option 3: Keyring (for interactive use)**

```bash
# Install keyring
uv tool install keyring

# Store credentials
keyring set https://upload.pypi.org/legacy/ __token__
# Enter your API token when prompted

# UV will automatically use keyring
uv publish
```

### Publish Your Package

```bash
# Build and publish in one step
uv build && uv publish

# Or publish existing dist files
uv publish dist/*
```

### Publishing to TestPyPI

Always test on TestPyPI first:

```bash
# Create a TestPyPI token at https://test.pypi.org/manage/account/token/

# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-AgEIcH...

# Test installation from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ my-package
```

---

## Publishing to Private Indexes

### Artifactory

```bash
# Set credentials
export UV_PUBLISH_USERNAME="your-username"
export UV_PUBLISH_PASSWORD="your-api-key"

# Publish
uv publish --publish-url https://artifactory.example.com/api/pypi/pypi-local/
```

### AWS CodeArtifact

```bash
# Get auth token
export CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token \
    --domain my-domain \
    --domain-owner 123456789012 \
    --query authorizationToken \
    --output text)

export UV_PUBLISH_USERNAME="aws"
export UV_PUBLISH_PASSWORD="$CODEARTIFACT_AUTH_TOKEN"

# Publish
uv publish --publish-url https://my-domain-123456789012.d.codeartifact.us-east-1.amazonaws.com/pypi/my-repo/
```

### Azure Artifacts

```bash
# Use PAT (Personal Access Token)
export UV_PUBLISH_USERNAME="your-username"
export UV_PUBLISH_PASSWORD="your-pat"

# Publish
uv publish --publish-url https://pkgs.dev.azure.com/org/project/_packaging/feed/pypi/upload/
```

### Google Artifact Registry

```bash
# Get access token
export UV_PUBLISH_USERNAME="oauth2accesstoken"
export UV_PUBLISH_PASSWORD=$(gcloud auth print-access-token)

# Publish
uv publish --publish-url https://us-central1-python.pkg.dev/my-project/my-repo/
```

---

## CI/CD Publishing

### GitHub Actions with Trusted Publishing

PyPI supports OIDC authentication for GitHub Actions (no secrets needed):

1. Configure trusted publisher on PyPI:
   - Go to https://pypi.org/manage/project/YOUR-PROJECT/settings/publishing/
   - Add GitHub as a trusted publisher

2. Create workflow:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v7

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        run: uv publish --trusted-publishing always
```

### GitHub Actions with API Token

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v7

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
        run: uv publish
```

### GitLab CI

```yaml
# .gitlab-ci.yml
publish:
  stage: deploy
  image: ghcr.io/astral-sh/uv:python3.12-bookworm-slim
  rules:
    - if: $CI_COMMIT_TAG
  script:
    - uv build
    - uv publish --token $PYPI_API_TOKEN
```

---

## Best Practices

### 1. Version Management

Use semantic versioning and consider tools like `bump2version`:

```bash
# Install bump2version
uvx bump2version patch  # 0.1.0 -> 0.1.1
uvx bump2version minor  # 0.1.1 -> 0.2.0
uvx bump2version major  # 0.2.0 -> 1.0.0
```

### 2. Always Test Before Publishing

```bash
# 1. Build
uv build

# 2. Test installation locally
uv venv /tmp/test-install
uv pip install --python /tmp/test-install dist/*.whl
/tmp/test-install/bin/python -c "import my_package; print(my_package.__version__)"

# 3. Publish to TestPyPI first
uv publish --publish-url https://test.pypi.org/legacy/ --token $TEST_PYPI_TOKEN

# 4. Test from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ my-package

# 5. Publish to PyPI
uv publish --token $PYPI_TOKEN
```

### 3. Include Necessary Files

Ensure your build includes all necessary files via `pyproject.toml`:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/tests",
    "/README.md",
    "/LICENSE",
]
```

### 4. Protect Your Tokens

- Never commit tokens to version control
- Use environment variables or CI/CD secrets
- Prefer trusted publishing (OIDC) when available
- Use scoped tokens with minimum required permissions

---

## Troubleshooting

### "Package already exists"

You cannot overwrite an existing version on PyPI. Bump the version number:

```bash
# Edit version in pyproject.toml, then:
uv build && uv publish
```

### "Invalid credentials"

```bash
# Verify your token
echo $UV_PUBLISH_TOKEN | head -c 20

# Try with explicit token
uv publish --token "pypi-AgEIcH..."
```

### "Missing metadata"

Ensure all required fields in `pyproject.toml`:

```toml
[project]
name = "required"
version = "required"
description = "recommended"
readme = "recommended"
```

### Build fails with "No module named..."

Ensure build dependencies are declared:

```toml
[build-system]
requires = ["hatchling"]  # or setuptools, flit-core, etc.
build-backend = "hatchling.build"
```

---

## Related Guides

- [UV Getting Started](../../../tutorials/languages/python/uv/uv-getting-started.md)
- [UV Workspaces](./uv-workspaces.md)
- [UV CI/CD Integration](./uv-ci-cd-integration.md)
- [Official UV Publishing Docs](https://docs.astral.sh/uv/guides/publish/)
