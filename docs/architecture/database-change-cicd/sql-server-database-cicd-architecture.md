### SQL Server Database CI/CD Architecture

This document defines a practical, production-grade CI/CD architecture for Microsoft SQL Server database objects (tables, views, stored procedures, functions, triggers, schemas). It includes tool options, best practices, recommended patterns, and example pipeline shapes for common CI platforms.

## Goals and non-goals

- Goals
  - Version, test, and deploy database schema and programmable objects safely and repeatably
  - Support incremental change with auditability and approvals
  - Handle environment-specific configuration and secrets securely
  - Detect and minimize schema drift between environments
  - Provide rollback/mitigation strategies
- Non-goals
  - Full infrastructure automation of SQL Server instances (covered elsewhere by IaC)
  - Data warehousing/ELT modeling (dbt, Synapse, etc. are out of scope here)

## Approaches and tools

There are two primary strategies for database delivery. Both are proven for SQL Server; the choice depends on team preferences and constraints.

- State-based (declarative)
  - Tools: SQL Server Data Tools (SSDT), DacFx, `sqlpackage` (DACPAC)
  - How it works: Source control contains a desired model of the database. During deploy, a diff is computed and applied.
  - Strengths: Simple desired-state model; automatic diffing; mature Microsoft tooling; built-in drift reports
  - Caveats: Complex/unsafe diffs may need customization; data migrations require pre/post-deploy scripts

- Migration-based (imperative)
  - Tools: Flyway (recommended), Liquibase
  - How it works: Source control contains an ordered series of migration scripts executed exactly once per environment.
  - Strengths: Explicit change history; deterministic; excellent for complex data migrations; easy to reason about roll-forward
  - Caveats: Requires discipline for idempotency/backward-compatibility; drift detection is opt-in

Either approach is valid. Many teams adopt a hybrid: migration-first for production deployments and SSDT/DACPAC for validation, review, and drift reporting.

## Recommended architecture (migration-first + optional SSDT validation)

- Source control layout
  - `database/`
    - `migrations/` (ordered SQL migrations; e.g., `V0001__create_tables.sql`)
    - `repeatable/` (repeatable scripts e.g., views, permissions; e.g., `R__views.sql`)
    - `test/` (tSQLt tests)
    - `seed/` (safe static data seeds)
    - `predeploy/` and `postdeploy/` (guardrails, data backfills, smoke checks)
  - Optionally: `ssdt/` (Visual Studio database project to produce DACPAC for diff/drift only)

- CI pipeline (per push / PR)
  1) Lint and static analysis
     - T-SQL linting (e.g., SQLFluff with `tsql` dialect)
     - Optional SonarQube rules for T-SQL
  2) Build/validate migrations
     - Spin up ephemeral SQL Server (container) and run `flyway migrate` against it
     - Run `flyway info` to verify state; fail on pending/failed
  3) Unit tests
     - Install tSQLt in the ephemeral DB; run tests (fail CI on red)
  4) Package artifacts
     - Publish a “migration bundle” (zipped migrations + config) as CI artifact
     - Optional: Build SSDT project to DACPAC; attach DACPAC and generated deployment script for review

- CD pipeline (multi-stage: Dev → Test → Staging → Prod)
  - Dev/Test: automatic on successful CI
  - Staging/Prod: gated with approvals and change windows
  - Steps per environment:
    1) Retrieve artifact (migration bundle, optional DACPAC)
    2) Resolve secrets/config from the platform vault (Key Vault, GitHub/Azure DevOps secrets)
    3) Pre-deploy checks (connectivity, blockers, required permissions, maintenance window)
    4) `flyway migrate` against target database
    5) Post-deploy validation (smoke tests; optional tSQLt subset)
    6) Observability hooks (metrics, logs, drift check schedule)

## Best practices

- Version control and review
  - All schema and programmable objects must be committed and peer-reviewed via PRs
  - Keep migrations small, incremental, and reversible (via forward fixes)

- Backward-compatible change pattern (expand/contract)
  - Expand: add new nullable columns, create new objects; deploy application changes to write/read new structures
  - Migrate/backfill data in batches; verify reads/writes
  - Contract: drop/rename old columns/objects in a later release

- Idempotency and safety
  - Use guards in scripts (existence checks) for repeatable objects (views, procs, permissions)
  - Separate destructive operations into explicit steps with approvals

- Data migrations
  - Use online, chunked updates to minimize locks; consider off-peak scheduling
  - Record timing and affected rows; alert on anomalies

- Rollback strategy
  - Prefer roll-forward: ship a corrective migration quickly
  - Keep recent verified backups and restore runbooks for catastrophic recovery
  - For risky releases, take a pre-change schema snapshot and enable point-in-time restore

- Security and secrets
  - Use least-privilege deployment identities; separate read/write/admin roles
  - Store secrets in the platform vault; never in repo or logs

- Drift detection
  - Schedule drift checks:
    - Flyway: `info`, `validate`, or `check` (enterprise features vary by edition)
    - SSDT/DacFx: `sqlpackage /Action:DriftReport` and schema compare reports
  - Treat drift as defects; address via migrations or configuration policy

- Testing
  - tSQLt for unit tests (functions, procedures, triggers)
  - Post-deploy smoke tests (object existence, critical stored proc calls)
  - Optionally performance tests on staging (query store/regression comparisons)

- Observability
  - Emit deployment events/metrics to centralized logging (duration, scripts run, rows affected)
  - Alert on failed migrations, long locks, or regression signals

## Tooling details

- Flyway (Community/Enterprise)
  - Pros: Simple, deterministic migrations; multi-DB; rich CI integrations
  - Features: Versioned and repeatable migrations, placeholders, callbacks, dry runs
  - Usage: `flyway -url=jdbc:sqlserver://... -user=... -password=... migrate`

- SSDT + DacFx + `sqlpackage`
  - Pros: First-party Microsoft tooling; strong diff and drift reporting; DACPAC artifact
  - Usage highlights:
    - Publish: `sqlpackage /Action:Publish /SourceFile:db.dacpac /TargetConnectionString:...`
    - Script only: `sqlpackage /Action:Script ...` (for review)
    - Drift report: `sqlpackage /Action:DriftReport ...`

- Liquibase (alternative to Flyway)
  - Pros: Mature migration framework; changelog YAML/XML/SQL; strong rollback patterns
  - Consider when: You prefer declarative changelogs and Liquibase ecosystem

- tSQLt
  - Unit test framework inside SQL Server; integrates with CI easily via T-SQL

- SQLFluff (tsql dialect)
  - Enforce style and some safety checks on T-SQL in CI

## Liquibase examples (CLI and GitHub Actions)

These examples target SQL Server. Adjust the JDBC URL and driver as needed for PostgreSQL or Snowflake.

### CLI

- Minimal update (inline credentials)

```bash
liquibase \
  --url="jdbc:sqlserver://<HOST>:<PORT>;databaseName=<DB>" \
  --username="<USER>" \
  --password="<PASS>" \
  --changelog-file="database/changelog/changelog.xml" \
  update
```

- Using environment variables (preferred for CI)

```bash
export LIQUIBASE_URL="jdbc:sqlserver://<HOST>:<PORT>;databaseName=<DB>"
export LIQUIBASE_USERNAME="<USER>"
export LIQUIBASE_PASSWORD="<PASS>"
export LIQUIBASE_CHANGELOG_FILE="database/changelog/changelog.xml"

liquibase update
```

- Dry run (generate SQL without executing)

```bash
liquibase updateSQL > deploy.sql
```

- Rollback by tag (ensure you tag deployments)

```bash
# Apply a tag after a successful deployment
liquibase tag --tag="release_2025_11_11"

# Roll back to a previous tag
liquibase rollback --tag="release_2025_10_31"
```

- Common JDBC URLs
  - PostgreSQL: `jdbc:postgresql://<HOST>:<PORT>/<DB>`
  - Snowflake: `jdbc:snowflake://<ACCOUNT>.snowflakecomputing.com/?db=<DB>&schema=<SCHEMA>`
    - Include Snowflake username/password (or keypair) and warehouse via parameters or properties.

### GitHub Actions

- Using the official Liquibase action

```yaml
name: liquibase-update
on:
  push:
    branches: [ main ]

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Set up Java (for JDBC)
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Liquibase update
        uses: liquibase/liquibase-github-action@v4
        with:
          operation: update
          changelogFile: database/changelog/changelog.xml
          url: ${{ secrets.DB_URL }}           # e.g. jdbc:sqlserver://...;databaseName=...
          username: ${{ secrets.DB_USER }}
          password: ${{ secrets.DB_PASS }}
          # classpath: drivers/                # if you provide custom JDBC drivers
```

- Using the Liquibase Docker CLI

```yaml
name: liquibase-update-docker
on: [workflow_dispatch]

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Liquibase update (Docker)
        env:
          DB_URL: ${{ secrets.DB_URL }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASS: ${{ secrets.DB_PASS }}
        run: |
          docker run --rm \
            -v "$GITHUB_WORKSPACE":/liquibase \
            liquibase/liquibase:latest \
            --url="$DB_URL" \
            --username="$DB_USER" \
            --password="$DB_PASS" \
            --changelog-file=database/changelog/changelog.xml \
            update
```

Tips:

- Store `DB_URL`, `DB_USER`, `DB_PASS` in environment or repository secrets; protect production environments with reviewers.
- For Snowflake/PostgreSQL, replace the JDBC URL and ensure the appropriate JDBC driver is available (either bundled or on `classpath`).

## Example pipeline shapes

Note: The exact YAML will depend on your platform. Below are outline steps to implement.

- GitHub Actions (outline)
  - Job: Build and test
    - Checkout → Set up SQL Server container → Lint SQL → Flyway migrate (ephemeral DB) → tSQLt tests → Upload artifact (migrations zip + configs; optional DACPAC)
  - Environments: dev, test, staging, prod with required reviewers
  - Job: Deploy (per environment)
    - Download artifact → Retrieve secrets → Pre-checks → Flyway migrate (target) → Post-deploy smoke → Notify

- Azure DevOps (outline)
  - Stage: Build
    - Tasks: PowerShell/Bash scripts to run SQLFluff, Flyway, tSQLt; PublishBuildArtifacts
  - Stages: Dev → Test → Staging → Prod (Approvals & checks)
    - Tasks: Key Vault secrets, Flyway migrate, post-deploy tests, notifications
  - Optional: Parallel SSDT stage to generate DACPAC + drift report for PR review

## Governance and change control

- PR templates must include: migration summary, risk level, data impact, rollback/mitigation plan
- Use environment protections and manual approvals for staging/prod
- Tag releases; attach artifacts (migration bundle, optional DACPAC and publish script)

## Operational runbooks (high level)

- Failed migration
  - Halt subsequent stages; assess failure; if safe, push corrective migration; else restore from recent backup following the restore runbook

- Drift found
  - Triage differences; create migrations to reconcile; investigate root cause (ad-hoc changes, hotfixes)

- Emergency hotfix
  - Create a single, minimal migration; run through dev/test quickly; deploy with explicit approval and after-hours scheduling if needed

## References

- Microsoft SSDT / DacFx / sqlpackage
  - `https://learn.microsoft.com/sql/ssdt/sql-server-data-tools`
  - `https://learn.microsoft.com/sql/tools/sqlpackage/sqlpackage`
- Flyway
  - `https://documentation.red-gate.com/fd`
- Liquibase
  - `https://docs.liquibase.com/`
- tSQLt
  - `https://tsqlt.org/`
- SQLFluff (tsql)
  - `https://docs.sqlfluff.com/en/stable/dialects.html#tsql`

## Recommendation summary

- Use migration-first delivery with Flyway for deterministic, auditable deployments across environments.
- Optionally maintain an SSDT project to generate DACPACs for PR-time diffs and scheduled drift reports.
- Enforce CI gates: lint → ephemeral migrate → unit tests → artifact → approvals → environment-by-environment deploy.
- Apply expand/contract and roll-forward strategies to keep releases safe and reversible.
