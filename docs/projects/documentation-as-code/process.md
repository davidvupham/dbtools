# Documentation as Code: Repeatable Implementation Process

This document is a **step-by-step, repeatable process** that another team can follow to implement documentation as code in their repository.

## Outcomes

After following this process, the target repo will have:

- A clear `docs/` structure and entry points
- Templates for repeatable documents (ADR/runbook/how-to)
- Local checks (pre-commit) for consistent quality
- CI checks (GitHub Actions) that block merges on doc breakage
- A documented workflow (PR checklists + ownership)

## Step 0: Choose scope and ownership

Define these up front:

- **What must be documented**
  - changes impacting users/operators
  - breaking changes and migrations
  - operational procedures and on-call runbooks
  - architecture decisions (ADRs)
- **Owners**
  - identify the team responsible for reviewing critical docs
  - use CODEOWNERS to enforce review

## Step 1: Create a docs entrypoint

Minimum:

- `docs/README.md` as a landing page
- `docs/` subfolders for how-tos, runbooks, reference, and architecture

A recommended structure is provided in [Structure](structure.md).

## Step 2: Add templates

Add templates so documentation is consistent and easy to create:

- ADR template (decisions)
- Runbook template (operations)
- How-to template (tasks)

Use the templates in `templates/` as a starting point.

## Step 3: Add local quality checks (pre-commit)

### Recommended policy

- Run **fast checks locally** (formatting/lint/spell)
- Run **full checks in CI** (including link checking)

### One-time install (Linux/WSL)

```bash
python3 -m pip install --user pre-commit
pre-commit --version
```

### One-time install (Windows PowerShell)

```powershell
py -m pip install --user pre-commit
pre-commit --version
```

### Add configuration

Copy the example:

- `tooling/pre-commit/pre-commit-config.yaml`

…into the **root of the target repository** as `.pre-commit-config.yaml`.

### Install hooks

Linux/WSL:

```bash
pre-commit install
pre-commit run --all-files
```

Windows PowerShell:

```powershell
pre-commit install
pre-commit run --all-files
```

### Optional: Run checks without pre-commit

Use the scripts in `tooling/scripts/` as a repeatable interface:

Linux/WSL:

```bash
bash tooling/scripts/run-doc-checks.sh
```

Windows PowerShell:

```powershell
pwsh -File tooling/scripts/run-doc-checks.ps1
```

## Step 4: Add CI checks (GitHub Actions)

Create a workflow in the target repo:

- `.github/workflows/docs-checks.yml`

Copy the example from:

- `tooling/github-actions/docs-checks.yml`

The example runs:

- Markdown lint (markdownlint)
- Spellcheck (cspell)
- Prose/style (vale)
- Link checking (lychee)

## Copy/paste checklist (source → destination)

Use this block to implement the tooling quickly in a **target repository**.

```text
# From THIS repo:
docs/projects/documentation-as-code/tooling/pre-commit/pre-commit-config.yaml
  -> <target-repo>/.pre-commit-config.yaml

docs/projects/documentation-as-code/tooling/github-actions/docs-checks.yml
  -> <target-repo>/.github/workflows/docs-checks.yml

docs/projects/documentation-as-code/tooling/markdownlint/markdownlint-cli2.yaml
  -> <target-repo>/.markdownlint-cli2.yaml

docs/projects/documentation-as-code/tooling/cspell/cspell.json
  -> <target-repo>/cspell.json

docs/projects/documentation-as-code/tooling/vale/vale.ini
  -> <target-repo>/.vale.ini

docs/projects/documentation-as-code/tooling/vale/styles/
  -> <target-repo>/styles/

docs/projects/documentation-as-code/tooling/lychee/lychee.toml
  -> <target-repo>/lychee.toml

docs/projects/documentation-as-code/tooling/scripts/run-doc-checks.sh
  -> <target-repo>/tooling/scripts/run-doc-checks.sh

docs/projects/documentation-as-code/tooling/scripts/run-doc-checks.ps1
  -> <target-repo>/tooling/scripts/run-doc-checks.ps1
```

## Step 5: Add PR governance (required for repeatability)

### CODEOWNERS

Add a `CODEOWNERS` entry for docs so changes get reviewed.

Example:

```text
# Docs ownership
/docs/ @platform-team
```

### PR checklist

Add (or update) the PR template to include doc prompts:

```markdown
- [ ] Docs updated (README/how-to/runbook/reference)
- [ ] ADR added/updated (if a decision was made)
- [ ] Runbook updated (if operational behavior changed)
```

### Branch protection

Enable required status checks:

- `docs-checks` (or whatever you name the workflow job)

## Step 6: Rollout plan (avoid blocking immediately)

Use a two-phase rollout:

1. **Observe (warn-only)**
   - Run checks in CI but do not block merges.
   - Fix the most common failures and tune dictionaries/exclusions.
2. **Enforce (block merges)**
   - Make CI required.
   - Keep local hooks enabled to catch issues earlier.

## Troubleshooting

- **Spellcheck false positives**: add project terms/acronyms to `cspell.json` (see tooling example).
- **Link checker noise**: configure exclusions for internal-only or unreachable URLs (see `lychee.toml`).
- **Markdown lint conflicts**: tune `.markdownlint-cli2.yaml` rather than disabling globally.
- **Windows execution policy**: call scripts via `pwsh -File` rather than relying on direct execution.
