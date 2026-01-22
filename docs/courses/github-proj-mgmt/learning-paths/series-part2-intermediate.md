# Tutorial Part 2: GitHub Projects and Planning

<!-- markdownlint-disable MD013 -->

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Level](https://img.shields.io/badge/Level-Intermediate-yellow)

> [!IMPORTANT]
> **Related Docs:** [Part 1: Issues](./series-part1-beginner.md) | [Part 3: Automation](./series-part3-advanced.md) | [Quick Reference](../quick_reference.md)

## Table of contents

- [Introduction](#introduction)
  - [Goals of Part 2](#goals-of-part-2)
  - [What you'll learn](#what-youll-learn)
  - [Prerequisites](#prerequisites)
- [Understanding GitHub Projects](#understanding-github-projects)
  - [What is a project?](#what-is-a-project)
  - [Project vs repository issues](#project-vs-repository-issues)
  - [Project scopes](#project-scopes)
- [Step 1: Create your first project](#step-1-create-your-first-project)
  - [Creating from the web interface](#creating-from-the-web-interface)
  - [Creating from the CLI](#creating-from-the-cli)
- [Step 2: Add items to your project](#step-2-add-items-to-your-project)
  - [Adding existing issues](#adding-existing-issues)
  - [Creating draft items](#creating-draft-items)
  - [Converting drafts to issues](#converting-drafts-to-issues)
- [Step 3: Configure custom fields](#step-3-configure-custom-fields)
  - [Built-in fields](#built-in-fields)
  - [Creating custom fields](#creating-custom-fields)
  - [Field types explained](#field-types-explained)
- [Step 4: Create views](#step-4-create-views)
  - [Board layout (Kanban)](#board-layout-kanban)
  - [Table layout (Spreadsheet)](#table-layout-spreadsheet)
  - [Roadmap layout (Timeline)](#roadmap-layout-timeline)
  - [Saving and naming views](#saving-and-naming-views)
- [Step 5: Filter, sort, and group](#step-5-filter-sort-and-group)
  - [Filtering syntax](#filtering-syntax)
  - [Sorting items](#sorting-items)
  - [Grouping by field](#grouping-by-field)
  - [Slice by dimension](#slice-by-dimension)
- [Step 6: Iteration planning](#step-6-iteration-planning)
  - [Creating iteration fields](#creating-iteration-fields)
  - [Planning sprints](#planning-sprints)
  - [Tracking velocity](#tracking-velocity)
- [Step 7: Cross-repository projects](#step-7-cross-repository-projects)
  - [Organization-level projects](#organization-level-projects)
  - [Adding items from multiple repos](#adding-items-from-multiple-repos)
- [Practical exercise: Sprint planning board](#practical-exercise-sprint-planning-board)
- [Troubleshooting](#troubleshooting)
- [Next steps](#next-steps)

---

## Introduction

This tutorial is **Part 2** of a comprehensive series on GitHub project management. Part 2 focuses on **GitHub Projects**—the flexible planning tool that brings together issues from one or more repositories into customizable views.

> [!NOTE]
> This tutorial covers **GitHub Projects** (the current version, sometimes called "Projects V2"), not the older "classic" project boards. Classic projects are deprecated and being phased out.

### Goals of Part 2

By the end of Part 2, you will have:

1. **Created a GitHub Project** with multiple views for different stakeholders
2. **Configured custom fields** for priority, effort estimation, and status tracking
3. **Built a Kanban board** for daily workflow management
4. **Created a table view** for sprint planning
5. **Set up a roadmap view** for timeline visualization
6. **Implemented iteration planning** for sprint-based development

**The end result:** A fully configured project with multiple views, custom fields, and iteration tracking ready for team collaboration.

### What you'll learn

In this tutorial, you'll learn:

- **Project fundamentals:**
  - Differences between projects and repository issue lists
  - User vs organization projects
  - Adding and managing project items

- **Views and layouts:**
  - Board layout for Kanban workflows
  - Table layout for detailed planning
  - Roadmap layout for timeline visualization

- **Custom fields:**
  - Single-select fields for status and priority
  - Number fields for effort estimation
  - Date fields for deadlines
  - Iteration fields for sprint planning

- **Planning techniques:**
  - Filtering and sorting for focus
  - Grouping for organization
  - Iteration planning for sprints

### Prerequisites

Before starting this tutorial, you should have:

- **Completed Part 1** or equivalent knowledge of GitHub Issues
- **A GitHub account** with a repository containing some issues
- **Basic understanding of** Kanban or Agile workflows (helpful but not required)

[↑ Back to Table of Contents](#table-of-contents)

---

## Understanding GitHub Projects

### What is a project?

A **GitHub Project** is a flexible planning tool that:

- **Aggregates items** from one or more repositories
- **Provides multiple views** of the same data (board, table, roadmap)
- **Supports custom fields** for tracking any data you need
- **Enables automation** for keeping status up to date

Think of a project as a customizable spreadsheet that is directly connected to your issues and pull requests.

### Project vs repository issues

| Feature | Repository Issues | GitHub Project |
|---------|-------------------|----------------|
| **Scope** | Single repository | Multiple repositories |
| **Views** | Single list | Board, table, roadmap |
| **Custom fields** | Labels only | Any field type |
| **Iteration tracking** | No | Yes |
| **Filtering** | Basic | Advanced |

**When to use Projects:**

- Managing work across multiple repositories
- Sprint or iteration planning
- Creating different views for different audiences
- Tracking custom data (effort, priority, team)

### Project scopes

Projects can be created at two levels:

| Scope | Owner | Best For |
|-------|-------|----------|
| **User project** | Your personal account | Personal work, side projects |
| **Organization project** | An organization | Team work, cross-repo planning |

> [!TIP]
> For team work, always create organization-level projects. They are shared with all organization members and can pull issues from any repo in the organization.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 1: Create your first project

### Creating from the web interface

**For a user project:**

1. Click your **profile picture** → **Your projects**
2. Click **"New project"**
3. Choose a **template** or start from scratch:
   - **Table**: Spreadsheet-like default view
   - **Board**: Kanban-style default view
   - **Roadmap**: Timeline default view
4. Give your project a **name** and **description**
5. Click **"Create project"**

**For an organization project:**

1. Go to your **organization page**
2. Click the **"Projects" tab**
3. Click **"New project"**
4. Choose a template and configure as above

### Creating from the CLI

```bash
# Create a user project
gh project create --owner "@me" --title "My Development Tasks"

# Create an organization project
gh project create --owner "my-org" --title "Q1 2026 Sprint Board"
```

**List your projects:**

```bash
# User projects
gh project list

# Organization projects
gh project list --owner "my-org"
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 2: Add items to your project

Projects contain **items**. Items can be:

- **Issues** from any repository
- **Pull requests** from any repository
- **Draft items** (notes that aren't yet issues)

### Adding existing issues

**From the project:**

1. Open your project
2. Click **"+ Add item"** at the bottom of a column (board) or table
3. **Paste an issue URL** or search for issues
4. Select the issue and press **Enter**

**From an issue:**

1. Open any issue
2. Click **"Projects"** in the right sidebar
3. Select the project to add it to

**Using the CLI:**

```bash
# Add a specific issue
gh project item-add PROJECT_NUMBER --owner OWNER --url "https://github.com/org/repo/issues/123"

# Example
gh project item-add 1 --owner "@me" --url "https://github.com/myorg/myrepo/issues/45"
```

**Bulk adding issues:**

```bash
# Add all open issues from a repository
gh issue list --repo org/repo --json url -q '.[].url' | while read url; do
  gh project item-add 1 --owner "org" --url "$url"
done
```

### Creating draft items

Draft items are quick notes that exist only in the project (not in any repository).

1. Click **"+ Add item"**
2. Type your note text (don't paste a URL)
3. Press **Enter**

Drafts appear with a different icon and can be converted to issues later.

### Converting drafts to issues

1. Open the draft item
2. Click **"Convert to issue"**
3. Select the **repository** for the new issue
4. The issue is created and linked to the project item

> [!TIP]
> Use drafts for quick brainstorming during planning sessions, then convert the ones you'll actually work on to issues.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 3: Configure custom fields

Custom fields let you track any data on your project items.

### Built-in fields

Every project has these built-in fields:

| Field | Description |
|-------|-------------|
| **Title** | Issue/PR title |
| **Assignees** | Who is assigned |
| **Status** | Workflow status (customizable) |
| **Labels** | Issue labels |
| **Linked Pull Requests** | Connected PRs |
| **Milestone** | Issue milestone |
| **Repository** | Source repository |
| **Reviewers** | PR reviewers |

### Creating custom fields

1. In your project, click **"+"** in the table header (or use the column menu)
2. Click **"New field"**
3. Configure the field:
   - **Name**: Field name
   - **Field type**: Select the type
   - **Options**: Configure type-specific options

**Using the CLI:**

```bash
# List existing fields
gh project field-list PROJECT_NUMBER --owner OWNER

# Create a single-select field
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "PROJECT_ID"
    dataType: SINGLE_SELECT
    name: "Priority"
    singleSelectOptions: [
      {name: "Critical", color: RED}
      {name: "High", color: ORANGE}
      {name: "Medium", color: YELLOW}
      {name: "Low", color: GREEN}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}'
```

### Field types explained

| Type | Use Case | Example |
|------|----------|---------|
| **Text** | Free-form notes | "Notes", "Dependencies" |
| **Number** | Quantities, estimates | "Story Points", "Hours" |
| **Date** | Deadlines, targets | "Due Date", "Start Date" |
| **Single Select** | Predefined options (one) | "Priority", "Status", "Team" |
| **Iteration** | Time-boxed periods | "Sprint", "Cycle" |

**Recommended custom fields:**

| Field | Type | Options |
|-------|------|---------|
| **Priority** | Single Select | Critical, High, Medium, Low |
| **Effort** | Number | Story points (1, 2, 3, 5, 8, 13) |
| **Team** | Single Select | Frontend, Backend, Design, DevOps |
| **Due Date** | Date | — |
| **Sprint** | Iteration | Configure sprint length |

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 4: Create views

Views let you visualize the same project data in different ways. Each view has its own layout, filters, grouping, and sorting.

### Board layout (Kanban)

The board layout displays items in columns, perfect for visualizing workflow stages.

**Creating a board view:**

1. Click **"+ New view"** (tab bar)
2. Select **"Board"**
3. Name it (e.g., "Sprint Board")

**Configuring columns:**

Columns are based on a **single-select field** (usually Status).

1. Click the **column menu** (⋮)
2. Add, rename, or reorder columns
3. Set column colors for visual distinction

**Example board setup:**

```text
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Backlog   │     Todo    │  In Progress │    Done     │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ ▢ Feature A │ ▢ Bug fix   │ ▢ Feature B │ ✓ Setup     │
│ ▢ Feature C │ ▢ Docs      │             │ ✓ API work  │
│ ▢ Research  │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Drag and drop** items between columns to update status.

### Table layout (Spreadsheet)

The table layout shows items in rows with sortable columns, ideal for detailed planning.

**Creating a table view:**

1. Click **"+ New view"**
2. Select **"Table"**
3. Name it (e.g., "Sprint Planning")

**Configuring columns:**

1. Click **"+"** in the header to add fields as columns
2. Drag column headers to reorder
3. Click column header to sort

**Example table setup:**

```text
| Title          | Status      | Priority | Effort | Assignee | Sprint   |
|----------------|-------------|----------|--------|----------|----------|
| Feature A      | Backlog     | High     | 5      | @alice   | Sprint 3 |
| Bug fix        | Todo        | Critical | 2      | @bob     | Sprint 2 |
| Feature B      | In Progress | Medium   | 8      | @charlie | Sprint 2 |
```

### Roadmap layout (Timeline)

The roadmap layout shows items on a timeline, useful for communicating plans to stakeholders.

**Creating a roadmap view:**

1. Click **"+ New view"**
2. Select **"Roadmap"**
3. Name it (e.g., "Release Roadmap")

**Configuring the timeline:**

- **Date field**: Select which date field determines item position
- **Zoom level**: Day, week, month, quarter
- **Group by**: Optionally group rows by a field

**Requirements for roadmap:**

- Items need a **date field** value to appear on the timeline
- Use **Iteration** field for sprint-based roadmaps

### Saving and naming views

Each view is saved with its configuration:

1. Make your changes (layout, filters, sorting)
2. Click the **view name** in the tab
3. Select **"Save changes"** or **"Save as new view"**

**Recommended view setup:**

| View Name | Layout | Purpose |
|-----------|--------|---------|
| Sprint Board | Board | Daily standup, workflow visibility |
| Backlog | Table | Grooming, prioritization |
| Sprint Planning | Table | Iteration planning, assignments |
| Roadmap | Roadmap | Stakeholder communication |
| My Items | Table | Personal filtered view |

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 5: Filter, sort, and group

Transform views to show exactly what you need.

### Filtering syntax

Click the **filter icon** or type in the filter bar:

**Basic filters:**

```text
status:Todo                    # Items with status "Todo"
status:"In Progress"           # Status with spaces (use quotes)
assignee:@me                   # Items assigned to you
assignee:username              # Items assigned to specific user
no:assignee                    # Unassigned items
label:bug                      # Items with specific label
priority:High                  # Custom field value
```

**Combining filters:**

```text
status:Todo,Doing              # Multiple values (OR)
status:Todo priority:High      # Multiple fields (AND)
-status:Done                   # Negation (NOT)
-no:assignee                   # Has assignee
```

**Date and iteration filters:**

```text
iteration:@current             # Current iteration
iteration:@next                # Next iteration
iteration:@previous            # Previous iteration
due:@today                     # Due today
due:>@today                    # Due after today
due:<2026-02-01                # Due before date
```

### Sorting items

1. Click a **column header** to sort by that field
2. Click again to reverse sort order
3. Shift+click to add secondary sort

Or use the **sort menu**:

1. Click **"Sort"** in the view menu
2. Select field and direction
3. Add additional sort levels

### Grouping by field

Group items into sections based on a field value:

1. Click **"Group by"** in the view menu
2. Select a field (e.g., Assignee, Priority, Team)

**Example grouped table:**

```text
▼ Priority: High
  | Feature A | Todo | 5 pts |
  | Bug fix   | Done | 2 pts |

▼ Priority: Medium
  | Feature B | In Progress | 8 pts |
  | Docs      | Todo        | 1 pt  |

▼ Priority: Low
  | Research  | Backlog | 3 pts |
```

### Slice by dimension

Slice breaks down the view by a dimension (similar to pivot tables):

1. Click **"Slice by"** in the view menu
2. Select a field (e.g., Sprint, Team)
3. Toggle between slices using the side panel

This is useful for seeing the same project from different perspectives without creating multiple views.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 6: Iteration planning

Iterations are time-boxed periods for planning work (sprints, cycles).

### Creating iteration fields

1. Add a new field of type **"Iteration"**
2. Configure iteration settings:
   - **Start date**: When iterations begin
   - **Duration**: Length of each iteration (1-4 weeks typical)

**Example configuration:**

```text
Field: Sprint
Start: January 6, 2026
Duration: 2 weeks

Iterations:
- Sprint 1: Jan 6 - Jan 19
- Sprint 2: Jan 20 - Feb 2
- Sprint 3: Feb 3 - Feb 16
- Sprint 4: Feb 17 - Mar 2
```

**Adding breaks:**

You can add breaks between iterations for holidays or planning periods:

1. Open iteration field settings
2. Click **"Add break"** between iterations
3. Configure break dates

### Planning sprints

**Sprint planning workflow:**

1. **Create a "Sprint Planning" table view** filtered to:
   - `iteration:@next no:assignee` (unplanned items)

2. **Sort by priority** to see most important items first

3. **Assign iterations** by:
   - Dragging items to the Sprint column value
   - Or editing the field directly

4. **Check capacity** by grouping by assignee and summing effort points

**Useful views for iteration planning:**

| View | Filter | Purpose |
|------|--------|---------|
| Current Sprint | `iteration:@current` | What we're working on now |
| Sprint Backlog | `iteration:@next status:Backlog` | Planning next sprint |
| Unplanned | `no:iteration -status:Done` | Items not yet scheduled |

### Tracking velocity

Velocity = story points completed per iteration.

**Manual tracking:**

1. Create a table view filtered to `iteration:@previous status:Done`
2. Sum the Effort field
3. Track over time in a spreadsheet

**Automated tracking:**

Part 3 covers automating velocity tracking with GitHub Actions.

> [!TIP]
> Start with 2-week iterations. Shorter iterations provide faster feedback but require more frequent planning. Adjust based on your team's needs.

[↑ Back to Table of Contents](#table-of-contents)

---

## Step 7: Cross-repository projects

One of the most powerful features of GitHub Projects is aggregating work from multiple repositories.

### Organization-level projects

Organization projects can include items from any repository in the organization.

**Benefits:**

- Single view of all team work
- Cross-team coordination
- Consistent workflow across repos
- Shared custom fields

**Creating an organization project:**

1. Go to **organization → Projects**
2. Create a new project
3. Add items from any organization repository

### Adding items from multiple repos

**Method 1: Direct URL**

Paste the full issue URL when adding items:

```text
https://github.com/org/frontend-repo/issues/123
https://github.com/org/backend-repo/issues/456
https://github.com/org/mobile-repo/issues/789
```

**Method 2: Search across repos**

1. Click **"+ Add item"**
2. Type your search query
3. Results include all repos you have access to

**Method 3: Automation**

Configure automations to auto-add new issues from specific repos (covered in Part 3).

**Using the Repository field:**

When working with cross-repo projects, add the **Repository** column to your table view to see which repo each item belongs to.

**Example multi-repo project:**

```text
| Title          | Repository   | Status      | Team     |
|----------------|--------------|-------------|----------|
| Login API      | backend      | In Progress | Backend  |
| Login UI       | frontend     | Todo        | Frontend |
| Push Notif     | mobile       | Backlog     | Mobile   |
| Auth Docs      | docs         | Todo        | Docs     |
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Practical exercise: Sprint planning board

Let's build a complete sprint planning system.

### Exercise: Team sprint board

**Step 1: Create the project**

```bash
gh project create --owner "@me" --title "Team Sprint Board"
```

**Step 2: Configure custom fields**

Create these fields in the project settings:

| Field | Type | Options |
|-------|------|---------|
| Status | Single Select | Backlog, Todo, In Progress, Review, Done |
| Priority | Single Select | Critical, High, Medium, Low |
| Effort | Number | (for story points) |
| Team | Single Select | Frontend, Backend, DevOps |
| Sprint | Iteration | 2-week iterations starting today |

**Step 3: Create views**

Create these views:

1. **Sprint Board** (Board)
   - Group by: Status
   - Filter: `iteration:@current`

2. **Sprint Planning** (Table)
   - Columns: Title, Priority, Effort, Assignee, Sprint
   - Sort: Priority descending
   - Filter: (none, show all)

3. **My Work** (Table)
   - Filter: `assignee:@me -status:Done`
   - Sort: Priority descending

4. **Team Roadmap** (Roadmap)
   - Date field: Sprint
   - Group by: Team

**Step 4: Add sample items**

Create test issues or add drafts:

```text
- [High] Implement user authentication (8 pts, Backend)
- [High] Design login screen (3 pts, Frontend)
- [Medium] Set up CI pipeline (5 pts, DevOps)
- [Medium] Add password reset (5 pts, Backend)
- [Low] Update documentation (2 pts, Docs)
```

**Step 5: Plan a sprint**

1. Open Sprint Planning view
2. Filter: `no:iteration`
3. Assign items to the current sprint until you reach capacity (~20-30 points for a small team)
4. Switch to Sprint Board to visualize the workflow

**Step 6: Simulate workflow**

Move items across the board as if you were working:
- Drag "Design login screen" to "In Progress"
- Drag "Set up CI pipeline" to "Review"
- Drag a completed item to "Done"

Observe how the views update automatically.

[↑ Back to Table of Contents](#table-of-contents)

---

## Troubleshooting

### Common issues

**Q: I can't add items from another repository**

A: Check that:
- For user projects: You have read access to the repository
- For org projects: The repository is in the same organization
- The issue/PR URL is correct and accessible

---

**Q: Custom fields don't appear on items**

A: Custom fields are project-specific. They only appear when viewing items within the project. The fields are stored on the project, not on the issues themselves.

---

**Q: Iteration dates are wrong**

A: Iterations are calculated from the start date you set. To adjust:
1. Open field settings
2. Modify the start date or duration
3. Add breaks for holidays if needed

---

**Q: Changes aren't saving**

A: Click **"Save changes"** in the view dropdown after modifying filters, sorts, or grouping. Unsaved changes are indicated by a dot on the view tab.

---

**Q: Roadmap shows no items**

A: Items need a date-based field value to appear on the roadmap. Ensure:
- You have a Date or Iteration field configured
- Items have values in that field
- The roadmap is configured to use that field

---

**Q: Board columns don't match my status options**

A: The board layout uses a single-select field for columns. To modify columns:
1. Edit the Status field options
2. Or switch to a different field for the board grouping

[↑ Back to Table of Contents](#table-of-contents)

---

## Next steps

You now have a fully functional GitHub Project with:

- Custom fields for tracking priority, effort, and team
- Multiple views for different purposes (board, table, roadmap)
- Iteration planning for sprint management
- Filtering and grouping for finding what you need

**Ready for more?** Continue to:

- **[Part 3: Automation and Advanced Workflows](./series-part3-advanced.md)** - Automate project management with built-in workflows, GitHub Actions, and the GraphQL API

**Additional resources:**

- [GitHub Docs: Planning and tracking with Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Docs: Best practices for Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)

---

[↑ Back to Table of Contents](#table-of-contents)
