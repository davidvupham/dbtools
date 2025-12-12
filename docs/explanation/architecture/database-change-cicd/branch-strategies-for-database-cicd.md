# Branch Strategies for Database CI/CD: Deployment Workflows

## Table of Contents

- [Introduction](#introduction)
- [What Are Branches?](#what-are-branches)
- [Why Branches Matter for CI/CD](#why-branches-matter-for-cicd)
- [Branch Strategy Fundamentals](#branch-strategy-fundamentals)
- [Common Branch Strategies](#common-branch-strategies)
- [Recommended Strategy for Teams Under 20](#recommended-strategy-for-teams-under-20)
- [Environment Mapping](#environment-mapping)
- [Complete Workflow Examples](#complete-workflow-examples)
- [Branch Protection Rules](#branch-protection-rules)
- [Best Practices](#best-practices)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Introduction

When implementing database CI/CD with GitHub Actions, your **branch strategy** determines how and when database changes get deployed to different environments (development, staging, production).

This document explains branch strategies in simple terms for teams new to Git workflows and CI/CD.

### Who This Document Is For

- ✅ Teams new to Git branching
- ✅ Developers learning CI/CD workflows
- ✅ Teams under 20 people implementing database automation
- ✅ Anyone confused about "when should we deploy what?"

### What You'll Learn

- What branches are and how they work
- How branches trigger deployments
- Recommended branch strategy for your team size
- Complete workflows from development to production
- Best practices and common pitfalls

## What Are Branches?

### Simple Explanation

A **branch** is like a **separate copy** of your code where you can make changes without affecting the main codebase.

**Think of it like:**
- Making a copy of a Word document to experiment with changes
- Working on a rough draft before finalizing
- Having multiple versions of the same project

### How Branches Work

```
main branch (the "official" version)
    |
    |--- feature/add-customer-status (your experimental copy)
    |
    |--- feature/add-order-table (teammate's experimental copy)
```

When you're done experimenting, you **merge** your branch back into the main branch.

### Visual Example

```
Timeline of work:

main:      A --- B --- C -------------- G --- H
                        \             /
feature branch:          D --- E --- F

A, B, C = commits on main
D, E, F = commits on feature branch
G = merge feature into main
H = continued work on main
```

### Why Use Branches?

1. **Isolation**: Your changes don't affect others
2. **Experimentation**: Try things without breaking production
3. **Collaboration**: Multiple people work simultaneously
4. **Review**: Changes reviewed before merging
5. **Safety**: Main branch stays stable

### Branch Basics

#### Creating a Branch

```bash
# See current branch
git branch
# Output: * main (asterisk shows current branch)

# Create new branch
git checkout -b feature/add-customer-table
# Creates branch named "feature/add-customer-table" and switches to it

# Now you're on the new branch
git branch
# Output:
#   main
# * feature/add-customer-table
```

#### Working on a Branch

```bash
# Make changes
vim database/changelog/changes/V0025__add_customer_table.sql

# Commit changes (saved on THIS branch only)
git add database/changelog/changes/V0025__add_customer_table.sql
git commit -m "Add customer table"

# Push branch to GitHub
git push origin feature/add-customer-table
```

#### Merging a Branch

```bash
# Switch back to main
git checkout main

# Merge your feature branch into main
git merge feature/add-customer-table

# Push updated main to GitHub
git push origin main
```

### Branches in GitHub

On GitHub, branches appear in:
- **Dropdown menu** at top of file browser
- **Pull Requests** (proposals to merge branches)
- **Branches page** (list of all branches)

## Why Branches Matter for CI/CD

### Branches Trigger Deployments

In GitHub Actions, workflows can trigger based on which branch changed:

```yaml
# Deploy to DEV when feature branches are pushed
on:
  push:
    branches:
      - 'feature/**'

# Deploy to PRODUCTION when main is pushed
on:
  push:
    branches:
      - 'main'
```

**This means**: Different branches deploy to different environments automatically!

### The Power of Branch-Based Deployment

```
You push code to feature/add-customer-table
    ↓
GitHub Actions sees: "This is a feature branch"
    ↓
Automatically deploys to DEVELOPMENT only
    ↓
You test in development
    ↓
You merge to main branch
    ↓
GitHub Actions sees: "This is main branch"
    ↓
Automatically deploys to STAGING
    ↓
After approval
    ↓
Automatically deploys to PRODUCTION
```

**No manual work needed!** The branch tells GitHub Actions what to do.

## Branch Strategy Fundamentals

### Core Concepts

#### 1. Main Branch (or Master)

**What it is**: The "official" version of your code.

**Rules:**
- ✅ Always works (should never be broken)
- ✅ Always ready for production
- ✅ Protected (can't push directly)
- ✅ Requires pull request + review

**Common names:**
- `main` (modern standard)
- `master` (older standard)

#### 2. Feature Branches

**What it is**: Temporary branches for new work.

**Purpose:**
- Develop new features
- Fix bugs
- Make database changes

**Naming:**
- `feature/description`
- `database/description`
- `bugfix/description`

**Lifecycle:**
```
Create → Work → Test → Review → Merge → Delete
```

#### 3. Environment Branches (Optional)

**What it is**: Branches representing environments.

**Examples:**
- `develop` → Development environment
- `staging` → Staging environment
- `main` → Production environment

**Not always needed** for small teams!

### Branch Naming Conventions

Good naming makes branches easy to understand:

**Good Examples:**
```
feature/add-customer-status
database/add-orders-table
bugfix/fix-email-constraint
hotfix/urgent-production-fix
release/v1.2.0
```

**Why good:**
- ✅ Prefix shows purpose
- ✅ Description is clear
- ✅ Easy to understand at a glance

**Bad Examples:**
```
johns-branch
test
fix
new-stuff
database-changes-v2-final-FINAL
```

**Why bad:**
- ❌ No context
- ❌ Unclear purpose
- ❌ Hard to understand

### Recommended Naming Convention

```
Type        Prefix          Example
─────────────────────────────────────────────────────
Feature     feature/        feature/add-loyalty-program
Database    database/       database/add-customers-table
Bug Fix     bugfix/         bugfix/fix-null-constraint
Hot Fix     hotfix/         hotfix/urgent-prod-fix
Release     release/        release/v1.2.0
```

## Common Branch Strategies

### Strategy 1: Simple Main Branch (Recommended for Small Teams)

**Structure:**
```
feature branches  →  main  →  Production
```

**How it works:**
1. Create feature branch from main
2. Develop and test
3. Create pull request to main
4. Review and approve
5. Merge to main
6. Main deploys to dev → staging → production

**Best for:**
- ✅ Teams under 10 people
- ✅ Simple projects
- ✅ Starting with CI/CD

**Pros:**
- ✅ Very simple
- ✅ Easy to understand
- ✅ Low overhead

**Cons:**
- ⚠️ Main branch is busy
- ⚠️ Less control over environments

### Strategy 2: GitFlow (Feature + Develop + Main)

**Structure:**
```
feature branches  →  develop  →  release  →  main
```

**How it works:**
1. Create feature branch from develop
2. Develop and test
3. Merge to develop (deploys to dev environment)
4. Create release branch from develop
5. Test in staging
6. Merge release to main (deploys to production)

**Best for:**
- ✅ Teams 10-30 people
- ✅ Scheduled releases
- ✅ Multiple features in flight

**Pros:**
- ✅ Clear separation
- ✅ Batch releases
- ✅ Stable main branch

**Cons:**
- ⚠️ More complex
- ⚠️ More branches to manage
- ⚠️ Longer to production

### Strategy 3: GitHub Flow (Recommended for Most Teams)

**Structure:**
```
feature branches  →  main (with environments)
```

**How it works:**
1. Create feature branch from main
2. Develop and test locally
3. Push feature branch (deploys to dev)
4. Create pull request to main
5. Review and approve
6. Merge to main
7. Main deploys through environments with approvals

**Best for:**
- ✅ Teams 5-20 people (YOUR SIZE!)
- ✅ Continuous deployment
- ✅ Modern CI/CD

**Pros:**
- ✅ Simple and powerful
- ✅ Fast to production
- ✅ Industry standard
- ✅ Good balance

**Cons:**
- ⚠️ Requires good testing

### Strategy Comparison

| Feature | Simple Main | GitFlow | GitHub Flow |
|---------|-------------|---------|-------------|
| **Complexity** | ✅ Very Low | ❌ High | ⚠️ Medium |
| **Branches** | 2 types | 5+ types | 2 types |
| **Time to Production** | ✅ Fast | ❌ Slow | ✅ Fast |
| **Best For Team Size** | 1-10 | 20-50+ | 5-20 |
| **Learning Curve** | ✅ Easy | ❌ Hard | ⚠️ Medium |
| **Flexibility** | ⚠️ Limited | ✅ High | ✅ Good |

## Recommended Strategy for Teams Under 20

### GitHub Flow + Environment Deployment

This is the **best balance** of simplicity and power for your team size.

**Branch Structure:**
```
feature/*, database/*, bugfix/*  →  main
                                      ↓
                                Development (auto)
                                      ↓
                                Staging (auto)
                                      ↓
                                Production (approval)
```

### Why This Works for You

✅ **Simple enough**: Only 2 branch types (feature branches + main)
✅ **Powerful enough**: Supports all environments
✅ **Safe**: Production requires approval
✅ **Fast**: Quick feedback loop
✅ **Standard**: Industry best practice

### Complete Workflow

#### Phase 1: Development

```bash
# 1. Start from main branch
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b database/add-customer-status

# 3. Make database changes
vim database/changelog/changes/V0025__add_customer_status.sql

# 4. Commit changes
git add database/changelog/changes/V0025__add_customer_status.sql
git commit -m "Add customer status column"

# 5. Push to GitHub
git push origin database/add-customer-status

# 6. GitHub Actions automatically:
#    ✅ Validates changelog
#    ✅ Deploys to DEVELOPMENT environment
#    ✅ Runs tests
```

**What happens:**
- Pushing feature branch triggers dev deployment
- You can test immediately
- No manual deployment needed

#### Phase 2: Testing

```bash
# Test in development environment
# Connect to dev database
# Verify changes work

# If issues found:
# 1. Make fixes on same branch
vim database/changelog/changes/V0025__add_customer_status.sql

# 2. Commit and push again
git commit -am "Fix status constraint"
git push origin database/add-customer-status

# 3. GitHub Actions redeploys to dev automatically
```

**Benefit**: Rapid iteration in dev environment

#### Phase 3: Code Review

```bash
# When satisfied with testing:
# 1. Go to GitHub website
# 2. Click "Pull Requests"
# 3. Click "New pull request"
# 4. Select:
#    Base: main
#    Compare: database/add-customer-status
# 5. Click "Create pull request"
# 6. Add description of changes
# 7. Request reviewers

# GitHub Actions automatically:
# ✅ Validates changelog syntax
# ✅ Generates SQL preview
# ✅ Posts preview in PR comments
# ✅ Runs all checks

# Reviewers:
# ✅ Review code changes
# ✅ See SQL preview
# ✅ Approve or request changes
```

**Benefit**: Team reviews before production

#### Phase 4: Merge and Deploy

```bash
# After approval:
# 1. Click "Merge pull request" on GitHub
# 2. Confirm merge
# 3. Delete feature branch (GitHub offers this)

# GitHub Actions automatically:
# ✅ Deploys to STAGING
# ✅ Waits for staging to complete
# ✅ Runs staging tests
# ✅ Waits 5 minutes (safety timer)
# ✅ Requests approval for PRODUCTION

# For production:
# 1. Go to Actions tab
# 2. Click workflow run
# 3. Click "Review deployments"
# 4. Approve production deployment
# 5. GitHub Actions deploys to PRODUCTION
```

**Benefit**: Safe, controlled production deployment

### GitHub Actions Configuration

Here's the complete workflow for this strategy:

```yaml
# .github/workflows/database-deployment.yml
name: Database CI/CD Pipeline

on:
  # Feature branches deploy to dev
  push:
    branches:
      - 'feature/**'
      - 'database/**'
      - 'bugfix/**'
    paths:
      - 'database/**'

  # Main branch deploys through all environments
  push:
    branches:
      - 'main'
    paths:
      - 'database/**'

  # Manual deployment option
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  # Feature branches → Development only
  deploy-feature-to-dev:
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/heads/feature/') || startsWith(github.ref, 'refs/heads/database/')
    name: Deploy Feature Branch to Development
    runs-on: ubuntu-latest
    environment: development

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      - name: Deploy to development
        run: |
          echo "Deploying branch: ${{ github.ref_name }}"
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.DEV_DB_URL }}" \
            --username="${{ secrets.DEV_DB_USERNAME }}" \
            --password="${{ secrets.DEV_DB_PASSWORD }}"

      - name: Comment on branch
        run: |
          echo "✅ Deployed to development"
          echo "Branch: ${{ github.ref_name }}"
          echo "Test at: https://dev.example.com"

  # Main branch → Staging
  deploy-main-to-staging:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      - name: Deploy to staging
        run: |
          echo "Deploying main to staging"
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.STAGE_DB_URL }}" \
            --username="${{ secrets.STAGE_DB_USERNAME }}" \
            --password="${{ secrets.STAGE_DB_PASSWORD }}"

      - name: Run tests
        run: |
          echo "Running staging tests..."
          # Add your test commands here

  # Main branch → Production (after staging)
  deploy-main-to-production:
    needs: deploy-main-to-staging
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production  # Requires approval

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Liquibase
        uses: liquibase/setup-liquibase@v2
        with:
          version: '4.32.0'

      - name: Deploy to production
        run: |
          echo "Deploying to production"
          liquibase update \
            --changelog-file=database/changelog/changelog.xml \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${{ secrets.PROD_DB_PASSWORD }}"

      - name: Tag deployment
        run: |
          TAG="production-${{ github.run_number }}-$(date +%Y%m%d)"
          echo "Creating tag: $TAG"
          liquibase tag "$TAG" \
            --url="${{ secrets.PROD_DB_URL }}" \
            --username="${{ secrets.PROD_DB_USERNAME }}" \
            --password="${{ secrets.PROD_DB_PASSWORD }}"

      - name: Notify team
        run: |
          echo "✅ Production deployment complete!"
          echo "Tag: production-${{ github.run_number }}"
          echo "Commit: ${{ github.sha }}"
```

## Environment Mapping

### Branch to Environment Mapping

Here's how branches map to environments:

```
Branch Pattern              →  Environment    →  Deployment
───────────────────────────────────────────────────────────
feature/*                   →  Development   →  Automatic
database/*                  →  Development   →  Automatic
bugfix/*                    →  Development   →  Automatic

main (merged)               →  Staging       →  Automatic
                            →  Production    →  Requires Approval

hotfix/* (emergency)        →  All           →  Manual trigger
```

### Visual Flow

```
Developer's Branch Workflow:

1. Create feature branch
   feature/add-customer-status

2. Push feature branch
   ↓
   Deploys to DEV automatically
   ↓
3. Test in DEV
   ↓
4. Create Pull Request to main
   ↓
5. Team reviews PR
   ↓
6. Merge to main
   ↓
   Deploys to STAGING automatically
   ↓
7. Test in STAGING
   ↓
8. Approve production
   ↓
   Deploys to PRODUCTION
```

### Environment Configuration

**Set up environments in GitHub:**

1. **Development Environment**
   ```
   Name: development
   Protection rules: None
   Secrets: DEV_DB_URL, DEV_DB_USERNAME, DEV_DB_PASSWORD
   ```

2. **Staging Environment**
   ```
   Name: staging
   Protection rules: None (or optional approval)
   Secrets: STAGE_DB_URL, STAGE_DB_USERNAME, STAGE_DB_PASSWORD
   ```

3. **Production Environment**
   ```
   Name: production
   Protection rules:
     ✅ Required reviewers: 1-2 people
     ✅ Wait timer: 5 minutes
     ✅ Deployment branches: main only
   Secrets: PROD_DB_URL, PROD_DB_USERNAME, PROD_DB_PASSWORD
   ```

## Complete Workflow Examples

### Example 1: Adding New Table

**Day 1: Development**

```bash
# Morning: Start new work
git checkout main
git pull origin main
git checkout -b database/add-orders-table

# Create changelog
cat > database/changelog/changes/V0030__add_orders_table.sql << 'EOF'
--liquibase formatted sql

--changeset yourname:V0030-001
--comment: Create orders table
CREATE TABLE orders (
  order_id INT PRIMARY KEY IDENTITY(1,1),
  customer_id INT NOT NULL,
  order_date DATETIME NOT NULL DEFAULT GETDATE(),
  total_amount DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id)
);
GO

--rollback DROP TABLE orders;
EOF

# Commit and push
git add database/changelog/changes/V0030__add_orders_table.sql
git commit -m "Add orders table"
git push origin database/add-orders-table

# ✅ Automatically deploys to DEV
# ✅ Receive notification (if configured)
# ✅ Check deployment in Actions tab
```

**Afternoon: Test and iterate**

```bash
# Test in development database
sqlcmd -Q "SELECT * FROM orders"  # Verify table exists

# Found issue: Need index on order_date
vim database/changelog/changes/V0030__add_orders_table.sql
# Add index changeset

git commit -am "Add index on order_date"
git push origin database/add-orders-table

# ✅ Redeploys to DEV automatically
# ✅ Test again
```

**Day 2: Review**

```
# On GitHub:
1. Create pull request: database/add-orders-table → main
2. Add description: "Adds orders table for order management"
3. Request reviewers

# Reviewers:
1. See SQL changes
2. See test results
3. Approve PR
```

**Day 3: Deploy**

```
# On GitHub:
1. Merge PR to main
2. GitHub Actions triggers:
   ✅ Deploys to STAGING (automatic)
   ✅ Waits 5 minutes
   ✅ Requests production approval

3. Test in staging
4. Approve production deployment
5. GitHub Actions:
   ✅ Deploys to PRODUCTION
   ✅ Creates tag: production-123
   ✅ Notifies team
```

### Example 2: Bug Fix

**Urgent: Found issue in production**

```bash
# Create hotfix branch
git checkout main
git pull origin main
git checkout -b hotfix/fix-order-constraint

# Fix the issue
vim database/changelog/changes/V0031__fix_order_constraint.sql

git add database/changelog/changes/V0031__fix_order_constraint.sql
git commit -m "Fix order constraint issue"
git push origin hotfix/fix-order-constraint

# Option 1: Follow normal process (recommended)
# - Create PR
# - Quick review
# - Merge to main
# - Deploy through staging → production

# Option 2: Emergency manual deployment
# - Go to Actions tab
# - Run "Manual Deployment" workflow
# - Select hotfix branch
# - Select production environment
# - Requires approval
# - Deploys directly
```

### Example 3: Multiple Developers

**Scenario: Two developers working simultaneously**

```bash
# Developer A: Adding customer status
git checkout -b database/add-customer-status
# ... work on changes ...
git push origin database/add-customer-status
# Deploys to DEV

# Developer B: Adding order notes
git checkout -b database/add-order-notes
# ... work on changes ...
git push origin database/add-order-notes
# Deploys to DEV

# Both changes deployed to DEV
# DEV database has both changes
# Each developer can test their feature

# Later: Merge to main one at a time
# Developer A merges first → deploys to staging/prod
# Developer B merges second → deploys to staging/prod
```

## Branch Protection Rules

### Why Protect Branches?

Branch protection prevents:
- ❌ Accidental direct pushes to main
- ❌ Bypassing code review
- ❌ Deploying untested code
- ❌ Breaking the main branch

### Essential Protection for Main Branch

**Minimum protection (set in GitHub):**

1. **Go to**: Repository → Settings → Branches
2. **Add rule** for `main` branch
3. **Configure:**

```
✅ Require pull request before merging
   ✅ Require 1 approval
   ✅ Dismiss stale reviews

✅ Require status checks to pass
   ✅ Validation check
   ✅ Test suite

✅ Require conversation resolution

✅ Do not allow bypassing the above settings

❌ Allow force pushes: NO
❌ Allow deletions: NO
```

### Recommended Protection Levels

**For main branch:**
```
Team size 1-5:   1 reviewer required
Team size 6-10:  1 reviewer required
Team size 11-20: 2 reviewers required
```

**For database changes (using CODEOWNERS):**
```
# .github/CODEOWNERS

# Default: Any team member can approve
* @yourcompany/developers

# Database changes: Senior developer must approve
database/** @yourcompany/senior-developers
```

## Best Practices

### 1. Keep Branches Short-Lived

**Good:**
```
Create branch Monday
Work 1-3 days
Merge Wednesday/Thursday
Delete branch

Branch lifetime: 1-3 days
```

**Bad:**
```
Create branch Monday
Work for 2 weeks
Branch gets outdated
Hard to merge
Conflicts everywhere

Branch lifetime: 2+ weeks ❌
```

**Why:** Long-lived branches:
- Accumulate conflicts
- Get out of sync with main
- Harder to review
- Higher merge risk

### 2. Sync with Main Regularly

```bash
# While working on feature branch
# Sync with main daily or every few commits

git checkout database/add-orders-table
git fetch origin
git merge origin/main

# OR use rebase (advanced)
git rebase origin/main
```

**Benefit**: Catches conflicts early, easier to resolve

### 3. One Feature Per Branch

**Good:**
```
Branch: database/add-orders-table
Changes:
✅ One orders table
✅ Related indexes
✅ Related constraints

Clear, focused changes
```

**Bad:**
```
Branch: database/various-changes
Changes:
❌ Orders table
❌ Customer status update
❌ Fix old constraint
❌ Add new indexes
❌ Refactor something

Too much, hard to review
```

### 4. Write Descriptive Commit Messages

**Good:**
```bash
git commit -m "Add orders table with customer relationship"
git commit -m "Add index on order_date for performance"
git commit -m "Fix NOT NULL constraint on orders.total_amount"
```

**Bad:**
```bash
git commit -m "updates"
git commit -m "fix"
git commit -m "more changes"
```

### 5. Test Before Creating PR

```bash
# Before creating pull request:

✅ Test locally if possible
✅ Push to feature branch
✅ Verify dev deployment succeeded
✅ Test in dev environment
✅ Only then create PR
```

### 6. Clean Up Branches

```bash
# After merging, delete feature branch

# On GitHub: Click "Delete branch" button after merge

# Locally:
git checkout main
git pull origin main
git branch -d database/add-orders-table

# Delete remote branch if not deleted on GitHub
git push origin --delete database/add-orders-table
```

**Why:** Keeps repository clean, easier to see active work

### 7. Use Branch Naming Conventions

**Follow team convention:**
```
feature/    - New features
database/   - Database changes
bugfix/     - Bug fixes
hotfix/     - Urgent production fixes
release/    - Release branches (if using GitFlow)
```

**Benefits:**
- Easy to understand purpose
- Can filter in GitHub
- Can apply different CI/CD rules
- Professional appearance

### 8. Never Commit Secrets

**Never:**
```bash
# BAD - contains password
git add liquibase.properties
git commit -m "Add config"

# liquibase.properties contains:
password=MySecretPassword123  ❌
```

**Always:**
```bash
# GOOD - use example file
git add liquibase.properties.example

# liquibase.properties.example contains:
password=YOUR_PASSWORD_HERE  ✅

# Add liquibase.properties to .gitignore
echo "liquibase.properties" >> .gitignore
```

### 9. Write Helpful PR Descriptions

**Good PR description:**
```
## Summary
Adds orders table to support order management feature

## Database Changes
- Creates orders table
- Adds foreign key to customers table
- Adds indexes for performance

## Testing
- ✅ Tested in dev environment
- ✅ Verified foreign key constraint
- ✅ Tested insert/update/delete operations

## Rollback
SQL provided in rollback section of changelog

## Related
Ticket: JIRA-1234
```

**Bad PR description:**
```
add orders table
```

### 10. Review Your Own PR First

Before requesting review:
```
1. Look at the PR yourself
2. Check for:
   ✅ Any debug code left in?
   ✅ Any unnecessary changes?
   ✅ All files included?
   ✅ Commit messages clear?
   ✅ Description complete?

3. Add comments explaining complex parts
4. Then request review
```

## Common Scenarios

### Scenario 1: Oops, Pushed to Wrong Branch

**Problem:**
```bash
# Meant to push to feature branch
# Accidentally pushed to main
git push origin main  ❌
```

**Solution:**
```bash
# If you haven't pushed yet:
git reset HEAD~1  # Undo last commit
git checkout -b feature/my-feature
git commit -m "My changes"
git push origin feature/my-feature

# If already pushed and main is protected:
# Good news: Protection prevents the push
# Error: "protected branch hook declined"

# If already pushed and main is NOT protected:
# Contact team lead immediately
# May need to revert commit
```

### Scenario 2: Merge Conflicts

**Problem:**
```bash
# Trying to merge to main
git merge origin/main

# Output:
CONFLICT (content): Merge conflict in database/changelog/changelog.xml
Automatic merge failed; fix conflicts and then commit the result.
```

**Solution:**
```bash
# 1. Open conflicted file
vim database/changelog/changelog.xml

# 2. Look for conflict markers:
<<<<<<< HEAD
Your changes
=======
Changes from main
>>>>>>> origin/main

# 3. Decide what to keep
# Keep both changes, fix manually

# 4. Remove conflict markers
# Save file

# 5. Mark as resolved
git add database/changelog/changelog.xml
git commit -m "Resolve merge conflict"
git push origin database/my-feature
```

### Scenario 3: Need to Undo Last Commit

**Before pushing:**
```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Undo last commit, discard changes
git reset --hard HEAD~1
```

**After pushing:**
```bash
# Create new commit that undoes previous
git revert HEAD
git push origin database/my-feature
```

### Scenario 4: Multiple Features Depend on Each Other

**Problem:**
```
Feature A: Add customers table
Feature B: Add orders table (needs customers)

How to handle dependency?
```

**Solution:**
```bash
# Option 1: Work sequentially
1. Finish Feature A
2. Merge A to main
3. Start Feature B from updated main

# Option 2: Stack branches
1. Create branch for Feature A
2. Create Feature B branch from Feature A
3. When A merges, rebase B onto main

# Option 3: Combine features
1. If both small, put in same branch
2. Create database/add-customers-and-orders
3. Deploy together
```

### Scenario 5: Emergency Production Fix

**Problem:**
```
Production is down!
Need to fix database issue immediately!
```

**Recommended process:**
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix

# 2. Make minimum necessary fix
vim database/changelog/changes/V0XXX__urgent_fix.sql
git commit -m "Urgent: Fix production issue"
git push origin hotfix/urgent-fix

# 3. Use manual deployment workflow
# Go to Actions → Manual Deployment
# Select: hotfix/urgent-fix branch
# Environment: production
# Requires approval (expedited)

# 4. After fixing production, follow normal process:
# - Create PR
# - Quick review
# - Merge to main
# - Ensure staging has fix too
```

## Troubleshooting

### Problem: Can't Push to Main

**Error:**
```
remote: error: GH006: Protected branch update failed
remote: error: Required status check "validate" is pending
```

**Solution:**
```
✅ This is correct behavior!
✅ Main branch is protected
✅ You should create a pull request instead

Steps:
1. Push to feature branch
2. Create pull request on GitHub
3. Get approval
4. Merge PR
```

### Problem: Feature Branch Is Behind Main

**Warning:**
```
This branch is 12 commits behind main
```

**Solution:**
```bash
# Update your feature branch
git checkout database/my-feature
git fetch origin
git merge origin/main

# Or use rebase (cleaner history)
git rebase origin/main

# Push updated branch
git push origin database/my-feature
```

### Problem: Accidentally Committed to Main

**If protected:**
```
✅ Can't push to main
✅ Protection saved you!
```

**If not protected and already pushed:**
```bash
# Contact team immediately
# May need to revert:
git revert <commit-sha>
git push origin main
```

### Problem: Branch Name Typo

**Wrong:**
```bash
git checkout -b databse/add-orders  # Typo!
```

**Fix:**
```bash
# Rename branch
git branch -m database/add-orders

# Update remote
git push origin :databse/add-orders  # Delete old name
git push origin database/add-orders  # Push new name
```

### Problem: Forgot to Pull Before Starting

**Result:**
```
Your branch and main have diverged
```

**Solution:**
```bash
# Pull with rebase
git pull --rebase origin main

# Or pull and merge
git pull origin main

# Then push
git push origin database/my-feature
```

## FAQ

### Q1: Should every database change have its own branch?

**A:** Generally yes:
```
✅ Each logical change gets its own branch
✅ Makes review easier
✅ Can deploy independently
✅ Clear history

Exception:
- Very small related changes can share a branch
- Example: Adding table + immediate fix to same table
```

### Q2: How long should branches stay open?

**A:** As short as possible:
```
✅ Ideal: 1-3 days
⚠️ Acceptable: Up to 1 week
❌ Too long: More than 1 week

Long branches:
- Get out of sync
- Accumulate conflicts
- Hard to review
```

### Q3: Can I work on multiple branches at once?

**A:** Yes, but be careful:
```bash
# Switch between branches
git checkout database/feature-a
# Work on feature A

git checkout database/feature-b
# Work on feature B

# Git keeps changes separate
# Just make sure to commit before switching
```

### Q4: What if I forget which branch I'm on?

**A:** Check current branch:
```bash
# Show current branch
git branch

# Or use prompt (shows in terminal)
# Many tools show current branch

# Output:
  main
* database/add-orders  ← You're here
  feature/something-else
```

### Q5: Should I delete branches after merging?

**A:** Yes, always:
```
✅ Delete after successful merge
✅ Keeps repository clean
✅ Easy to see active work
✅ Prevents confusion

GitHub offers "Delete branch" button after merge
```

### Q6: Can I deploy from any branch?

**A:** Depends on your workflow:
```
Feature branches → DEV only (automatic)
Main branch → All environments (with approvals)
Hotfix branches → Can deploy anywhere (manual)
```

### Q7: What if two people create branches with same name?

**A:** Git allows it, but avoid:
```
Use unique names:
✅ database/john-add-orders
✅ database/add-orders-jira-1234
✅ database/add-orders-v2

This rarely happens with good naming conventions
```

### Q8: How do I know what's deployed where?

**A:** Check GitHub:
```
1. Go to Environments in repository
2. See deployment history per environment
3. See which commit is deployed
4. See who approved

Or query database:
SELECT * FROM DATABASECHANGELOG
ORDER BY DATEEXECUTED DESC;
```

### Q9: Can I skip staging and go straight to production?

**A:** Technically yes, but **don't**:
```
❌ Bad idea - no testing in staging
✅ Always test in staging first
✅ Catch issues before production
✅ Staging exists for a reason

Exception: Hotfix with manual deployment
But still test if possible
```

### Q10: What if main branch gets broken?

**A:** Fix immediately:
```
Option 1: Revert the breaking commit
git revert <commit-sha>

Option 2: Fix forward
Create hotfix branch
Fix issue
Fast-track through review
Merge

Option 3: Rollback deployment
Use Liquibase rollback
Fix code
Redeploy

Always: Learn from it, improve protection rules
```

## Summary

### Key Takeaways

1. **Use GitHub Flow** - Best for teams under 20
2. **Feature branches deploy to dev** - Automatic testing
3. **Main branch deploys through all environments** - With approvals
4. **Keep branches short-lived** - 1-3 days ideal
5. **Protect main branch** - Require reviews
6. **Delete merged branches** - Keep repository clean
7. **Sync regularly** - Merge main into feature branch
8. **One feature per branch** - Easier to review
9. **Test before creating PR** - Save reviewers' time
10. **Use clear naming** - `database/description` format

### Recommended Workflow for Your Team

```
For daily work:
1. Create feature branch
2. Push to GitHub (deploys to dev)
3. Test in dev
4. Create pull request
5. Team reviews
6. Merge to main
7. Deploys through staging → production
```

### Quick Reference

**Branch Commands:**
```bash
# Create and switch to new branch
git checkout -b database/my-feature

# See current branch
git branch

# Switch branches
git checkout main

# Update from main
git merge origin/main

# Delete branch
git branch -d database/my-feature
```

**Branch Patterns:**
```
feature/*    - New features
database/*   - Database changes
bugfix/*     - Bug fixes
hotfix/*     - Urgent fixes
```

**Environment Mapping:**
```
Feature branches → Development (auto)
Main branch      → Staging (auto) → Production (approval)
```

### Your Next Steps

1. **Set up branch protection** on main branch
2. **Create CODEOWNERS** for database folder
3. **Configure environments** in GitHub
4. **Try the workflow** with a test change
5. **Train team** on branch strategy
6. **Document** your team's process

---

**Document Version**: 1.0
**Last Updated**: November 2025
**For Teams**: Under 20 people
**Strategy**: GitHub Flow with Environment Deployment
**Related Documents**:
- [Repository Strategy Guide](./repository-strategies-for-database-cicd.md)
- [GitHub Actions Tutorial](./sqlserver-liquibase-github-actions-tutorial.md)
- [Best Practices](../../../best-practices/liquibase/github-actions.md)

**Questions?** Review the FAQ or discuss with your team lead.

**Ready to implement?** Follow the [GitHub Actions Tutorial](./sqlserver-liquibase-github-actions-tutorial.md) to set up your workflows!
