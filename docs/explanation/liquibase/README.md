# Liquibase Documentation - Where to Start

> **Last Updated:** January 6, 2026

This directory contains comprehensive documentation for Liquibase database schema management. **Use this guide to navigate the right documents for your needs.**

## 🚀 Quick Start

**New to Liquibase?** Start here:

1. **[Liquibase Concepts Guide](./liquibase-concepts.md)**
   - What is Liquibase?
   - Core concepts (Changelog, Changeset, Change Types)
   - How it works
   - Different ways to use it
   - Key decisions to make

2. **[Liquibase Architecture Guide](./liquibase-architecture.md)**
   - Our directory structure and standards
   - How we organize changelogs across teams
   - Naming conventions
   - Design decisions we've made

3. **[Liquibase Operations Guide](../../how-to/liquibase/liquibase-operations-guide.md)**
   - How to author changes
   - How to deploy changes
   - Best practices for development

4. **[Liquibase Reference](../../reference/liquibase/liquibase-reference.md)**
   - Command reference
   - Configuration reference
   - Troubleshooting
   - Glossary

## 📚 Document Map

### For Different User Roles

| Role | Read These First |
|:---|:---|
| **New Liquibase User** | Concepts → Architecture → Operations |
| **Developer Adding Schema Changes** | Operations → Reference (for troubleshooting) |
| **DBA/DevOps Deploying Changes** | Architecture → Operations → Reference |
| **Tech Lead Planning Architecture** | Concepts → Architecture → Secure Implementation Analysis |
| **Troubleshooting Issues** | Reference (Troubleshooting section) |

### For Different Scenarios

| Scenario | Document | Section |
|:---|:---|:---|
| I'm confused about what Liquibase does | Concepts | [What is Liquibase?](./liquibase-concepts.md#what-is-liquibase) |
| I want to understand the core concepts | Concepts | [Core Concepts](./liquibase-concepts.md#core-concepts) |
| I want to understand our architecture | Architecture | [Design Principles](./liquibase-architecture.md#design-principles) |
| I need to create a changeset | Operations | [Authoring Changes](../../how-to/liquibase/liquibase-operations-guide.md#authoring-changes) |
| I need to deploy changes | Operations | [Execution Patterns](../../how-to/liquibase/liquibase-operations-guide.md#execution-patterns) |
| I need to roll back changes | Operations | [Rollback Strategy](../../how-to/liquibase/liquibase-operations-guide.md#rollback-strategy) |
| I need to detect/handle drift | Drift Management | [Understanding Drift](./liquibase-drift-management.md) + [Operations](../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation) |
| I'm seeing an error | Reference | [Troubleshooting](../../reference/liquibase/liquibase-reference.md#troubleshooting) |
| I need to integrate with CI/CD | Architecture | [Execution Methods](./liquibase-concepts.md#execution-methods) |
| I need to migrate an existing database | Operations | [Migration from Legacy](../../how-to/liquibase/liquibase-operations-guide.md#migration-from-legacy) |
| Should we use Liquibase Pro/Secure? | Secure Implementation Analysis | All sections |

## 📖 Full Document List

### 1. **Concepts Guide** (Read First!)
📄 [liquibase-concepts.md](./liquibase-concepts.md)

**What it covers:**
- What Liquibase is and why use it
- Core concepts clearly explained with analogies
- How Liquibase works under the hood
- The different ways to use Liquibase
- Key decisions you need to make
- Common patterns

**When to read:**
- ✅ You're new to Liquibase
- ✅ You want to understand the fundamentals
- ✅ You're explaining Liquibase to others
- ✅ You're designing your Liquibase strategy

---

### 2. **Architecture Guide** (Our Implementation)
📄 [liquibase-architecture.md](./liquibase-architecture.md)

**What it covers:**
- Our directory structure for organizing changelogs
- How we organize by team, application, platform
- Naming conventions for everything
- Repository strategy (separate repo per team)
- Design decisions and rationale
- Advanced patterns (cross-platform databases, etc.)
- Scaling patterns

**When to read:**
- ✅ You need to understand our architecture decisions
- ✅ You're setting up a new team repository
- ✅ You're creating changelogs following our standards
- ✅ You're integrating multiple platforms

**Prerequisites:** Read Concepts Guide first

---

### 3. **Operations Guide** (Day-to-Day Work)
📄 [how-to/liquibase/liquibase-operations-guide.md](../../how-to/liquibase/liquibase-operations-guide.md)

**What it covers:**
- How to write changesets
- Best practices for authoring changes
- How to handle preconditions and contexts
- How to deploy changes (locally, CI/CD, Docker)
- How to handle rollbacks
- How to detect and fix drift
- Testing strategies
- How to adopt Liquibase for existing databases

**When to read:**
- ✅ You're creating a changeset
- ✅ You're deploying changes
- ✅ You need to roll back
- ✅ You're troubleshooting deployment issues
- ✅ You're adopting Liquibase for a legacy database

**Prerequisites:** Read Concepts Guide first (Architecture helpful but not required)

---

### 4. **Reference Guide** (Lookup When Needed)
📄 [reference/liquibase/liquibase-reference.md](../../reference/liquibase/liquibase-reference.md)

**What it covers:**
- Edition differences (Community vs Pro vs Secure)
- Liquibase limitations by platform
- MongoDB-specific reference
- Configuration reference (environment variables)
- Changeset attributes reference
- Flowfile actions reference
- Troubleshooting section with common issues
- Glossary of terms
- Official documentation links

**When to read:**
- ✅ You're looking up a specific command or attribute
- ✅ You're troubleshooting an error
- ✅ You need to understand platform limitations
- ✅ You're configuring environment variables
- ✅ You're looking up terminology

**Prerequisites:** Concepts Guide (for glossary reference)

---

### 5. **Drift Management** (Understanding Drift)
📄 [drift-management.md](./liquibase-drift-management.md)

**What it covers:**
- What database drift is and why it matters
- Common causes of drift
- Types of drift (missing, unexpected, changed)
- Detection vs. generation capabilities
- Remediation strategies
- Best practices for prevention

**When to read:**
- ✅ You want to understand what drift is
- ✅ You're planning drift management strategy
- ✅ You need to explain drift to stakeholders

**Prerequisites:** Basic Liquibase concepts

---

### 6. **Secure Edition Implementation Analysis** (Strategic Planning)
📄 [liquibase-secure-edition-implementation-analysis.md](./liquibase-secure-edition-implementation-analysis.md)

**What it covers:**
- Analysis of Liquibase Pro/Secure features
- Feature comparison matrix
- Implementation complexity assessment
- Cost-benefit analysis for each feature
- Custom implementation approaches
- When licensing makes sense vs. when to build custom

**When to read:**
- ✅ You're evaluating whether to purchase Liquibase Pro/Secure
- ✅ You're planning to implement Pro features with Community Edition
- ✅ You're assessing engineering effort for custom features
- ✅ You're making budget decisions

**Prerequisites:** Concepts Guide + Architecture Guide

---

## 🔗 Document Relationships

```
CONCEPTS GUIDE (Foundation)
    ↓
    ├─→ ARCHITECTURE GUIDE (Our Implementation)
    │        ↓
    │        └─→ SECURE IMPLEMENTATION ANALYSIS (Licensing Decisions)
    │
    └─→ OPERATIONS GUIDE (Day-to-Day Work)
             ↓
             └─→ REFERENCE GUIDE (Lookup & Troubleshooting)
```

## ❓ Common Questions

### "Which document should I read?"

**If you're a:**
- **Total beginner:** Start with Concepts → then pick your next doc based on role
- **Developer:** Concepts → Operations, reference others as needed
- **DevOps/DBA:** Concepts → Architecture → Operations → Reference (as needed)
- **Tech Lead/Manager:** Concepts → Architecture → Secure Analysis

### "I just want to write a changeset, where do I go?"

1. Quick concept review: [Core Concepts - Changeset](./liquibase-concepts.md#changeset)
2. How to write it: [Operations - Authoring Changes](../../how-to/liquibase/liquibase-operations-guide.md#authoring-changes)
3. Our naming standards: [Architecture - Conventions](./liquibase-architecture.md#conventions--standards)

### "Everything is too deep, where's a quick intro?"

👉 Start with [Concepts Guide - Core Concepts](./liquibase-concepts.md#core-concepts) section. It's written for beginners.

### "I found an error, how do I fix it?"

1. Search in [Reference - Troubleshooting](../../reference/liquibase/liquibase-reference.md#troubleshooting)
2. If not found, check [Operations Guide - Testing Strategy](../../how-to/liquibase/liquibase-operations-guide.md#testing-strategy)
3. If still stuck, ask your team's Liquibase lead

### "I need to set up a new repository for my team"

1. Skim [Architecture - Repository Strategy](./liquibase-architecture.md#repository-strategy)
2. Read [Architecture - Directory Structure](./liquibase-architecture.md#directory-structure)
3. Read [Architecture - Conventions](./liquibase-architecture.md#conventions--standards)
4. Use it as a checklist when creating your repo

## 🔍 Search Tips

- **Looking for "changelog"?** → Concepts ([Changelog](./liquibase-concepts.md#changelog))
- **Looking for "rollback"?** → Operations ([Rollback Strategy](../../how-to/liquibase/liquibase-operations-guide.md#rollback-strategy))
- **Looking for "preconditions"?** → Operations ([Using Preconditions](../../how-to/liquibase/liquibase-operations-guide.md#using-preconditions))
- **Looking for "properties"?** → Architecture ([Properties Files](./liquibase-architecture.md#properties-files))
- **Looking for "directory structure"?** → Architecture ([Directory Structure](./liquibase-architecture.md#directory-structure))
- **Looking for "drift detection"?** → Concepts ([Understanding Drift](./liquibase-drift-management.md)) or Operations ([Drift Detection](../../how-to/liquibase/liquibase-operations-guide.md#drift-detection-and-remediation))
- **Looking for an error message?** → Reference ([Troubleshooting](../../reference/liquibase/liquibase-reference.md#troubleshooting))

## 📞 Getting Help

**Before asking for help, check:**

1. This README to find the right document
2. The relevant document's table of contents
3. Use Ctrl+F to search within the document
4. Check the [Reference Guide - Troubleshooting](../../reference/liquibase/liquibase-reference.md#troubleshooting)

**If you still need help:**
- Ask your team's Liquibase lead
- Check the [Official Liquibase Documentation](https://docs.liquibase.com/)
- Post in your team's Slack channel

## 📝 How We Keep Docs Updated

- **Concepts Guide:** Updated when fundamental Liquibase changes
- **Architecture Guide:** Updated when standards change
- **Operations Guide:** Updated quarterly with new procedures
- **Reference Guide:** Updated with each tool version
- **Secure Analysis:** Updated yearly or when feature changes

Last update: January 6, 2026
