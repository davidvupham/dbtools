# How to set up project memory for Claude Code

**[← Back to Claude Code how-to guides](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 18, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Claude_Code-blue)

> [!IMPORTANT]
> **Prerequisites:** Claude Code CLI installed and authenticated, a project directory.

## Overview

This guide shows you how to set up a project memory system that persists knowledge across Claude Code sessions. You create four markdown files that track bugs, architectural decisions, configuration facts, and work history.

## Steps

### 1. Create the project notes directory

```bash
mkdir -p docs/project_notes
```

### 2. Create the bug log file

Create `docs/project_notes/bugs.md`:

```markdown
# Bug log

Track bugs, their solutions, and prevention strategies.

---

<!-- Add entries below in reverse chronological order -->
```

### 3. Create the decisions file

Create `docs/project_notes/decisions.md`:

```markdown
# Architectural decision records

Track architectural decisions with context and trade-offs.

---

<!-- Add ADR entries below -->
```

### 4. Create the key facts file

Create `docs/project_notes/key_facts.md`:

```markdown
# Key facts

Project configuration, ports, URLs, and important constants.

> [!WARNING]
> **Never store secrets here.** Use `.env` files (gitignored), cloud secrets managers, or CI/CD variables for passwords, API keys, and tokens.

## Safe to store

- Hostnames and URLs
- Port numbers
- Project identifiers
- Service account email addresses (identity only)
- Environment names

---

<!-- Add configuration sections below -->
```

### 5. Create the issues file

Create `docs/project_notes/issues.md`:

```markdown
# Work log

Track completed work with ticket references.

---

<!-- Add work log entries below -->
```

### 6. Update CLAUDE.md with memory-aware protocols

Add this section to your project's `CLAUDE.md`:

```markdown
## Project memory system

This project maintains institutional knowledge in `docs/project_notes/`.

### Memory files

- **bugs.md** - Bug log with dates, solutions, and prevention notes
- **decisions.md** - Architectural Decision Records (ADRs) with context
- **key_facts.md** - Project configuration, ports, important URLs
- **issues.md** - Work log with ticket IDs and descriptions

### Memory-aware protocols

**Before proposing architectural changes:**
- Check `docs/project_notes/decisions.md` for existing decisions
- Verify the proposed approach doesn't conflict with past choices

**When encountering errors or bugs:**
- Search `docs/project_notes/bugs.md` for similar issues
- Apply known solutions if found
- Document new bugs and solutions when resolved

**When looking up project configuration:**
- Check `docs/project_notes/key_facts.md` for ports, URLs, service accounts
- Prefer documented facts over assumptions
```

## Verification

After completing these steps, verify your setup:

```bash
ls -la docs/project_notes/
```

You should see:

```text
bugs.md
decisions.md
key_facts.md
issues.md
```

## Adding your first entries

### Add a bug entry

When you fix a bug, add an entry to `docs/project_notes/bugs.md`:

```markdown
### 2026-01-18 - Connection refused error on staging

- **Issue**: API requests failing with "connection refused" on port 5432
- **Root Cause**: VPN disconnected, database not accessible from local network
- **Solution**: Reconnect to VPN before running integration tests
- **Prevention**: Add VPN check to test setup script
```

### Add a decision entry

When you make an architectural decision, add an entry to `docs/project_notes/decisions.md`:

```markdown
### ADR-001: Use PostgreSQL for primary database (2026-01-18)

**Context:**
- Need relational database for user data and transactions
- Team has existing PostgreSQL expertise

**Decision:**
- Use PostgreSQL 15 with pgvector extension for embeddings

**Alternatives Considered:**
- MySQL -> Rejected: Less JSON support, team less familiar
- MongoDB -> Rejected: Need ACID transactions for financial data

**Consequences:**
- Benefits: Strong consistency, familiar tooling, good performance
- Trade-offs: Schema migrations required, less flexible than document store
```

### Add a key fact entry

Add configuration details to `docs/project_notes/key_facts.md`:

```markdown
## Database configuration

- PostgreSQL port: 5432
- Redis port: 6379
- Development database: `localhost:5432/myapp_dev`

## API endpoints

- Production: https://api.example.com/v1
- Staging: https://api.staging.example.com/v1
```

## Related guides

- [Tutorial: Customizing Claude Code](../../tutorials/claude-code-customization.md)
- [Reference: Claude Code configuration](../../reference/claude-code/configuration.md)
- [Best practices: Claude Code skills](../../best-practices/claude-code-skills.md)

## Sources

- [SpillwaveSolutions Project Memory](https://github.com/SpillwaveSolutions/project-memory) - Project memory skill implementation
- "Build Your First Claude Code Skill" by Rick Hightower - Original project memory concept
