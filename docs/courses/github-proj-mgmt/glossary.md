# GitHub Project Management Glossary

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-GitHub_Projects-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Course Overview](./course_overview.md)

## Table of contents

- [Core concepts](#core-concepts)
- [Issues terminology](#issues-terminology)
- [Projects terminology](#projects-terminology)
- [Views and layouts](#views-and-layouts)
- [Fields and data](#fields-and-data)
- [Automation concepts](#automation-concepts)
- [API terminology](#api-terminology)

## Core concepts

| Term | Definition |
|------|------------|
| **Issue** | A trackable unit of work within a repository (bug, feature, task, or discussion) |
| **Project** | A customizable, flexible tool for planning and tracking work across issues and pull requests |
| **Pull Request (PR)** | A proposal to merge changes from one branch to another, often linked to issues |
| **Repository** | A container for project code, issues, and related files |
| **Organization** | A shared account for teams to collaborate across multiple repositories |

[↑ Back to Table of Contents](#table-of-contents)

## Issues terminology

| Term | Definition |
|------|------------|
| **Assignee** | The person responsible for completing an issue |
| **Label** | A tag used to categorize and filter issues (e.g., "bug", "enhancement") |
| **Milestone** | A collection of issues grouped toward a specific goal or deadline |
| **Issue Template** | A predefined format for creating new issues with consistent structure |
| **Sub-issue** | An issue that is a child of another issue, creating a hierarchy |
| **Linked Issue** | An issue connected to another issue or pull request using keywords or manual linking |
| **Stale Issue** | An issue that has been inactive for a defined period |
| **Triage** | The process of reviewing and categorizing new issues |

[↑ Back to Table of Contents](#table-of-contents)

## Projects terminology

| Term | Definition |
|------|------------|
| **Project Board** | A visual representation of work using columns (Kanban-style) |
| **Project Table** | A spreadsheet-like view of project items with sortable columns |
| **Project Roadmap** | A timeline view showing items plotted on a date-based axis |
| **Project Item** | Any issue, pull request, or draft item added to a project |
| **Draft Item** | A quick note or placeholder in a project that is not yet a full issue |
| **Archive** | A collection of completed or hidden items removed from active views |

[↑ Back to Table of Contents](#table-of-contents)

## Views and layouts

| Term | Definition |
|------|------------|
| **View** | A saved configuration of how project items are displayed (layout, filters, grouping) |
| **Layout** | The visual format of a view: board, table, or roadmap |
| **Board Layout** | Kanban-style columns for visualizing workflow stages |
| **Table Layout** | Spreadsheet-style rows and columns for detailed data |
| **Roadmap Layout** | Timeline view for planning work over time |
| **Filter** | Criteria to show only items matching specific conditions |
| **Group By** | Organizing items into sections based on a field value |
| **Sort** | Ordering items by a specific field (ascending or descending) |
| **Slice By** | Breaking down a view by a specific dimension (similar to pivot tables) |

[↑ Back to Table of Contents](#table-of-contents)

## Fields and data

| Term | Definition |
|------|------------|
| **Field** | A data attribute attached to project items (built-in or custom) |
| **Built-in Field** | Default fields provided by GitHub (Title, Assignees, Labels, Milestone, Repository) |
| **Custom Field** | User-defined fields added to a project |
| **Text Field** | A custom field for free-form text input |
| **Number Field** | A custom field for numeric values (effort points, estimates) |
| **Date Field** | A custom field for date values |
| **Single Select** | A custom field with predefined options (one selection allowed) |
| **Iteration Field** | A special field for time-boxed work periods (sprints) |
| **Status Field** | A single-select field specifically for workflow states |

[↑ Back to Table of Contents](#table-of-contents)

## Automation concepts

| Term | Definition |
|------|------------|
| **Workflow** | An automated process that performs actions based on triggers |
| **Built-in Workflow** | Pre-configured automations provided by GitHub Projects |
| **Trigger** | An event that starts a workflow (e.g., issue created, PR merged) |
| **Action** | A task performed by a workflow (e.g., set status, add to project) |
| **GitHub Actions** | GitHub's CI/CD platform that can be used to automate project tasks |
| **Workflow File** | A YAML file defining a GitHub Actions workflow (`.github/workflows/`) |

[↑ Back to Table of Contents](#table-of-contents)

## API terminology

| Term | Definition |
|------|------------|
| **REST API** | GitHub's traditional HTTP-based API for programmatic access |
| **GraphQL API** | GitHub's query language API offering flexible, precise data retrieval |
| **Query** | A GraphQL operation to read data |
| **Mutation** | A GraphQL operation to modify data |
| **Node ID** | A unique identifier for GitHub objects used in the GraphQL API |
| **Personal Access Token (PAT)** | A credential for authenticating API requests |
| **Scope** | Permissions granted to a token (e.g., `project`, `read:project`) |
| **Rate Limit** | The maximum number of API requests allowed in a time period |
| **Webhook** | An HTTP callback that sends data to external services when events occur |
| **GitHub CLI (gh)** | Command-line tool for interacting with GitHub, including projects |

[↑ Back to Table of Contents](#table-of-contents)

---

## Quick reference: Common terms by part

### Part 1 terms

Issue, Label, Milestone, Assignee, Template, Linked Issue, Triage

### Part 2 terms

Project, View, Layout, Board, Table, Roadmap, Field, Custom Field, Iteration, Filter, Group By, Status

### Part 3 terms

Workflow, Trigger, Action, GitHub Actions, GraphQL, Query, Mutation, Node ID, Token, Webhook

---

[↑ Back to Table of Contents](#table-of-contents)
