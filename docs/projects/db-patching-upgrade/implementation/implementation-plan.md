# Automate Patching and Upgrade

## Best Practice Workflow

We follow the **Architecture First** approach:

1. **Architecture/Design** (Strategy & Specs) -> **DONE**.
2. **Shared Libraries** (Core Logic in Python/PowerShell).
3. **Orchestration** (GitHub Actions wiring it together).

## Phase 1: Shared Libraries (The Core)

* **Goal**: Implement the "Business Logic" of patching in reusable packages.
* **Tasks**:
  * [ ] **Python**: Extend `gds_database` with `DatabaseEngine` abstract base class.
  * [ ] **Python**: Implement `PostgresEngine` (Patroni-aware patching).
  * [ ] **Python**: Implement `MongoEngine` (ReplicaSet-aware patching).
  * [ ] **PowerShell**: Create/Update `GDS.SQLServer` module with `Invoke-GdsSqlPatch` (DSC wrapper).

## Phase 2: Orchestration (The Glue)

* **Goal**: Create the runners and workflows that call the shared libraries.
* **Tasks**:
  * [ ] **Ansible**: Create `db_patch` role that simply wraps the `gds_database` Python calls.
  * [ ] **GitHub Actions**: Create `version-scraper.yml` (Weekly).
  * [ ] **GitHub Actions**: Create `patch-deploy.yml` (Manual Dispatch).

## Phase 3: Versioning & Compliance

* **Goal**: Implement the "GitOps" registry.
* **Tasks**:
  * [ ] Create `db_versions.yml` schema.
  * [ ] Write `scrape_versions.py` (for Mongo/PG).
  * [ ] Write `Get-SqlServerVersions.ps1` (for Windows).

## Phase 4: Verification

* **Goal**: Prove it works safely.
* **Tasks**:
  * [ ] **Dry Run**: Execute `patch-deploy.yml` with `dry_run=true` against all Dev DBs.
  * [ ] **Failure Test**: Intentionally break a node and verify the automation stops/alerts (does not cascade).
