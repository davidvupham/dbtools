# Best practices for Claude Code skills

**[← Back to best practices index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 18, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Claude_Code-blue)

> [!IMPORTANT]
> Follow these practices to create skills that are maintainable, effective, and widely adopted.

## Table of contents

- [Skill design principles](#skill-design-principles)
- [Writing effective descriptions](#writing-effective-descriptions)
- [Structuring skill files](#structuring-skill-files)
- [Project memory best practices](#project-memory-best-practices)
- [Security considerations](#security-considerations)
- [Common anti-patterns](#common-anti-patterns)

---

## Skill design principles

### 1. Solve a real problem you actually have

Build skills when you notice yourself:

- Repeating the same explanation to Claude (or teammates)
- Looking up the same information repeatedly
- Following the same multi-step process manually
- Wishing Claude "just knew" something about your project

**Anti-pattern:** Building skills for hypothetical problems. If you haven't experienced the pain, you won't design the right solution.

### 2. Keep it focused (one skill = one purpose)

Resist the urge to create a "super skill" that does everything. Composable, focused skills are more reusable and easier to maintain.

**Good:**
- `project-memory` handles memory
- `code-review` handles reviews

**Bad:**
- `project-everything` tries to manage memory, reviews, deployments, and coffee orders

### 3. Use progressive disclosure

Keep SKILL.md under 500 lines. Put detailed information in separate files that Claude reads only when needed.

```text
.claude/skills/data-analysis/
├── SKILL.md              # Overview (under 500 lines)
├── STATISTICS.md         # Detailed statistical methods
├── API.md                # API reference
└── scripts/
    └── validate.py       # Helper scripts
```

### 4. Make it look like standard documentation

Files in `docs/` get maintained. Files in `ai-memory/` get ignored.

Name your files and directories using conventions your team already follows. If decisions would normally go in an `adr/` folder, put them there.

[↑ Back to table of contents](#table-of-contents)

---

## Writing effective descriptions

The `description` field tells Claude when to activate your skill. It's arguably the most important part.

### Include specific trigger phrases

Include 3-5 phrases users might naturally say:

```yaml
description: Set up and maintain a structured project memory system in docs/project_notes/ that tracks bugs with solutions, architectural decisions, key project facts, and work history. Use this skill when asked to "set up project memory", "track our decisions", "log a bug fix", "update project memory", or "initialize memory system".
```

### Test your triggers

Verify activation by trying variations:

- "help me track decisions" vs "set up decision tracking" vs "I want to log our architectural choices"

If Claude doesn't activate the skill, refine your description.

### Avoid jargon-heavy triggers

Use phrases users actually say:

**Good:**
- "set up project memory"
- "log this bug"
- "update key facts"

**Bad:**
- "initialize documentation subsystem"
- "persist institutional knowledge artifacts"

[↑ Back to table of contents](#table-of-contents)

---

## Structuring skill files

### Include templates and examples

Show the exact format you want. Claude follows examples more reliably than abstract instructions.

**Less effective:**

```markdown
Create a bug entry with relevant information
```

**More effective:**

```markdown
### YYYY-MM-DD - Bug Title
- **Issue**: What went wrong
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid it in the future
```

### Use clear section headings

Structure your SKILL.md consistently:

1. **Overview** - What the skill does
2. **When to use this skill** - Trigger conditions
3. **Core capabilities** - What it can do
4. **Templates and references** - Format examples
5. **Example workflows** - Step-by-step scenarios
6. **Success criteria** - How to verify it worked

### Reference supporting files

Don't cram everything into SKILL.md. Link to detailed documentation:

```markdown
For security checklist, see [SECURITY.md](SECURITY.md).
For API reference, see [API.md](API.md).
```

[↑ Back to table of contents](#table-of-contents)

---

## Project memory best practices

### Memory file organization

Use all four files for their intended purposes:

| File | Content | Signs of misuse |
|------|---------|-----------------|
| `bugs.md` | Bug solutions with prevention | Contains configuration info |
| `decisions.md` | ADRs with context and trade-offs | Contains work log entries |
| `key_facts.md` | Configuration, ports, URLs | Exceeds 100 lines (likely contains decisions) |
| `issues.md` | Work log with ticket references | Contains bug solutions |

### Entry format consistency

Consistency matters because Claude can parse structured formats reliably, even months later.

**Bug entry format:**

```markdown
### YYYY-MM-DD - Brief Bug Description
- **Issue**: What went wrong
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid it in the future
```

**Decision entry format:**

```markdown
### ADR-XXX: Decision Title (YYYY-MM-DD)

**Context:**
- Why the decision was needed

**Decision:**
- What was chosen

**Alternatives Considered:**
- Option 1 -> Why rejected

**Consequences:**
- Benefits and trade-offs
```

### Keep entries scannable

Each entry should be scannable in 30 seconds. If you need more detail, link to a separate document.

### Include prevention in bug entries

The **Prevention** field transforms bugs from "problems we fixed" into "lessons we learned." Six months from now, Claude can warn you before you hit the same issue.

### Mark outdated decisions as superseded

Don't delete old decisions. Mark them:

```markdown
**Status:** Superseded by ADR-027

### ADR-003: Use REST for all APIs (2024-01-15)
...
```

Future developers might wonder why old code uses REST.

[↑ Back to table of contents](#table-of-contents)

---

## Security considerations

### Never store secrets in memory files

Memory files are version-controlled markdown. Never store:

| Category | Examples | Risk |
|----------|----------|------|
| Authentication | Passwords, API keys, tokens | Direct credential theft |
| Service accounts | GCP/AWS JSON key files, private keys | Service impersonation |
| OAuth | Client secrets, refresh tokens | Account takeover |
| Database | Connection strings with passwords | Data breach |
| Infrastructure | SSH private keys, VPN credentials | Network intrusion |

### Safe to store

| Category | Examples | Why safe |
|----------|----------|----------|
| Hostnames | `api.staging.example.com` | Public DNS, no auth value |
| Ports | `PostgreSQL: 5432`, `Redis: 6379` | Standard ports, no access |
| Project IDs | `gcp-project-id: my-app-prod` | Useless without credentials |
| Email addresses | `service-account@project.iam.gserviceaccount.com` | Identity, not authentication |
| Environment names | `staging`, `production`, `dev` | No security value |

### Where secrets belong

| Storage method | Use case |
|----------------|----------|
| `.env` files (gitignored) | Local development |
| Cloud secrets managers | Production (GCP Secret Manager, AWS Secrets Manager) |
| CI/CD variables | Automated pipelines (GitHub Actions secrets) |
| Password managers | Team credential sharing (1Password, Bitwarden) |

### If you've already committed secrets

1. **Rotate immediately** - The secret may already be cloned elsewhere
2. Removing from git history isn't enough
3. Audit access logs if available

[↑ Back to table of contents](#table-of-contents)

---

## Common anti-patterns

### The documentation ghost town

**Problem:** Set up project memory with enthusiasm, add three entries, then never touch it again.

**Solution:** Add memory updates to your workflow, not your todo list.
- After every bug fix: "Log this in bugs.md"
- After every architectural discussion: "Add an ADR for this decision"

### The novel-length entry

**Problem:** Bug entries become multi-page essays. Nobody reads them.

**Solution:** Use structured format. Link to separate documents for details.

### The everything file

**Problem:** All information goes into `key_facts.md`, which grows to 500 lines.

**Solution:** Use all four files. If `key_facts.md` exceeds 100 lines, it probably contains decisions disguised as facts.

### The secret stash

**Problem:** API keys in `key_facts.md` "just for convenience."

**Solution:** Use `.env` files. Add to `.gitignore`. No exceptions.

### The stale decisions

**Problem:** ADR-003 says "Use REST" but the team migrated to GraphQL years ago.

**Solution:** Review quarterly. Mark superseded decisions. Don't delete history.

### The island memory

**Problem:** One developer maintains project memory religiously. Others don't know it exists.

**Solution:** Add a section about project memory to your README or onboarding docs. Mention it in PR reviews: "This bug fix should be documented in bugs.md."

[↑ Back to table of contents](#table-of-contents)

---

## Summary checklist

Before publishing a skill:

- [ ] Solves a real problem you've experienced
- [ ] Focused on one purpose
- [ ] Description includes 3-5 trigger phrases users naturally say
- [ ] SKILL.md under 500 lines
- [ ] Templates show exact format expected
- [ ] No secrets in any files
- [ ] Tested activation with phrase variations

[↑ Back to table of contents](#table-of-contents)

---

## Sources

- [Agent Skill Standard](https://agentskills.io) - Cross-platform skill specification
- [Anthropic Skills](https://github.com/anthropics/skills) - Official example skills from Anthropic
- [Vercel Labs Agent Skills](https://github.com/vercel-labs/agent-skills) - Production skill examples (React, web design, deployment)
- [SpillwaveSolutions Project Memory](https://github.com/SpillwaveSolutions/project-memory) - Project memory skill implementation
- "Build Your First Claude Code Skill" by Rick Hightower - Project memory skill tutorial

[↑ Back to table of contents](#table-of-contents)
