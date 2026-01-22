# GitHub Project Management Course Overview

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-GitHub_Projects-blue)

> [!IMPORTANT]
> **Related Docs:** [Quick Reference](./quick_reference.md) | [Glossary](./glossary.md)

## Table of contents

- [Course description](#course-description)
- [Learning objectives](#learning-objectives)
- [Target audience](#target-audience)
- [Prerequisites](#prerequisites)
- [Course structure](#course-structure)
- [What you will build](#what-you-will-build)
- [Support](#support)

## Course description

This comprehensive course teaches project management using GitHub's native tools: Issues, Projects, and automation workflows. You'll learn to plan and track work for individuals, teams, and organizations, integrating project management directly with your code repository.

By the end of this course, you will be able to manage software development projects entirely within GitHub, from initial planning through release.

[↑ Back to Table of Contents](#table-of-contents)

## Learning objectives

By completing this course, you will be able to:

### Part 1: Fundamentals

1. **Create and manage GitHub Issues** with clear titles, descriptions, and acceptance criteria
2. **Organize work with labels** using consistent naming conventions and color schemes
3. **Group issues into milestones** to track progress toward specific goals
4. **Use issue templates** to standardize bug reports and feature requests
5. **Link issues and pull requests** for traceability

### Part 2: Projects and planning

6. **Create GitHub Projects** at the repository and organization level
7. **Design custom views** using table, board, and roadmap layouts
8. **Define custom fields** including single-select, iteration, number, and date fields
9. **Plan iterations and sprints** using built-in iteration tracking
10. **Filter, sort, and group** project items for different stakeholders

### Part 3: Automation

11. **Configure built-in workflows** for automatic status updates
12. **Create GitHub Actions** to automate project management tasks
13. **Use the GraphQL API** to query and mutate project data
14. **Integrate external tools** with GitHub Projects
15. **Implement advanced patterns** for enterprise-scale project management

[↑ Back to Table of Contents](#table-of-contents)

## Target audience

This course is designed for:

- **Developers** who want to track their own work and contribute to team projects
- **Team leads** responsible for planning and coordinating team work
- **Project managers** transitioning to GitHub-based workflows
- **DevOps engineers** implementing CI/CD with project tracking
- **Open source maintainers** managing community contributions

[↑ Back to Table of Contents](#table-of-contents)

## Prerequisites

Before starting this course, you should have:

- **A GitHub account** (free tier is sufficient)
  - Create one at [github.com/signup](https://github.com/signup)

- **Basic GitHub familiarity**
  - Understanding of repositories
  - Ability to navigate the GitHub web interface
  - Basic knowledge of commits and pull requests

- **For Part 3 (Automation)**:
  - Basic understanding of YAML syntax
  - Familiarity with GitHub Actions concepts (helpful but not required)
  - Command line basics for API examples

**No prior project management tool experience required!** This course explains all concepts from the ground up.

[↑ Back to Table of Contents](#table-of-contents)

## Course structure

| Part | Title | Topics |
|------|-------|--------|
| **1** | [GitHub Issues Fundamentals](./learning-paths/series-part1-beginner.md) | Issues, labels, milestones, templates, linking |
| **2** | [GitHub Projects and Planning](./learning-paths/series-part2-intermediate.md) | Projects, views, custom fields, iterations, filtering |
| **3** | [Automation and Advanced Workflows](./learning-paths/series-part3-advanced.md) | Built-in workflows, GitHub Actions, GraphQL API, integrations |

### Supplemental guides

- [Jira vs GitHub: Comparison and Migration](./learning-paths/tutorial-supplement-jira-migration.md) - Feature comparison, migration tools, integration options

### Skill progression

```text
Part 1 (Beginner)          Part 2 (Intermediate)       Part 3 (Advanced)
─────────────────          ─────────────────────       ─────────────────
Issues                     Projects                    Built-in Workflows
Labels                     Table View                  GitHub Actions
Milestones        ──►      Board View          ──►     GraphQL API
Templates                  Roadmap View                Integrations
Linking                    Custom Fields               Enterprise Patterns
                           Iterations
                           Filtering & Grouping
```

[↑ Back to Table of Contents](#table-of-contents)

## What you will build

Throughout this course, you will build a complete project management system for a sample software project:

### Part 1 deliverables

- Issue templates for bugs, features, and documentation
- A label taxonomy with consistent naming and colors
- Milestones for release planning
- Linked issues and pull requests

### Part 2 deliverables

- A GitHub Project with multiple views:
  - **Team Board**: Kanban-style view for daily standups
  - **Sprint Table**: Tabular view for iteration planning
  - **Roadmap**: Timeline view for stakeholder communication
- Custom fields for priority, effort estimation, and team assignment
- Iteration configuration for sprint planning

### Part 3 deliverables

- Automated workflows that:
  - Add new issues/PRs to the project automatically
  - Update status when PRs are merged
  - Set due dates based on iteration
  - Archive completed items
- A GitHub Action workflow for cross-repository project management
- GraphQL queries for custom reporting

[↑ Back to Table of Contents](#table-of-contents)

## Support

- See each tutorial's troubleshooting section for common issues
- **Community Resources**:
  - [GitHub Community Discussions](https://github.com/orgs/community/discussions)
  - [GitHub Skills](https://skills.github.com/) - Interactive learning
  - [GitHub Docs](https://docs.github.com/en/issues) - Official documentation

---

[↑ Back to Table of Contents](#table-of-contents)
