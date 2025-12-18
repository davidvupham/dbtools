# Dev Container – Maintainers Guide

This document is for maintainers of the dev container configuration. It complements the developer-facing docs and functional spec.

## Pointers

- Developer quickstart: [docs/development/devcontainer.md](../docs/development/devcontainer.md)
- Functional & architecture spec: [docs/development/devcontainer-functional-spec.md](../docs/development/devcontainer-functional-spec.md)
- Technical architecture (diagram): [docs/development/devcontainer-architecture.md](../docs/development/devcontainer-architecture.md)
- Container config: [.devcontainer/devcontainer.json](devcontainer.json), [.devcontainer/Dockerfile](Dockerfile)

## Lifecycle expectations

- Image: Red Hat UBI 9 base; installs `unixODBC`, `msodbcsql18`, `mssql-tools18`, PowerShell 7 via Microsoft RHEL 9 repo.
- postCreate: registers `ipykernel` as `gds` and installs local packages (user site) using system Python.
- Optional JupyterLab: controlled by `ENABLE_JUPYTERLAB=1` (default off).
- postStart: not used (kept empty); VS Code server dirs are handled by VS Code itself.

## Verification

- VS Code task: “Dev: Verify Dev Container” (default test task) runs [scripts/verify_devcontainer.sh](../scripts/verify_devcontainer.sh).
- Make target: `make verify-devcontainer` performs the same checks.
- SQL tests require `MSSQL_SA_PASSWORD` if you want live connection checks.

## Change guidelines

- Favor a single consolidated `microdnf`/`dnf` RUN in Dockerfile; keep packages minimal.
- Use dynamic `${localEnv:USER}` for container user to match host user and enable proper file ownership.
- Keep multi-repo mount via `workspaceMount` to `/workspaces`.
- Avoid embedding secrets; use VS Code tasks or environment variables.

## Legacy status

- Legacy variant-specific artifacts under `.devcontainer/` have been removed.
- `.devcontainer/postCreate.sh` should remain system-Python-only; remove any legacy venv references if discovered.

## Common operations

- Rebuild container: VS Code → “Dev Containers: Rebuild and Reopen in Container”.
- Register kernelspec manually (if needed):

  ```bash
  python3 -m ipykernel install --user --name gds --display-name "Python (gds)"
  ```

- Enable JupyterLab for a session:

  ```bash
  ENABLE_JUPYTERLAB=1 code .
  # or add containerEnv in a devcontainer.local.json override
  ```
