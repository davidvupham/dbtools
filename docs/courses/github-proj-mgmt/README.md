# GitHub Project Management Tutorial Series

**[← Back to Courses Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-GitHub_Projects-blue)

> [!IMPORTANT]
> **Related Docs:** [Course Overview](./course_overview.md) | [Quick Reference](./quick_reference.md) | [Glossary](./glossary.md)

## Introduction

This is a **comprehensive tutorial series** on GitHub project management, designed to take you from basic issue tracking to fully automated project workflows. Whether you are a solo developer or part of a large team, this course teaches you how to effectively plan, track, and manage work using GitHub's native tools.

### Core philosophy: Master the fundamentals, then automate

We believe you cannot effectively automate what you do not understand. Therefore, this tutorial series is structured in three progressive phases:

1. **Phase 1: The basics (Part 1)**
    - Learn GitHub Issues, labels, and milestones.
    - Create and organize issues for task tracking.
    - Understand *how* GitHub tracks work before adding complexity.

2. **Phase 2: Projects and planning (Part 2)**
    - Create GitHub Projects with custom views and fields.
    - Use board, table, and roadmap layouts effectively.
    - Implement iteration planning and team workflows.

3. **Phase 3: Automation and integration (Part 3)**
    - Configure built-in workflows and GitHub Actions.
    - Use the GraphQL API for advanced automation.
    - Integrate with external tools and create custom workflows.

## Directory structure

The `docs/courses/github-proj-mgmt/` directory is organized as follows:

```text
docs/courses/github-proj-mgmt/
├── README.md                  <-- You are here (Navigation Hub)
├── course_overview.md         <-- Learning objectives, prerequisites
├── quick_reference.md         <-- Common commands and UI shortcuts
├── glossary.md                <-- Terminology definitions
├── learning-paths/            <-- All Tutorial Content
│   ├── series-part1-beginner.md      (Basics: Issues, Labels, Milestones)
│   ├── series-part2-intermediate.md  (Projects: Views, Fields, Planning)
│   ├── series-part3-advanced.md      (Automation: Workflows, API, Actions)
│   └── tutorial-supplement-jira-migration.md  (Jira Comparison & Migration)
```

## Quick resources

- **[Course Overview](./course_overview.md)** - Learning objectives, prerequisites
- **[Quick Reference](./quick_reference.md)** - Common commands and keyboard shortcuts
- **[Glossary](./glossary.md)** - Terminology definitions

## Learning paths

Choose the path that fits your experience level.

### Recommended path (Beginner to Advanced)

*Best for: Users new to GitHub project management or those wanting a solid foundation.*

1. **[Part 1: GitHub Issues fundamentals](./learning-paths/series-part1-beginner.md)**
    - *Goal*: Learn to create, organize, and manage issues with labels and milestones.

2. **[Part 2: GitHub Projects and planning](./learning-paths/series-part2-intermediate.md)**
    - *Goal*: Create projects, customize views, and implement iteration-based workflows.

3. **[Part 3: Automation and advanced workflows](./learning-paths/series-part3-advanced.md)**
    - *Goal*: Automate project management with built-in workflows, GitHub Actions, and the GraphQL API.

---

### Fast track (Experienced users)

*Best for: Users familiar with basic issue tracking who want to jump to specific topics.*

- Already comfortable with Issues? Start with **[Part 2: Projects](./learning-paths/series-part2-intermediate.md)**
- Need automation only? Jump to **[Part 3: Automation](./learning-paths/series-part3-advanced.md)**

---

### Supplemental guides

- **[Jira vs GitHub: Comparison and Migration](./learning-paths/tutorial-supplement-jira-migration.md)**
  - Feature comparison between Jira and GitHub Projects
  - When to choose each tool
  - Step-by-step migration guide with tools and scripts
  - Integration options for using both together

---

## Method comparison: Manual vs automated

| Feature | Manual (Parts 1 & 2) | Automated (Part 3) |
| :--- | :--- | :--- |
| **Task Creation** | Manual issue creation | Auto-create from templates/triggers |
| **Status Updates** | Manual drag-and-drop | Auto-update on PR merge/close |
| **Field Population** | Manual entry | Auto-fill via workflows |
| **Cross-repo Tracking** | Manual linking | Unified project views |
| **Best For** | Small teams, learning | Large teams, enterprise |

## External resources

### Official GitHub documentation

- [GitHub Issues Documentation](https://docs.github.com/en/issues)
- [Planning and Tracking with Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Best Practices for Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
- [Quickstart for Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)

### Recommended tutorials and guides

- [Graphite: How to use GitHub for project management](https://graphite.com/guides/github-project-management-guide)
- [ZenHub: GitHub Project Management Guide](https://www.zenhub.com/github-project-management)
- [Intro to GraphQL using custom fields in GitHub Projects](https://some-natalie.dev/blog/graphql-intro/)
- [AlgoCademy: How to Use GitHub Issues to Manage Project Tasks](https://algocademy.com/blog/how-to-use-github-issues-to-manage-project-tasks/)

### Video courses

- [GitHub Skills](https://skills.github.com/) - Official interactive courses
- [LinkedIn Learning: GitHub Project Management](https://www.linkedin.com/learning/topics/github)

## Frequently asked questions

### Q: Do I need to finish Part 1 before Part 2?

**A:** Recommended but not required. Part 2 builds on concepts from Part 1 (issues, labels, milestones). If you are already comfortable creating and organizing issues, you can start with Part 2.

### Q: Can I use GitHub Projects without GitHub Actions?

**A:** Yes. Parts 1 and 2 cover manual project management workflows that work without any automation. Part 3 adds automation as an enhancement, not a requirement.

### Q: Is GitHub Projects free?

**A:** Yes. GitHub Projects is available on all GitHub plans, including free accounts. Some advanced features (like organization-level projects with certain settings) may require a paid plan.

### Q: How does this compare to Jira or other tools?

**A:** GitHub Projects is designed for teams that want project management integrated with their code repository. It is simpler than Jira but tightly integrated with pull requests, issues, and GitHub Actions. For teams already using GitHub for code, it reduces context switching. See our detailed **[Jira vs GitHub: Comparison and Migration Guide](./learning-paths/tutorial-supplement-jira-migration.md)** for a complete feature comparison, migration strategies, and integration options.

## Troubleshooting and help

- **Issues Problems**: Check [Part 1 Troubleshooting](./learning-paths/series-part1-beginner.md#troubleshooting)
- **Projects Problems**: Check [Part 2 Troubleshooting](./learning-paths/series-part2-intermediate.md#troubleshooting)
- **Automation Problems**: Check [Part 3 Troubleshooting](./learning-paths/series-part3-advanced.md#troubleshooting)
- **Community**:
  - [GitHub Community Discussions](https://github.com/orgs/community/discussions)
  - [GitHub Support](https://support.github.com/)

---

[↑ Back to Top](#github-project-management-tutorial-series)
