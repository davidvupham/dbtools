# Documentation as Code: Standards

These standards are intentionally lightweight so teams can adopt them quickly.

## Document requirements

Each page should include:

- A clear H1 title
- Intended audience (who should read this)
- Preconditions/prerequisites (if any)
- Step-by-step instructions for how-to/runbook pages
- Expected outcomes (what “success” looks like)

## Markdown conventions

- Use `##` headings for major sections; keep heading depth reasonable.
- Prefer relative links between docs:
  - Good: `[Runbook](../runbooks/rotate-keys.md)`
  - Avoid: absolute links to branches that change.
- Prefer reference-style links when many links appear in a section.

## Code blocks

- Always tag fenced blocks:

```text
```powershell
# ...
```
```

- Avoid screenshots for commands/output unless absolutely necessary.

## Link rules

- Internal docs should use **relative links**.
- External links should be **stable**; prefer vendor docs over blog posts.
- Avoid bare URLs in prose; wrap them in Markdown links.

## Writing style

- Use short sentences and concrete verbs.
- Prefer “do X” over passive voice.
- Prefer consistent terminology (enforced via Vale terminology rules).

## Quality gates (recommended)

- No broken links (CI)
- No obvious spelling mistakes (local + CI)
- Markdown style is consistent (local + CI)
- Terminology rules are enforced (CI)
