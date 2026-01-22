# How to Manage Dependencies with UV

**[<- Back to UV How-to Index](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Dependencies-green)

> [!IMPORTANT]
> **Related Docs:** [Migration Guide](./uv-migrate-from-pip.md) | [Workspaces](./uv-workspaces.md) | [Build & Publish](./uv-build-publish.md)

## Table of contents

- [Sync dependencies](#sync-dependencies)
- [Manage legacy requirements.txt](#manage-legacy-requirementstxt)
  - [Install from requirements.txt](#install-from-requirementstxt)
  - [Compile requirements.txt from pyproject.toml](#compile-requirementstxt-from-pyprojecttoml)
  - [Export from uv.lock](#export-from-uvlock)
- [Private Package Indexes](#private-package-indexes)
  - [Configure Index URLs](#configure-index-urls)
  - [Authentication](#authentication)
  - [Per-Package Index Configuration](#per-package-index-configuration)
- [Cache Management](#cache-management)
  - [View Cache Information](#view-cache-information)
  - [Clear Cache](#clear-cache)
  - [Custom Cache Location](#custom-cache-location)
  - [Offline Mode](#offline-mode)
- [Advanced Dependency Features](#advanced-dependency-features)
  - [Dependency Groups](#dependency-groups)
  - [Optional Dependencies](#optional-dependencies)
  - [Version Constraints](#version-constraints)
- [Related Guides](#related-guides)

---

## Sync dependencies

If you clone a repo with a `uv.lock` file, you can install everything exactly as specified in the lockfile:

```bash
uv sync
```

This creates/updates the `.venv` and installs all packages.

**Useful options:**

```bash
# Fail if lock file is outdated (good for CI)
uv sync --frozen

# Skip development dependencies
uv sync --no-dev

# Include specific dependency group
uv sync --group docs

# Sync all groups
uv sync --all-groups
```

---

## Manage legacy requirements.txt

`uv` respects legacy workflows and can interact with standard requirements files.

### Install from requirements.txt

To install dependencies from a `requirements.txt` into specific virtual environment:

```bash
uv pip install -r requirements.txt
```

### Compile requirements.txt from pyproject.toml

If you need to generate a `requirements.txt` for a legacy system that doesn't support `uv` (or for simple sharing):

```bash
uv pip compile pyproject.toml -o requirements.txt
```

### Export from uv.lock

Export your lock file to requirements format:

```bash
# Export all dependencies
uv export -o requirements.txt

# Export without dev dependencies
uv export --no-dev -o requirements.txt

# Export with exact versions (frozen)
uv export --frozen -o requirements.txt
```

---

## Private Package Indexes

### Configure Index URLs

**In pyproject.toml:**

```toml
[tool.uv]
# Primary index (replaces PyPI)
index-url = "https://private.pypi.example.com/simple"

# Additional indexes (searched after primary)
extra-index-url = [
    "https://pypi.org/simple",
    "https://another.index.example.com/simple",
]
```

**Via environment variables:**

```bash
export UV_INDEX_URL="https://private.pypi.example.com/simple"
export UV_EXTRA_INDEX_URL="https://pypi.org/simple"
```

**Via command line:**

```bash
uv add --index-url https://private.pypi.example.com/simple my-package
```

### Authentication

UV supports several authentication methods for private indexes:

**1. Environment Variables (Recommended for CI)**

```bash
# Generic credentials
export UV_INDEX_URL="https://user:password@private.pypi.example.com/simple"

# Or use separate variables for specific indexes
export UV_HTTP_BASIC_PRIVATE_USERNAME="myuser"
export UV_HTTP_BASIC_PRIVATE_PASSWORD="mypassword"
```

**2. .netrc File**

Create `~/.netrc`:

```
machine private.pypi.example.com
login myuser
password mypassword
```

Secure permissions:

```bash
chmod 600 ~/.netrc
```

**3. Keyring Integration**

```bash
# Install keyring
uv tool install keyring

# Store credentials
keyring set https://private.pypi.example.com/simple myuser
# Enter password when prompted

# UV automatically uses keyring
uv add my-private-package
```

**4. AWS CodeArtifact**

```bash
# Get temporary token
export CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token \
    --domain my-domain \
    --domain-owner 123456789012 \
    --query authorizationToken \
    --output text)

# Configure UV
export UV_INDEX_URL="https://aws:${CODEARTIFACT_AUTH_TOKEN}@my-domain-123456789012.d.codeartifact.us-east-1.amazonaws.com/pypi/my-repo/simple/"
```

**5. Google Artifact Registry**

```bash
export UV_INDEX_URL="https://oauth2accesstoken:$(gcloud auth print-access-token)@us-central1-python.pkg.dev/my-project/my-repo/simple/"
```

**6. Azure Artifacts**

```bash
# Use PAT (Personal Access Token)
export UV_INDEX_URL="https://user:${AZURE_PAT}@pkgs.dev.azure.com/org/project/_packaging/feed/pypi/simple/"
```

### Per-Package Index Configuration

Specify different indexes for specific packages:

```toml
[tool.uv.sources]
# Install from specific index
my-private-package = { index = "private" }

# Install from Git
my-git-package = { git = "https://github.com/org/repo.git", branch = "main" }

# Install from URL
my-url-package = { url = "https://example.com/package.whl" }

[tool.uv.index]
private = "https://private.pypi.example.com/simple"
```

---

## Cache Management

UV uses a global cache to speed up operations and save disk space.

### View Cache Information

```bash
# Show cache directory location
uv cache dir

# Show cache size
uv cache size
```

### Clear Cache

```bash
# Clear entire cache
uv cache clean

# Clear cache for specific package
uv cache clean requests

# Remove unused cache entries (safer)
uv cache prune
```

### Custom Cache Location

```bash
# Set cache directory via environment variable
export UV_CACHE_DIR="/path/to/custom/cache"

# Or in pyproject.toml is not supported - use env var
```

### Offline Mode

Work without network access using cached packages:

```bash
# Enable offline mode
export UV_OFFLINE=1

# Or per-command
uv sync --offline

# Disable caching entirely (not recommended)
export UV_NO_CACHE=1
```

---

## Advanced Dependency Features

### Dependency Groups

Organize dependencies into logical groups:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]
test = [
    "pytest>=8.0",
    "coverage>=7.0",
    "pytest-cov>=4.0",
]
```

Use groups:

```bash
# Sync with specific group
uv sync --group docs

# Sync all groups
uv sync --all-groups

# Add to specific group
uv add --group test pytest-xdist
```

### Optional Dependencies

For library authors, define optional feature sets:

```toml
[project.optional-dependencies]
postgres = ["psycopg2>=2.9"]
mysql = ["mysqlclient>=2.1"]
all = ["psycopg2>=2.9", "mysqlclient>=2.1"]
```

Install with extras:

```bash
uv add "my-package[postgres]"
uv add "my-package[all]"
```

### Version Constraints

```toml
[project]
dependencies = [
    # Minimum version
    "requests>=2.28",

    # Exact version
    "pydantic==2.5.0",

    # Version range
    "numpy>=1.24,<2.0",

    # Compatible release (>=1.4.0, <2.0.0)
    "fastapi~=1.4.0",

    # Exclude specific versions
    "urllib3>=1.26,!=2.0.0",
]
```

---

## Related Guides

- [UV Getting Started](../../../tutorials/python/uv/uv-getting-started.md)
- [UV Migration Guide](./uv-migrate-from-pip.md)
- [UV Build & Publish](./uv-build-publish.md)
- [UV Workspaces](./uv-workspaces.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
