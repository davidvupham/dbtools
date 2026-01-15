# Liquibase Versioning and Changeset Best Practices

<!-- markdownlint-disable MD013 -->

**[← Back to Liquibase Documentation Index](../../explanation/liquibase/README.md)** — Navigation guide for all Liquibase docs

This document covers best practices for versioning, changesets, and release management when using Liquibase.

## Table of Contents

- [Versioning Conventions](#versioning-conventions)
  - [Changeset File Numbers](#changeset-file-numbers-v0001-v0002-)
  - [Release Tags](#release-tags-release-v11-release-v12-)
  - [When to Bump the Major Version](#when-to-bump-the-major-version)
- [One Change Per Changeset](#one-change-per-changeset)
- [Summary](#summary)

---

## Versioning Conventions

This section explains the two versioning schemes used in Liquibase workflows and how they relate to each other.

### Changeset File Numbers (V0001, V0002, ...)

The `V####` prefix on changeset files is a **sequential identifier** for individual database changes:

| File | Purpose |
|------|---------|
| `V0000__baseline.mssql.sql` | Initial database state (baseline) |
| `V0001__add_orders_table.mssql.sql` | First change after baseline |
| `V0002__add_orders_index.mssql.sql` | Second change |

**Why 4 digits?** The 4-digit format (0000-9999) supports up to 10,000 changesets per database. This is sufficient for most projects—even with daily changes, 9,999 changesets would span over 27 years. If you anticipate needing more, you can use 5 or 6 digits (e.g., `V00001`, `V000001`).

### Release Tags (release-v1.1, release-v1.2, ...)

Release tags are **Liquibase markers** applied after deployment to identify rollback points:

| Changeset | Release Tag | Relationship |
|-----------|-------------|--------------|
| V0001 | `release-v1.1` | Minor version matches changeset number |
| V0002 | `release-v1.2` | Minor version matches changeset number |
| V0003 | `release-v1.3` | Minor version matches changeset number |

**Recommended convention:** The minor version matches the changeset number (`V000X` → `release-v1.X`). This makes it easy to correlate tags with their corresponding changesets.

### When to Bump the Major Version

Reserve major version bumps for significant milestones:

| Changeset | Release Tag | Scenario |
|-----------|-------------|----------|
| V0004 | `release-v2.4` | Breaking schema change (e.g., dropping a table) |
| V0005 | `release-v2.5` | Continues in v2.x series |

The changeset number continues incrementing globally while the major version indicates the release series. This preserves the ability to identify the changeset from the tag (`v2.4` → V0004).

---

## One Change Per Changeset

Liquibase recommends **one change per changeset** as a best practice. This:

- Improves deployment control and predictability
- Simplifies rollback (each changeset can be rolled back independently)
- Reduces risk of partial failures leaving the database in an unexpected state

### What Counts as "One Change"

| Acceptable (One Changeset) | Should Be Separate Changesets |
|----------------------------|-------------------------------|
| `CREATE TABLE` with inline constraints | `CREATE TABLE` + separate `ALTER TABLE ADD CONSTRAINT` |
| Single `CREATE INDEX` | Multiple `CREATE INDEX` statements |
| Single `ADD COLUMN` | `ADD COLUMN` + `CREATE INDEX` on that column |

### Impact on Changeset Count

With strict one-change-per-changeset, active projects typically generate 50-200 changesets per year. The 4-digit format (V0001-V9999) accommodates this well. For very long-lived or high-velocity projects, use 5 digits (V00001) for 100,000 changesets.

> **Note:** Liquibase Pro includes a `OneChangePerChangeset` policy check to enforce this practice. See [Liquibase Documentation](https://docs.liquibase.com/liquibase-pro/policy-checks/checks/changelog-checks/one-change-per-changeset.html) for details.

---

## Summary

| Concept | Format | Purpose |
|---------|--------|---------|
| Changeset file | `V####__description.sql` | Sequential change identifier, determines execution order |
| Release tag | `release-v{major}.{changeset}` | Rollback marker, correlates to changeset number |
| One change per changeset | Single DDL statement per file | Improves rollback granularity and deployment control |
