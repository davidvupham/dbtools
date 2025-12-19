# Dev Container – Maintainers Guide

This document is for maintainers of the dev container configuration. It complements the developer-facing docs and functional spec.

## Pointers

- Developer quickstart: [docs/development/devcontainer.md](../docs/development/devcontainer.md)
- Functional & architecture spec: [docs/development/devcontainer-functional-spec.md](../docs/development/devcontainer-functional-spec.md)
- Technical architecture (diagram): [docs/development/devcontainer-architecture.md](../docs/development/devcontainer-architecture.md)
- Container config: [.devcontainer/devcontainer.json](devcontainer.json), [.devcontainer/Dockerfile](Dockerfile)

## Lifecycle expectations

- Image: Red Hat UBI 9 base; installs `unixODBC`, `msodbcsql18`, and `mssql-tools18` via the Microsoft RHEL 9 repo.
- postCreate: uses system `/usr/bin/python3` only to bootstrap `uv`, then provisions/uses a repo-local `.venv/` and installs tooling + local packages into that venv; registers `ipykernel` as `gds`.
- Optional JupyterLab: controlled by `ENABLE_JUPYTERLAB=1` (default off).
- postStart: not used (kept empty); VS Code server dirs are handled by VS Code itself.

## Verification

- VS Code task: “Dev: Verify Dev Container” (default test task) runs [scripts/verify_devcontainer.sh](../scripts/verify_devcontainer.sh).
- Make target: `make verify-devcontainer` performs the same checks.
- SQL tests require `MSSQL_SA_PASSWORD` if you want live connection checks.

## Change guidelines

- Favor a single consolidated `microdnf`/`dnf` RUN in Dockerfile; keep packages minimal.
- Use dynamic `${localEnv:USER}` for container user to match host user and enable proper file ownership.
- Keep multi-repo mount via `workspaceMount` to `/workspaces/devcontainer`.
- Avoid embedding secrets; use VS Code tasks or environment variables.

## Legacy status

- Legacy variant-specific artifacts under `.devcontainer/` have been removed.
- `.devcontainer/postCreate.sh` should keep the uv + repo-local `.venv/` approach as the canonical path; system Python is a bootstrap fallback only.

## Common operations

- Rebuild container: VS Code → “Dev Containers: Rebuild and Reopen in Container”.
- Register kernelspec manually (if needed):

  ```bash
  python -m ipykernel install --user --name gds --display-name "Python (gds)"
  ```

- Enable JupyterLab for a session:

  ```bash
  # Recommended: add containerEnv in a .devcontainer/devcontainer.local.json override
  ```
