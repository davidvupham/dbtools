# Technical Design: Database Patching Automation

## 1. Directory Structure

The automation code will reside in `src/dbtools`:

* `gds_database/`: **Existing Python Package**. All Linux engine logic (Postgres, Mongo) MUST go here.
* `PowerShell/`: **Existing PowerShell Modules**.
  * `GDS.SQLServer/`: New or existing module for SQL logic.
* `ansible/roles/db_patch/`: Thin wrapper role that calls `gds_database` scripts.

## 2. Shared Libraries Implementation

### 2.1 Python (`gds_database`)

We must extend the `gds_database` package with a standard interface.

```python
class DatabaseEngine(ABC):
    @abstractmethod
    def patch(self, target_version: str) -> bool:
        """Minor version in-place update."""
        pass

    @abstractmethod
    def upgrade(self, target_version: str) -> bool:
        """Major version migration."""
        pass

    @abstractmethod
    def clone_cluster(self, target_env: str) -> str:
        """Create an ephemeral clone for pre-flight testing. Returns connection string."""
        pass
```

### 2.2 PowerShell (`GDS.SQLServer`)

Reuse existing functions from `GDS.Common` where applicable. New functions should be generic.

## 3. Linux Implementation (Ansible)

### 3.1 Role: `db_patch`

This unified role will handle both PostgreSQL and MongoDB patching.

### 3.2 Variables

* `db_engine`: "postgres" or "mongo".
* `db_version`: Target version string (e.g., "14.5-1").
* `db_cluster_name`: Identifier for the cluster.
* `patch_strategy`: "rolling" (default) or "all_at_once" (dev only).

### 2.3 Task Flow

1. **`preflight.yml`**:
    * Check space (`ansible.builtin.assert`).
    * Check backup status (call custom script or API).
2. **`main.yml`**:
    * Include engine-specific tasks: `postgres.yml` or `mongo.yml`.
3. **`postgres.yml`**:
    * Check Patroni cluster health (API call).
    * Pause Patroni node.
    * Update binaries (`ansible.builtin.yum` / `apt`).
    * Resume Patroni node.
    * Wait for health (`uri` module loop).
4. **`mongo.yml`**:
    * Identify Primary and Secondaries (`rs.status()`).
    * **Loop**: Iterate through all identified Secondaries (supports 1 to 4+).
        * Stop `mongod`.
        * Update binaries.
        * Start `mongod`.
        * Wait for `stateStr: SECONDARY`.
    * StepDown Primary.
    * Patch former Primary.

## 3. Windows Implementation (PowerShell DSC v3)

### 3.1 Module: `GDS.SQLServer`

A script module utilizing **PowerShell DSC v3** (cross-platform / PS 7+ compatible syntax where possible).

### 3.2 Functions & Resources

* **`Get-GdsSqlClusterHealth`**: Returns object with cluster health status.
* **`Invoke-GdsSqlPatch`**: Wraps `Invoke-DscResource` or standard DSC Configuration.
  * Resource: `SqlSetup` (from `SqlServerDsc` module).
  * Property: `UpdateEnabled = $true`.
* **`Suspend-GdsSqlNode`**: Suspend the node in AOAG (Data Movement).
* **`Resume-GdsSqlNode`**: Resumes data movement.

### 3.3 Workflow Script `Patch-SqlServer-Cluster.ps1`

A controller script that accepts a list of nodes and iterates through them:

1. Connect to Primary to determine topology.
2. Sort nodes: Secondaries first, Primary last.
3. Loop through nodes calling the functions defined above.

## 4.  **Safety Mechanisms**

* **Mutex/Lock**: Ensure only one patch process runs per cluster at a time.
* **Verification**: Ansible `uri` allows strict status code checking. PowerShell `Invoke-Sqlcmd` allows querying `sys.dm_hadr_availability_replica_states`.

## 5. Orchestration (GitHub Actions)

We utilize **GitHub Actions** self-hosted runners (to access internal DBs) for all operations.

### 5.1 Workflows

* **`version-scraper.yml`**: Scheduled (Weekly). Runs the Python/PowerShell scrapers and creates PRs.
* **`compliance-audit.yml`**: Scheduled (Daily). Runs Ansible/PowerShell in "Check Mode" to detect drift.
* **`patch-deploy.yml`**: Manual/Dispatch.
  * **Inputs**: `target_cluster`, `target_version`, `dry_run`.
    * **Jobs**:
        1. **`ephemeral-test`**:
            * Calls `gds_database`: `clone_cluster()` -> `patch()` -> `validate()` -> `destroy()`.
            * *Gate*: Fails workflow if this job fails.
        2. **`pre-flight`**: Validates Prod cluster health.
        3. **`patch-canary`** (if strategy=canary):
            * Patches 1 node.
            * *Gate*: Manual Approval or Timer (12h) to proceed.
        4. **`patch-fleet`**: Patches remaining nodes.
        5. **`post-flight`**: Verifies logic execution.
