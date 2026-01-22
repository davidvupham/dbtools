# Tutorial Part 1: GitHub Issues Fundamentals

<!-- markdownlint-disable MD013 -->

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Level](https://img.shields.io/badge/Level-Beginner-brightgreen)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](../quick_reference.md) | [Glossary](../glossary.md) | [Part 2: Projects](./series-part2-intermediate.md)

## Table of contents

- [Introduction](#introduction)
  - [Goals of Part 1](#goals-of-part-1)
  - [What you'll learn](#what-youll-learn)
  - [Prerequisites](#prerequisites)
- [Understanding GitHub Issues](#understanding-github-issues)
  - [What is an issue?](#what-is-an-issue)
  - [Anatomy of a good issue](#anatomy-of-a-good-issue)
- [Step 1: Create your first issue](#step-1-create-your-first-issue)
- [Step 2: Organize with labels](#step-2-organize-with-labels)
  - [Default labels](#default-labels)
  - [Creating custom labels](#creating-custom-labels)
  - [Label naming conventions](#label-naming-conventions)
- [Step 3: Group work with milestones](#step-3-group-work-with-milestones)
  - [Creating milestones](#creating-milestones)
  - [Assigning issues to milestones](#assigning-issues-to-milestones)
- [Step 4: Create issue templates](#step-4-create-issue-templates)
  - [Bug report template](#bug-report-template)
  - [Feature request template](#feature-request-template)
  - [Using template chooser](#using-template-chooser)
- [Step 5: Link issues and pull requests](#step-5-link-issues-and-pull-requests)
  - [Linking with keywords](#linking-with-keywords)
  - [Manual linking](#manual-linking)
  - [Cross-repository references](#cross-repository-references)
- [Step 6: Triage and manage issues](#step-6-triage-and-manage-issues)
  - [Filtering issues](#filtering-issues)
  - [Assigning issues](#assigning-issues)
  - [Closing and reopening](#closing-and-reopening)
- [Practical exercise: Set up a project](#practical-exercise-set-up-a-project)
- [Troubleshooting](#troubleshooting)
- [Next steps](#next-steps)

---

## Introduction

This tutorial is **Part 1** of a comprehensive series on GitHub project management. Part 1 focuses on **GitHub Issues**—the foundation of all project management in GitHub. Before you can use Projects (Part 2) or automation (Part 3), you need to understand how to create, organize, and manage issues effectively.

### Goals of Part 1

By the end of Part 1, you will have:

1. **Created well-structured issues** with clear titles, descriptions, and acceptance criteria
2. **Organized issues with labels** using a consistent naming convention
3. **Grouped related issues into milestones** for release planning
4. **Created issue templates** for consistent bug reports and feature requests
5. **Linked issues to pull requests** for traceability

**The end result:** A repository with organized issues, a clear label taxonomy, milestones for planning, and templates for future contributions.

### What you'll learn

In this tutorial, you'll learn:

- **Issue fundamentals:**
  - How to write effective issue titles and descriptions
  - Using task lists and markdown formatting
  - Mentioning users and teams

- **Organization techniques:**
  - Creating a label taxonomy with prefixes
  - Color-coding labels for visual clarity
  - Using milestones for time-based planning

- **Templates and automation:**
  - Creating YAML-based issue templates
  - Configuring template chooser
  - Using form elements for structured input

- **Workflow best practices:**
  - Linking issues to code changes
  - Triage processes for incoming issues
  - Using filters to find what you need

### Prerequisites

Before starting this tutorial, you should have:

- **A GitHub account** (free tier is sufficient)
  - Create one at [github.com/signup](https://github.com/signup)

- **A test repository** to practice with
  - You can create a new repository or use an existing one
  - We recommend creating a fresh repository for learning

- **Basic GitHub web interface familiarity**
  - Navigating repositories
  - Basic understanding of commits

**No coding experience required!** This tutorial is entirely web-based.

[↑ Back to Table of Contents](#table-of-contents)

---

## Understanding GitHub Issues

### What is an issue?

A GitHub **Issue** is a trackable unit of work within a repository. Issues can represent:

- **Bugs**: Something is broken and needs fixing
- **Features**: New functionality to be added
- **Tasks**: General work items or to-dos
- **Questions**: Discussions or requests for information
- **Documentation**: Content that needs to be written or updated

Issues are the atomic unit of project management in GitHub. Everything else—labels, milestones, projects—builds on top of issues.

> [!NOTE]
> Issues are not just for bugs. Many teams use issues for all types of work, including research tasks, design reviews, and meeting notes.

### Anatomy of a good issue

A well-written issue contains:

| Component | Purpose | Example |
|-----------|---------|---------|
| **Title** | Concise summary of the issue | "Login button unresponsive on mobile" |
| **Description** | Detailed explanation | Steps to reproduce, expected vs actual behavior |
| **Labels** | Categorization | `bug`, `priority:high`, `area:frontend` |
| **Assignee** | Who is responsible | @username |
| **Milestone** | Release or sprint grouping | "v1.0 Release" |
| **Linked PRs** | Related code changes | #45 |

**Example of a well-written bug issue:**

```markdown
## Bug description
The login button on the mobile web app does not respond to taps on iOS Safari.

## Steps to reproduce
1. Open the app on iOS Safari (iPhone 12, iOS 17)
2. Navigate to the login page
3. Enter valid credentials
4. Tap the "Login" button

## Expected behavior
User should be logged in and redirected to the dashboard.

## Actual behavior
Nothing happens. No error message, no loading indicator.

## Environment
- Device: iPhone 12
- OS: iOS 17.2
- Browser: Safari
- App version: 2.1.0

## Screenshots
[Attach screenshot here]

## Acceptance criteria
- [ ] Login button works on iOS Safari
- [ ] Loading indicator appears during authentication
- [ ] Error message displays if login fails
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 1: Create your first issue

Let's create your first issue using the GitHub web interface.

### Using the web interface

1. **Navigate to your repository** on GitHub

2. **Click the "Issues" tab** in the repository navigation
   - If you don't see the Issues tab, go to Settings → Features → check "Issues"

3. **Click "New issue"** (green button on the right)

4. **Fill in the issue details:**

   **Title:** Write a clear, concise title
   ```
   Add user profile page with avatar upload
   ```

   **Description:** Provide context and details using markdown
   ```markdown
   ## Summary
   We need a user profile page where users can view and edit their information.

   ## Requirements
   - Display user's name, email, and bio
   - Allow avatar image upload (max 2MB, jpg/png only)
   - Save changes with validation feedback

   ## Acceptance criteria
   - [ ] Profile page accessible at /profile
   - [ ] Avatar upload working with size/type validation
   - [ ] Changes persist after page refresh
   - [ ] Mobile responsive design
   ```

5. **Click "Submit new issue"**

### Using the GitHub CLI

If you prefer the command line, you can use the GitHub CLI (`gh`):

```bash
# Create a simple issue
gh issue create --title "Add user profile page" --body "Description here"

# Create with labels and assignee
gh issue create \
  --title "Add user profile page with avatar upload" \
  --body "## Summary\nWe need a user profile page..." \
  --label "enhancement" \
  --assignee "@me"
```

> [!TIP]
> Use task lists (checkboxes) in your issue description. GitHub tracks completion percentage and shows it in issue lists.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 2: Organize with labels

Labels are tags that help categorize and filter issues. A good label system makes it easy to find issues and understand their status at a glance.

### Default labels

GitHub provides default labels for new repositories:

| Label | Color | Purpose |
|-------|-------|---------|
| `bug` | Red | Something isn't working |
| `documentation` | Blue | Improvements or additions to documentation |
| `duplicate` | Gray | This issue or PR already exists |
| `enhancement` | Cyan | New feature or request |
| `good first issue` | Purple | Good for newcomers |
| `help wanted` | Green | Extra attention is needed |
| `invalid` | Gray | This doesn't seem right |
| `question` | Pink | Further information is requested |
| `wontfix` | White | This will not be worked on |

### Creating custom labels

To create a custom label:

1. **Go to Issues → Labels** (or click "Labels" button on Issues page)
2. **Click "New label"**
3. **Enter label details:**
   - **Label name:** Use a prefix for organization (e.g., `priority:high`)
   - **Description:** Explain when to use this label
   - **Color:** Choose a color that groups similar labels

**Using the GitHub CLI:**

```bash
# Create a label
gh label create "priority:high" --description "Urgent issues" --color "b60205"

# Create multiple labels
gh label create "priority:medium" --color "ff9f1c"
gh label create "priority:low" --color "e4e669"
```

### Label naming conventions

We recommend using **prefixed labels** for organization:

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `type:` | Issue category | `type:bug`, `type:feature`, `type:chore` |
| `priority:` | Urgency level | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` |
| `status:` | Current state | `status:blocked`, `status:needs-review`, `status:ready` |
| `area:` | Code area | `area:frontend`, `area:backend`, `area:api`, `area:database` |
| `effort:` | Size estimate | `effort:small`, `effort:medium`, `effort:large`, `effort:epic` |

**Recommended label set to create:**

```bash
# Type labels
gh label create "type:bug" --color "d73a4a" --description "Something isn't working"
gh label create "type:feature" --color "0e8a16" --description "New feature or enhancement"
gh label create "type:chore" --color "fef2c0" --description "Maintenance or cleanup"
gh label create "type:docs" --color "d4c5f9" --description "Documentation changes"

# Priority labels
gh label create "priority:critical" --color "b60205" --description "Must be fixed immediately"
gh label create "priority:high" --color "ff9f1c" --description "Important, fix soon"
gh label create "priority:medium" --color "fbca04" --description "Normal priority"
gh label create "priority:low" --color "e4e669" --description "Nice to have"

# Status labels
gh label create "status:blocked" --color "d93f0b" --description "Blocked by another issue"
gh label create "status:needs-info" --color "cc317c" --description "Needs more information"
gh label create "status:ready" --color "0e8a16" --description "Ready to be worked on"

# Area labels (customize for your project)
gh label create "area:frontend" --color "1d76db" --description "Frontend/UI changes"
gh label create "area:backend" --color "5319e7" --description "Backend/API changes"
gh label create "area:database" --color "006b75" --description "Database changes"
```

> [!WARNING]
> Avoid creating too many labels. A good rule of thumb is 15-25 labels maximum. Too many labels lead to inconsistent usage and confusion.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 3: Group work with milestones

Milestones group issues and pull requests that share a common goal or deadline. Use milestones for:

- **Releases:** v1.0, v1.1, v2.0
- **Sprints:** Sprint 1, Sprint 2
- **Features:** "User Authentication", "Payment Integration"
- **Quarters:** Q1 2026, Q2 2026

### Creating milestones

1. **Go to Issues → Milestones**
2. **Click "New milestone"**
3. **Fill in the details:**
   - **Title:** Clear name (e.g., "v1.0 Release")
   - **Due date:** Optional deadline
   - **Description:** Goals and scope

**Using the GitHub CLI:**

```bash
# Create a milestone
gh api repos/{owner}/{repo}/milestones \
  -f title="v1.0 Release" \
  -f description="Initial public release with core features" \
  -f due_on="2026-03-01T00:00:00Z"
```

**Example milestone structure:**

```text
Milestone: v1.0 Release
Due: March 1, 2026
Description: Initial public release including:
- User authentication
- Basic profile management
- Dashboard with key metrics
```

### Assigning issues to milestones

1. **Open an issue**
2. **Click "Milestone" in the right sidebar**
3. **Select the milestone**

Or when creating an issue:

```bash
gh issue create \
  --title "Implement login page" \
  --milestone "v1.0 Release"
```

**Milestone progress tracking:**

GitHub automatically calculates milestone completion based on closed issues:

```text
v1.0 Release
████████████░░░░░░░░ 60% complete (12 of 20 issues closed)
Due by March 1, 2026
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 4: Create issue templates

Issue templates ensure contributors provide consistent, complete information. Templates are stored in `.github/ISSUE_TEMPLATE/` directory.

### Bug report template

Create `.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Bug Report
description: Report a bug or unexpected behavior
title: "[Bug]: "
labels: ["type:bug", "status:needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!

  - type: textarea
    id: description
    attributes:
      label: Bug description
      description: A clear description of what the bug is
      placeholder: Tell us what happened
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: How can we reproduce this issue?
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. Scroll down to '...'
        4. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
      description: What did you expect to happen?
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual behavior
      description: What actually happened?
    validations:
      required: true

  - type: dropdown
    id: severity
    attributes:
      label: Severity
      description: How severe is this bug?
      options:
        - Critical (app unusable)
        - High (major feature broken)
        - Medium (feature impaired)
        - Low (minor inconvenience)
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: |
        Browser, OS, app version, etc.
      placeholder: |
        - OS: macOS 14.2
        - Browser: Chrome 120
        - App version: 2.1.0

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: If applicable, add screenshots to help explain your problem

  - type: checkboxes
    id: terms
    attributes:
      label: Checklist
      options:
        - label: I have searched for existing issues
          required: true
        - label: I have provided all required information
          required: true
```

### Feature request template

Create `.github/ISSUE_TEMPLATE/feature_request.yml`:

```yaml
name: Feature Request
description: Suggest a new feature or enhancement
title: "[Feature]: "
labels: ["type:feature", "status:needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a feature! Please fill out the form below.

  - type: textarea
    id: problem
    attributes:
      label: Problem statement
      description: What problem does this feature solve?
      placeholder: I'm always frustrated when...
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: Proposed solution
      description: Describe the solution you'd like
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives considered
      description: Any alternative solutions or features you've considered?

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      description: How important is this feature to you?
      options:
        - Nice to have
        - Important
        - Critical for my use case
    validations:
      required: true

  - type: textarea
    id: context
    attributes:
      label: Additional context
      description: Add any other context, mockups, or screenshots
```

### Using template chooser

Create `.github/ISSUE_TEMPLATE/config.yml` to customize the template chooser:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Community Discussion
    url: https://github.com/org/repo/discussions
    about: Ask questions and discuss ideas
  - name: Documentation
    url: https://docs.example.com
    about: Check our documentation first
```

Now when users click "New issue", they see a chooser with your templates.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 5: Link issues and pull requests

Linking connects issues to the code changes that address them. This provides traceability and can automatically close issues when PRs are merged.

### Linking with keywords

Use these keywords in commit messages or PR descriptions to link and auto-close issues:

| Keyword | Example |
|---------|---------|
| `close`, `closes`, `closed` | `closes #123` |
| `fix`, `fixes`, `fixed` | `fixes #123` |
| `resolve`, `resolves`, `resolved` | `resolves #123` |

**In a commit message:**

```bash
git commit -m "Add login form validation

This adds client-side validation for the login form including
email format checking and password requirements.

Fixes #123"
```

**In a pull request description:**

```markdown
## Summary
This PR adds the user profile page with avatar upload functionality.

## Changes
- Added ProfilePage component
- Implemented avatar upload with size/type validation
- Added profile API endpoints

## Related Issues
Closes #45
Fixes #46
Resolves #47
```

### Manual linking

You can also link issues manually:

1. **Open an issue or PR**
2. **Click "Development" in the right sidebar** (for issues) or "Linked issues" (for PRs)
3. **Search for and select the issue/PR to link**

### Cross-repository references

Link issues across repositories using the full reference format:

```markdown
# Same organization
Relates to org/other-repo#123

# Full URL
See https://github.com/org/repo/issues/456
```

> [!TIP]
> Use "Relates to #123" for issues that are connected but should not be auto-closed.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 6: Triage and manage issues

Triage is the process of reviewing, categorizing, and prioritizing new issues. A good triage process ensures nothing falls through the cracks.

### Filtering issues

Use filters to find specific issues:

**Basic filters:**

```text
is:issue is:open                    # All open issues
is:issue is:closed                  # All closed issues
is:issue label:bug                  # Issues with bug label
is:issue -label:wontfix             # Issues without wontfix label
is:issue assignee:@me               # Issues assigned to you
is:issue no:assignee                # Unassigned issues
is:issue no:milestone               # Issues without milestone
```

**Advanced filters:**

```text
is:issue is:open label:"type:bug" label:"priority:high"
is:issue is:open no:label           # Untriaged issues
is:issue created:>2026-01-01        # Created after date
is:issue updated:<2026-01-15        # Not updated since date
is:issue comments:0                 # No comments yet
```

**Save filters as views:**

Click "Save" after applying filters to create a saved view for quick access.

### Assigning issues

Assign issues to clarify responsibility:

1. **Open the issue**
2. **Click "Assignees" in the right sidebar**
3. **Search for and select a user**

Or use the CLI:

```bash
gh issue edit 123 --add-assignee "username"
```

> [!NOTE]
> Issues can have multiple assignees. Use this for pair programming or shared responsibility.

### Closing and reopening

**Close an issue:**

- Click "Close issue" at the bottom of the issue
- Optionally add "Close as completed" or "Close as not planned"

**Using CLI:**

```bash
gh issue close 123 --comment "Fixed in PR #456"
gh issue close 123 --reason "not planned"
gh issue reopen 123
```

**Triage checklist:**

For each new issue:

- [ ] Is it a duplicate? → Close with link to original
- [ ] Is it valid? → Add appropriate labels
- [ ] Is scope clear? → Request more info if needed
- [ ] What's the priority? → Add priority label
- [ ] Who should work on it? → Assign if known
- [ ] Which release? → Add to milestone

[↑ Back to Table of Contents](#table-of-contents)

---

## Practical exercise: Set up a project

Let's put everything together by setting up a sample project.

### Exercise: Task management app

Create a repository and set up project management for a simple task management application.

**Step 1: Create the repository**

```bash
gh repo create task-manager-demo --public --description "Demo task management app"
cd task-manager-demo
```

**Step 2: Create the label taxonomy**

```bash
# Type labels
gh label create "type:bug" --color "d73a4a"
gh label create "type:feature" --color "0e8a16"
gh label create "type:chore" --color "fef2c0"

# Priority labels
gh label create "priority:high" --color "ff9f1c"
gh label create "priority:medium" --color "fbca04"
gh label create "priority:low" --color "e4e669"

# Status labels
gh label create "status:blocked" --color "d93f0b"
gh label create "status:ready" --color "0e8a16"

# Remove default labels (optional)
gh label delete "bug" --yes
gh label delete "enhancement" --yes
```

**Step 3: Create milestones**

```bash
# Create via API
gh api repos/:owner/:repo/milestones -f title="v0.1 MVP" -f description="Minimum viable product"
gh api repos/:owner/:repo/milestones -f title="v0.2 Polish" -f description="UX improvements"
```

**Step 4: Create issue templates**

Create the `.github/ISSUE_TEMPLATE/` directory and add the templates from Step 4.

**Step 5: Create sample issues**

```bash
gh issue create --title "Set up project structure" \
  --body "Create initial folder structure and configuration files" \
  --label "type:chore,priority:high" \
  --milestone "v0.1 MVP"

gh issue create --title "Implement task CRUD operations" \
  --body "Users should be able to create, read, update, and delete tasks" \
  --label "type:feature,priority:high" \
  --milestone "v0.1 MVP"

gh issue create --title "Add task filtering" \
  --body "Filter tasks by status, date, and priority" \
  --label "type:feature,priority:medium" \
  --milestone "v0.2 Polish"
```

**Step 6: Verify your setup**

```bash
gh issue list
gh label list
```

Visit your repository on GitHub to see the organized issues!

[↑ Back to Table of Contents](#table-of-contents)

---

## Troubleshooting

### Common issues

**Q: I don't see the Issues tab**

A: Issues might be disabled for the repository. Go to Settings → General → Features → check "Issues".

---

**Q: My labels disappeared**

A: Labels are repository-specific. If you switched repositories, you need to recreate labels. Consider using a script to standardize labels across repositories.

---

**Q: Keywords aren't auto-closing issues**

A: Auto-close keywords only work when:
- The PR is merged into the default branch
- The keyword format is correct (`closes #123`, not `close #123:` or `closes: #123`)
- The issue and PR are in the same repository (or you use full references)

---

**Q: I can't assign someone to an issue**

A: Users can only be assigned if they:
- Have write access to the repository, OR
- Have previously commented on the issue, OR
- Are a member of the organization (for org repos)

---

**Q: Issue templates aren't showing up**

A: Ensure:
- Templates are in `.github/ISSUE_TEMPLATE/` directory
- YAML files are valid (use a YAML validator)
- File extension is `.yml` or `.yaml`

[↑ Back to Table of Contents](#table-of-contents)

---

## Next steps

Congratulations! You now understand the fundamentals of GitHub Issues. You can:

- Create well-structured issues with clear acceptance criteria
- Organize work with labels and milestones
- Use templates for consistent issue creation
- Link issues to code changes for traceability

**Ready for more?** Continue to:

- **[Part 2: GitHub Projects and Planning](./series-part2-intermediate.md)** - Create projects, customize views, and implement sprint planning
- **[Part 3: Automation and Advanced Workflows](./series-part3-advanced.md)** - Automate project management with workflows and APIs

---

[↑ Back to Table of Contents](#table-of-contents)
