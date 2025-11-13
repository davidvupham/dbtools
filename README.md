# DBTools Monorepo

DBTools is the shared engineering workspace for the GDS team. The repository combines production-grade Python packages, PowerShell automation modules, operational runbooks, and supporting assets for building and operating database-centric solutions across multiple environments.

## Key Capabilities
- Database client libraries for Snowflake, PostgreSQL, SQL Server, MongoDB, and Vault
- Shared abstractions (`gds-database`) that provide consistent connection patterns
- Operational services such as the Snowflake replication monitor and notification pipelines
- PowerShell tooling for Active Directory export, logging, and NuGet packaging workflows
- Comprehensive documentation, architecture notes, and CI/CD automation scripts

## Repository Layout

### Python packages
- `gds_database/` – Common abstractions and base classes for database connectivity
- `gds_postgres/` – PostgreSQL implementation on top of `gds-database`
- `gds_mssql/` – Microsoft SQL Server client with Kerberos and pooling support
- `gds_mongodb/` – MongoDB client with advanced configuration and CRUD helpers
- `gds_snowflake/` – Snowflake utilities used by monitoring tools and automation
- `gds_vault/` – HashiCorp Vault client with pluggable authentication and caching
- `gds_notification/` – Design docs and stubs for the alert ingestion service
- `gds_snmp_receiver/` – SNMP trap receiver service with FastAPI and worker pipeline
- `snowflake_monitoring/` – Application that monitors Snowflake replication health

Each package exposes its own README with full installation, configuration, and API guidance.

### PowerShell automation
- `PowerShell/Modules/GDS.Common` – PSFramework-based logging utilities shared across modules
- `PowerShell/Modules/GDS.NuGet` – Build, package, and publish helpers for PowerShell modules
- `PowerShell/Modules/GDS.ActiveDirectory` – Cmdlets for exporting AD users/groups to SQL Server
- Additional MSSQL and Windows-focused modules live alongside these core components
- Convenience scripts such as `PowerShell/BuildAllModules.ps1` and `Install-GDSModulesFromJFrog.ps1`

See `PowerShell/README.md` for module usage, build instructions, and CI pipeline details.

### Documentation & supporting assets
- `docs/` – Tutorials, architecture reviews, deployment guides, dev container walkthroughs, and historical prompts
- `schemas/` – Avro and JSON schema definitions used by data services
- `scripts/` and `examples/` – Helper utilities and sample integrations
- `cert/`, `data/`, and `dist/` – Test fixtures, generated artifacts, and packaged outputs
- Top-level evaluation reports (e.g., `GDS_ARCHITECTURE_EVALUATION_2025-11-06.md`) capture design history

## Development Quick Start

### Python workflow
1. Install Python 3.9+ and create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
2. Navigate into the target package (for example `cd gds_database`) and install dev extras: `pip install -e .[dev]`
3. Run tests with `pytest` (most packages provide additional examples under `tests/` or `examples/`)
4. Lint and format code using `ruff` via the repo helper: `./lint.sh`, `./lint.sh --fix`, or run `ruff check .`
5. Build distributions when needed with `python -m build` or the package-specific build scripts

### PowerShell workflow
1. Review `PowerShell/README.md` for prerequisites (PowerShell 7+, PSFramework, SQL/AD modules)
2. Add `PowerShell/Modules` to `PSModulePath` or import modules directly with `Import-Module GDS.Common`
3. Use `PowerShell/BuildAllModules.ps1` to run validation, build NuGet packages, and optionally publish
4. Execute `PowerShell/Install-GDSModulesFromJFrog.ps1` to install modules from Artifactory repositories
5. Run Pester tests and `Invoke-ScriptAnalyzer` as described in the module documentation

### Dev container workflow (VS Code)
1. Install the VS Code Dev Containers extension and ensure Docker is available locally
2. Open the repository in VS Code and choose **Dev Containers: Reopen in Container** (or use `code .` from within an existing container)
3. The dev container boots with Python, PowerShell 7, PSFramework, and other tooling preinstalled for a consistent environment
4. For first-time setup, tips, and troubleshooting, reference:
   - `docs/vscode/DEVCONTAINER_BEGINNERS_GUIDE.md`
   - `docs/vscode/DEVCONTAINER.md`
   - `docs/vscode/VSCODE_SETUP.md`

## Copilot in Dev Containers

- Remote extensions: The dev containers install `GitHub.copilot` and `GitHub.copilot-chat` automatically. After pulling updates, run “Dev Containers: Rebuild Container” to ensure they are installed in the remote host.
- Sign in: In the Dev Container window (green corner status), open Accounts → GitHub → Sign in. Approve the sign-in request for the remote window when prompted.
- Quick checks if sign-in fails:
   - Connectivity and proxy variables from inside the container:

```bash
curl -I https://api.github.com
nslookup github.com || getent hosts github.com
env | grep -iE 'http_proxy|https_proxy|no_proxy'
```

- Corporate proxy/CA configuration (if applicable):
   - VS Code setting: set `http.proxy` in the Dev Container window and reload.
   - System trust: add your corporate root CA and refresh trust store, then expose to Node-based extensions:

```bash
sudo cp /path/to/corp-root-ca.crt /usr/local/share/ca-certificates/corp.crt
sudo update-ca-certificates
echo 'export NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/corp.crt' | sudo tee -a /etc/profile.d/node-extra-ca.sh >/dev/null
```

   - Environment variables (set in container if required): `HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY`.

## Automation & CI
- Ruff, Black, and pytest are configured via `pyproject.toml`, `.pre-commit-config.yaml`, and `lint.sh`
- GitHub Actions workflow `.github/workflows/powershell-modules-jfrog.yml` validates, builds, and publishes PowerShell modules to JFrog Artifactory
- Documentation under `PowerShell/Modules/GDS.NuGet/` describes the CI/CD pipeline, secrets, and runbook steps

## Documentation
- Module and package documentation: see the README within each component directory
- `PowerShell/FINAL_IMPLEMENTATION_SUMMARY.md` and `PowerShell/MODULE_ORGANIZATION.md` outline the PowerShell architecture
- Detailed guides in `PowerShell/Modules/GDS.NuGet/` (NuGet build, JFrog publishing) and `PowerShell/Modules/GDS.Common/` (logging)
- Dev container guides: `docs/vscode/DEVCONTAINER_BEGINNERS_GUIDE.md`, `docs/vscode/DEVCONTAINER.md`, and `docs/vscode/DEVCONTAINER_SQLTOOLS.md`
- Architecture and implementation reports in the repo root (for example `PACKAGE_CREATION_SUMMARY.md`, `SNOWFLAKE_CONNECTIVITY_TESTING_GUIDE.md`)

## Contributing & Support
- Use GitHub Issues at https://github.com/davidvupham/dbtools/issues for bug reports and feature requests
- Follow package-specific contributing guidance where provided (e.g., `docs/DEVELOPER_GUIDE.md` within each package)
- Contact the GDS engineering team via gds@example.com for internal support or onboarding assistance
