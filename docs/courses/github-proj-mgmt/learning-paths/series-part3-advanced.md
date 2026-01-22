# Tutorial Part 3: Automation and Advanced Workflows

<!-- markdownlint-disable MD013 -->

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Level](https://img.shields.io/badge/Level-Advanced-red)

> [!IMPORTANT]
> **Related Docs:** [Part 1: Issues](./series-part1-beginner.md) | [Part 2: Projects](./series-part2-intermediate.md) | [Quick Reference](../quick_reference.md)

## Table of contents

- [Introduction](#introduction)
  - [Goals of Part 3](#goals-of-part-3)
  - [What you'll learn](#what-youll-learn)
  - [Prerequisites](#prerequisites)
- [Understanding project automation](#understanding-project-automation)
  - [Automation options overview](#automation-options-overview)
  - [When to use each approach](#when-to-use-each-approach)
- [Step 1: Configure built-in workflows](#step-1-configure-built-in-workflows)
  - [Available built-in workflows](#available-built-in-workflows)
  - [Enabling and configuring workflows](#enabling-and-configuring-workflows)
  - [Auto-add to project](#auto-add-to-project)
- [Step 2: Create GitHub Actions workflows](#step-2-create-github-actions-workflows)
  - [Understanding the workflow structure](#understanding-the-workflow-structure)
  - [Adding items to projects](#adding-items-to-projects)
  - [Updating item fields](#updating-item-fields)
  - [Complete workflow example](#complete-workflow-example)
- [Step 3: Use the GraphQL API](#step-3-use-the-graphql-api)
  - [Authentication setup](#authentication-setup)
  - [Finding IDs](#finding-ids)
  - [Common queries](#common-queries)
  - [Common mutations](#common-mutations)
- [Step 4: Build a custom reporting workflow](#step-4-build-a-custom-reporting-workflow)
  - [Weekly status report](#weekly-status-report)
  - [Velocity tracking](#velocity-tracking)
  - [Stale item alerts](#stale-item-alerts)
- [Step 5: Cross-repository automation](#step-5-cross-repository-automation)
  - [Central project for multiple repos](#central-project-for-multiple-repos)
  - [Syncing status across repos](#syncing-status-across-repos)
- [Step 6: Webhooks and external integrations](#step-6-webhooks-and-external-integrations)
  - [Setting up webhooks](#setting-up-webhooks)
  - [Common integrations](#common-integrations)
- [Enterprise patterns](#enterprise-patterns)
  - [Organization-wide automation](#organization-wide-automation)
  - [Audit and compliance](#audit-and-compliance)
  - [Rate limiting considerations](#rate-limiting-considerations)
- [Practical exercise: Automated project workflow](#practical-exercise-automated-project-workflow)
- [Troubleshooting](#troubleshooting)
- [Next steps](#next-steps)

---

## Introduction

This tutorial is **Part 3** of a comprehensive series on GitHub project management. Part 3 focuses on **automation**—using built-in workflows, GitHub Actions, and the GraphQL API to automate routine project management tasks.

> [!WARNING]
> This tutorial requires familiarity with YAML syntax and basic programming concepts. If you're new to GitHub Actions, consider reviewing the [GitHub Actions documentation](https://docs.github.com/en/actions) first.

### Goals of Part 3

By the end of Part 3, you will have:

1. **Configured built-in workflows** to auto-add and update items
2. **Created GitHub Actions** that manage project items programmatically
3. **Used the GraphQL API** to query and modify project data
4. **Built custom reporting workflows** for status updates and velocity tracking
5. **Implemented cross-repository automation** for organization-wide projects

**The end result:** An automated project management system that reduces manual work and keeps your project data accurate.

### What you'll learn

In this tutorial, you'll learn:

- **Built-in workflows:**
  - Auto-adding issues/PRs to projects
  - Automatic status updates on events
  - Archiving completed items

- **GitHub Actions:**
  - Workflow triggers for project automation
  - Using the GraphQL API in workflows
  - Managing secrets and permissions

- **GraphQL API:**
  - Querying project data
  - Mutating fields and items
  - Finding IDs for automation

- **Advanced patterns:**
  - Cross-repository workflows
  - Custom reporting
  - Enterprise-scale automation

### Prerequisites

Before starting this tutorial, you should have:

- **Completed Parts 1 and 2** or equivalent knowledge
- **A GitHub account** with admin access to a repository
- **Basic YAML syntax knowledge** for workflow files
- **Optional**: Familiarity with GraphQL concepts

[↑ Back to Table of Contents](#table-of-contents)

---

## Understanding project automation

### Automation options overview

GitHub provides three levels of automation for Projects:

| Level | Method | Complexity | Best For |
|-------|--------|------------|----------|
| **Simple** | Built-in Workflows | Low | Basic auto-add and status updates |
| **Medium** | GitHub Actions | Medium | Custom logic, cross-repo |
| **Advanced** | GraphQL API | High | Full control, external integrations |

### When to use each approach

**Built-in workflows:**

- Auto-add new issues/PRs to a project
- Update status when PRs are merged/closed
- Archive items that meet criteria

**GitHub Actions:**

- Custom logic (e.g., set priority based on labels)
- Cross-repository automation
- Scheduled tasks (e.g., weekly reports)
- Integration with external services

**GraphQL API directly:**

- Complex queries (e.g., analytics dashboards)
- Bulk operations
- External tool integration
- Real-time updates via webhooks

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 1: Configure built-in workflows

GitHub Projects include built-in automation workflows that require no coding.

### Available built-in workflows

| Workflow | Trigger | Action |
|----------|---------|--------|
| **Item added to project** | Item added | Set field value |
| **Item reopened** | Issue/PR reopened | Set status |
| **Item closed** | Issue/PR closed | Set status |
| **Code changes requested** | PR review requested changes | Set status |
| **Code review approved** | PR approved | Set status |
| **Pull request merged** | PR merged | Set status |
| **Auto-archive items** | Criteria met | Archive item |
| **Auto-add to project** | Issue/PR created | Add to project |

### Enabling and configuring workflows

1. Open your **project**
2. Click **"..."** (menu) → **"Workflows"**
3. Select a workflow to configure
4. Toggle **"On"** to enable
5. Configure the action:
   - Select the **field** to update
   - Select the **value** to set

**Example: Auto-set status when PR is merged**

1. Enable **"Pull request merged"** workflow
2. Set: **Status** → **"Done"**

Now when any PR linked to a project item is merged, the item's status is automatically set to "Done".

### Auto-add to project

The **Auto-add to project** workflow adds new issues and PRs automatically.

**Configuration:**

1. Enable the **"Auto-add to project"** workflow
2. Set the **filter** to control what gets added:

```text
# Add all issues
is:issue

# Add issues with specific label
is:issue label:tracked

# Add from specific repo only
is:issue repo:org/specific-repo

# Add high-priority items only
is:issue label:priority:high,priority:critical
```

**Example filters:**

| Filter | Adds |
|--------|------|
| `is:issue` | All issues |
| `is:pr` | All pull requests |
| `is:issue is:open` | Open issues only |
| `is:issue label:bug` | Issues labeled "bug" |
| `is:issue -label:wontfix` | Issues not labeled "wontfix" |

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 2: Create GitHub Actions workflows

For custom automation, use GitHub Actions with the GraphQL API.

### Understanding the workflow structure

Create `.github/workflows/project-automation.yml`:

```yaml
name: Project Automation

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, ready_for_review, closed]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - name: Add to project
        uses: actions/add-to-project@v1.0.2
        with:
          project-url: https://github.com/orgs/ORG/projects/PROJECT_NUMBER
          github-token: ${{ secrets.PROJECT_TOKEN }}
```

### Adding items to projects

**Using the official action:**

```yaml
name: Add Issue to Project

on:
  issues:
    types: [opened]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v1.0.2
        with:
          project-url: https://github.com/users/USERNAME/projects/1
          github-token: ${{ secrets.PROJECT_TOKEN }}
```

**Creating a token:**

1. Go to **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Create a token with:
   - **Repository access**: The repositories you want to automate
   - **Permissions**:
     - `Issues`: Read and write
     - `Pull requests`: Read and write
     - `Projects`: Read and write

3. Add the token as a repository secret:
   - Go to **Repository Settings** → **Secrets and variables** → **Actions**
   - Add secret named `PROJECT_TOKEN`

### Updating item fields

To update fields, use the GraphQL API in your workflow:

```yaml
name: Set Priority on Bug

on:
  issues:
    types: [labeled]

jobs:
  set-priority:
    runs-on: ubuntu-latest
    if: github.event.label.name == 'type:bug'
    steps:
      - name: Get project item
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          # Get the issue's project item ID
          ITEM_ID=$(gh api graphql -f query='
            query($issue: Int!, $owner: String!, $repo: String!) {
              repository(owner: $owner, name: $repo) {
                issue(number: $issue) {
                  projectItems(first: 10) {
                    nodes {
                      id
                      project { title }
                    }
                  }
                }
              }
            }
          ' -f owner="${{ github.repository_owner }}" \
            -f repo="${{ github.event.repository.name }}" \
            -F issue=${{ github.event.issue.number }} \
            --jq '.data.repository.issue.projectItems.nodes[0].id')

          echo "ITEM_ID=$ITEM_ID" >> $GITHUB_ENV

      - name: Set priority to High
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          gh api graphql -f query='
            mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $project
                itemId: $item
                fieldId: $field
                value: { singleSelectOptionId: $value }
              }) {
                projectV2Item { id }
              }
            }
          ' -f project="PROJECT_ID" \
            -f item="$ITEM_ID" \
            -f field="PRIORITY_FIELD_ID" \
            -f value="HIGH_OPTION_ID"
```

### Complete workflow example

Here's a complete workflow that:
1. Adds new issues to a project
2. Sets status to "Todo"
3. Sets priority based on labels

```yaml
name: Project Automation

on:
  issues:
    types: [opened, labeled]

env:
  PROJECT_ID: "PVT_kwXXXXXXXX"
  STATUS_FIELD_ID: "PVTSSF_XXXXXX"
  PRIORITY_FIELD_ID: "PVTSSF_YYYYYY"
  TODO_OPTION_ID: "XXXXXXXX"
  HIGH_PRIORITY_ID: "YYYYYYYY"
  CRITICAL_PRIORITY_ID: "ZZZZZZZZ"

jobs:
  project-automation:
    runs-on: ubuntu-latest
    steps:
      - name: Add issue to project
        if: github.event.action == 'opened'
        uses: actions/add-to-project@v1.0.2
        id: add-to-project
        with:
          project-url: https://github.com/orgs/myorg/projects/1
          github-token: ${{ secrets.PROJECT_TOKEN }}

      - name: Set initial status
        if: github.event.action == 'opened'
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          gh api graphql -f query='
            mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $project
                itemId: $item
                fieldId: $field
                value: { singleSelectOptionId: $value }
              }) {
                projectV2Item { id }
              }
            }
          ' -f project="${{ env.PROJECT_ID }}" \
            -f item="${{ steps.add-to-project.outputs.itemId }}" \
            -f field="${{ env.STATUS_FIELD_ID }}" \
            -f value="${{ env.TODO_OPTION_ID }}"

      - name: Set priority for critical bugs
        if: |
          github.event.action == 'labeled' &&
          (github.event.label.name == 'priority:critical' || github.event.label.name == 'type:bug')
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          # First find the item ID
          ITEM_ID=$(gh api graphql -f query='
            query($issue: Int!, $owner: String!, $repo: String!) {
              repository(owner: $owner, name: $repo) {
                issue(number: $issue) {
                  projectItems(first: 1) {
                    nodes { id }
                  }
                }
              }
            }
          ' -f owner="${{ github.repository_owner }}" \
            -f repo="${{ github.event.repository.name }}" \
            -F issue=${{ github.event.issue.number }} \
            --jq '.data.repository.issue.projectItems.nodes[0].id')

          if [ -n "$ITEM_ID" ]; then
            PRIORITY_VALUE="${{ env.HIGH_PRIORITY_ID }}"
            if [ "${{ github.event.label.name }}" == "priority:critical" ]; then
              PRIORITY_VALUE="${{ env.CRITICAL_PRIORITY_ID }}"
            fi

            gh api graphql -f query='
              mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
                updateProjectV2ItemFieldValue(input: {
                  projectId: $project
                  itemId: $item
                  fieldId: $field
                  value: { singleSelectOptionId: $value }
                }) {
                  projectV2Item { id }
                }
              }
            ' -f project="${{ env.PROJECT_ID }}" \
              -f item="$ITEM_ID" \
              -f field="${{ env.PRIORITY_FIELD_ID }}" \
              -f value="$PRIORITY_VALUE"
          fi
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 3: Use the GraphQL API

The GraphQL API provides full control over project data.

### Authentication setup

**Create a Personal Access Token:**

1. Go to **Settings** → **Developer settings** → **Personal access tokens**
2. Choose **Fine-grained tokens** (recommended) or **Tokens (classic)**
3. Grant necessary scopes:
   - `project` (read/write for projects)
   - `repo` (if accessing private repos)

**Using the token:**

```bash
# Environment variable
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# With curl
curl -H "Authorization: bearer $GITHUB_TOKEN" \
     -X POST \
     -d '{"query":"{ viewer { login } }"}' \
     https://api.github.com/graphql

# With GitHub CLI
gh api graphql -f query='{ viewer { login } }'
```

### Finding IDs

You need node IDs for most API operations. Here's how to find them:

**Project ID:**

```bash
# User project
gh api graphql -f query='
  query($user: String!, $number: Int!) {
    user(login: $user) {
      projectV2(number: $number) {
        id
        title
      }
    }
  }
' -f user="USERNAME" -F number=1

# Organization project
gh api graphql -f query='
  query($org: String!, $number: Int!) {
    organization(login: $org) {
      projectV2(number: $number) {
        id
        title
      }
    }
  }
' -f org="ORG_NAME" -F number=1
```

**Field IDs:**

```bash
gh api graphql -f query='
  query($id: ID!) {
    node(id: $id) {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
            ... on ProjectV2Field {
              id
              name
            }
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
              }
            }
            ... on ProjectV2IterationField {
              id
              name
              configuration {
                iterations {
                  id
                  title
                  startDate
                  duration
                }
              }
            }
          }
        }
      }
    }
  }
' -f id="PROJECT_ID"
```

### Common queries

**List project items:**

```graphql
query {
  node(id: "PROJECT_ID") {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                text
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2FieldCommon { name } }
              }
            }
          }
          content {
            ... on Issue {
              title
              number
              state
            }
            ... on PullRequest {
              title
              number
              state
            }
          }
        }
      }
    }
  }
}
```

**Get items by status:**

```bash
gh api graphql -f query='
  query($id: ID!) {
    node(id: $id) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValueByName(name: "Status") {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
              }
            }
            content {
              ... on Issue { title number }
            }
          }
        }
      }
    }
  }
' -f id="PROJECT_ID" | jq '.data.node.items.nodes[] | select(.fieldValueByName.name == "Todo")'
```

### Common mutations

**Add item to project:**

```graphql
mutation {
  addProjectV2ItemById(input: {
    projectId: "PROJECT_ID"
    contentId: "ISSUE_NODE_ID"
  }) {
    item {
      id
    }
  }
}
```

**Update single-select field:**

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "FIELD_ID"
    value: { singleSelectOptionId: "OPTION_ID" }
  }) {
    projectV2Item {
      id
    }
  }
}
```

**Update text field:**

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "FIELD_ID"
    value: { text: "My note here" }
  }) {
    projectV2Item {
      id
    }
  }
}
```

**Update number field:**

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "FIELD_ID"
    value: { number: 5 }
  }) {
    projectV2Item {
      id
    }
  }
}
```

**Set iteration:**

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "ITERATION_FIELD_ID"
    value: { iterationId: "ITERATION_ID" }
  }) {
    projectV2Item {
      id
    }
  }
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 4: Build a custom reporting workflow

Create automated reports using scheduled workflows.

### Weekly status report

Create `.github/workflows/weekly-report.yml`:

```yaml
name: Weekly Project Report

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate report
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
          PROJECT_ID: "PVT_kwXXXXXX"
        run: |
          # Fetch all items
          ITEMS=$(gh api graphql -f query='
            query($id: ID!) {
              node(id: $id) {
                ... on ProjectV2 {
                  items(first: 100) {
                    nodes {
                      fieldValueByName(name: "Status") {
                        ... on ProjectV2ItemFieldSingleSelectValue { name }
                      }
                      content {
                        ... on Issue { title number state }
                      }
                    }
                  }
                }
              }
            }
          ' -f id="$PROJECT_ID")

          # Count by status
          TODO=$(echo "$ITEMS" | jq '[.data.node.items.nodes[] | select(.fieldValueByName.name == "Todo")] | length')
          IN_PROGRESS=$(echo "$ITEMS" | jq '[.data.node.items.nodes[] | select(.fieldValueByName.name == "In Progress")] | length')
          DONE=$(echo "$ITEMS" | jq '[.data.node.items.nodes[] | select(.fieldValueByName.name == "Done")] | length')

          # Create report
          echo "## Weekly Project Report" > report.md
          echo "" >> report.md
          echo "**Generated:** $(date)" >> report.md
          echo "" >> report.md
          echo "### Status Summary" >> report.md
          echo "| Status | Count |" >> report.md
          echo "|--------|-------|" >> report.md
          echo "| Todo | $TODO |" >> report.md
          echo "| In Progress | $IN_PROGRESS |" >> report.md
          echo "| Done | $DONE |" >> report.md

          cat report.md

      - name: Create issue with report
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue create \
            --title "Weekly Report: $(date +%Y-%m-%d)" \
            --body-file report.md \
            --label "type:report"
```

### Velocity tracking

Track story points completed per sprint:

```yaml
name: Sprint Velocity Report

on:
  schedule:
    - cron: '0 9 * * 1'  # End of sprint (adjust)
  workflow_dispatch:

jobs:
  velocity:
    runs-on: ubuntu-latest
    steps:
      - name: Calculate velocity
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
          PROJECT_ID: "PVT_kwXXXXXX"
        run: |
          # Get items completed in current iteration
          ITEMS=$(gh api graphql -f query='
            query($id: ID!) {
              node(id: $id) {
                ... on ProjectV2 {
                  items(first: 100) {
                    nodes {
                      fieldValueByName(name: "Status") {
                        ... on ProjectV2ItemFieldSingleSelectValue { name }
                      }
                      fieldValueByName(name: "Effort") {
                        ... on ProjectV2ItemFieldNumberValue { number }
                      }
                      fieldValueByName(name: "Sprint") {
                        ... on ProjectV2ItemFieldIterationValue { title }
                      }
                    }
                  }
                }
              }
            }
          ' -f id="$PROJECT_ID")

          # Sum effort for completed items
          VELOCITY=$(echo "$ITEMS" | jq '
            [.data.node.items.nodes[]
              | select(.fieldValueByName.name == "Done")
              | .fieldValueByName[1].number // 0
            ] | add // 0')

          echo "Sprint Velocity: $VELOCITY points"
```

### Stale item alerts

Alert on items that haven't been updated:

```yaml
name: Stale Item Alert

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC

jobs:
  check-stale:
    runs-on: ubuntu-latest
    steps:
      - name: Find stale items
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          # Find issues in "In Progress" for over 7 days
          STALE=$(gh issue list \
            --search "is:open updated:<$(date -d '7 days ago' +%Y-%m-%d)" \
            --json number,title,updatedAt \
            --jq '.[] | "- #\(.number): \(.title) (updated: \(.updatedAt))"')

          if [ -n "$STALE" ]; then
            echo "## Stale Items Alert" > alert.md
            echo "" >> alert.md
            echo "The following items haven't been updated in 7+ days:" >> alert.md
            echo "" >> alert.md
            echo "$STALE" >> alert.md

            gh issue create \
              --title "Stale Items Alert: $(date +%Y-%m-%d)" \
              --body-file alert.md \
              --label "type:alert"
          fi
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 5: Cross-repository automation

Manage projects across multiple repositories.

### Central project for multiple repos

Create a single workflow that runs in each repository:

```yaml
# .github/workflows/add-to-central-project.yml
name: Add to Central Project

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v1.0.2
        with:
          project-url: https://github.com/orgs/MY_ORG/projects/1
          github-token: ${{ secrets.ORG_PROJECT_TOKEN }}
```

**Deploy to multiple repos:**

Use a GitHub Actions workflow to sync the workflow file:

```yaml
# In a central "workflow-templates" repo
name: Sync Workflows

on:
  push:
    paths: ['workflows/**']

jobs:
  sync:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repo: [repo1, repo2, repo3]
    steps:
      - uses: actions/checkout@v4

      - name: Sync workflow to ${{ matrix.repo }}
        env:
          GH_TOKEN: ${{ secrets.ORG_TOKEN }}
        run: |
          gh api repos/myorg/${{ matrix.repo }}/contents/.github/workflows/add-to-central-project.yml \
            -X PUT \
            -f message="Sync workflow from template" \
            -f content="$(base64 -w0 workflows/add-to-central-project.yml)"
```

### Syncing status across repos

Keep related items in sync:

```yaml
name: Sync Status

on:
  issues:
    types: [closed, reopened]

jobs:
  sync-status:
    runs-on: ubuntu-latest
    steps:
      - name: Update project status
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
          PROJECT_ID: "PVT_kwXXXXXX"
          STATUS_FIELD_ID: "PVTSSF_XXXXXX"
          DONE_STATUS_ID: "XXXXXXXX"
          TODO_STATUS_ID: "YYYYYYYY"
        run: |
          # Get item ID
          ITEM_ID=$(gh api graphql -f query='
            query($url: URI!) {
              resource(url: $url) {
                ... on Issue {
                  projectItems(first: 1) {
                    nodes { id }
                  }
                }
              }
            }
          ' -f url="${{ github.event.issue.html_url }}" \
            --jq '.data.resource.projectItems.nodes[0].id')

          if [ -n "$ITEM_ID" ]; then
            STATUS_VALUE="${{ github.event.action == 'closed' && env.DONE_STATUS_ID || env.TODO_STATUS_ID }}"

            gh api graphql -f query='
              mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
                updateProjectV2ItemFieldValue(input: {
                  projectId: $project
                  itemId: $item
                  fieldId: $field
                  value: { singleSelectOptionId: $value }
                }) {
                  projectV2Item { id }
                }
              }
            ' -f project="$PROJECT_ID" \
              -f item="$ITEM_ID" \
              -f field="$STATUS_FIELD_ID" \
              -f value="$STATUS_VALUE"
          fi
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 6: Webhooks and external integrations

### Setting up webhooks

Webhooks send HTTP requests when events occur.

**Create a webhook:**

1. Go to **Repository Settings** → **Webhooks**
2. Click **"Add webhook"**
3. Configure:
   - **Payload URL**: Your server endpoint
   - **Content type**: `application/json`
   - **Secret**: A secure string for validation
   - **Events**: Select events to trigger the webhook

**Webhook payload for project events:**

```json
{
  "action": "edited",
  "projects_v2_item": {
    "id": "PVTI_xxx",
    "node_id": "PVTI_xxx",
    "project_node_id": "PVT_xxx",
    "content_node_id": "I_xxx",
    "content_type": "Issue"
  },
  "changes": {
    "field_value": {
      "field_node_id": "PVTSSF_xxx",
      "field_type": "single_select"
    }
  }
}
```

### Common integrations

**Slack notifications:**

```yaml
name: Slack Notification

on:
  issues:
    types: [opened]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send to Slack
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload: |
            {
              "text": "New issue: ${{ github.event.issue.title }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*<${{ github.event.issue.html_url }}|${{ github.event.issue.title }}>*\n${{ github.event.issue.body }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Discord notifications:**

```yaml
- name: Send to Discord
  env:
    DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
  run: |
    curl -H "Content-Type: application/json" \
         -d '{"content": "New issue: ${{ github.event.issue.title }}\n${{ github.event.issue.html_url }}"}' \
         "$DISCORD_WEBHOOK"
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Enterprise patterns

### Organization-wide automation

For large organizations, use **reusable workflows**:

```yaml
# org/.github/workflows/project-automation.yml
name: Reusable Project Automation

on:
  workflow_call:
    inputs:
      project-url:
        required: true
        type: string
    secrets:
      token:
        required: true

jobs:
  automation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v1.0.2
        with:
          project-url: ${{ inputs.project-url }}
          github-token: ${{ secrets.token }}
```

**Call from any repo:**

```yaml
name: Project Automation

on:
  issues:
    types: [opened]

jobs:
  add-to-project:
    uses: myorg/.github/.github/workflows/project-automation.yml@main
    with:
      project-url: https://github.com/orgs/myorg/projects/1
    secrets:
      token: ${{ secrets.PROJECT_TOKEN }}
```

### Audit and compliance

Track all project changes:

```yaml
name: Audit Log

on:
  projects_v2_item:
    types: [created, edited, deleted]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Log change
        run: |
          echo "Project item ${{ github.event.action }}"
          echo "Item: ${{ github.event.projects_v2_item.node_id }}"
          echo "By: ${{ github.actor }}"
          echo "Time: ${{ github.event.projects_v2_item.updated_at }}"
```

### Rate limiting considerations

GitHub API has rate limits:

- **GraphQL**: 5,000 points per hour
- **REST**: 5,000 requests per hour

**Best practices:**

1. **Cache data** when possible
2. **Batch operations** instead of individual calls
3. **Use conditional requests** with ETags
4. **Monitor usage** with the `rateLimit` query

```graphql
query {
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Practical exercise: Automated project workflow

Build a complete automated workflow.

### Exercise: Full automation setup

**Goal:** Create a workflow that:
1. Adds new issues to a project
2. Sets initial status to "Backlog"
3. Sets priority based on labels
4. Updates status when PRs are merged

**Step 1: Get your project IDs**

```bash
# Get project ID
gh project list --format json | jq '.'

# Get field IDs
gh project field-list PROJECT_NUMBER --owner "@me" --format json
```

**Step 2: Create the workflow**

Create `.github/workflows/project-automation.yml`:

```yaml
name: Complete Project Automation

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [closed]

env:
  PROJECT_URL: "https://github.com/users/USERNAME/projects/1"
  # Replace these with your actual IDs from step 1
  PROJECT_ID: "PVT_kwXXXXXX"
  STATUS_FIELD_ID: "PVTSSF_XXXXXX"
  PRIORITY_FIELD_ID: "PVTSSF_YYYYYY"
  BACKLOG_STATUS_ID: "XXXXXXXX"
  DONE_STATUS_ID: "YYYYYYYY"
  HIGH_PRIORITY_ID: "ZZZZZZZZ"

jobs:
  add-new-issues:
    if: github.event_name == 'issues' && github.event.action == 'opened'
    runs-on: ubuntu-latest
    outputs:
      itemId: ${{ steps.add.outputs.itemId }}
    steps:
      - name: Add to project
        id: add
        uses: actions/add-to-project@v1.0.2
        with:
          project-url: ${{ env.PROJECT_URL }}
          github-token: ${{ secrets.PROJECT_TOKEN }}

      - name: Set initial status
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          gh api graphql -f query='
            mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $project
                itemId: $item
                fieldId: $field
                value: { singleSelectOptionId: $value }
              }) {
                projectV2Item { id }
              }
            }
          ' -f project="${{ env.PROJECT_ID }}" \
            -f item="${{ steps.add.outputs.itemId }}" \
            -f field="${{ env.STATUS_FIELD_ID }}" \
            -f value="${{ env.BACKLOG_STATUS_ID }}"

  set-priority:
    if: |
      github.event_name == 'issues' &&
      github.event.action == 'labeled' &&
      contains(github.event.label.name, 'priority:')
    runs-on: ubuntu-latest
    steps:
      - name: Update priority
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          ITEM_ID=$(gh api graphql -f query='
            query($url: URI!) {
              resource(url: $url) {
                ... on Issue {
                  projectItems(first: 1) {
                    nodes { id }
                  }
                }
              }
            }
          ' -f url="${{ github.event.issue.html_url }}" \
            --jq '.data.resource.projectItems.nodes[0].id')

          if [ -n "$ITEM_ID" ] && [ "${{ github.event.label.name }}" == "priority:high" ]; then
            gh api graphql -f query='
              mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
                updateProjectV2ItemFieldValue(input: {
                  projectId: $project
                  itemId: $item
                  fieldId: $field
                  value: { singleSelectOptionId: $value }
                }) {
                  projectV2Item { id }
                }
              }
            ' -f project="${{ env.PROJECT_ID }}" \
              -f item="$ITEM_ID" \
              -f field="${{ env.PRIORITY_FIELD_ID }}" \
              -f value="${{ env.HIGH_PRIORITY_ID }}"
          fi

  update-on-merge:
    if: |
      github.event_name == 'pull_request' &&
      github.event.action == 'closed' &&
      github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Find linked issues
        env:
          GH_TOKEN: ${{ secrets.PROJECT_TOKEN }}
        run: |
          # Extract issue numbers from PR body
          ISSUES=$(echo "${{ github.event.pull_request.body }}" | grep -oP '(close|closes|fix|fixes|resolve|resolves)\s+#\K\d+' || true)

          for ISSUE_NUM in $ISSUES; do
            ITEM_ID=$(gh api graphql -f query='
              query($owner: String!, $repo: String!, $issue: Int!) {
                repository(owner: $owner, name: $repo) {
                  issue(number: $issue) {
                    projectItems(first: 1) {
                      nodes { id }
                    }
                  }
                }
              }
            ' -f owner="${{ github.repository_owner }}" \
              -f repo="${{ github.event.repository.name }}" \
              -F issue="$ISSUE_NUM" \
              --jq '.data.repository.issue.projectItems.nodes[0].id')

            if [ -n "$ITEM_ID" ]; then
              gh api graphql -f query='
                mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
                  updateProjectV2ItemFieldValue(input: {
                    projectId: $project
                    itemId: $item
                    fieldId: $field
                    value: { singleSelectOptionId: $value }
                  }) {
                    projectV2Item { id }
                  }
                }
              ' -f project="${{ env.PROJECT_ID }}" \
                -f item="$ITEM_ID" \
                -f field="${{ env.STATUS_FIELD_ID }}" \
                -f value="${{ env.DONE_STATUS_ID }}"
            fi
          done
```

**Step 3: Add the secret**

1. Go to **Repository Settings** → **Secrets** → **Actions**
2. Add `PROJECT_TOKEN` with your PAT

**Step 4: Test**

1. Create a new issue - should be added to project with "Backlog" status
2. Add `priority:high` label - should update priority field
3. Create a PR with "Fixes #X" - merge it, issue status should become "Done"

[↑ Back to Table of Contents](#table-of-contents)

---

## Troubleshooting

### Common issues

**Q: Actions fail with "Resource not accessible by integration"**

A: The token lacks required permissions. Ensure your PAT has:
- `project` scope for project access
- `repo` scope for private repositories

---

**Q: GraphQL returns "Could not resolve to a node"**

A: The ID is incorrect or you don't have access. Verify:
- The ID format matches (e.g., `PVT_` for projects)
- You have permission to access the resource
- The resource still exists

---

**Q: Built-in workflows don't trigger**

A: Built-in workflows only trigger for items already in the project. The "Auto-add" workflow adds items, then other workflows can trigger.

---

**Q: Rate limit exceeded**

A: You've hit API limits. Solutions:
- Wait for the reset (check `rateLimit` query)
- Optimize queries to fetch only needed data
- Cache results where possible
- Consider using GitHub Apps for higher limits

---

**Q: Workflow runs but nothing happens**

A: Check the workflow logs:
1. Go to **Actions** tab
2. Click the workflow run
3. Expand each step to see output
4. Look for error messages or empty results

[↑ Back to Table of Contents](#table-of-contents)

---

## Next steps

Congratulations! You've completed the GitHub Project Management course. You now know how to:

- Create and manage issues with labels and milestones (Part 1)
- Build projects with custom views, fields, and iterations (Part 2)
- Automate project management with workflows and APIs (Part 3)

**Continue learning:**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub GraphQL API Explorer](https://docs.github.com/en/graphql/overview/explorer)
- [GitHub Skills](https://skills.github.com/) - Interactive courses

**Related guides in this course:**

- [Jira vs GitHub: Comparison and Migration](./tutorial-supplement-jira-migration.md)

---

[↑ Back to Table of Contents](#table-of-contents)
