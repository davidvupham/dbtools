# Architecture Strategy: Database Patching & Upgrades

## 1. Executive Summary

This document defines the high-level architectural strategy for patching and upgrading database engines (PostgreSQL, MongoDB, SQL Server) with a focus on maximizing availability (Zero Downtime where possible) and data safety.

## 2. General Design Principles

1. **Automation First**: All operations must be fully automated via Ansible (Linux) or PowerShell/DSC (Windows) to reduce human error.
2. **Rolling Upgrades**: Leverage clustering capabilities (Replica Sets, Availability Groups) to patch nodes sequentially without taking the service offline.
3. **Failover Awareness**: The automation must be "cluster-aware", managing traffic redirection and role switching (Primary/Secondary) gracefully.
4. **Immutable Recovery**: Always ensure a restoration point (backup or snapshot) exists before mutation.
5. **Strict/GitOps Versioning**: Versions are not chosen ad-hoc. A central [Version Registry](../design/versioning-strategy.md) defines the "Approved" and "Target" versions for every environment.
6. **Orchestration**: All workflows are driven by **GitHub Actions** (CI/CD).
7. **Code Reusability**: Logic must be implemented in shared libraries (`gds_database` Python package, `GDS.*` PowerShell modules) to ensure consistency across the enterprise.

## 3. Patching vs. Upgrades Strategy

There is a strict distinction between **Patching** (Minor) and **Upgrades** (Major).

* **Patching (Minor)**: In-place binary update (e.g., `apt-get upgrade`, `yum update`, SQL Server CU). Low risk, fast, reversible via package rollback.
* **Upgrades (Major)**: Data format change (e.g., PostgreSQL 14 -> 15). High risk, requires data migration (`pg_upgrade` or Logical Replication).
  * **Strategy**: Major upgrades should generally prefer **Blue/Green** (New Cluster) over Rolling In-Place where possible, to ensure a clean fallback.

## 4. Engine-Specific Strategies

### 4.1 PostgreSQL (Linux)

* **Architecture**: High Availability using Patroni or similar streaming replication clusters.
* **Minor Version Patching**:
  * **Method**: Rolling Patch.
* **Architecture**: High Availability using Patroni or similar streaming replication clusters.
* **Minor Version Patching**:
  * **Method**: Rolling Patch.
  * **Flow**: Patch Replica -> Verify -> Patch Replica 2 -> Switchover (Planned Failover) -> Patch Old Primary.
* **Major Version Upgrade**:
  * **Method**: `pg_upgrade` with hard links (Fast) or Logical Replication (Blue/Green) for minimal downtime major upgrades.
  * **Recommendation**: Default to Blue/Green using new infrastructure for Major versionumps to ensure clean OS/Lib state.

### 3.2 MongoDB (Linux)

* **Architecture**: Replica Sets (PSS - Primary-Secondary-Secondary). Supports up to 5 members (1 Primary, 4 Secondaries) for high resilience.
* **Patching & Upgrades**:
  * **Method**: Rolling Upgrade.
  * **Flow**:
        1. Upgrade Secondaries one by one (loop through all 4).
        2. `rs.stepDown()` on Primary.
        3. Wait for election of new Primary (upgraded node).
        4. Upgrade the former Primary.
  * **Constraint**: `featureCompatibilityVersion` must be managed carefully at the end of the chain.

### 3.3 Microsoft SQL Server (Windows)

* **Architecture**: AlwaysOn Availability Groups (AOAG).
* **Patching & Upgrades**:
  * **Tooling**: PowerShell DSC v3 (latest) or Ansible (via `ansible.windows` collection).
    * *Note: Ansible can be used to orchestrate Windows patching seamlessly, but DSC v3 offers robust configuration state management.*
  * **Method**: Rolling Upgrade.
  * **Flow**:
        1. Patch Secondary Replicas.
        2. Verify synchronization state (`Synchronized`).
        3. Perform Manual Failover to a patched Secondary.
        4. Patch the former Primary.
  * **Constraint**: SQL Server allows mixed-version modes temporarily for this exact process.

## 5. Advanced Enterprise Patterns

To ensure "Zero Downtime" and minimizing blast radius, we adopt the following advanced patterns:

### 5.1 Pre-Flight Ephemeral Testing

Before touching *any* production node, the automation MUST:

1. **Clone**: Create a thin-clone or restore a recent backup of the target cluster to a temporary (ephemeral) environment.
2. **Test**: Execute the patch workflow on this ephemeral cluster.
3. **Validate**: Run a synthetic transaction suite.
4. **Destroy**: Tear down the environment.

### 5.2 Canary Rollouts (The "Baking" Period)

For large clusters (> 10 nodes), we do not patch all Secondaries immediately.

1. **Canary**: Patch 1 Secondary.
2. **Bake**: Wait 4-24 hours.
3. **Observe**: Check specific "Canary Metrics" (Error Rate, Latency).
4. **Resume**: If healthy, proceed to remaining fleet.

## 6. Rollback Strategy

* **In-Place Rollback**: Generally not supported for database engine binaries after data file upgrade.
* **Cluster Rollback**: If the first node fails, stop. Do not failover.
* **Disaster Recovery**: Restore from Backup/Snapshot if cluster is corrupted.
* **Blue/Green Fallback**: For Major upgrades, if "Green" fails, simply switch VIP/DNS back to "Blue" (Instant Rollback).

## 7. Next Steps

* Define **Functional Specifications** for the automation tools that will execute these logic flows.
