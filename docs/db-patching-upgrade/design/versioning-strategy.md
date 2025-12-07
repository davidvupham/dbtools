# Version Management Strategy

## 1. Overview

To ensure stability and auditability, database versions are managed via a **GitOps-driven Version Registry**. We do not auto-upgrade based solely on upstream availability; instead, we curate a list of "Approved Versions" in code.

## 2. The Version Registry (`db_versions.yml`)

The source of truth for all database versions is a YAML file stored in the repository.

```yaml
# src/dbtools/db_versions.yml
postgres:
  latest_approved: "14.9"
  production_locked: "14.8" # Pin production to a specific stable version
  eol_date: "2026-11-11"

mongodb:
  latest_approved: "7.0.2"
  production_locked: "6.0.10"
  manifest_url: "https://opsmanager.mongodb.com/static/version_manifest/7.0.json"

sqlserver:
  latest_approved: "16.0.4085.2" (2022 CU10)
  production_locked: "16.0.1000.6" (2022 RTM)
```

## 3. Version Discovery (Actual State)

### 3.1 Linux (Ansible)

A "Audit" playbook runs daily to capture the running version of every node.

* **Postgres**: `psql -c "SELECT version()"`
* **Mongo**: `mongosh --eval "db.version()"`

### 3.2 Windows (PowerShell)

A scheduled task runs `Get-GdsSqlVersion` (wrapping `SELECT @@VERSION` or `SERVERPROPERTY('ProductVersion')`) against the inventory.

### 3.3 Compliance Reporting

The "Actual" versions are compared against the `db_versions.yml` "Production Locked" version.

* **Match**: Compliance (Green).
* **Mismatch (Lower)**: Needs Patch (Yellow/Red).
* **Mismatch (Higher)**: Drift/Unauthorized Change (Red).

## 4. Upstream Monitoring (Vendor Repositories)

We rely on authoritative vendor sources ("repos") to detect new releases.

### 4.1 Linux (MongoDB)

* **Source**: MongoDB Ops Manager Version Manifest.
* **URL**: `https://opsmanager.mongodb.com/static/version_manifest/7.0.json` (Replace `7.0` with target major version).
* **Mechanism**: A Python script parses this JSON manifest to find the latest available `7.0.x` release.

### 4.2 Linux (PostgreSQL)

* **Source**: PostgreSQL.org Source Listing / RSS.
* **URL**: `https://www.postgresql.org/ftp/source/` (Structured listing) or RSS feeds.
* **Mechanism**: A Python script scrapes the directory listing to find the highest semantic version.

### 4.3 Windows (Microsoft SQL Server)

* **Source**: Microsoft SQL Server Release Services / Redgate API.
* **Primary URL (Official)**: `https://learn.microsoft.com/en-us/sql/database-engine/install-windows/latest-updates-for-microsoft-sql-server` (and associated Excel export).
* **Secondary URL (Community/API)**: `https://sqlserverupdates.com/api/scraping/` (Maintained by Redgate, widely used for automation).
* **Mechanism**: A PowerShell script queries these endpoints to identify the latest `CU` (Cumulative Update) and `GDR` (General Distribution Release) for the target major version.

**Workflow (GitHub Actions)**:

1. **Schedule**: `on: schedule` (Weekly) triggers the `version-scraper` workflow.
2. **Scrape**: Runners execute scrapers against these **Vendor Repos**.
3. **PR**: If a new version is greater than `latest_approved`, the action uses `peter-evans/create-pull-request` to update `db_versions.yml`.
4. **Approve**: DBA reviews the Release Notes and merges the PR.
5. **Deploy**: Once merged, the `patch-deploy` workflow can now target this new version.
