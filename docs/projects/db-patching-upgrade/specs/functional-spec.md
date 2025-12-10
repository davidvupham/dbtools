# Functional Specification: Database Patching Tools

## 1. Overview

This specification describes the requirements for the automation tools (Ansible playbooks, PowerShell scripts) that will execute the patching and upgrade strategies defined in the Architecture document.

## 2. User Interfaces

### 2.1 Inputs

### 2.1 Inputs (GitHub Actions / Dispatch)

The tool (via `patch-deploy.yml`) must accept:

* `target_cluster`: Inventory/Cluster ID (e.g., `mongo-prod-01`).
* `target_version`: The version string. *Must correspond to an entry in Approved Registry (`db_versions.yml`).*
* `strategy`: `rolling` (Standard) or `canary` (Patch 1 node then pause).
* `dry_run`: `true`/`false`.
* `skip_ephemeral_test`: `true`/`false` (Emergency override only).

### 2.2 Outputs

* **Standard Output**: Real-time progress logs (Steps completed, Current Node).
* **Exit Codes**:
  * `0`: Success.
  * `1`: General Error (Script failure).
  * `2`: Pre-flight Check Failure (Safe abort).
  * `3`: Post-flight Check Failure (Cluster degraded).

## 3. Functional Requirements

### 3.1 Scheduling & Constraints (Business Rules)

The tool MUST enforce the following schedule and lifecycle rules:

1. **Maintenance Window**: Patching operations are restricted to the **3rd Saturday of the Month** (unless `maintenance_window=false` override is passed).
2. **New Builds**: All *newly provisioned* instances MUST automatically use the "Latest Approved" version defined in `db_versions.yml`.
3. **Patch Queue**: When a vendor releases a new patch, it is NOT applied immediately. It involves:
    * **Week 1-2**: Version Scraper detects it -> QA verifies in Ephemeral/Dev.
    * **3rd Saturday**: The patch is applied to Production.

### 3.2 Pre-Flight Checks

Before any mutation, the tool MUST verify:

1. **Version Registry**: Target version is marked "Approved" in `db_versions.yml`.
2. **Ephemeral Test Pass**: Unless skipped, a temporary clone of the cluster was successfully patched and validated (Status: `PASS`).
3. **Cluster Health**: All nodes are up, replication is synchronous/healthy.
4. **Backups**: Verify the last backup timestamp is within SLA (e.g., < 24 hours).

### 3.2 Execution Logic

1. **Canary Step** (If `strategy=canary`):
    * Patch 1 Secondary node.
    * **Pause/Bake**: Wait for specified duration or manual approval signal.
    * **Analyze**: Check error rates. Abort if high.
2. **Drain**: Mark node as unschedulable.
3. **Stop**: Gracefully stop the database service.
4. **Patch/Upgrade**: Apply the package update.
5. **Start**: Start the service.
6. **Wait**: Poll for service readiness and data sync (Catchup).

### 3.3 Post-Flight Checks

After patching a node, the tool MUST verify:

1. **Version**: Query the DB engine to confirm the version matches `target_version`.
2. **Rejoin**: Verify the node has rejoined the cluster and is catching up.
3. **Health**: Verify no error logs in the last 5 minutes.

## 4. Failure Handling

* **Stop-on-Error**: If any step fails on a node, execution MUST halt immediately.
* **No Auto-Rollback**: Due to data risk, the tool should NOT automatically revert DB binaries unless it is a purely atomic transaction. Manual intervention is preferred for DB state issues.
