# Runbooks Folder Structure Proposal

**Document Version:** 1.0
**Date:** 2026-01-20
**Status:** Proposed
**Author:** Application Infrastructure Team

## Table of Contents

- [Executive summary](#executive-summary)
- [Background](#background)
- [Options](#options)
  - [Option A: Task-type first](#option-a-task-type-first)
  - [Option B: Platform first](#option-b-platform-first)
- [Comparison matrix](#comparison-matrix)
- [Industry standards and best practices](#industry-standards-and-best-practices)
- [Recommendation](#recommendation)
- [Migration considerations](#migration-considerations)
- [Decision](#decision)
- [References](#references)

## Executive summary

This document presents two folder structure options for organizing runbooks across multiple database platforms and task types. The goal is to establish a consistent, scalable structure that supports operational efficiency and aligns with industry best practices.

**Recommendation:** Option A (task-type first) based on alignment with existing repository patterns, industry standards from Google SRE and GitLab, and operational workflow optimization.

[↑ Back to Table of Contents](#table-of-contents)

## Background

### Current state

The `docs/runbooks/` directory currently uses a hybrid approach:

```text
docs/runbooks/
├── README.md
├── Enable_WinRM_HTTPS.md
├── alerts/                                    # Task-type first organization
│   ├── README.md
│   ├── linux/
│   │   ├── README.md
│   │   └── alert-cpu-load.md
│   ├── mssql/
│   │   ├── README.md
│   │   ├── alert-cpu-utilization.md
│   │   ├── notification-backup-job-running.md
│   │   ├── notification-maintenance-window.md
│   │   └── report-daily-backup.md
│   ├── ssas/
│   │   ├── README.md
│   │   └── alert-offline.md
│   └── windows/
│       ├── README.md
│       └── alert-cpu-load.md
├── gmsa/                                      # Technology/workflow based
│   ├── README.md
│   ├── dpa/
│   │   └── migrate-dpa-service-to-gmsa.md
│   └── sql-entry/
│       └── migrate-solarwinds-sql-entry-to-gmsa.md
└── podman/                                    # Technology specific
    └── maintenance.md
```

**Current inventory:**

| Category | Platform/Technology | Runbook Count |
|----------|---------------------|---------------|
| alerts | mssql | 4 |
| alerts | ssas | 1 |
| alerts | linux | 1 |
| alerts | windows | 1 |
| gmsa | dpa | 1 |
| gmsa | sql-entry | 1 |
| podman | - | 1 |
| other | Enable_WinRM_HTTPS | 1 |
| **Total** | | **11** |

### Problem statement

As we expand runbook coverage to include maintenance, backup, failover, and other operational procedures across multiple database platforms, we need a consistent folder structure that:

1. Scales across platforms (SQL Server, SSAS, SSIS, PostgreSQL, MongoDB, Snowflake)
2. Supports multiple task types (alerts, maintenance, backup, failover, patching)
3. Enables efficient navigation during incident response
4. Aligns with team organization and operational workflows
5. Follows industry best practices

### Scope

This proposal covers the organization of platform-specific operational runbooks. It does not address:

- Technology-specific workflows (gmsa/, podman/) which follow scenario-based organization
- General documentation outside the runbooks directory

[↑ Back to Table of Contents](#table-of-contents)

## Options

### Option A: Task-type first

Organize by operational task category, then by platform.

```text
docs/runbooks/
├── README.md
├── alerts/
│   ├── README.md
│   ├── mssql/
│   │   ├── README.md
│   │   ├── alert-cpu-utilization.md
│   │   └── alert-blocking-detected.md
│   ├── ssas/
│   │   ├── README.md
│   │   └── alert-offline.md
│   ├── postgresql/
│   │   └── ...
│   └── mongodb/
│       └── ...
├── maintenance/
│   ├── README.md
│   ├── mssql/
│   │   ├── README.md
│   │   ├── index-rebuild.md
│   │   ├── statistics-update.md
│   │   └── integrity-check.md
│   ├── ssas/
│   │   ├── README.md
│   │   └── cube-processing.md
│   ├── postgresql/
│   │   ├── README.md
│   │   ├── vacuum-analyze.md
│   │   └── reindex.md
│   └── mongodb/
│       ├── README.md
│       └── compact-collections.md
├── backup/
│   ├── README.md
│   ├── mssql/
│   ├── postgresql/
│   └── mongodb/
├── failover/
│   ├── README.md
│   ├── mssql/
│   ├── postgresql/
│   └── mongodb/
├── patching/
│   ├── README.md
│   ├── mssql/
│   ├── postgresql/
│   └── mongodb/
├── gmsa/                      # Existing: workflow-based
│   ├── dpa/
│   └── sql-entry/
└── podman/                    # Existing: technology-specific
```

#### Advantages

| Benefit | Description |
|---------|-------------|
| **Consistent with existing structure** | Matches current `alerts/{platform}/` pattern |
| **No migration required** | Existing content stays in place |
| **Task-oriented navigation** | Engineers asking "how do I do maintenance?" find all platforms together |
| **Cross-platform comparison** | Easy to compare procedures across platforms (e.g., all backup runbooks) |
| **Supports task-type indexes** | Each task category can have a comprehensive README with platform matrix |
| **Aligns with SRE practices** | Google SRE organizes by operational concern first |

#### Disadvantages

| Concern | Description |
|---------|-------------|
| **Platform content scattered** | PostgreSQL runbooks spread across alerts/, maintenance/, backup/ |
| **Deeper paths** | `runbooks/maintenance/mssql/index-rebuild.md` (4 levels) |
| **Team ownership ambiguity** | If teams own platforms, content is distributed |

### Option B: Platform first

Organize by database platform, then by task type.

```text
docs/runbooks/
├── README.md
├── mssql/
│   ├── README.md
│   ├── alerts/
│   │   ├── README.md
│   │   ├── alert-cpu-utilization.md
│   │   └── alert-blocking-detected.md
│   ├── maintenance/
│   │   ├── README.md
│   │   ├── index-rebuild.md
│   │   └── statistics-update.md
│   ├── backup/
│   │   └── ...
│   └── failover/
│       └── ...
├── ssas/
│   ├── README.md
│   ├── alerts/
│   └── maintenance/
├── postgresql/
│   ├── README.md
│   ├── alerts/
│   ├── maintenance/
│   ├── backup/
│   └── failover/
├── mongodb/
│   ├── README.md
│   ├── alerts/
│   ├── maintenance/
│   └── backup/
├── snowflake/
│   ├── README.md
│   ├── alerts/
│   └── maintenance/
├── gmsa/                      # Existing: workflow-based
│   ├── dpa/
│   └── sql-entry/
└── podman/                    # Existing: technology-specific
```

#### Advantages

| Benefit | Description |
|---------|-------------|
| **Platform-centric view** | All SQL Server runbooks in one location |
| **Team ownership clarity** | If teams own platforms, all their content is together |
| **Simpler platform onboarding** | New platform DBAs find everything in one place |
| **Platform-specific indexes** | Each platform README lists all available runbooks |

#### Disadvantages

| Concern | Description |
|---------|-------------|
| **Requires migration** | Existing `alerts/` structure must be reorganized |
| **Inconsistent task coverage** | Harder to ensure all platforms have the same runbook types |
| **Cross-platform comparison difficult** | Comparing backup procedures requires navigating multiple directories |
| **Diverges from existing pattern** | Breaks consistency with current `alerts/{platform}/` structure |
| **Deeper paths** | `runbooks/mssql/maintenance/index-rebuild.md` (4 levels) - same depth |

[↑ Back to Table of Contents](#table-of-contents)

## Comparison matrix

| Criteria | Option A (Task-Type First) | Option B (Platform First) |
|----------|---------------------------|--------------------------|
| **Alignment with existing structure** | Matches current pattern | Requires restructuring |
| **Migration effort** | None | High (move all alerts/) |
| **Navigation for "How do I do X?"** | Optimal | Requires checking each platform |
| **Navigation for "What exists for platform Y?"** | Requires checking each task type | Optimal |
| **Cross-platform consistency** | Easy to verify | Harder to maintain |
| **Industry alignment** | Google SRE, GitLab | Some enterprise IT orgs |
| **Scalability** | Scales with task types | Scales with platforms |
| **Index/catalog maintenance** | Per-task-type catalogs | Per-platform catalogs |
| **On-call engineer workflow** | Matches incident response flow | Matches platform expertise |

[↑ Back to Table of Contents](#table-of-contents)

## Industry standards and best practices

### Google SRE

Google's Site Reliability Engineering practices recommend organizing by **operational concern** rather than by service or platform:

> "Structure playbook entries based on severity, impact, metric, background, mitigation and discovery."
> — [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)

Google SRE teams are often organized by **technology type** (e.g., storage, networking) rather than by product, which supports task-type-first organization for runbooks.

### GitLab documentation standards

GitLab organizes documentation by **audience and purpose**:

> "Documentation is divided into audience-focused folders: user, administration, and development."
> — [GitLab Folder Structure](https://docs.gitlab.com/development/documentation/site_architecture/folder_structure/)

This principle supports organizing runbooks by what the operator is trying to accomplish (alerts, maintenance, backup) rather than by platform.

### Diátaxis framework

The [Diátaxis framework](https://diataxis.fr/) used in this repository emphasizes organizing by **user need**:

- Tutorials (learning)
- How-to guides (task completion)
- Reference (information lookup)
- Explanation (understanding)

Runbooks are "how-to guides" for operations. Organizing by task type aligns with "what is the user trying to accomplish?"

### Azure Automation best practices

Microsoft recommends simulating folder structure through naming conventions:

> "Use a structure for Runbooks names to simulate a folder structure: Project_Type_DescriptiveFunction"
> — [Kelverion Azure Automation Best Practices](https://www.kelverion.com/blog/azure-automation-best-practices)

This translates to task-type-first: `Alerting_Monitor_SCOM`, `Maintenance_Index_Rebuild`.

### System Center Orchestrator

Microsoft's Orchestrator guidance recommends folder hierarchies based on **process flow**:

> "Use a 'Folder' and 'Subfolder' structure for runbooks... To show the flow of execution and aid supportability, give your folders numbers."
> — [Kelverion Orchestrator Best Practices](https://www.kelverion.com/blog/system-center-orchestrator-best-practices)

### Google documentation best practices

Google's internal documentation standards emphasize:

> "A small set of fresh and accurate docs is better than a large assembly of documentation in various states of disrepair."
> — [Google Style Guide](https://google.github.io/styleguide/docguide/best_practices.html)

This favors whichever structure is easier to maintain consistently. Task-type-first enables easier cross-platform consistency checks.

### Summary of industry alignment

| Source | Recommended Approach |
|--------|---------------------|
| Google SRE | Task/operational concern first |
| GitLab | Audience/purpose first |
| Diátaxis | User need first |
| Azure Automation | Task-type in naming convention |
| Write the Docs | Purpose-driven organization |

[↑ Back to Table of Contents](#table-of-contents)

## Recommendation

**Recommended: Option A (Task-Type First)**

### Rationale

1. **Consistency**: Matches existing `alerts/{platform}/` structure with zero migration
2. **Industry alignment**: Follows Google SRE, GitLab, and Diátaxis recommendations
3. **Operational workflow**: On-call engineers typically respond to a type of issue (alert, maintenance need) and then identify the platform
4. **Cross-platform governance**: Easier to ensure all platforms have required runbooks for each task type
5. **Scalability**: Adding new task types (e.g., `security/`, `compliance/`) is straightforward

### Addressing platform-centric navigation

To support engineers who think "I need all PostgreSQL runbooks," add platform index files:

```text
docs/runbooks/
├── platforms/
│   ├── mssql.md          # Index linking to all MSSQL runbooks across task types
│   ├── ssas.md
│   ├── postgresql.md
│   └── mongodb.md
```

Example `platforms/postgresql.md`:

```markdown
# PostgreSQL Runbooks

Quick reference to all PostgreSQL operational runbooks.

## Alerts
- [Connection pool exhausted](../alerts/postgresql/alert-connection-pool-exhausted.md)
- [Replication lag](../alerts/postgresql/alert-replication-lag.md)

## Maintenance
- [VACUUM and ANALYZE](../maintenance/postgresql/vacuum-analyze.md)
- [Reindex](../maintenance/postgresql/reindex.md)

## Backup
- [pg_dump procedures](../backup/postgresql/pg-dump.md)
- [Point-in-time recovery](../backup/postgresql/pitr.md)
```

This provides both organizational patterns without duplicating content.

[↑ Back to Table of Contents](#table-of-contents)

## Migration considerations

### Option A: No migration required

The existing structure already follows task-type-first for alerts. New directories are additive:

```bash
# Create new task-type directories
mkdir -p docs/runbooks/{maintenance,backup,failover,patching}/{mssql,ssas,postgresql,mongodb,snowflake}

# Create platform index directory
mkdir -p docs/runbooks/platforms
```

### Option B: Full migration required

Moving to platform-first requires relocating all existing alert runbooks:

```bash
# Example migration (disruptive)
mkdir -p docs/runbooks/mssql/alerts
mv docs/runbooks/alerts/mssql/* docs/runbooks/mssql/alerts/
# Repeat for each platform...
# Update all cross-references...
```

**Risk**: Broken links, git history fragmentation, team retraining.

[↑ Back to Table of Contents](#table-of-contents)

## Decision

**Status:** Proposed

| Role | Name | Decision | Date |
|------|------|----------|------|
| Proposal Author | | | 2026-01-20 |
| Team Lead | | | |
| DBA Lead | | | |
| SRE Lead | | | |

### Discussion notes

*To be filled during team review*

### Final decision

*To be recorded after team consensus*

[↑ Back to Table of Contents](#table-of-contents)

## References

- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)
- [Google SRE Team Organization](https://cloud.google.com/blog/products/devops-sre/how-sre-teams-are-organized-and-how-to-get-started)
- [Google Documentation Best Practices](https://google.github.io/styleguide/docguide/best_practices.html)
- [GitLab Documentation Folder Structure](https://docs.gitlab.com/development/documentation/site_architecture/folder_structure/)
- [Diátaxis Framework](https://diataxis.fr/)
- [Azure Automation Best Practices - Kelverion](https://www.kelverion.com/blog/azure-automation-best-practices)
- [System Center Orchestrator Best Practices - Kelverion](https://www.kelverion.com/blog/system-center-orchestrator-best-practices)
- [Runbook Best Practices - IncidentHub](https://blog.incidenthub.cloud/The-No-Nonsense-Guide-to-Runbook-Best-Practices)
- [SRE Runbooks Tutorial](https://sreschool.com/blog/comprehensive-tutorial-on-runbooks-in-site-reliability-engineering/)
- [Docs as Code - Write the Docs](https://www.writethedocs.org/guide/docs-as-code/)

[↑ Back to Table of Contents](#table-of-contents)
