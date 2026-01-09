# Tutorial Comparison: Part 3 vs End-to-End Guide

## Overview

Both tutorials cover GitHub Actions CI/CD with Liquibase, but they serve different purposes and audiences.

---

## Key Differences

### 1. **Purpose & Audience**

#### `series-part3-cicd.md` (Part 3 of Series)
- **Purpose:** Part 3 of a structured 3-part learning series
- **Audience:** Learners following the complete series sequentially
- **Assumes:** You've completed Part 1 and Part 2 first
- **Focus:** Adding CI/CD to an existing local Liquibase project

#### `guide-end-to-end-pipeline.md` (Standalone End-to-End)
- **Purpose:** Single comprehensive guide from scratch to CI/CD
- **Audience:** Developers/DBAs who want one complete tutorial
- **Assumes:** Basic Git/GitHub knowledge, but new to Liquibase/CI/CD
- **Focus:** Complete journey from local setup → GitHub → CI/CD

---

### 2. **Scope & Coverage**

#### `series-part3-cicd.md`
- **Starts at:** Step 6 (GitHub repository setup)
- **Skips:** Local environment setup (covered in Part 1)
- **Covers:**
  - Git repository creation
  - Self-hosted runner setup (references `guide-runner-setup.md`)
  - GitHub Actions workflows
  - Multi-environment pipeline
  - Branch-based workflow (multi-user tutorial setup)

#### `guide-end-to-end-pipeline.md`
- **Starts at:** Step 1 (complete local setup)
- **Covers everything:**
  - Phase 1: Local environment setup (Steps 1-5)
    - Setup helper scripts
    - SQL Server container
    - Database creation
    - Baseline generation
    - Baseline deployment
  - Phase 2: Git/GitHub (Steps 6-8)
  - Phase 3: CI/CD (Steps 9-12)
  - Phase 4: Integration (Steps 13-14)
  - Phase 5: Best practices

---

### 3. **Prerequisites**

#### `series-part3-cicd.md`
**Requires:**
- ✅ Completed Part 1: Baseline setup
- ✅ (Recommended) Completed Part 2: Manual deployment
- ✅ Existing Liquibase project at `$LIQUIBASE_TUTORIAL_DATA_DIR`
- ✅ Baseline deployed to dev/stg/prd
- ✅ Environment properties files created

**What you already have:**
- Local project structure
- Helper scripts configured
- SQL Server containers running
- Baseline changelog generated

#### `guide-end-to-end-pipeline.md`
**Requires:**
- ✅ Docker installed
- ✅ Git installed
- ✅ GitHub account
- ✅ Repository cloned locally
- ✅ Helper scripts available (but walks through setup)

**What you start with:**
- Nothing - builds everything from scratch

---

### 4. **Tutorial Structure**

#### `series-part3-cicd.md`
```
Prerequisites (assumes Part 1 & 2 done)
├── Phase 2: Git/GitHub (Steps 6-8)
│   ├── Step 6: Create GitHub repo
│   ├── Step 7: Initialize Git (first person)
│   └── Step 8: Create personal branch (all learners)
├── Phase 3: CI/CD (Steps 9-13)
│   ├── Step 9: Database locations
│   ├── Step 10: Self-hosted runner setup
│   ├── Step 11: GitHub Secrets
│   ├── Step 12: First workflow
│   └── Step 13: Multi-env pipeline
├── Phase 4: Integration (Steps 14-15)
└── Phase 5: Best practices
```

#### `guide-end-to-end-pipeline.md`
```
Prerequisites (minimal - just tools)
├── Phase 1: Local Setup (Steps 1-5)
│   ├── Step 1: Setup helper
│   ├── Step 2: Start containers
│   ├── Step 3: Create databases
│   ├── Step 4: Create project & baseline
│   └── Step 5: Deploy baseline
├── Phase 2: Git/GitHub (Steps 6-8)
├── Phase 3: CI/CD (Steps 9-12)
├── Phase 4: Integration (Steps 13-14)
└── Phase 5: Best practices
```

---

### 5. **Multi-User Support**

#### `series-part3-cicd.md`
- **Emphasizes:** Branch-based multi-user tutorial setup
- **Features:**
  - Branch-based approach (`tutorial-*` branches)
  - Workflows trigger on individual branches
  - Shared repository with collaborators
  - Each learner has personal branch
- **Use case:** Classroom/workshop with multiple learners

#### `guide-end-to-end-pipeline.md`
- **Focus:** Single-user workflow
- **Workflow:** Main branch → CI/CD pipeline
- **Use case:** Individual developer learning

---

### 6. **Runner Setup Detail**

#### `series-part3-cicd.md`
- **Step 10:** Provides checklist and basic setup
- **References:** `guide-runner-setup.md` for detailed instructions
- **Approach:** "Quick setup" with link to comprehensive guide
- **Verification:** Checklist before proceeding

#### `guide-end-to-end-pipeline.md`
- **Step 9a:** Inline runner setup instructions
- **Self-contained:** All setup steps included
- **Approach:** Complete instructions in one place
- **Verification:** Less detailed (assumes you follow steps)

---

### 7. **Database Architecture**

#### `series-part3-cicd.md`
- **Assumes:** Three separate containers (`mssql_dev`, `mssql_stg`, `mssql_prd`)
- **Ports:** 14331, 14332, 14333 (defaults)
- **Network:** `liquibase_tutorial`
- **JDBC URLs:** `localhost:PORT` (from runner perspective)

#### `guide-end-to-end-pipeline.md`
- **Uses:** Single container (`mssql_liquibase_tutorial`)
- **Port:** 14333 (host), 1433 (container)
- **Network:** `liquibase_tutorial`
- **JDBC URLs:** `mssql_liquibase_tutorial:1433` (container name)
- **Note:** Simplified for tutorial (same database name for all envs)

---

### 8. **Workflow Triggers**

#### `series-part3-cicd.md`
```yaml
on:
  push:
    branches:
      - 'tutorial-*'  # All tutorial branches
    paths:
      - 'database/**'
```

#### `guide-end-to-end-pipeline.md`
```yaml
on:
  push:
    branches:
      - main  # Main branch
    paths:
      - 'database/**'
```

---

## When to Use Which Tutorial

### Use `series-part3-cicd.md` when:
- ✅ You're following the 3-part series sequentially
- ✅ You've completed Part 1 and Part 2
- ✅ You already have a local Liquibase project set up
- ✅ You're in a multi-user tutorial/classroom setting
- ✅ You want branch-based workflows
- ✅ You prefer modular learning (one concept per part)

### Use `guide-end-to-end-pipeline.md` when:
- ✅ You want a single comprehensive tutorial
- ✅ You're starting from scratch
- ✅ You prefer self-contained documentation
- ✅ You're learning independently (not in a class)
- ✅ You want to see the complete flow in one document
- ✅ You don't want to reference multiple documents

---

## Relationship to Other Guides

### `guide-runner-setup.md`
- **Purpose:** Detailed self-hosted runner setup guide
- **Referenced by:** Both tutorials
- **Content:** Comprehensive runner configuration, troubleshooting, advanced topics
- **Use when:** You need detailed runner setup or troubleshooting

### `series-part1-baseline.md` & `series-part2-manual.md`
- **Purpose:** Foundation tutorials (local setup, manual workflows)
- **Required for:** `series-part3-cicd.md`
- **Optional for:** `guide-end-to-end-pipeline.md` (includes similar content inline)

---

## Summary Table

| Aspect | `series-part3-cicd.md` | `guide-end-to-end-pipeline.md` |
|--------|------------------------|-------------------------------|
| **Type** | Part 3 of series | Standalone comprehensive guide |
| **Prerequisites** | Part 1 & 2 completed | Minimal (just tools) |
| **Starting Point** | Step 6 (Git setup) | Step 1 (local setup) |
| **Local Setup** | Assumes done | Includes Phase 1 |
| **Multi-User** | Branch-based emphasis | Single-user focus |
| **Runner Setup** | References detailed guide | Inline instructions |
| **Database Setup** | 3 containers (dev/stg/prd) | 1 container (simplified) |
| **Workflow Triggers** | `tutorial-*` branches | `main` branch |
| **Best For** | Sequential learning | One-stop tutorial |

---

## Recommendation

**For new learners:**
- Start with `guide-end-to-end-pipeline.md` if you want everything in one place
- Or follow the series: Part 1 → Part 2 → Part 3 for structured learning

**For classroom/workshop:**
- Use `series-part3-cicd.md` for its multi-user branch-based approach

**For detailed runner setup:**
- Both reference `guide-runner-setup.md` for comprehensive runner configuration

---

**Both tutorials are valid and serve different learning styles. Choose based on your preference for modular vs. comprehensive learning.**
