# Dev Container

Quick links:

- Developer guide: [docs/development/devcontainer.md](../docs/development/devcontainer.md)
  - [Verification steps](../docs/development/devcontainer.md#verify)
- Functional & architecture spec: [docs/development/devcontainer-functional-spec.md](../docs/development/devcontainer-functional-spec.md)
- Technical architecture (diagram): [docs/development/devcontainer-architecture.md](../docs/development/devcontainer-architecture.md)
- Maintainers: [.devcontainer/MAINTAINERS.md](MAINTAINERS.md)

## Canonical Configuration (Red Hat UBI 9 + Python 3.13 via uv)

- Base image: Red Hat UBI 9 (`registry.access.redhat.com/ubi9/ubi`).
- Python `3.13` provisioned via `uv` during `postCreate`. Run commands with `uv run <command>`.
- System tooling: `msodbcsql18`, `mssql-tools18` (`sqlcmd`), `unixODBC` dev headers, PowerShell 7.
- Multi-repo: parent folder mounted at `/workspaces/devcontainer`; workspace at `/workspaces/devcontainer/<repo>`.
- Optional: `ENABLE_JUPYTERLAB=1` for JupyterLab, `ENABLE_DBATOOLS=1` for dbatools PowerShell module.
- Docker access: host socket mounted; user auto-added to docker group during `postCreate`.

### Rebuild & Verify

1. Dev Containers: Rebuild and Reopen in Container
2. Run the default task "Dev: Verify Dev Container" or:

```bash
make verify-devcontainer
```

### WSL Notes

- Use Docker Desktop with WSL2 backend, and keep the repo under the WSL Linux filesystem for best performance.
- The same UBI 9 image runs in WSL; verification tasks and port forwarding work identically.
