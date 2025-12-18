# Dev Container – Maintainers Guide

This document is for maintainers of the dev container configuration. It complements the developer-facing docs and functional spec.

## Pointers

- Developer quickstart: [docs/development/devcontainer.md](../docs/development/devcontainer.md)
- Functional & architecture spec: [docs/development/devcontainer-functional-spec.md](../docs/development/devcontainer-functional-spec.md)
- Technical architecture (diagram): [docs/development/devcontainer-architecture.md](../docs/development/devcontainer-architecture.md)
- Container config: [.devcontainer/devcontainer.json](devcontainer.json), [.devcontainer/Dockerfile](Dockerfile)

## Lifecycle expectations

- Image: Red Hat UBI 9 base; installs `unixODBC`, `msodbcsql18`, `mssql-tools18`, PowerShell 7 via Microsoft RHEL 9 repo.
- postCreate: creates `.venv`, installs base tooling + `pyodbc`, registers `ipykernel` as `gds`.
- Optional JupyterLab: controlled by `ENABLE_JUPYTERLAB=1` (default off).
- postStart: installs local packages in editable mode, keeps VS Code server dirs sane.

## Verification

- VS Code task: “Dev: Verify Dev Container” (default test task) runs [scripts/verify_devcontainer.sh](../scripts/verify_devcontainer.sh).
- Make target: `make verify-devcontainer` performs the same checks.
- SQL tests require `MSSQL_SA_PASSWORD` if you want live connection checks.

## Change guidelines

- Favor a single consolidated `microdnf`/`dnf` RUN in Dockerfile; keep packages minimal.
- Preserve non-root `vscode` user, read-only SSH mount, and `docker.sock` mount only if needed.
- Keep multi-repo mount via `workspaceMount` to `/workspaces`.
- Avoid embedding secrets; use VS Code tasks or environment variables.

## Legacy status

- Conda-based variants and troubleshooting artifacts under `.devcontainer/` have been removed.
- `.devcontainer/postCreate.sh` should remain venv-only; remove any remaining Conda fallbacks if discovered.

## Common operations

- Rebuild container: VS Code → “Dev Containers: Rebuild and Reopen in Container”.
- Force venv refresh:

  ```bash
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip ruff pytest pytest-cov pyright pyodbc ipykernel
  python -m ipykernel install --user --name gds --display-name "Python (gds)"
  ```

- Enable JupyterLab for a session:

  ```bash
  ENABLE_JUPYTERLAB=1 code .
  # or add containerEnv in a devcontainer.local.json override
  ```
