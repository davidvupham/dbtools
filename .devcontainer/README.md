# Dev Container

Quick links:

- Developer guide: [docs/development/devcontainer.md](../docs/development/devcontainer.md)
  - [Verification steps](../docs/development/devcontainer.md#verify)
- Functional & architecture spec: [docs/development/devcontainer-functional-spec.md](../docs/development/devcontainer-functional-spec.md)
- Technical architecture (diagram): [docs/development/devcontainer-architecture.md](../docs/development/devcontainer-architecture.md)
- Maintainers: [.devcontainer/MAINTAINERS.md](MAINTAINERS.md)

## Canonical Configuration (Red Hat UBI 9 + Python 3.13 via uv)

- Base image: Red Hat UBI 9 (`registry.access.redhat.com/ubi9/ubi`).
- Python `3.13` is provisioned during `postCreate` via `uv` into a repo-local venv at `.venv/` (system `/usr/bin/python3` remains available as fallback).
- System tooling: `msodbcsql18`, `mssql-tools18` (`sqlcmd`), `unixODBC` dev headers, PowerShell 7 (installed via Microsoft RHEL 9 repo).
- Multi-repo: parent folder mounted at `/workspaces/devcontainer`; workspace at `/workspaces/devcontainer/<repo>`.
- Optional JupyterLab: set `ENABLE_JUPYTERLAB=1` to install during `postCreate`.
- Docker access: the host Docker socket is mounted at `/var/run/docker.sock`. During `postCreate`, we automatically add the devcontainer user to the socket's group so `docker` commands work. If you still see "permission denied", reopen your terminals (group membership is picked up on new shells).

### Rebuild & Verify

1. Dev Containers: Rebuild and Reopen in Container
2. Run the default task "Dev: Verify Dev Container" or:

```bash
make verify-devcontainer
```

### WSL Notes

- Use Docker Desktop with WSL2 backend, and keep the repo under the WSL Linux filesystem for best performance.
- The same UBI 9 image runs in WSL; verification tasks and port forwarding work identically.
