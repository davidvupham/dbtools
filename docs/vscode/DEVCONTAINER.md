# Dev Container Setup

This repository includes a VS Code Dev Container to provide a reproducible Miniconda-based Python environment.

## What you get

- Base image: Miniconda3 (continuumio/miniconda3:latest)
- Conda environment: `gds` with the latest available Python
- Auto-activation of `gds` for interactive shells
- Python extensions preinstalled (Python, Pylance, GitHub Copilot)
- Post-create command installs local editable packages: gds_database, gds_postgres, gds_snowflake, gds_vault

For a step-by-step beginner’s walkthrough (what Docker is, how the Dockerfile and devcontainer.json work, and how to build/run), see:
- `DEVCONTAINER_BEGINNERS_GUIDE.md`

## Open in Dev Container

1. Ensure you have the "Dev Containers" extension installed.
2. Open this folder in VS Code.
3. When prompted, "Reopen in Container".
   - Or run: Command Palette → Dev Containers: Rebuild and Reopen in Container

## Notes

- Default interpreter is `/opt/conda/envs/gds/bin/python`
- To verify:
  ```bash
  python -V
  which python
  conda env list
  ```
- Update the `postCreateCommand` in `.devcontainer/devcontainer.json` if you want to customize package installs.

### Kerberos configuration (optional)

- A template is provided at `.devcontainer/krb5/krb5.conf`. Edit this file to set your REALM and KDC.
- The dev container bind-mounts this file to `/etc/krb5.conf` and sets `KRB5_CONFIG` accordingly.
- To acquire a ticket:
  ```bash
  kinit user@EXAMPLE.COM
  klist
  ```
  Replace realm and KDC to match your environment.
