# gds_dbtool Testing Guide

This directory contains the integration and unit tests for the `gds_dbtool` CLI.

## Integration Tests

The integration tests run against a **real HashiCorp Vault instance** running in a container. This ensures that the CLI correctly handles authentication, networking, and API interactions in an environment that closely mirrors production.

### Prerequisites

1.  **Container Runtime**: You must have **Podman** (recommended for RHEL/Linux) or **Docker** installed.
    - The test runner will automatically detect `podman` first, then fall back to `docker`.
2.  **UV Package Manager**: The project uses `uv` for dependency management and running tests.

### Running the Tests

To run the full suite of integration tests:

```bash
# Navigate to the monorepo root (or python/gds_dbtool)
cd python/gds_dbtool

# Run tests using uv
uv run pytest tests/integration/test_vault_integration.py -v
```

### Configuration Options

#### Corporate Proxies
If you are behind a corporate proxy and cannot pull images from Docker Hub, you can specify a registry prefix using the `REGISTRY_PREFIX` environment variable.

```bash
export REGISTRY_PREFIX="docker-remote.artifactory.corp/"
uv run pytest tests/integration/test_vault_integration.py -v
```

### How It Works

1.  **Fixture Setup** (`conftest.py`):
    - Automatically builds a Vault container image from `tests/docker/Dockerfile`.
    - Starts the container on port 8200.
    - Waits for the Vault service to be healthy (`/sys/health`).
2.  **Test Configuration**:
    - Injects a `VAULT_TOKEN=root` environment variable.
    - Patches the application configuration to point to `http://localhost:8200`.
    - Patches `load_token` to bypass local keyring/file storage.
3.  **Authentication**:
    - The tests simulate an authenticated state using the root token, bypassing the need for an interactive `login` command during automated testing.

### troubleshooting

**`Command not found: podman` or `docker`**
Ensure your container runtime is in your `$PATH`.
- **RHEL/Fedora**: `sudo dnf install podman`
- **WSL 2**: Ensure Docker Desktop integration is enabled for your distro.

**`ConnectionRefusedError`**
If tests fail to connect, check if port **8200** is already in use by another Vault instance. The tests require this port to be free on localhost.

**`Auth Errors`**
If you see authentication errors, ensure `tests/integration/conftest.py` is correctly patching `gds_dbtool.commands.vault.load_token`. This should be handled automatically by the test fixtures.
