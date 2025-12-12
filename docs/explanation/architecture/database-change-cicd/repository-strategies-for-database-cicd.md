# Repository Strategies for Database CI/CD: Single vs Multiple Repositories

## Table of Contents

- [Introduction](#introduction)
- [What is a Repository?](#what-is-a-repository)
- [Understanding the Decision](#understanding-the-decision)
- [Single Repository Approach (Monorepo)](#single-repository-approach-monorepo)
- [Multiple Repository Approach (Polyrepo)](#multiple-repository-approach-polyrepo)
- [Detailed Comparison](#detailed-comparison)
- [Real-World Scenarios](#real-world-scenarios)
- [Best Practices by Team Size](#best-practices-by-team-size)
- [Decision Framework](#decision-framework)
- [Migration Strategies](#migration-strategies)
- [Common Pitfalls](#common-pitfalls)
- [Recommendations](#recommendations)
- [FAQ](#faq)

## Introduction

When implementing database CI/CD with GitHub Actions, one of the first decisions you'll face is: **Should database changes live in the same repository as application code, or in a separate repository?**

This document explains both approaches in simple terms, helping you make the right choice for your team.

### Who This Document Is For

- ✅ Teams new to GitHub and version control
- ✅ Developers deciding on repository structure
- ✅ Team leads planning CI/CD implementation
- ✅ Anyone confused about "monorepo vs polyrepo"

### What You'll Learn

- What repositories are and why they matter
- Pros and cons of each approach
- How to choose the right strategy
- Best practices for your team size
- How to avoid common mistakes

## What is a Repository?

Before we dive in, let's clarify what a repository (or "repo") is.

### Simple Explanation

A **repository** is like a **project folder** that contains:
- Your code files
- History of all changes (who changed what, when)
- Version history (like track changes in Word)
- Configuration for automated processes

**Think of it like:**
- A Google Drive folder with complete history
- A project folder with built-in time travel
- A shared workspace where everyone's changes are tracked

### Repository in GitHub

When using GitHub, a repository:
- Lives at a URL: `https://github.com/yourcompany/yourproject`
- Contains all files for a project
- Tracks every change ever made
- Enables collaboration between team members
- Triggers automated workflows (CI/CD)

**Example Repository Structure:**
```
my-application/
├── src/                    # Application source code
│   ├── controllers/
│   ├── models/
│   └── services/
├── tests/                  # Test files
├── database/              # Database changes (Liquibase)
│   └── changelog/
├── .github/               # GitHub Actions workflows
│   └── workflows/
├── README.md              # Project documentation
└── package.json           # Dependencies
```

### Why Repository Structure Matters

The way you organize repositories affects:
- **How team members collaborate** - Who can see and change what
- **How deployments work** - What gets deployed together
- **How changes are reviewed** - What changes are reviewed together
- **How access is controlled** - Who has access to what

## Understanding the Decision

### The Core Question

**Should database changes and application code live in the same repository or separate repositories?**

```
Option 1: SAME REPOSITORY (Monorepo)
my-application/
├── src/                    # App code
└── database/              # Database changes
    └── changelog/

Option 2: SEPARATE REPOSITORIES (Polyrepo)
my-application/            # Repository 1
└── src/                   # App code only

my-application-db/         # Repository 2
└── database/              # Database changes only
    └── changelog/
```

### Why This Matters for CI/CD

Your repository structure determines:
- **When deployments happen** - Together or independently
- **Who can approve changes** - Same people or different teams
- **How changes are coordinated** - Automatic or manual
- **What your CI/CD workflows look like** - Simple or complex

## Single Repository Approach (Monorepo)

### What It Is

**Definition**: All code for a project lives in ONE repository - application code, database changes, tests, configuration, everything.

**Visual:**
```
https://github.com/yourcompany/customer-service
│
├── src/                              # Application code
│   ├── api/
│   ├── services/
│   └── models/
│
├── database/                         # Database changes
│   └── changelog/
│       ├── changelog.xml
│       ├── baseline/
│       └── changes/
│
├── tests/                            # Tests
│   ├── unit/
│   └── integration/
│
├── .github/workflows/                # CI/CD workflows
│   ├── app-deploy.yml
│   └── database-deploy.yml
│
└── README.md
```

### How It Works

#### 1. Developer Workflow

```bash
# 1. Clone the repository (get everything)
git clone https://github.com/yourcompany/customer-service
cd customer-service

# 2. Create a branch for your work
git checkout -b feature/add-customer-status

# 3. Make changes to BOTH app and database
# Edit application code
vim src/services/customer-service.js

# Edit database schema
vim database/changelog/changes/V0023__add_customer_status.sql

# 4. Commit BOTH changes together
git add src/services/customer-service.js
git add database/changelog/changes/V0023__add_customer_status.sql
git commit -m "Add customer status feature"

# 5. Push to GitHub
git push origin feature/add-customer-status

# 6. Create Pull Request (PR)
# Team reviews BOTH app and database changes together

# 7. After approval, merge to main
# GitHub Actions automatically deploys BOTH app and database
```

#### 2. CI/CD Workflow

```yaml
# .github/workflows/full-stack-deploy.yml
name: Full Stack Deployment

on:
  push:
    branches: [main]

jobs:
  # Deploy database changes first
  deploy-database:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy database changes
        run: liquibase update

  # Then deploy application (depends on database)
  deploy-application:
    needs: deploy-database  # Wait for database first
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy application
        run: npm run deploy
```

**What happens:**
1. Developer pushes code to main branch
2. GitHub Actions deploys database changes
3. GitHub Actions waits for database to complete
4. GitHub Actions deploys application
5. Everything is deployed together automatically

### Advantages (Pros)

#### ✅ 1. Atomic Changes

**What it means**: App and database changes happen together as one unit.

**Why it's good:**
- No version mismatch between app and database
- Can't deploy app without matching database changes
- Can't deploy database without matching app changes

**Example scenario:**
```
Your app adds a new feature that requires a new database column.

Single repo:
✅ One commit contains both changes
✅ One pull request for both
✅ Both deploy together
✅ Impossible to have mismatch
```

#### ✅ 2. Simplified Coordination

**What it means**: No need to sync between multiple repositories.

**Why it's good:**
- Don't need to track "which app version needs which database version"
- One commit SHA represents complete state
- Rollback is simple - everything goes back together

**Example scenario:**
```
Bug found in production!

Single repo:
✅ Rollback to previous commit
✅ App AND database go back together
✅ System is consistent
```

#### ✅ 3. Easier Code Review

**What it means**: Reviewers see complete picture in one pull request.

**Why it's good:**
- See how app uses database changes
- Understand complete feature
- Better context for review

**Example PR view:**
```
Pull Request #123: Add customer loyalty program

Files changed:
✅ src/services/loyalty-service.js          (reviewer sees app logic)
✅ database/changelog/changes/V0050.sql    (reviewer sees schema)
✅ tests/loyalty.test.js                   (reviewer sees tests)

Reviewer can see: "Ah, the app expects this column, and here's where it's created"
```

#### ✅ 4. Simpler for Small Teams

**What it means**: Less overhead, fewer repositories to manage.

**Why it's good:**
- One repository to clone
- One set of issues/PRs
- One place to look for everything
- Less context switching

**Daily work:**
```
Developer's morning:
✅ Open one repository
✅ See all relevant code
✅ Make changes
✅ Test locally
✅ Push to one place
```

#### ✅ 5. Easier Local Development

**What it means**: Everything you need is in one place.

**Why it's good:**
- Clone once, have everything
- Run full stack locally
- Test app with database together
- Simpler setup for new developers

**New developer onboarding:**
```
Day 1:
✅ Clone one repository
✅ Run setup script
✅ Have complete working environment
   (Takes 30 minutes)
```

#### ✅ 6. Single Source of Truth

**What it means**: One place to look for current state.

**Why it's good:**
- No confusion about versions
- One commit history
- One place for documentation
- Clear ownership

### Disadvantages (Cons)

#### ❌ 1. Mixed Concerns

**What it means**: Application and database code live together.

**Why it can be bad:**
- Less clear separation of responsibilities
- Database code mixed with application code
- Harder to apply different standards to each

**Example issue:**
```
Your team has different rules for app vs database:

- App code: Junior developers can approve
- Database: Only senior DBAs can approve

Single repo makes this harder to enforce
```

#### ❌ 2. Shared Access Control

**What it means**: Everyone with repo access can see and change everything.

**Why it can be bad:**
- Can't restrict database access to specific people
- All developers see database credentials in CI/CD
- Harder to implement separation of duties

**Example issue:**
```
Security requirement:
"Only DBAs should approve production database changes"

Single repo:
❌ All developers can see database code
❌ Hard to restrict who approves database PRs
❌ CI/CD secrets visible to all
```

#### ❌ 3. Coupled Deployment

**What it means**: Database and app deploy together always.

**Why it can be bad:**
- Can't deploy database fixes without deploying app
- Can't deploy app fixes without triggering database pipeline
- Less flexibility in deployment timing

**Example issue:**
```
Scenario: Bug in application, database is fine

Single repo:
❌ Deploy app fix
❌ Triggers database pipeline too (unnecessary)
❌ Takes longer
❌ More risk
```

#### ❌ 4. Large Repository Size

**What it means**: Repository grows with all code.

**Why it can be bad:**
- Slower to clone
- More files to navigate
- Longer build times
- More complex CI/CD

**Example issue:**
```
After 2 years:
- App code: 10,000 files
- Database: 500 changelogs
- Tests: 5,000 files
- Total: 15,500 files

❌ Clone takes 5 minutes
❌ Search is slower
❌ CI/CD takes longer
```

#### ❌ 5. Build Complexity

**What it means**: CI/CD needs to handle different types of code.

**Why it can be bad:**
- Workflows need to detect what changed
- Different tools for app vs database
- More complex pipeline logic

**Example workflow complexity:**
```yaml
jobs:
  detect-changes:
    # Complex logic to detect what changed

  deploy-database:
    if: database files changed

  deploy-app:
    if: app files changed

  deploy-both:
    if: both changed
```

### When to Use Single Repository

✅ **Best for:**
- **Small teams** (under 20 people)
- **Tightly coupled** app and database changes
- **Rapid development** environments
- **Simple deployment** needs
- **Startups** and growing companies
- **Microservices** (one repo per service)

✅ **Use when:**
- Most changes affect both app and database
- Team members work on both app and database
- Deployment happens at same time
- Coordination overhead is costly
- Team prefers simplicity

## Multiple Repository Approach (Polyrepo)

### What It Is

**Definition**: Application code and database changes live in SEPARATE repositories.

**Visual:**
```
Repository 1: Application
https://github.com/yourcompany/customer-service
│
├── src/                              # Application code only
│   ├── api/
│   ├── services/
│   └── models/
│
├── tests/                            # Application tests
│
├── .github/workflows/                # App deployment only
│   └── app-deploy.yml
│
└── README.md

Repository 2: Database
https://github.com/yourcompany/customer-service-database
│
├── database/                         # Database changes only
│   └── changelog/
│       ├── changelog.xml
│       ├── baseline/
│       └── changes/
│
├── docs/                             # Database documentation
│
├── .github/workflows/                # Database deployment only
│   └── database-deploy.yml
│
└── README.md
```

### How It Works

#### 1. Developer Workflow

```bash
# Scenario: Add customer status feature

# PART 1: Database Changes First
# 1. Clone database repository
git clone https://github.com/yourcompany/customer-service-database
cd customer-service-database

# 2. Create branch for database changes
git checkout -b database/add-customer-status

# 3. Add database changes
vim database/changelog/changes/V0023__add_customer_status.sql

# 4. Commit and push
git add database/changelog/changes/V0023__add_customer_status.sql
git commit -m "Add customer status column"
git push origin database/add-customer-status

# 5. Create Pull Request in database repo
# DBA reviews and approves

# 6. Merge and deploy to dev/staging
# Note the version: v0023

# PART 2: Application Changes Second
# 7. Clone application repository
cd ..
git clone https://github.com/yourcompany/customer-service
cd customer-service

# 8. Create branch for app changes
git checkout -b feature/add-customer-status

# 9. Update application code
vim src/services/customer-service.js
# Add note: "Requires database version v0023"

# 10. Commit and push
git add src/services/customer-service.js
git commit -m "Add customer status feature (requires DB v0023)"
git push origin feature/add-customer-status

# 11. Create Pull Request in app repo
# Team reviews app code

# 12. Merge and deploy
```

#### 2. CI/CD Workflow

**Database Repository:**
```yaml
# customer-service-database/.github/workflows/database-deploy.yml
name: Database Deployment

on:
  push:
    branches: [main]

jobs:
  deploy-database:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy database changes
        run: liquibase update

      - name: Tag version
        run: |
          VERSION=$(grep "version" version.txt)
          git tag $VERSION
          # Other repos can reference this version
```

**Application Repository:**
```yaml
# customer-service/.github/workflows/app-deploy.yml
name: Application Deployment

on:
  push:
    branches: [main]

jobs:
  deploy-application:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy application
        run: npm run deploy
```

**What happens:**
1. Database changes deployed independently
2. Application changes deployed independently
3. Need to coordinate versions manually
4. Each has its own approval workflow

### Advantages (Pros)

#### ✅ 1. Clear Separation of Concerns

**What it means**: Database and application are truly separate.

**Why it's good:**
- Clear boundaries
- Different teams can own different repos
- Easier to apply different standards
- Better organization

**Example:**
```
Team structure:
- App Team owns: customer-service repo
- DBA Team owns: customer-service-database repo

✅ Clear ownership
✅ Different approval workflows
✅ Different access controls
```

#### ✅ 2. Independent Access Control

**What it means**: Different people can access different repositories.

**Why it's good:**
- Restrict database access to DBAs only
- Developers can't see production database credentials
- Separation of duties for compliance
- Fine-grained permissions

**Example:**
```
Repository permissions:

customer-service (App):
✅ All developers: Read + Write
✅ Junior developers: Can approve PRs

customer-service-database (DB):
✅ All developers: Read only
✅ Senior DBAs: Write + Approve
✅ Auditors: Read access

Better security and compliance!
```

#### ✅ 3. Independent Deployment

**What it means**: Deploy database and application separately.

**Why it's good:**
- Fix database issues without deploying app
- Fix app issues without touching database
- Different deployment schedules
- More flexibility

**Example scenarios:**
```
Scenario 1: Database performance issue
✅ Deploy database index fix
✅ Don't touch application
✅ Faster deployment
✅ Less risk

Scenario 2: Application bug
✅ Deploy app hotfix
✅ Don't trigger database pipeline
✅ Quicker fix
```

#### ✅ 4. Specialized Workflows

**What it means**: Each repo can have workflows specific to its needs.

**Why it's good:**
- Database workflows can enforce DBA review
- App workflows can be faster/simpler
- Different testing strategies
- Different deployment strategies

**Example:**
```
Database repo workflow:
✅ Requires 2 DBA approvals
✅ Runs database-specific tests
✅ Generates SQL preview
✅ Checks for breaking changes
✅ Deploys during maintenance windows

App repo workflow:
✅ Requires 1 developer approval
✅ Runs application tests
✅ Deploys anytime
✅ Faster feedback
```

#### ✅ 5. Smaller Repository Size

**What it means**: Each repo contains less code.

**Why it's good:**
- Faster to clone
- Easier to navigate
- Faster builds
- Simpler structure

**Example:**
```
Database repo:
- Only 500 changelog files
- Clone in 10 seconds
- Easy to find changes

App repo:
- Only application code
- Clone in 30 seconds
- Focus on app logic
```

#### ✅ 6. Different Release Cadences

**What it means**: Database and app can release at different frequencies.

**Why it's good:**
- Database changes: Weekly (planned)
- App changes: Daily (as needed)
- Flexibility in timing
- Reduced coordination

**Example:**
```
Release schedule:

Database:
✅ Every Friday during maintenance window
✅ Planned changes batch together
✅ DBAs available for issues

Application:
✅ Multiple times per day
✅ Continuous deployment
✅ Fast feature delivery
```

### Disadvantages (Cons)

#### ❌ 1. Coordination Overhead

**What it means**: Need to manually coordinate between repositories.

**Why it's bad:**
- Track which app version needs which database version
- Manually sync deployments
- More planning required
- Higher cognitive load

**Example issue:**
```
Developer needs to remember:
❌ "This app feature requires database v0023"
❌ "Make sure database deploys first"
❌ "Wait for database deployment to complete"
❌ "Check database version in each environment"

More things to track and remember!
```

#### ❌ 2. Version Tracking Complexity

**What it means**: Hard to know which versions work together.

**Why it's bad:**
- Need external tracking
- Risk of version mismatch
- Deployment order matters
- Rollback is complex

**Example issue:**
```
Production issue:

Single repo:
✅ Rollback to commit abc123
✅ Both app and database rollback
✅ Consistent state

Multiple repos:
❌ Which app version?
❌ Which database version?
❌ Do they work together?
❌ Need to check compatibility matrix
```

#### ❌ 3. Split Pull Requests

**What it means**: One feature requires PRs in multiple repositories.

**Why it's bad:**
- Reviewers need to look at multiple PRs
- Lose context switching between repos
- Harder to see complete picture
- More administrative overhead

**Example:**
```
Adding customer loyalty feature:

Pull Request #145 (Database repo):
- Add loyalty_points table
- Add customer_tier table

Pull Request #789 (App repo):
- Add loyalty service
- Add loyalty API endpoints

Reviewer must:
❌ Open both PRs
❌ Switch between repositories
❌ Understand how they fit together
❌ Make sure both get merged
```

#### ❌ 4. More Complex Setup

**What it means**: New developers need to clone multiple repositories.

**Why it's bad:**
- Longer onboarding
- More setup steps
- Need to understand multiple repos
- Easy to miss a repository

**Example onboarding:**
```
New developer setup:

Multiple repos:
❌ Clone app repository
❌ Clone database repository
❌ Clone configuration repository
❌ Set up each repository separately
❌ Understand how they connect
❌ Configure credentials for each
   (Takes 2-3 hours)

vs Single repo:
✅ Clone one repository
✅ Run setup script
✅ Done
   (Takes 30 minutes)
```

#### ❌ 5. Deployment Order Dependencies

**What it means**: Must deploy in correct order.

**Why it's bad:**
- Database must deploy first
- App must wait for database
- Manual coordination required
- Risk of partial deployments

**Example issue:**
```
Deployment day:

Correct order:
1. Deploy database v0023
2. Wait for completion
3. Verify database
4. Deploy app v1.5.0

What can go wrong:
❌ Deploy app first → breaks (missing database changes)
❌ Deploy database, forget app → inconsistent
❌ Database deployment fails → need to coordinate rollback

More points of failure!
```

#### ❌ 6. Duplicate Infrastructure

**What it means**: Need to set up similar things in each repository.

**Why it's bad:**
- Duplicate CI/CD setup
- Duplicate documentation
- Duplicate issue tracking
- More maintenance

**Example:**
```
Things to maintain in EACH repo:

Database repo:
- GitHub Actions workflows
- Secrets configuration
- Branch protection rules
- Issue templates
- Documentation

App repo:
- GitHub Actions workflows
- Secrets configuration
- Branch protection rules
- Issue templates
- Documentation

Everything is duplicated!
```

### When to Use Multiple Repositories

✅ **Best for:**
- **Large teams** (20+ people)
- **Separate teams** (developers vs DBAs)
- **Shared database** (multiple applications)
- **Different deployment schedules**
- **Strict compliance** requirements
- **Enterprise** organizations

✅ **Use when:**
- Need different access controls
- Database and app deploy independently
- Multiple applications share one database
- Separation of duties required
- Different teams own different components

## Detailed Comparison

### Side-by-Side Feature Comparison

| Feature | Single Repository | Multiple Repositories |
|---------|------------------|----------------------|
| **Setup Complexity** | ✅ Simple (clone once) | ❌ Complex (clone multiple) |
| **Coordination** | ✅ Automatic | ❌ Manual |
| **Code Review** | ✅ See complete change | ❌ Split across repos |
| **Access Control** | ❌ Same for all | ✅ Different per repo |
| **Deployment** | ❌ Coupled | ✅ Independent |
| **Version Tracking** | ✅ Single version | ❌ Track multiple versions |
| **Onboarding Time** | ✅ 30 minutes | ❌ 2-3 hours |
| **Repository Size** | ❌ Larger | ✅ Smaller |
| **Separation of Duties** | ❌ Difficult | ✅ Easy |
| **Rollback** | ✅ Simple (one commit) | ❌ Complex (coordinate) |
| **CI/CD Complexity** | ⚠️ Medium | ❌ High |
| **Best for Team Size** | ✅ Under 20 | ✅ Over 20 |

### Workflow Comparison

#### Scenario: Add New Feature

**Single Repository:**
```
Time: 2 hours total

1. Create branch (1 minute)
2. Write app code (45 minutes)
3. Write database changes (45 minutes)
4. Test locally (15 minutes)
5. Create 1 PR (5 minutes)
6. Review (10 minutes - see everything)
7. Merge (1 minute)
8. Auto-deploy both (10 minutes)

✅ Simple
✅ Everything together
✅ 1 PR to review
```

**Multiple Repositories:**
```
Time: 3-4 hours total

1. Create database branch (1 minute)
2. Write database changes (45 minutes)
3. Create database PR (5 minutes)
4. Wait for DBA review (1 hour - if available)
5. Merge database PR (1 minute)
6. Wait for database deployment (10 minutes)
7. Verify database (5 minutes)
8. Create app branch (1 minute)
9. Write app code (45 minutes)
10. Test with new database (15 minutes)
11. Create app PR (5 minutes)
12. Review (10 minutes)
13. Merge (1 minute)
14. Auto-deploy app (10 minutes)

❌ More steps
❌ More waiting
❌ 2 PRs to coordinate
```

### Cost Comparison

#### Time Investment

**Single Repository:**
```
Setup: 1 day
Maintenance: 2 hours/month
Developer efficiency: High
Coordination time: Low

Annual cost (team of 10):
- Setup: 1 day
- Maintenance: 24 hours/year
- Coordination: ~50 hours/year
Total: ~75 hours/year
```

**Multiple Repositories:**
```
Setup: 3 days (multiple repos)
Maintenance: 4 hours/month (per repo)
Developer efficiency: Medium
Coordination time: High

Annual cost (team of 10):
- Setup: 3 days
- Maintenance: 96 hours/year (4 × 2 repos × 12 months)
- Coordination: ~200 hours/year
Total: ~320 hours/year
```

**Difference**: ~245 hours/year (6 weeks of work)

## Real-World Scenarios

### Scenario 1: Small Startup (5 developers)

**Situation:**
- 5 full-stack developers
- Everyone works on everything
- Rapid development
- Deploy multiple times per day
- No dedicated DBA

**Challenge:**
"We're moving fast and breaking things. Need simple workflows."

**Recommendation: SINGLE REPOSITORY**

**Why:**
```
✅ Everyone works on app and database
✅ Deploy together constantly
✅ Don't need complex access control
✅ Want fastest development speed
✅ Coordination overhead would slow us down
```

**Implementation:**
```
customer-app/
├── frontend/
├── backend/
├── database/
│   └── changelog/
└── .github/workflows/
    └── deploy.yml    # Deploy everything together
```

**Results:**
```
✅ Developers productive from day 1
✅ Features ship faster
✅ Less context switching
✅ Simple deployment: push to main, everything deploys
```

### Scenario 2: Growing Company (15 developers)

**Situation:**
- 12 developers, 3 senior developers who handle database
- Still one product
- Deploy app daily, database weekly
- Starting to need more control

**Challenge:**
"We want to move fast but need some oversight on database changes."

**Recommendation: SINGLE REPOSITORY with protection**

**Why:**
```
✅ Still one team, one product
✅ Can use branch protection for database
✅ Use GitHub CODEOWNERS for database folder
✅ Simpler than multiple repos
⚠️ Add approval workflow for database changes
```

**Implementation:**
```
customer-app/
├── src/
├── database/          # Requires senior dev approval
│   └── changelog/
├── .github/
│   ├── workflows/
│   └── CODEOWNERS    # database/* needs senior approval
```

**CODEOWNERS file:**
```
# Default: Any developer can approve
*  @yourcompany/developers

# Database changes: Senior developers must approve
database/**  @yourcompany/senior-developers
```

**Results:**
```
✅ Database changes have oversight
✅ Still simple one-repo workflow
✅ Junior devs can still see and learn
✅ Deployment stays simple
```

### Scenario 3: Medium Company (25 developers, 2 DBAs)

**Situation:**
- 25 application developers
- 2 dedicated DBAs
- Multiple applications share same database
- Database changes need DBA approval
- Different deployment schedules

**Challenge:**
"Multiple apps use the same database. DBAs need full control of database."

**Recommendation: MULTIPLE REPOSITORIES**

**Why:**
```
✅ Multiple apps need same database
✅ DBAs own database repository
✅ Different access controls needed
✅ Different deployment schedules
✅ Clear separation of duties
```

**Implementation:**
```
customer-app/          # App team owns
├── src/
└── .github/workflows/

order-app/             # App team owns
├── src/
└── .github/workflows/

shared-database/       # DBA team owns
├── database/
│   └── changelog/
│       ├── customers/
│       ├── orders/
│       └── shared/
└── .github/workflows/
    └── db-deploy.yml  # DBA approval required
```

**Access Control:**
```
customer-app:
✅ App developers: Full access

order-app:
✅ App developers: Full access

shared-database:
✅ All developers: Read only (can see changes)
✅ DBAs: Full access
✅ DBAs: Required approvers
```

**Results:**
```
✅ Clear ownership
✅ DBAs control database
✅ Apps can deploy independently
✅ Database changes reviewed by experts
✅ Better compliance
```

### Scenario 4: Enterprise (100+ developers)

**Situation:**
- 100+ developers across multiple teams
- Dedicated DBA team (10 DBAs)
- Dozens of applications
- Multiple shared databases
- Strict compliance requirements
- Change control board

**Challenge:**
"Need enterprise-grade governance and compliance."

**Recommendation: MULTIPLE REPOSITORIES with governance**

**Why:**
```
✅ Must have separation of duties
✅ Audit requirements
✅ Different teams own different components
✅ Complex approval workflows
✅ Need fine-grained access control
```

**Implementation:**
```
app-team-1/repos/
  ├── service-a/
  ├── service-b/
  └── service-c/

app-team-2/repos/
  ├── service-d/
  └── service-e/

dba-team/repos/
  ├── database-customer/
  ├── database-order/
  ├── database-inventory/
  └── database-shared/
```

**Governance:**
```
Database repositories:
✅ DBAs: Full access
✅ Developers: Read only
✅ Requires 2 DBA approvals
✅ Requires change control ticket
✅ Automatic compliance checks
✅ Deployment windows enforced
✅ Complete audit trail
```

**Results:**
```
✅ Meets compliance requirements
✅ Clear audit trail
✅ Separation of duties
✅ Independent team velocity
✅ Scalable governance
```

## Best Practices by Team Size

### Team: 1-5 People

**Recommendation: Single Repository**

```
Structure:
my-app/
├── src/
├── database/
└── .github/workflows/
    └── deploy.yml    # Deploy everything
```

**Best Practices:**
- ✅ Keep it simple
- ✅ Deploy app and database together
- ✅ One approval workflow
- ✅ Fast iteration over governance
- ✅ Everyone can approve changes

**Avoid:**
- ❌ Don't overcomplicate
- ❌ Don't create separate repos (overkill)
- ❌ Don't add heavy approval processes

### Team: 5-10 People

**Recommendation: Single Repository with Protection**

```
Structure:
my-app/
├── src/
├── database/        # Protected folder
└── .github/
    ├── workflows/
    └── CODEOWNERS   # Database needs senior approval
```

**Best Practices:**
- ✅ Use CODEOWNERS for database folder
- ✅ Require senior developer approval for database
- ✅ Still keep everything in one repo
- ✅ Use branch protection on main
- ✅ Separate workflows for app vs database

**Configuration:**
```yaml
# .github/CODEOWNERS
database/**  @yourcompany/senior-devs

# Branch protection:
main branch:
- Require PR reviews: 1
- Require status checks
- No force pushes
```

### Team: 10-20 People

**Recommendation: Single Repository OR Multiple (Your Choice)**

At this size, either approach works. Choose based on:

**Choose Single Repository If:**
- ✅ One product/service
- ✅ Tightly coupled app and database
- ✅ Deploy together frequently
- ✅ Team prefers simplicity

**Choose Multiple Repositories If:**
- ✅ Multiple apps share database
- ✅ Database team emerging
- ✅ Need stronger access control
- ✅ Different deployment schedules

**Best Practices (Either Approach):**
- ✅ Clear approval workflows
- ✅ Automated testing
- ✅ Code review required
- ✅ Protected main branch
- ✅ Environment-based deployment

### Team: 20+ People

**Recommendation: Multiple Repositories**

```
Structure:
app-repos/
├── service-1/
├── service-2/
└── service-3/

database-repos/
├── database-shared/
└── database-service-specific/
```

**Best Practices:**
- ✅ Separate repositories by ownership
- ✅ DBAs own database repositories
- ✅ Different access controls per repo
- ✅ Independent deployment pipelines
- ✅ Version compatibility tracking
- ✅ Formal change management

**Governance:**
```
Database repositories:
- Require 2 approvals (DBAs)
- Automatic compliance checks
- Change control integration
- Deployment windows
- Rollback procedures

Application repositories:
- Require 1 approval
- Continuous deployment
- Independent release cadence
```

## Decision Framework

### Questions to Ask

Use this framework to decide which approach is right for you.

#### Question 1: How many people on your team?

```
1-10 people
  → Lean toward SINGLE repository
  → Coordination overhead not worth it

10-20 people
  → Either approach works
  → Consider other factors

20+ people
  → Lean toward MULTIPLE repositories
  → Need better separation
```

#### Question 2: Who owns database changes?

```
Same people who develop the app
  → SINGLE repository
  → No need for separation

Dedicated DBA team
  → MULTIPLE repositories
  → Clear ownership boundaries
```

#### Question 3: How often do database and app change together?

```
Usually together (>70% of the time)
  → SINGLE repository
  → Benefit from atomic changes

Sometimes together (30-70%)
  → Either approach
  → Consider other factors

Rarely together (<30%)
  → MULTIPLE repositories
  → Benefit from independent deployment
```

#### Question 4: Do you need different access controls?

```
Same access for everyone
  → SINGLE repository
  → No need for complexity

Different access for database vs app
  → MULTIPLE repositories
  → Or single repo with CODEOWNERS
```

#### Question 5: What are your compliance requirements?

```
Basic or none
  → SINGLE repository
  → Simple is fine

Moderate (SOX, HIPAA)
  → MULTIPLE repositories with governance
  → Better audit trail

Strict (FDA, PCI)
  → MULTIPLE repositories REQUIRED
  → Separation of duties mandatory
```

#### Question 6: How many applications share the database?

```
One application, one database
  → SINGLE repository
  → Keep them together

Multiple applications, one database
  → MULTIPLE repositories
  → Database is shared resource
```

### Decision Matrix

| Your Situation | Single Repo | Multiple Repos |
|----------------|-------------|----------------|
| Team < 10 people | ✅ **Recommended** | ❌ Overkill |
| Team 10-20 people | ✅ Good | ✅ Good |
| Team 20+ people | ⚠️ Gets complex | ✅ **Recommended** |
| Same people own app & DB | ✅ **Yes** | ❌ Unnecessary |
| Separate DBA team | ❌ Difficult | ✅ **Yes** |
| Deploy together | ✅ **Yes** | ❌ Overhead |
| Deploy independently | ❌ Complex | ✅ **Yes** |
| One app | ✅ **Yes** | ⚠️ Can work |
| Multiple apps | ❌ Messy | ✅ **Yes** |
| Basic compliance | ✅ **Yes** | ✅ Better |
| Strict compliance | ⚠️ Can work | ✅ **Required** |

### Simple Recommendation

**For teams under 20 people with one application:**
→ Start with SINGLE repository

**For teams over 20 people or multiple applications:**
→ Use MULTIPLE repositories

**Not sure?**
→ Start with SINGLE, split later if needed

## Migration Strategies

### From Single to Multiple Repositories

If you start with single repository and need to split later:

#### Step 1: Plan the Split

```
Current:
my-app/
├── src/
├── database/
└── tests/

Future:
my-app/              (Keep this)
├── src/
└── tests/

my-app-database/     (New)
├── database/
└── .github/workflows/
```

#### Step 2: Create Database Repository

```bash
# 1. Create new repository on GitHub
# Name: my-app-database

# 2. Clone existing repository
git clone https://github.com/yourcompany/my-app my-app-database
cd my-app-database

# 3. Remove application code (keep only database)
git filter-branch --subdirectory-filter database -- --all

# 4. Push to new repository
git remote set-url origin https://github.com/yourcompany/my-app-database
git push -u origin main
```

#### Step 3: Clean Up Application Repository

```bash
# In application repository
cd my-app

# Remove database folder
git rm -r database/
git commit -m "Move database to separate repository"
git push origin main
```

#### Step 4: Update CI/CD

Update workflows in both repositories to work independently.

#### Step 5: Update Documentation

Document the change and new workflow for team.

### From Multiple to Single Repository

If you want to combine repositories:

#### Step 1: Prepare

```bash
# 1. Create new combined repository
mkdir my-app-combined
cd my-app-combined
git init

# 2. Add application code
git remote add app https://github.com/yourcompany/my-app
git fetch app
git merge app/main --allow-unrelated-histories

# 3. Add database code in subdirectory
git remote add database https://github.com/yourcompany/my-app-database
git fetch database
git read-tree --prefix=database/ database/main
git commit -m "Merge database repository"

# 4. Push to new repository
git remote add origin https://github.com/yourcompany/my-app-combined
git push -u origin main
```

#### Step 2: Update CI/CD

Create combined workflows that deploy both.

#### Step 3: Migrate Team

Update documentation, train team on new structure.

## Common Pitfalls

### Pitfall 1: Starting Too Complex

**Mistake:**
```
Team of 5 people creates:
- Application repository
- Database repository
- Configuration repository
- Documentation repository
- Infrastructure repository

❌ Way too complex for small team!
```

**Solution:**
```
Start simple:
✅ One repository with everything
✅ Add complexity as you grow
```

### Pitfall 2: Poor Documentation

**Mistake:**
```
Multiple repositories with no documentation of:
❌ Which app version needs which database version
❌ How to coordinate deployments
❌ What order to deploy in
```

**Solution:**
```
Document clearly:
✅ Version compatibility matrix
✅ Deployment procedures
✅ Rollback processes
✅ Who to contact for help
```

### Pitfall 3: Inconsistent Naming

**Mistake:**
```
customer-service/        (App)
CustomerDB/              (Database)
customer_infrastructure/ (Infrastructure)

❌ Inconsistent naming causes confusion
```

**Solution:**
```
Use consistent naming:
✅ customer-service/
✅ customer-service-database/
✅ customer-service-infrastructure/
```

### Pitfall 4: No Version Tracking

**Mistake:**
```
Multiple repos, no way to track what works together
❌ "Which database version does app v2.3.1 need?"
```

**Solution:**
```
Document versions:
✅ Add DATABASE_VERSION file in app repo
✅ Use release notes
✅ Tag coordinated releases
```

### Pitfall 5: Forgetting About New Developers

**Mistake:**
```
Multiple repositories, no onboarding documentation
New developer:
❌ "Which repositories do I need?"
❌ "How do I set them all up?"
❌ "How do they fit together?"
```

**Solution:**
```
Create onboarding guide:
✅ List of all repositories
✅ Setup script for all repos
✅ Architecture diagram
✅ How components fit together
```

## Recommendations

### For Your Team (Under 20 People)

Based on your team size, here are my recommendations:

#### Recommendation: START with Single Repository

**Why:**
```
✅ Your team is under 20 people (perfect size)
✅ Simpler to implement and maintain
✅ Easier coordination
✅ Faster development
✅ Lower overhead
✅ Can split later if needed
```

#### Initial Structure

```
your-application/
├── src/                        # Application code
│   ├── api/
│   ├── services/
│   └── models/
│
├── database/                   # Database changes
│   └── changelog/
│       ├── changelog.xml
│       ├── baseline/
│       └── changes/
│
├── tests/                      # All tests
│   ├── unit/
│   ├── integration/
│   └── database/
│
├── .github/                    # CI/CD
│   └── workflows/
│       ├── ci.yml              # Continuous Integration
│       └── deploy.yml          # Deployment
│
├── docs/                       # Documentation
│   ├── database/
│   └── api/
│
└── README.md
```

#### Add Protection as You Grow

As your team grows, add these protections:

**At 10 people:**
```yaml
# .github/CODEOWNERS
database/**  @yourcompany/senior-developers

# Requires senior developer to approve database changes
```

**At 15 people:**
```yaml
# Add separate workflows
.github/workflows/
├── app-deploy.yml       # Deploy app
└── database-deploy.yml  # Deploy database (requires approval)
```

**At 20+ people:**
```
Consider splitting if:
✅ You have dedicated DBA team
✅ Multiple apps share database
✅ Different deployment schedules needed
✅ Compliance requirements increase
```

### Gradual Transition Plan

```
Phase 1 (Months 1-6):
✅ Single repository
✅ Simple workflows
✅ Everyone approves

Phase 2 (Months 6-12):
✅ Still single repository
✅ Add CODEOWNERS for database
✅ Separate workflows

Phase 3 (Months 12-18, if needed):
✅ Evaluate if split needed
✅ If yes, plan migration
✅ If no, stay with single repo
```

## FAQ

### Q1: Can I change my mind later?

**A:** Yes! You can always:
- Split single repository into multiple
- Combine multiple repositories into single
- Git preserves full history in either case

It's work, but it's doable.

### Q2: What if different developers have different permissions?

**A:** In single repository, use:
- **CODEOWNERS file** to require specific approvers for database folder
- **Branch protection rules** to enforce reviews
- **GitHub Teams** for different permission levels

Example:
```
# .github/CODEOWNERS
* @yourcompany/developers
database/** @yourcompany/database-team
```

### Q3: Can we have some apps in single repo, others separate?

**A:** Yes! Common patterns:
- **Microservices**: Each service has its own repo (app + database)
- **Shared database**: Database in separate repo, multiple app repos
- **Hybrid**: Core app in single repo, microservices separate

Choose what makes sense for each component.

### Q4: How do we handle database shared by multiple apps?

**A:** Multiple repositories:
```
app-1/              # Application 1
app-2/              # Application 2
app-3/              # Application 3
shared-database/    # Shared by all

# shared-database is separate
# All apps reference it
```

### Q5: What about infrastructure code?

**A:** Options:
- **Single repo**: Add infrastructure/ folder
- **Separate repo**: Create infrastructure repository
- **Hybrid**: Infrastructure per application

For teams under 20: Keep infrastructure with application.

### Q6: How do we track which versions work together?

**Multiple repositories:**
```
# In application repository
# Add file: database-version.txt
v0.23.5

# Or in package.json / requirements.txt
"database-version": "0.23.5"

# Or in README
## Compatibility
App v2.1.0 requires Database v0.23.5
```

### Q7: What if we need stricter compliance later?

**A:** You can always:
1. Add more approval workflows
2. Split into multiple repositories
3. Add automated compliance checks
4. Implement change control

Start simple, add governance as needed.

### Q8: How do rollbacks work?

**Single repository:**
```bash
# Rollback to previous version
git revert <commit-sha>
git push

# Both app and database rollback together
```

**Multiple repositories:**
```bash
# Must coordinate both:
# 1. Rollback database
cd database-repo
git revert <commit-sha>
git push

# 2. Rollback application
cd app-repo
git revert <commit-sha>
git push

# Make sure versions are compatible!
```

## Summary

### Key Takeaways

1. **For teams under 20 people**: Start with single repository
2. **For teams over 20 people**: Consider multiple repositories
3. **You can always change**: Not a permanent decision
4. **Start simple**: Add complexity as you grow
5. **Document everything**: Especially if using multiple repositories

### Quick Decision Guide

```
Choose SINGLE repository if:
✅ Team is under 20 people
✅ Same people work on app and database
✅ Deploy together frequently
✅ Want simple workflow
✅ Starting out with CI/CD

Choose MULTIPLE repositories if:
✅ Team is over 20 people
✅ Dedicated DBA team
✅ Multiple apps share database
✅ Need strong access control
✅ Different deployment schedules
✅ Compliance requirements
```

### Your Next Steps

1. **Assess your team**: Size, structure, needs
2. **Choose approach**: Use decision framework
3. **Start simple**: Don't over-engineer
4. **Document**: Write down your decision and rationale
5. **Implement**: Follow the tutorials
6. **Iterate**: Improve based on experience

---

**Document Version**: 1.0
**Last Updated**: November 2025
**For Teams**: Under 20 people
**Related Documents**:
- [Branch Strategy Guide](./branch-strategies-for-database-cicd.md)
- [GitHub Actions Tutorial](../../../../tutorials/liquibase/sqlserver-liquibase-github-actions-tutorial.md)
- [Best Practices](../../../../best-practices/liquibase/github-actions.md)

**Questions?** Review the FAQ or consult with your team lead.
