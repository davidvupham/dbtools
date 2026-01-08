# Liquibase Glossary

## Core Concepts

| Term | Definition |
|------|------------|
| **Changelog** | Master file that lists all database changes in order (XML, YAML, SQL, or JSON format) |
| **Changeset** | A single unit of change (one or more SQL statements) with a unique identifier (author:id) |
| **Baseline** | Initial snapshot of an existing database, used when adopting Liquibase for an existing system |
| **Formatted SQL** | Liquibase-specific SQL format with metadata comments (`--liquibase formatted sql`, `--changeset`) |

## Commands

| Term | Definition |
|------|------------|
| **update** | Applies all pending (undeployed) changesets to the database |
| **updateSQL** | Generates SQL that would be run by `update`, without executing it (dry run) |
| **changelogSync** | Marks changesets as executed without running them (used for baselines) |
| **rollback** | Reverts changes back to a previous state (by tag, count, or date) |
| **status** | Shows which changesets are pending (not yet applied) |
| **diff** | Compares database state to changelog and shows differences |
| **diffChangeLog** | Generates a changelog from differences between database and reference |
| **generateChangeLog** | Creates a changelog from an existing database (for baselining) |
| **tag** | Creates a named marker in deployment history for rollback targets |

## Tracking Tables

| Table | Purpose |
|-------|---------|
| **DATABASECHANGELOG** | Records every changeset that has been applied (author, id, date, etc.) |
| **DATABASECHANGELOGLOCK** | Prevents concurrent Liquibase executions against the same database |

## Deployment Concepts

| Term | Definition |
|------|------------|
| **Drift** | Unauthorized or untracked changes made directly to a database outside Liquibase |
| **Environment Promotion** | Moving changes through dev → staging → production |
| **Idempotent** | A change that can be applied multiple times with the same result |
| **Precondition** | A check that must pass before a changeset executes |

## File Types

| Extension | Description |
|-----------|-------------|
| `.mssql.sql` | Formatted SQL for Microsoft SQL Server |
| `.postgresql.sql` | Formatted SQL for PostgreSQL |
| `.xml` | XML changelog format |
| `.yaml` | YAML changelog format |
