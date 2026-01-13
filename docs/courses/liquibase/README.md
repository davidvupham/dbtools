# 🚀 Start Here: Liquibase + Database DevOps Tutorial Series

## Introduction

This is a **comprehensive tutorial series** on implementing database CI/CD with Liquibase. It is designed to take you from "manual updates" to "fully automated pipeline" in a structured, safe way.

### Core Philosophy: Manual First, Then Automate

We believe you cannot effectively automate what you do not understand. Therefore, this tutorial series is structured in two distinct phases:

1. **Phase 1: The Manual Workflow (Parts 1 & 2)**
    - Learn Liquibase concepts (changelogs, tracking tables, drift).
    - Execute commands manually (`update`, `rollback`) against local Docker containers.
    - Understand *how* Liquibase works before hiding it behind a pipeline.

2. **Phase 2: The Automated Pipeline (Part 3)**
    - Only after mastering the basics do we introduce GitHub Actions.
    - Wire your local project into a CI/CD pipeline.
    - Focus on DevOps concepts (runners, secrets, gates) rather than struggling with Liquibase basics.

## 📂 Directory Structure

The `docs/courses/liquibase/` directory is organized as follows:

```text
docs/courses/liquibase/
├── README.md                  <-- You are here (Navigation Hub)
├── course_overview.md         <-- Learning objectives, prerequisites
├── quick_reference.md         <-- Common commands cheat sheet
├── glossary.md                <-- Terminology definitions
├── liquibase_course_design.md <-- Requirements and design
├── BEST_PRACTICES_MODULARITY.md <-- Modularity and reusability best practices
├── REFACTORING_SUMMARY.md <-- Refactoring documentation
├── learning-paths/            <-- All Tutorial Content
│   ├── series-part1-baseline.md    (Manual: Setup & Baseline)
│   ├── series-part2-manual.md      (Manual: Deployment Lifecycle)
│   ├── tutorial-supplement-runner-setup.md       (Infra: Self-Hosted Runner)
│   ├── series-part3-cicd.md        (Automation: GitHub Actions)
│   └── tutorial-supplement-end-to-end-pipeline.md (Advanced: The "All-in-One" Path)
├── docker/                    <-- Docker Compose for tutorial
├── scripts/                   <-- Reusable modular scripts (see scripts/README.md)
└── runner_config/             <-- Runner environment configs
```

## 📋 Quick Resources

- **[Course Overview](./course_overview.md)** - Learning objectives, time estimates, prerequisites
- **[Quick Reference](./quick_reference.md)** - Common commands and scripts cheat sheet
- **[Scripts Documentation](./scripts/README.md)** - All available scripts and naming conventions
- **[Glossary](./glossary.md)** - Terminology definitions

## 📚 Learning Paths

Choose the path that fits your experience level.

### ✅ Recommended Path (Beginner to Intermediate)

*Best for: Users new to specific tools or those wanting a solid foundation.*

1. **[Part 1: Baseline Setup](./learning-paths/series-part1-baseline.md)**
    - *Goal*: Get a running SQL Server, install Liquibase, and capture an existing database state.

2. **[Part 2: Manual Lifecycle](./learning-paths/series-part2-manual.md)**
    - *Goal*: Practice the daily developer workflow (create migration -> deploy -> rollback) locally.

3. **[Infra Guide: Runner Setup](./learning-paths/tutorial-supplement-runner-setup.md)**
    - *Goal*: Set up a free local GitHub Actions runner to test pipelines without cloud costs.

4. **[Part 3: CI/CD Automation](./learning-paths/series-part3-cicd.md)**
    - *Goal*: Connect your local project to GitHub and build a Dev -> Stage -> Prod pipeline.

---

### 🚀 Fast Track (Advanced Users)

*Best for: Experienced DevOps engineers who just want the code.*

- **[End-to-End Pipeline Guide](./learning-paths/tutorial-supplement-end-to-end-pipeline.md)**
  - The entire process (Local -> CI/CD) in one guide. Acts as a navigation map referencing the series parts. Good for searching or "ctrl+f", less good for step-by-step learning.

---

## ⚖️ Method Comparison: Local vs CI/CD

| Feature | Local Docker (Parts 1 & 2) | GitHub Actions (Part 3) |
| :--- | :--- | :--- |
| **Execution** | Manual (`lb update`) | Automated (Git Push) |
| **Visibility** | Terminal Output | GitHub Actions Logs |
| **Security** | Local properties file | GitHub Secrets |
| **Approval** | None (You are root) | Environment Protection Rules |
| **Best For** | Development, Learning, Debugging | Staging, Production, Audit Compliance |

## ❓ Frequently Asked Questions

### Q: Do I need to finish Part 1 & 2 before Part 3?

**A:** Highly recommended. Use Part 3 only if you are already comfortable with Liquibase command line, baselines, and drift detection. If you jump straight to CI/CD, debugging "why did my pipeline fail?" becomes much harder if you don't know the underlying Liquibase error.


### Q: Why do you suggest a self-hosted runner?

**A:** It allows you to complete the entire CI/CD tutorial **locally** and for **free**, without needing to open firewall ports to GitHub cloud runners. It simulates a "private network" deployment common in enterprise environments.

### Q: Where are the helper scripts?

**A:** Check the `scripts/` folder. All scripts use descriptive names (e.g., `setup_liquibase_environment.sh`, `start_mssql_containers.sh`) making them self-documenting and reusable. The tutorial relies on `setup_tutorial.sh` to configure easy aliases like `lb` (Liquibase wrapper) and `sqlcmd-tutorial`. See [Scripts Documentation](./scripts/README.md) for a complete list.

## 🆘 Troubleshooting & Help

- **Liquibase Issues**: Check `learning-paths/series-part1-baseline.md` troubleshooting section.
- **Runner Issues**: Check `learning-paths/tutorial-supplement-runner-setup.md`.
- **Community**:
  - [Liquibase Forum](https://forum.liquibase.org/)
  - [GitHub Community](https://github.com/orgs/community/discussions)

---
