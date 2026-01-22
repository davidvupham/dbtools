# GitHub Project Management Quick Reference

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-GitHub_Projects-blue)

> [!IMPORTANT]
> **Related Docs:** [Glossary](./glossary.md) | [Course Overview](./course_overview.md)

## Table of contents

- [Keyboard shortcuts](#keyboard-shortcuts)
- [GitHub CLI commands](#github-cli-commands)
- [Issue linking keywords](#issue-linking-keywords)
- [Label conventions](#label-conventions)
- [Filter syntax](#filter-syntax)
- [Markdown tips for issues](#markdown-tips-for-issues)
- [GraphQL quick reference](#graphql-quick-reference)

## Keyboard shortcuts

### Global shortcuts (any GitHub page)

| Shortcut | Action |
|----------|--------|
| `?` | Open keyboard shortcuts help |
| `s` or `/` | Focus search bar |
| `g` + `n` | Go to notifications |
| `g` + `d` | Go to dashboard |

### Repository shortcuts

| Shortcut | Action |
|----------|--------|
| `g` + `c` | Go to Code tab |
| `g` + `i` | Go to Issues tab |
| `g` + `p` | Go to Pull Requests tab |
| `g` + `b` | Go to Projects tab |
| `c` | Create new issue (on Issues tab) |

### Issues and pull requests

| Shortcut | Action |
|----------|--------|
| `l` | Open/filter by labels |
| `a` | Set assignee |
| `m` | Set milestone |
| `p` | Set project |
| `r` | Request review (PRs only) |
| `e` | Edit issue/PR body |
| `Ctrl + Enter` | Submit comment |
| `Ctrl + Shift + p` | Preview comment |

### Project board shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Open selected item |
| `Space` | Toggle item selection |
| `Esc` | Close side panel |
| `Cmd/Ctrl + k` | Open command palette |
| `↑` / `↓` | Navigate items |

[↑ Back to Table of Contents](#table-of-contents)

## GitHub CLI commands

### Issues

```bash
# List issues
gh issue list
gh issue list --label "bug"
gh issue list --assignee "@me"
gh issue list --milestone "v1.0"

# Create issue
gh issue create --title "Bug: Login fails" --body "Description here"
gh issue create --title "Feature" --label "enhancement" --assignee "username"

# View and edit
gh issue view 123
gh issue edit 123 --add-label "priority:high"
gh issue close 123
gh issue reopen 123

# Comments
gh issue comment 123 --body "Working on this"
```

### Projects

```bash
# List projects
gh project list
gh project list --owner "org-name"

# View project
gh project view 1
gh project view 1 --owner "org-name"

# Create project
gh project create --title "Sprint 1" --owner "@me"

# Add item to project
gh project item-add 1 --owner "@me" --url "https://github.com/owner/repo/issues/123"

# Edit project item field
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --text "value"
```

### Pull requests

```bash
# List PRs
gh pr list
gh pr list --state "open"

# Create PR
gh pr create --title "Add feature" --body "Description"
gh pr create --fill  # Auto-fill from commits

# Review
gh pr view 123
gh pr checkout 123
gh pr merge 123
```

[↑ Back to Table of Contents](#table-of-contents)

## Issue linking keywords

Use these keywords in commit messages or PR descriptions to automatically close issues when the PR is merged:

| Keyword | Example |
|---------|---------|
| `close` | `close #123` |
| `closes` | `closes #123` |
| `closed` | `closed #123` |
| `fix` | `fix #123` |
| `fixes` | `fixes #123` |
| `fixed` | `fixed #123` |
| `resolve` | `resolve #123` |
| `resolves` | `resolves #123` |
| `resolved` | `resolved #123` |

### Cross-repository linking

```text
# Same organization
fixes org/repo#123

# Full URL
fixes https://github.com/org/repo/issues/123
```

[↑ Back to Table of Contents](#table-of-contents)

## Label conventions

### Recommended label prefixes

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `type:` | Issue category | `type:bug`, `type:feature`, `type:docs` |
| `priority:` | Urgency level | `priority:critical`, `priority:high`, `priority:low` |
| `status:` | Current state | `status:blocked`, `status:in-review`, `status:needs-info` |
| `area:` | Code area | `area:frontend`, `area:api`, `area:database` |
| `effort:` | Size estimate | `effort:small`, `effort:medium`, `effort:large` |

### Recommended color scheme

| Category | Color | Hex Code |
|----------|-------|----------|
| Bug | Red | `#d73a4a` |
| Feature | Green | `#0e8a16` |
| Enhancement | Blue | `#a2eeef` |
| Documentation | Purple | `#d4c5f9` |
| Priority: Critical | Dark Red | `#b60205` |
| Priority: High | Orange | `#ff9f1c` |
| Priority: Low | Gray | `#e4e669` |

[↑ Back to Table of Contents](#table-of-contents)

## Filter syntax

### Issues filter syntax

```text
# Basic filters
is:issue is:open
is:issue is:closed
is:pr is:merged

# Assignee and author
assignee:username
author:username
mentions:username
assignee:@me

# Labels (use quotes for spaces)
label:bug
label:"priority:high"
-label:wontfix

# Milestones
milestone:"v1.0"
no:milestone

# Time-based
created:>2026-01-01
updated:<2026-01-15
closed:2026-01-01..2026-01-31

# Combine filters
is:issue is:open label:bug assignee:@me
```

### Project filter syntax

```text
# Field filters
status:Todo
status:"In Progress"
assignees:username
priority:High

# Negation
-status:Done
-no:assignees

# Multiple values
status:Todo,Doing
label:bug,critical

# Date and iteration
iteration:@current
iteration:@next
due:@today
due:>@today
```

[↑ Back to Table of Contents](#table-of-contents)

## Markdown tips for issues

### Task lists

```markdown
- [ ] Incomplete task
- [x] Completed task
- [ ] Another task
```

### Mentions and references

```markdown
@username          # Mention user
@org/team-name     # Mention team
#123               # Reference issue/PR
owner/repo#123     # Cross-repo reference
commit-sha         # Reference commit
```

### Code blocks

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Tables

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

### Collapsible sections

```markdown
<details>
<summary>Click to expand</summary>

Hidden content here.

</details>
```

### Alerts/Admonitions

```markdown
> [!NOTE]
> Useful information.

> [!WARNING]
> Important warning.

> [!TIP]
> Helpful tip.
```

[↑ Back to Table of Contents](#table-of-contents)

## GraphQL quick reference

### Authentication

```bash
# Set token
export GITHUB_TOKEN="ghp_your_token_here"

# Use with curl
curl -H "Authorization: bearer $GITHUB_TOKEN" \
     -X POST \
     -d '{"query":"{ viewer { login } }"}' \
     https://api.github.com/graphql
```

### Common queries

```graphql
# Get user's projects
query {
  viewer {
    projectsV2(first: 10) {
      nodes {
        id
        title
        number
      }
    }
  }
}

# Get project items
query {
  node(id: "PROJECT_NODE_ID") {
    ... on ProjectV2 {
      items(first: 20) {
        nodes {
          id
          content {
            ... on Issue {
              title
              number
            }
          }
        }
      }
    }
  }
}
```

### Common mutations

```graphql
# Add item to project
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

# Update field value
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

### Finding IDs

```bash
# Get project ID
gh project list --format json | jq '.projects[0].id'

# Get field IDs for a project
gh project field-list PROJECT_NUMBER --owner OWNER --format json
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Quick links

- [GitHub Issues Documentation](https://docs.github.com/en/issues)
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub GraphQL API Explorer](https://docs.github.com/en/graphql/overview/explorer)

---

[↑ Back to Table of Contents](#table-of-contents)
