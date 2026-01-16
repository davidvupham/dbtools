# GitHub for Project Management: A Practical Tutorial

This tutorial shows how to use GitHub as a lightweight-yet-powerful project management platform. You’ll set up a workflow that supports planning, tracking, collaboration, and delivery—without leaving your repo.


## Who this is for

- Teams managing work directly in code repositories
- Project leads who need visibility without heavy tooling
- Individual contributors who want clear prioritization and status


## Outcomes

By the end, you will:

- Structure your repo for planning and delivery
- Track work with Issues, Labels, Milestones, Projects
- Run work via Pull Requests, Reviews, and CI Checks
- Automate routines with Actions, Templates, and Saved Replies
- Report progress using Boards, Insights, and Releases

---

## 1) Repository Setup

### 1.1 Core structure

Create a clear, discoverable structure:

- docs/: docs, tutorials, runbooks, decision records
- src/ or services/: source code per component
- tests/: unit/integration tests
- .github/: repository configuration and templates

Recommended files:

- README.md: overview, setup, quick start
- CONTRIBUTING.md: how to propose changes, conventions
- CODEOWNERS: ownership for paths/features
- SECURITY.md: how to report vulnerabilities
- LICENSE: licensing terms

### 1.2 Branching and protection

- Default: `main` is release-ready; use short-lived feature branches.
- Enable branch protection (Settings → Branches):
  - Require PR reviews (e.g., 1–2 approvals)
  - Require status checks (CI green) before merge
  - Dismiss stale reviews on new commits
  - Require signed commits (optional)

---

## 2) Plan with Issues, Labels, Milestones

### 2.1 Issue types

Use templates to standardize reporting and intake. Common types:

- Feature: user story or capability
- Bug: defect report with reproduction steps
- Task/Chore: maintenance or refactor
- Documentation: docs or knowledge updates

Add templates in `.github/ISSUE_TEMPLATE/`:

- feature.md, bug.md, task.md, docs.md

### 2.2 Labels

Define a small, stable set:

- Type: `type:feature`, `type:bug`, `type:docs`, `type:task`
- Priority: `P0`, `P1`, `P2`
- Status: `status:backlog`, `status:in-progress`, `status:blocked`, `status:needs-review`
- Area: `area:database`, `area:api`, `area:frontend`, etc.

Tips:

- Keep ≤ 30 labels; prefer prefixes for clarity
- Document label meanings in `CONTRIBUTING.md`

### 2.3 Milestones

Use Milestones for time-boxed goals:

- Examples: `2025-Q1`, `v1.0 Launch`, `HammerDB Benchmark Sprint`
- Assign due dates; track Burndown under Milestones → `Insights`

---

## 3) Organize with GitHub Projects (Boards)

Projects (beta) provide Kanban boards and custom views.

### 3.1 Create a project

- Go to your org/user → Projects → New project (beta)
- Choose table or board view; connect to repo issues/PRs

### 3.2 Suggested fields

- Status: Backlog → In Progress → In Review → Done
- Priority: P0/P1/P2
- Size: S/M/L or T-shirt sizes
- Owner: assignee display
- Target: Milestone or Release

### 3.3 Views

- Board: status workflow
- Table: sortable fields
- Sprint: filter by Milestone or date range
- Bugs: filter `type:bug`

Automations:

- Auto-add new issues from selected repos
- Move to `In Review` when PR opens; `Done` when PR merges

---

## 4) Execute with Pull Requests

### 4.1 PR lifecycle

- Create feature branch: `feature/<area>-<short-desc>`
- Open PR early (draft) to enable discussion
- Link PR to Issue (`Fixes #123`) for auto-close on merge
- Request reviewers via CODEOWNERS or manual selection

### 4.2 Reviews

- Use structured checklist:
  - Scope: aligned to Issue; no hidden work
  - Tests: unit/integration added or updated
  - Security & secrets: no secrets or risky changes
  - Docs: README or user-facing docs updated
- Prefer comments tied to lines; resolve threads before merge

### 4.3 Merge strategy

- Squash commits for clean history (recommended)
- Rebase if you need linear history; avoid merge commits unless necessary

---

## 5) Automate with GitHub Actions

### 5.1 CI essentials

Add workflows in `.github/workflows/`:

- `ci.yml`: run tests, lint, build on push/PR
- `codeql.yml`: security code scanning
- `release.yml`: tag releases, build artifacts

Example `ci.yml` skeleton:
```yaml
name: CI
on:
  pull_request:
  push:
    branches: [ main ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt || pip install -e .
      - run: pytest -q
```

### 5.2 Policies and gates

- Require CI green before merge via branch protection
- Add secret scanning and Dependabot alerts

---

## 6) Templates, Discussions, Saved Replies

### 6.1 Issue/PR templates

- Standardize intake and reviews
- Include acceptance criteria, definition of done, test plan

### 6.2 Discussions

- Enable at repo level for ideation, Q&A, RFCs
- Convert Discussion to Issue when ready to execute

### 6.3 Saved replies

- Use for common responses: reproduction requests, triage outcomes, onboarding

---

## 7) Reporting and Insights

### 7.1 Boards and filters

- Review weekly: Backlog, In Progress, Blocked
- Use filters like `label:P0` `assignee:@me` `milestone:v1.0`

### 7.2 Milestones and burndown

- Track open vs closed; adjust scope to hit dates

### 7.3 Releases and changelogs

- Use GitHub Releases with tags (e.g., `v1.2.0`)
- Auto-generate notes from merged PRs; link to artifacts

### 7.4 Code review health

- Insights → Pull requests: time-to-merge, review count
- Look for PRs lingering > 5 days; rebalance reviewers

---

## 8) Security and Compliance

- Enable `CODEOWNERS` for sensitive areas
- Turn on Secret scanning and Push protection
- Use `CODEQL` and `Dependabot` for static analysis and dependencies
- Require 2FA for org members; limit admin permissions
- Store secrets in GitHub Actions Secrets or Vault, never in code

---

## 9) Scaling Patterns

- Monorepo: use labels/areas to partition ownership; CI matrices
- Multi-repo: standardize templates and workflows across repos via org-level defaults
- Iteration cadences: weekly triage + sprint boards; quarterly milestones

---

## 10) Quick Start Checklist

- Create `.github/ISSUE_TEMPLATE/*` and `PULL_REQUEST_TEMPLATE.md`
- Define labels, priorities, areas
- Set branch protections and required checks
- Create a Project board with Status, Priority, Owner
- Add CI workflow and CodeQL
- Document contribution flow in `CONTRIBUTING.md`

---

## Appendix: Useful Snippets

### Autoclose issues via PR description

- Include: `Fixes #<issue-number>` or `Closes #<issue-number>`

### Link PR to project automatically (example)

```yaml
name: Link PR to Project
on:
  pull_request:
    types: [opened]
jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/orgs/<org>/projects/<id>
          github-token: ${{ secrets.GH_TOKEN }}
```

### Sample label set (CSV)

 ```csv
name,color,description
P0,ff0000,Highest priority
P1,ffa500,High priority
P2,ffd700,Medium priority
status:backlog,7f8c8d,Not started
status:in-progress,2980b9,Work in progress
status:blocked,8e44ad,Blocked by dependency
status:needs-review,16a085,Ready for review
type:bug,e74c3c,Defect
type:feature,2ecc71,New capability
type:docs,3498db,Documentation
area:database,1abc9c,Database related
```

---

## Adoption Tips

- Start small: use Issues + PRs + CI first
- Add Projects and Milestones once labels stabilize
- Review and prune labels quarterly
- Keep PRs small (≤ 300 LoC) to speed review
- Write decisions in `docs/` to capture context
