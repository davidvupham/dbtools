# Dev Container – Maintainers Guide

This document is for maintainers of the dev container configuration. It complements the developer-facing docs and functional spec.

## Pointers

- Developer quickstart: [docs/development/devcontainer.md](../docs/development/devcontainer.md)
- Functional & architecture spec: [docs/development/devcontainer-functional-spec.md](../docs/development/devcontainer-functional-spec.md)
- Technical architecture (diagram): [docs/development/devcontainer-architecture.md](../docs/development/devcontainer-architecture.md)
- Container config: [.devcontainer/devcontainer.json](devcontainer.json), [.devcontainer/Dockerfile](Dockerfile)

## Lifecycle expectations

- Image: Red Hat UBI 9 base; installs `unixODBC`, `msodbcsql18`, `mssql-tools18`, and PowerShell 7 via the Microsoft RHEL 9 repo.
- postCreate: installs `uv`, provisions Python 3.13, runs `uv sync --group devcontainer` to install all workspace packages and tooling; registers `ipykernel` as `gds`.
- Optional: `ENABLE_JUPYTERLAB=1` for JupyterLab, `ENABLE_DBATOOLS=1` for dbatools module.
- postStart: not used (kept empty).

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
- Use `uv run <command>` for all Python commands (no manual venv activation needed).

## Common operations

- Rebuild container: VS Code → “Dev Containers: Rebuild and Reopen in Container”.
- Register kernelspec manually (if needed):

  ```bash
  uv run python -m ipykernel install --user --name gds --display-name "Python (gds)"
  ```

- Enable JupyterLab for a session:

  ```bash
  # Recommended: add containerEnv in a .devcontainer/devcontainer.local.json override
  ```
