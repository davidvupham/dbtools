# Documentation as Code: Recommended Structure

This is a practical structure for internal-only documentation that is easy to navigate and supports mixed tooling.

## Information architecture (what goes where)

A simple and effective breakdown:

- **How-to**: “How do I do X?” (task-oriented)
- **Runbooks**: operational procedures and incident response
- **Reference**: exact facts (configs, parameters, standards)
- **Architecture**: system overviews, diagrams, decisions

## Recommended folder structure (monorepo style)

```text
repo-root/
  docs/
    README.md
    how-to/
    runbooks/
    reference/
    architecture/
    adrs/
    templates/
```

## Recommended folder structure (project-based, like this repo)

```text
docs/
  projects/
    <project-name>/
      README.md
      architecture/
      design/
      implementation/
      operations/
      specs/
      testing/
      management/
```

## Naming conventions

- Prefer **kebab-case** filenames: `how-to-rotate-passwords.md`
- Use **short, descriptive titles** in H1
- Keep “one topic per page” and link to related pages

## Entry points

- `docs/README.md` is the global landing page
- Each project folder has its own `README.md` with:
  - a documentation table (what exists and where)
  - quick links
  - a short checklist for getting started

## Code and configuration snippets

Use fenced blocks with language tags:

- SQL: `sql`
- PowerShell: `powershell`
- Python: `python`
- Terraform/Vault HCL: `hcl`
- Ansible/YAML: `yaml`
- Shell: `bash`

This enables syntax highlighting in Git UIs and IDEs.
