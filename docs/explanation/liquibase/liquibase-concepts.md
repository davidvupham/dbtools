# Liquibase Concepts Guide

**🔗 [← Back to Liquibase Documentation Index](./README.md)** — Navigation guide for all Liquibase docs

> **Document Version:** 1.0
> **Last Updated:** January 12, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production - Actively Maintained

![Liquibase Version](https://img.shields.io/badge/Liquibase-5.0%2B-blue)
![Document Status](https://img.shields.io/badge/Status-Production-green)

> [!IMPORTANT]
> **Related Docs:** [Architecture](./liquibase-architecture.md) | [Operations](../../how-to/liquibase/liquibase-operations-guide.md) | [Reference](../../reference/liquibase/liquibase-reference.md) | [Formatted SQL](../../reference/liquibase/liquibase-formatted-sql-guide.md)

## Table of Contents

- [What is Liquibase?](#what-is-liquibase)
- [Why Use Liquibase?](#why-use-liquibase)
- [Core Concepts](#core-concepts)
  - [Changelog](#changelog)
  - [Changeset](#changeset)
  - [Change Types](#change-types)
  - [Tracking Tables](#tracking-tables)
- [How Liquibase Works](#how-liquibase-works)
  - [Basic Workflow](#basic-workflow)
  - [Deployment Process](#deployment-process)
  - [Change Detection](#change-detection)
- [Ways to Use Liquibase](#ways-to-use-liquibase)
  - [Changelog Formats](#changelog-formats)
  - [Execution Methods](#execution-methods)
  - [Integration Options](#integration-options)
- [Key Decisions to Make](#key-decisions-to-make)
  - [Changelog Format](#changelog-format)
  - [Directory Structure](#directory-structure)
  - [Change Granularity](#change-granularity)
  - [Rollback Strategy](#rollback-strategy)
  - [Environment Management](#environment-management)
- [Common Patterns](#common-patterns)
  - [Master Changelog Pattern](#master-changelog-pattern)
  - [Release-Based Organization](#release-based-organization)
  - [Baseline Strategy](#baseline-strategy)
- [Liquibase Editions](#liquibase-editions)
- [Next Steps](#next-steps)
- [Related Documentation](#related-documentation)

## What is Liquibase?

**Liquibase is a database schema change management solution** that enables you to track, version, and deploy database changes using a version control approach similar to application code.

Think of it as **"Git for your database schema"** - it tracks every change, knows what's been applied where, and can deploy changes consistently across environments.

### The Problem Liquibase Solves

Without Liquibase:
- Database changes are manual, error-prone, and undocumented
- No clear history of when/why schema changes were made
- Difficult to keep dev, test, and prod databases in sync
- Hard to roll back changes when something goes wrong
- Multiple developers may conflict when making schema changes

With Liquibase:
- **Version controlled** - All changes tracked in files alongside application code
- **Auditable** - Complete history of who changed what and when
- **Repeatable** - Same changes deploy identically across all environments
- **Automated** - Integrate with CI/CD pipelines
- **Reversible** - Roll back changes when needed

[↑ Back to Table of Contents](#table-of-contents)

## Why Use Liquibase?

| Benefit | Description |
|:---|:---|
| **Database-Agnostic** | Write changes once, deploy to PostgreSQL, SQL Server, Oracle, MySQL, MongoDB, Snowflake, and more |
| **Version Control Integration** | Store changelogs in Git/SVN alongside application code |
| **Environment Consistency** | Ensure dev, test, stage, and prod have identical schemas |
| **CI/CD Integration** | Automate deployments with Jenkins, GitHub Actions, GitLab CI, Azure DevOps |
| **Safe Deployments** | Preconditions, validations, and automatic rollback support |
| **Audit Trail** | Complete history of all schema changes and who made them |
| **Team Collaboration** | Multiple developers can work on database changes simultaneously |

[↑ Back to Table of Contents](#table-of-contents)

## Core Concepts

### Changelog

A **changelog** is a text file that contains a sequential list of all database changes.

**Think of it as:** A ledger or journal that records every modification to your database schema.

**Key Points:**
- Written in SQL, XML, YAML, or JSON
- Stored in version control (Git)
- Contains multiple changesets
- Deployed in order from top to bottom

**Simple Example (YAML):**

```yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: alice
      changes:
        - createTable:
            tableName: customer
            columns:
              - column:
                  name: id
                  type: int
                  autoIncrement: true
              - column:
                  name: name
                  type: varchar(255)

  - changeSet:
      id: 2
      author: bob
      changes:
        - addColumn:
            tableName: customer
            columns:
              - column:
                  name: email
                  type: varchar(255)
```

### Changeset

A **changeset** is a single unit of change in your changelog. It's the smallest deployable piece.

**Think of it as:** A Git commit for your database - one logical change with a unique identifier.

**Key Points:**
- Uniquely identified by `id + author + filepath`
- Contains one or more change types (ideally just one)
- Runs exactly once by default (unless `runAlways` or `runOnChange` specified)
- Either succeeds completely or fails completely (transactional)

**Changeset Anatomy:**

```yaml
- changeSet:
    id: 20260106-1200-PROJ-123-add-customer-email    # Unique ID
    author: alice                                      # Who made the change
    comment: Adding email field for customer notifications  # Why
    changes:
      - addColumn:
          tableName: customer
          columns:
            - column:
                name: email
                type: varchar(255)
                constraints:
                  nullable: false
    rollback:
      - dropColumn:
          tableName: customer
          columnName: email
```

### Change Types

**Change Types** specify what operation to perform on the database.

Liquibase provides two models:

#### 1. Platform-Agnostic Change Types (Recommended)

Can be defined in **YAML, JSON, or XML**. Liquibase translates these to database-specific SQL:

| Change Type | Purpose | Example |
|:---|:---|:---|
| `createTable` | Create a new table | `createTable: tableName: customer` |
| `addColumn` | Add column to existing table | `addColumn: tableName: customer` |
| `createIndex` | Create an index | `createIndex: tableName: customer` |
| `addForeignKeyConstraint` | Add foreign key | `addForeignKeyConstraint` |
| `loadData` | Insert data from CSV | `loadData: file: data.csv` |

**Benefits:**
- Same changelog works on PostgreSQL, SQL Server, Oracle, etc.
- Liquibase generates optimal SQL for each database
- Automatic rollback statements for many change types

**Drawbacks:**
- **No SQL Audit History:** This is a major drawback. The actual SQL executed is generated dynamically, so there is no permanent record of the exact code run against the database in your version control. This often disqualifies platform-agnostic change types for organizations with strict auditing requirements.
- **Limited Database-Specific Features:** Cannot use platform-specific features like PostgreSQL partial indexes or Oracle storage parameters
- **Performance Control:** Generated SQL may not be optimized for specific high-performance requirements
- **Coverage:** Not all database operations are supported by standard change types

#### 2. Raw SQL (When You Need Control)

Write database-specific SQL directly using either embedded SQL in YAML or "Formatted SQL" files.

**Option A: Embedded in YAML**

```yaml
- changeSet:
    id: 3
    author: alice
    changes:
      - sql:
          sql: |
            CREATE INDEX idx_customer_email 
            ON customer(email) 
            WHERE email IS NOT NULL;
      - rollback:
          sql: DROP INDEX idx_customer_email;
```

**Option B: Formatted SQL File (.sql)**

Use standard SQL with Liquibase-specific comments to define changesets. This gives you full control over SQL while maintaining tracking.

**[👉 Read the full Formatted SQL Guide](../../reference/liquibase/liquibase-formatted-sql-guide.md)** for detailed syntax on rollbacks, preconditions, and attributes.

```sql
--liquibase formatted sql

--changeset alice:3
CREATE INDEX idx_customer_email 
ON customer(email) 
WHERE email IS NOT NULL;
--rollback DROP INDEX idx_customer_email;
```

**Use when:**
- Leveraging database-specific features (e.g., PostgreSQL partial indexes)
- Performance-critical queries requiring specific syntax
- Platform-agnostic change types don't support your use case

#### 3. Custom Change Types (Java) & External Commands

**Custom Change Types** (implementing `CustomSqlChange` or `CustomTaskChange`) are **Java-only** because they compile to classes loaded by Liquibase.

**[👉 Read the full Custom Java Change Guide](../../reference/liquibase/custom-java-change-guide.md)** for implementation details, examples of masking data, and API integration.

However, you can use **`executeCommand`** to run scripts in **Python, bash, PowerShell, Node.js**, or any other language:

```yaml
- changeSet:
    id: 5
    author: alice
    changes:
      - executeCommand:
          executable: python
          args:
            - arg: {value: "scripts/migrate_data.py"}
```

**Use Custom Change Types (Java) when:**
- You want tightly integrated logic that can generate SQL (for preview)
- You need to access Liquibase internal APIs
- You want platform independence (Java runs everywhere)

**Use `executeCommand` (Scripts) when:**
- You have existing scripts in other languages
- You need to interact with OS-level tools
- Logic is too complex for standard SQL

### Tracking Tables

Liquibase creates two tables in your database to track changes:

#### DATABASECHANGELOG

**Purpose:** Records every changeset that's been deployed.

**Contains:**
- `ID` - Changeset ID
- `AUTHOR` - Who created it
- `FILENAME` - Which changelog file
- `DATEEXECUTED` - When it ran
- `MD5SUM` - Checksum to detect modifications
- `DESCRIPTION` - What it did
- `EXECTYPE` - How it ran (EXECUTED, RERAN, SKIPPED)

**Think of it as:** The deployment history for your database.

#### DATABASECHANGELOGLOCK

**Purpose:** Prevents multiple Liquibase instances from deploying simultaneously.

**Contains:**
- `ID` - Lock ID
- `LOCKED` - Is the database locked?
- `LOCKGRANTED` - When was it locked?
- `LOCKEDBY` - Who holds the lock?

**Think of it as:** A mutex/lock to ensure only one deployment happens at a time.

[↑ Back to Table of Contents](#table-of-contents)

## How Liquibase Works

### Basic Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Developer writes changes in changelog file              │
│    (SQL, YAML, XML, or JSON)                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Commit changelog to version control (Git)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Run: liquibase update                                    │
│    (CLI, CI/CD pipeline, Docker, application startup)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Liquibase reads changelog and checks DATABASECHANGELOG  │
│    to see what's already been deployed                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Liquibase deploys only NEW changesets                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Each deployed changeset recorded in DATABASECHANGELOG   │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Process

When you run `liquibase update`:

**Step 1: Acquire Lock**
- Check `DATABASECHANGELOGLOCK` table
- If locked, wait or fail
- Acquire lock to prevent concurrent deployments

**Step 2: Read Changelog**
- Parse changelog file (SQL, YAML, XML, JSON)
- Validate syntax and structure
- Check global preconditions (e.g., "only run on PostgreSQL")

**Step 3: Compare Changes**
- Query `DATABASECHANGELOG` table
- For each changeset in changelog:
  - Check if `id + author + filepath` exists in tracking table
  - If exists, skip (already deployed)
  - If new, mark for deployment

**Step 4: Execute Changes**
- For each new changeset:
  - Check changeset-level preconditions (e.g., "table must not exist")
  - Execute change types (CREATE TABLE, ADD COLUMN, etc.)
  - Calculate checksum (MD5)
  - Insert record into `DATABASECHANGELOG`
  - Commit transaction

**Step 5: Release Lock**
- Update `DATABASECHANGELOGLOCK` to unlocked
- Exit

### Change Detection

**How does Liquibase know what to run?**

Liquibase uses a **three-part unique identifier** for each changeset:

```
id + author + filepath = unique identifier
```

**Example:**

| Changeset in File | Already in Database? | Action |
|:---|:---|:---|
| `id: 1, author: alice, file: changelog.yaml` | ✅ Yes | Skip |
| `id: 2, author: bob, file: changelog.yaml` | ✅ Yes | Skip |
| `id: 3, author: alice, file: changelog.yaml` | ❌ No | **Deploy** |

**Important:** Once deployed, changesets should **never be modified**. Liquibase uses checksums to detect unauthorized changes.

[↑ Back to Table of Contents](#table-of-contents)

## Ways to Use Liquibase

### Changelog Formats

You can write changelogs in multiple formats. Choose based on your team's preferences and needs.

| Format | When to Use | Pros | Cons |
|:---|:---|:---|:---|
| **SQL** | You want full control over exact SQL | Familiar syntax, precise control, no abstraction | Database-specific, verbose, manual rollbacks |
| **YAML** | You want readability and portability | Human-readable, database-agnostic, compact | Learning curve for syntax |
| **XML** | Enterprise standards require XML | Well-defined schema, IDE autocomplete | Verbose, less readable |
| **JSON** | Integrating with JSON-based tools | Machine-readable, API-friendly | Less human-readable than YAML |

**Can you mix formats?** Yes! Your master changelog (XML/YAML/JSON) can include SQL, XML, YAML, and JSON files.

### Execution Methods

| Method | Use Case | Example |
|:---|:---|:---|
| **Command Line (CLI)** | Manual deployments, testing | `liquibase update` |
| **Docker** | Containerized environments | `docker run liquibase/liquibase update` |
| **CI/CD Pipeline** | Automated deployments | GitHub Actions, Jenkins, GitLab CI |
| **Kubernetes Init Container** | Deploy before app starts | Init container in pod spec |
| **Application Startup** | Embed in app code | Java API, Spring Boot integration |
| **Maven/Gradle** | Build tool integration | `mvn liquibase:update` |

### Integration Options

**CI/CD Platforms:**
- GitHub Actions
- GitLab CI/CD
- Jenkins
- Azure DevOps
- CircleCI
- TeamCity

**Build Tools:**
- Maven
- Gradle
- Ant

**Frameworks:**
- Spring Boot
- Quarkus
- Micronaut

**Orchestration:**
- Kubernetes (Init Containers)
- Docker Compose
- Helm Charts

[↑ Back to Table of Contents](#table-of-contents)

## Key Decisions to Make

Before implementing Liquibase, you need to make several architectural decisions:

### Changelog Format

**Decision:** Which format should we use for changelogs?

| Option | Best For |
|:---|:---|
| **SQL** | DBAs who need full control, database-specific optimizations |
| **YAML** | Developer-friendly, multi-database support, readability |
| **XML** | Enterprise shops with XML standards, complex preconditions |
| **JSON** | API-driven workflows, machine-generated changes |

**Recommendation:** Use **Formatted SQL** as the primary standard for all teams. It provides the best balance of control, auditability, and distinct diffs. Use YAML/XML only for the master changelog (`changelog.xml`) to include the SQL files.

### Directory Structure

**Decision:** How should we organize changelog files?

**Option A: Flattened (Standard)**
```
database/
  changelog/
    changelog.xml              # Master entry point
    baseline/
      V0000__baseline.sql      # Initial schema
    changes/
      V20260112__init.sql      # Timestamped changes
      V20260113__feature.sql
```
**Best for:** Most projects. Simple, sorts chronologically, easy to navigate.

**Option B: Application-First**
```
applications/
  payments_api/
    database/
      changelog.xml
      changes/
        V...
```
**Best for:** Monorepos with multiple distinct services.

### Change Granularity

**Decision:** How many changes should be in each changeset?

| Approach | When to Use |
|:---|:---|
| **One change per changeset** (Recommended) | Most cases - easier to debug, clearer history |
| **Multiple related changes** | Transactional requirement (e.g., add column + index together) |
| **Batch changes** | Performance (thousands of small changes) |

**Example (One Change per Changeset):**
```yaml
- changeSet:
    id: 1
    author: alice
    changes:
      - createTable: customer

- changeSet:
    id: 2
    author: alice
    changes:
      - addColumn: email to customer

- changeSet:
    id: 3
    author: alice
    changes:
      - createIndex: on customer.email
```

### Rollback Strategy

**Decision:** How will we handle rollbacks?

| Strategy | Approach | When to Use |
|:---|:---|:---|
| **Explicit Rollback** | Define rollback SQL for each changeset | Critical changes, production |
| **Automatic Rollback** | Let Liquibase generate rollback | Simple changes (ADD COLUMN) |
| **Forward-Only** | Never roll back, only forward fixes | High-velocity teams |
| **Rollback Tags** | Tag releases for rollback points | Version-based deployments |

**Recommendation:** Use **explicit rollback** for DROP operations and production changes. Use **rollback tags** at release boundaries.

### Environment Management

**Decision:** How will we handle multiple environments (dev, test, prod)?

| Approach | How It Works | Pros | Cons |
|:---|:---|:---|:---|
| **Properties Files** | Separate properties file per environment | Simple, explicit | Manual file management |
| **Environment Variables** | Inject connection info at runtime | Secure, CI/CD friendly | More complex setup |
| **Contexts** | Tag changesets with contexts (dev, prod) | Selective execution | Risk of env drift |
| **Separate Branches** | Git branch per environment | Full isolation | Merge complexity |

**Recommendation:** Use **properties files** for connection info + **environment variables** for secrets. Same changelogs deploy everywhere.

[↑ Back to Table of Contents](#table-of-contents)

## Common Patterns

### Master Changelog Pattern

**Problem:** Managing hundreds of changelog files becomes unwieldy.

**Solution:** Create a master changelog that includes all other changelogs:

```yaml
# db.changelog-master.yaml
databaseChangeLog:
  - include:
      file: releases/1.0/db.changelog-1.0.yaml
  - include:
      file: releases/2.0/db.changelog-2.0.yaml
  - include:
      file: releases/3.0/db.changelog-3.0.yaml
```

```yaml
# releases/1.0/db.changelog-1.0.yaml
databaseChangeLog:
  - include:
      file: 001-create-customer-table.yaml
  - include:
      file: 002-add-customer-indexes.yaml
  - tagDatabase:
      tag: v1.0
```

**Benefits:**
- Single entry point for all changes
- Logical grouping by release/feature
- Easy to navigate and understand structure

### Release-Based Organization

**Problem:** Changes accumulate over time; hard to track what's in each version.

**Solution:** Organize changesets into release folders:

```
releases/
  1.0/
    db.changelog-1.0.yaml
    001-create-tables.yaml
    002-add-indexes.yaml
  1.1/
    db.changelog-1.1.yaml
    001-add-email-column.yaml
  2.0/
    db.changelog-2.0.yaml
    001-refactor-customer-table.yaml
```

**Benefits:**
- Clear version history
- Tag releases for rollback points
- Aligns with application versioning

### Baseline Strategy

**Problem:** Adopting Liquibase for an existing database with complex schema.

**Solution:** Create a baseline snapshot of current state:

```bash
# Generate baseline from existing database
liquibase generate-changelog --changelog-file=baseline/db.changelog-baseline.yaml

# Mark baseline as already applied (don't re-run)
liquibase changelog-sync
```

Then start adding new changes:

```yaml
databaseChangeLog:
  - include:
      file: baseline/db.changelog-baseline.yaml
  - tagDatabase:
      tag: baseline
  - include:
      file: releases/1.0/db.changelog-1.0.yaml
```

**Benefits:**
- Clean starting point for existing databases
- Don't have to reverse-engineer all historical changes
- New databases can run baseline, existing databases skip it

[↑ Back to Table of Contents](#table-of-contents)

## Liquibase Editions

Liquibase offers multiple editions with different features:

| Feature | Community (Free) | Pro (Paid) | Secure (Enterprise) |
|:---|:---:|:---:|:---:|
| **Core Commands** (update, rollback, diff) | ✅ | ✅ | ✅ |
| **SQL, XML, YAML, JSON Changelogs** | ✅ | ✅ | ✅ |
| **Database Support** (50+ databases) | ✅ | ✅ | ✅ |
| **Command Line (CLI)** | ✅ | ✅ | ✅ |
| **Maven/Gradle/Ant Integration** | ✅ | ✅ | ✅ |
| **Rollback by Tag/Date/Count** | ✅ | ✅ | ✅ |
| **Structured Logging (JSON)** | ❌ | ✅ | ✅ |
| **Operation Reports** (drift, update) | ❌ | ✅ | ✅ |
| **Policy Checks** (quality gates) | ❌ | ✅ | ✅ |
| **Secrets Management** (Vault, AWS) | ❌ | ✅ | ✅ |
| **Native Executors** (performance) | ❌ | ✅ | ✅ |
| **Targeted Rollbacks** (specific changesets) | ❌ | ✅ | ✅ |
| **Flow Files** (advanced orchestration) | ❌ | ✅ | ✅ |
| **Central Dashboard** | ❌ | ❌ | ✅ |
| **Change Approvals** | ❌ | ❌ | ✅ |
| **Deployment Simulation** | ❌ | ❌ | ✅ |

**Note:** This document focuses on **Liquibase Community** features. Our architecture implements several Pro/Secure patterns using custom automation.

[↑ Back to Table of Contents](#table-of-contents)

## Next Steps

Now that you understand the core concepts, proceed to:

1. **[Liquibase Architecture Guide](./liquibase-architecture.md)** - Learn how we've designed our Liquibase implementation
2. **[Liquibase Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md)** - Hands-on guides for common tasks
3. **[Liquibase Reference](../../reference/liquibase/liquibase-reference.md)** - Command reference, glossary, troubleshooting

**Quick Start:**
1. Install Liquibase CLI
2. Create your first changelog (YAML recommended)
3. Run `liquibase update` against a dev database
4. Inspect `DATABASECHANGELOG` table to see tracked changes
5. Add a new changeset and run `liquibase update` again

[↑ Back to Table of Contents](#table-of-contents)

## Related Documentation

- **[Liquibase Architecture Guide](./liquibase-architecture.md)** - Multi-platform, multi-team directory structure and standards
- **[Liquibase Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md)** - Step-by-step procedures for deployments, rollbacks, baselines
- **[Liquibase Reference](../../reference/liquibase/liquibase-reference.md)** - Command reference, glossary, limitations, troubleshooting
- **[Official Liquibase Documentation](https://docs.liquibase.com/)** - Liquibase.com official docs
