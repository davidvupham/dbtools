# DBTools Monorepo

DBTools is the shared engineering workspace for the GDS team. The repository combines production-grade Python packages, PowerShell automation modules, operational runbooks, and supporting assets for building and operating database-centric solutions across multiple environments.

## Key Capabilities
- Database client libraries for Snowflake, PostgreSQL, SQL Server, MongoDB, and Vault
- Shared abstractions (`gds-database`) that provide consistent connection patterns
- **Observability & Messaging**: Unified metrics (`gds_metrics`), Kafka integration (`gds_kafka`), and alerting
- **Benchmarking**: Automated performance testing frameworks (`gds_benchmark`, `gds_hammerdb`)
- Operational services such as the Snowflake replication monitor and notification pipelines
- **Infrastructure as Code**: Ansible playbooks for Windows management and PowerShell automation
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
- `gds_liquibase/` – Database change management with Liquibase integration and CI/CD workflows
- `gds_kafka/` – Kafka producer/consumer clients, metrics, and logging handlers
- `gds_metrics/` – Unified metrics collector supporting OpenTelemetry, Prometheus, and Kafka backends
- `gds_benchmark/` – Abstract interfaces and models for performance benchmarking tools
- `gds_hammerdb/` – Automated HammerDB benchmarking for PostgreSQL and SQL Server
- `gds_notification/` – Design docs and stubs for the alert ingestion service
- `gds_snmp_receiver/` – SNMP trap receiver service with FastAPI and worker pipeline
- `snowflake_monitoring/` – Application that monitors Snowflake replication health

Each package exposes its own README with full installation, configuration, and API guidance.

### Ansible automation
- `ansible/` – Playbooks and roles for Windows server management
  - `windows_service_account_rights.yml` – Manage service account privileges (Lock Pages, Volume Maintenance)
  - `roles/windows_service_account_rights/` – Reusable role for user rights assignment

### PowerShell automation
- `PowerShell/Modules/GDS.Logging` – PSFramework-based logging utilities (replaces `GDS.Common`)
- `PowerShell/Modules/GDS.NuGet` – Build, package, and publish helpers for PowerShell modules
- `PowerShell/Modules/GDS.ActiveDirectory` – Cmdlets for exporting AD users/groups to SQL Server
- `PowerShell/Modules/GDS.MSSQL.AvailabilityGroups` – SQL Server availability group management
- `PowerShell/Modules/GDS.MSSQL.Build` – SQL Server build and deployment automation
- `PowerShell/Modules/GDS.MSSQL.Core` – Core SQL Server cmdlets and utilities
- `PowerShell/Modules/GDS.MSSQL.Monitor` – SQL Server monitoring and alerting
- `PowerShell/Modules/GDS.Security` – Script signing and certificate management utilities
- `PowerShell/Modules/GDS.Windows` – Windows OS administration and WinRM configuration (replaces `GDS.WindowsOS`)
- Convenience scripts such as `PowerShell/BuildAllModules.ps1` and `Install-GDSModulesFromJFrog.ps1`

See `PowerShell/README.md` for module usage, build instructions, and CI pipeline details.

### Documentation & supporting assets
- `docs/tutorials/` – Comprehensive tutorials for:
  - Liquibase database change management with SQL Server
  - Kafka and RabbitMQ message queue integration
  - Python OOP concepts and exercises
  - Docker containerization
  - PowerShell beginners guide
  - Vault secret management
- `docs/how-to/` – Task-oriented guides:
  - Configure WinRM over HTTPS (`docs/how-to/Configure-WinRM-HTTPS.md`)
- `docs/explanation/` – Background and concepts:
  - Windows Certificates and CSRs (`docs/explanation/Windows-Certificates-and-CSRs.md`)
- `docs/architecture/` – Architecture documentation for:
  - Database change CI/CD pipelines
  - Liquibase integration patterns
  - OpenTelemetry observability architecture
- `docs/vscode/` – Dev container setup guides and troubleshooting. See [docs/development/vscode/README.md](docs/development/vscode/README.md)
- `docs/runbooks/` – Operational procedures and runbooks
- `docs/development/` – Development guidelines and standards (including Coding Standards)
- `schemas/` – Avro and JSON schema definitions used by data services
- `scripts/` and `examples/` – Helper utilities and sample integrations
- `docker/` – Docker configurations for development and testing environments
- `cert/`, `data/`, and `dist/` – Test fixtures, generated artifacts, and packaged outputs
- Top-level reports (e.g., `PACKAGE_CREATION_SUMMARY.md`, `SNOWFLAKE_CONNECTIVITY_TESTING_GUIDE.md`) capture project history

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
   - `docs/development/vscode/devcontainer-beginners-guide.md`
   - `docs/development/vscode/devcontainer.md`
   - `docs/development/vscode/features.md`

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
- Detailed guides in `PowerShell/Modules/GDS.NuGet/` (NuGet build, JFrog publishing) and `PowerShell/Modules/GDS.Logging/` (logging)
- Dev container guides: `docs/development/vscode/devcontainer-beginners-guide.md`, `docs/development/vscode/devcontainer.md`, and `docs/development/vscode/devcontainer-sqltools.md`
- Liquibase tutorial: `docs/tutorials/liquibase/sqlserver-liquibase-tutorial.md` – Comprehensive guide with hands-on examples
- Architecture documentation: `docs/architecture/` covers database change CI/CD, Liquibase patterns, and OpenTelemetry observability
- Tutorial catalog: `docs/tutorials/README.md` indexes all available learning resources
- Implementation reports in the repo root (e.g., `PACKAGE_CREATION_SUMMARY.md`, `SNOWFLAKE_CONNECTIVITY_TESTING_GUIDE.md`)

## Contributing & Support
- Use GitHub Issues at https://github.com/davidvupham/dbtools/issues for bug reports and feature requests
- Follow package-specific contributing guidance where provided (e.g., `docs/DEVELOPER_GUIDE.md` within each package)
- Contact the GDS engineering team via gds@example.com for internal support or onboarding assistance
