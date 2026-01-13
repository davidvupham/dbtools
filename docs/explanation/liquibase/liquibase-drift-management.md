# Understanding Database Drift

**🔗 [← Back to Liquibase Documentation Index](./README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 1.0
> **Last Updated:** January 12, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production - Actively Maintained

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md) | [Reference](../../reference/liquibase/liquibase-reference.md)

This document explains what database drift is, why it matters, and the conceptual approaches to managing it. For step-by-step procedures, see the [Operations Guide - Drift Detection](../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation).

## Table of Contents

- [What is Database Drift?](#what-is-database-drift)
- [Why Drift Matters](#why-drift-matters)
- [Common Causes of Drift](#common-causes-of-drift)
- [Types of Drift](#types-of-drift)
- [How Liquibase Detects Drift](#how-liquibase-detects-drift)
  - [Detection vs. Generation](#detection-vs-generation)
  - [Snapshot-Based Detection](#snapshot-based-detection)
- [Drift Remediation Strategies](#drift-remediation-strategies)
  - [Strategy 1: Revert the Drift](#strategy-1-revert-the-drift)
  - [Strategy 2: Accept the Drift](#strategy-2-accept-the-drift)
  - [Strategy 3: Sync Without Deployment](#strategy-3-sync-without-deployment)
- [Best Practices](#best-practices)
- [Further Reading](#further-reading)

---

## What is Database Drift?

**Database drift** occurs when the actual state of a database diverges from its expected or documented state. This happens when changes are made directly to a database outside of the normal change management process—without going through Liquibase changelogs.

Think of drift like this: Your Liquibase changelog represents the "source of truth" for what your database schema should look like. When someone makes a manual change directly to the database, the database state "drifts" away from what your changelogs describe.

```text
┌─────────────────────┐         ┌─────────────────────┐
│   Changelog State   │    ≠    │  Actual Database    │
│   (Expected)        │  DRIFT  │  (Reality)          │
├─────────────────────┤         ├─────────────────────┤
│ • customer table    │         │ • customer table    │
│ • orders table      │         │ • orders table      │
│                     │         │ • loyalty_points    │ ← Unexpected!
│ • IX_orders_date    │         │                     │ ← Missing!
└─────────────────────┘         └─────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Why Drift Matters

Drift creates several serious problems:

| Problem | Impact |
|---------|--------|
| **Deployment failures** | Future changesets may fail because they expect a different schema state |
| **Environment inconsistency** | Dev, staging, and production databases become different from each other |
| **Audit gaps** | Changes aren't tracked, breaking compliance requirements |
| **Rollback failures** | Rollback scripts may fail or cause data loss |
| **Testing unreliability** | Tests pass in dev but fail in production due to schema differences |

**Example scenario:**

1. DBA adds an index directly to production to fix a performance issue
2. Weeks later, a developer adds the same index via a changeset
3. Deployment to production fails: "Index already exists"
4. Team spends hours debugging what should have been a routine deployment

[↑ Back to Table of Contents](#table-of-contents)

## Common Causes of Drift

| Cause | Example |
|-------|---------|
| **Emergency hotfixes** | DBA adds an index directly to fix a production performance issue |
| **Manual troubleshooting** | Developer adds a column to debug an issue and forgets to remove it |
| **Shadow IT** | Team member makes changes without going through change management |
| **Migration tool bypass** | Scripts run directly on database instead of through Liquibase |
| **Failed deployments** | Partial deployment leaves database in inconsistent state |
| **Third-party tools** | External applications create objects in your schema |
| **Database restoration** | Restoring from backup to a different point in time |

[↑ Back to Table of Contents](#table-of-contents)

## Types of Drift

Liquibase categorizes drift into three types:

| Type | Meaning | Risk Level | Example |
|------|---------|------------|---------|
| **Missing** | Object exists in expected state but not in database | HIGH - May break application | Index was dropped manually |
| **Unexpected** | Object exists in database but not in expected state | MEDIUM - Unauthorized change | Column was added manually |
| **Changed** | Object exists in both but properties differ | MEDIUM - May cause inconsistency | Column size was modified |

**Risk assessment guidance:**

- **Missing objects** are typically the most dangerous—if your application expects an index or constraint and it's gone, queries may fail or data integrity may be compromised.
- **Unexpected objects** are often benign but indicate process breakdown. They may also cause confusion or unexpected behavior.
- **Changed objects** can range from harmless (comment changed) to critical (data type changed).

[↑ Back to Table of Contents](#table-of-contents)

## How Liquibase Detects Drift

### Detection vs. Generation

Liquibase has two related but distinct capabilities:

| Capability | Command | Description |
|------------|---------|-------------|
| **Detection** | `diff`, `snapshot` | Identifies differences between database states |
| **Generation** | `diffChangeLog` | Creates changesets to remediate differences |

> **Important:** Liquibase can **detect** more object types than it can automatically **generate** changesets for. Complex objects like stored procedures may be detected as "changed" but require manual changeset creation.

For example, Liquibase can detect that a stored procedure's checksum changed (indicating modification), but it may not be able to generate a perfect `CREATE OR REPLACE PROCEDURE` statement automatically.

### Snapshot-Based Detection

The recommended approach for drift detection uses **snapshots**—point-in-time captures of your database schema stored as JSON files.

**Why snapshots are better than comparing live databases:**

1. **Immutability** - Snapshots don't change, providing a reliable reference point
2. **Speed** - No need to connect to a second live database
3. **Availability** - Works even when other environments are unavailable
4. **History** - Keep snapshots over time to track when drift occurred

**Conceptual workflow:**

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Deploy     │ ──► │   Capture    │ ──► │   Compare    │
│   Changes    │     │   Snapshot   │     │   Later      │
└──────────────┘     └──────────────┘     └──────────────┘
                           │                     │
                           ▼                     ▼
                     baseline.json          Current DB
                     (Known Good)           (Actual State)
```

[↑ Back to Table of Contents](#table-of-contents)

## Drift Remediation Strategies

Once drift is detected, you have three main strategies for handling it:

### Strategy 1: Revert the Drift

**When to use:** The drift was unintended and should be removed.

This approach restores the database to match your changelog by manually reversing the unauthorized changes. Use this when:

- Someone made an unauthorized change
- A hotfix was applied and needs to be removed
- The drift causes issues with deployments

**Conceptual steps:**

1. Identify exactly what drifted (using `diff`)
2. Write SQL to reverse the change
3. Execute the reversal
4. Verify drift is resolved

### Strategy 2: Accept the Drift

**When to use:** The drift represents a legitimate change that should be kept and tracked.

This approach creates a Liquibase changeset from the drift so it becomes part of your version-controlled changelog. Use this when:

- An emergency hotfix was applied and needs to be documented
- The change is valid but bypassed the normal process
- You need to bring other environments into sync

**Conceptual steps:**

1. Generate a changelog from the drift (using `diffChangeLog`)
2. Review and edit the generated changelog
3. Add to your master changelog
4. Use `changelogSync` to mark as deployed (since it already exists)

### Strategy 3: Sync Without Deployment

**When to use:** Multiple environments have drifted in the same way and you want to align the changelog tracking.

This approach uses `changelogSync` to update the DATABASECHANGELOG table without actually running the changesets. Use this when:

- A change was applied manually to multiple environments
- You're adopting Liquibase on an existing database
- You need to mark changes as "already done"

[↑ Back to Table of Contents](#table-of-contents)

## Best Practices

### Preventive Measures

| Practice | Description |
|----------|-------------|
| **Enforce change management** | All database changes must go through Liquibase changelogs |
| **Restrict direct access** | Limit who can make direct DDL changes to databases |
| **Use separate credentials** | Application accounts shouldn't have DDL permissions |
| **Document emergency procedures** | Have a clear process for emergency hotfixes that includes changelog updates |
| **Train team members** | Ensure everyone understands the importance of using Liquibase |

### Detection Practices

| Practice | Description |
|----------|-------------|
| **Snapshot after every deployment** | Capture known-good state immediately after changes |
| **Schedule regular drift checks** | Run drift detection daily or before each deployment |
| **Monitor production closely** | Production should have the strictest drift monitoring |
| **Use CI/CD gates** | Fail deployments if drift is detected |
| **Alert on drift** | Send notifications when drift is found |

### Remediation Practices

| Practice | Description |
|----------|-------------|
| **Investigate root cause** | Understand why drift occurred before fixing |
| **Document decisions** | Record why drift was reverted or accepted |
| **Update processes** | If drift keeps recurring, fix the underlying process |
| **Test remediation** | Verify the fix in lower environments first |
| **Communicate changes** | Inform the team about drift and resolution |

[↑ Back to Table of Contents](#table-of-contents)

## Further Reading

- **[Operations Guide - Drift Detection](../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation)** - Step-by-step procedures for detecting and remediating drift
- **[Reference - Supported Objects](../../reference/liquibase/liquibase-reference.md#drift-detection-supported-objects)** - Which objects Liquibase can detect by platform
- **[Reference - Diff Commands](../../reference/liquibase/liquibase-reference.md#drift-detection-commands)** - Command reference for drift-related operations
- **[Official Liquibase Documentation](https://docs.liquibase.com/workflows/liquibase-community/drift-detection.html)** - Liquibase drift detection documentation
