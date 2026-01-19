# Customizing Claude Code: skills, hooks, CLAUDE.md, and MCP

**[← Back to tutorials index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 18, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Claude_Code-blue)

> [!IMPORTANT]
> This tutorial teaches you how to customize Claude Code to fit your workflow using its four main extension mechanisms.

## Table of contents

- [The problem: AI amnesia](#the-problem-ai-amnesia)
- [Prerequisites](#prerequisites)
- [Part 1: CLAUDE.md - project memory](#part-1-claudemd---project-memory)
- [Part 2: Hooks - automatic event-driven actions](#part-2-hooks---automatic-event-driven-actions)
- [Part 3: MCP - external tool integration](#part-3-mcp---external-tool-integration)
- [Part 4: Skills and slash commands](#part-4-skills-and-slash-commands)
- [Part 5: Building a project memory skill](#part-5-building-a-project-memory-skill)
- [Putting it together](#putting-it-together)
- [Common pitfalls and how to avoid them](#common-pitfalls-and-how-to-avoid-them)
- [Next steps](#next-steps)
- [Sources](#sources)
- [Appendix: Template collections](#appendix-template-collections)

---

## The problem: AI amnesia

Every AI coding assistant shares a frustrating limitation: they forget everything between sessions. Start a new chat, and Claude doesn't know:

- That you spent 45 minutes discovering your staging environment uses port 5433, not 5432
- That you chose PostgreSQL over MongoDB because of your team's existing expertise
- That the "connection refused" error always means the VPN disconnected

All that hard-won knowledge? Gone. Every. Single. Time.

The hidden cost is staggering. If you spend just 30 minutes per week re-solving problems you've already solved, that's 26 hours per year of wasted time per developer.

This tutorial shows you how to solve this with Claude Code's customization features.

[↑ Back to table of contents](#table-of-contents)

---

## Prerequisites

- Claude Code CLI installed and authenticated
- A project directory to work in
- Basic familiarity with the command line

### What you learn

| Feature | Purpose | Example use case |
|---------|---------|------------------|
| CLAUDE.md | Project memory and instructions | Store build commands, architecture notes |
| Hooks | Automatic actions on events | Auto-format code after edits |
| MCP | External tool integration | Query databases, access GitHub |
| Skills/Commands | Reusable prompts and workflows | PR reviews, commit messages |

[↑ Back to table of contents](#table-of-contents)

---

## Part 1: CLAUDE.md - project memory

CLAUDE.md is a markdown file that Claude automatically reads at startup. It acts as persistent memory for your project.

### Creating your first CLAUDE.md

The quickest way to start:

```bash
claude
> /init
```

This creates a starter file. Alternatively, create it manually:

```bash
touch CLAUDE.md
```

### What to include

A well-structured CLAUDE.md contains:

```markdown
# CLAUDE.md

## Build and test commands

```bash
make test        # Run all tests
make lint        # Run linter
make build       # Build the project
```

## Architecture

This project uses:
- `src/` - Main application code
- `tests/` - Test files
- `docs/` - Documentation

Key patterns:
- Repository pattern for data access
- Factory pattern for object creation

## Code style

- Use 4-space indentation
- Prefer f-strings over .format()
- Type hints required for public functions
```

### Memory hierarchy

Claude Code reads memory files in this order (later files override earlier):

| Priority | Location | Scope |
|----------|----------|-------|
| 1 | `/etc/claude-code/CLAUDE.md` | System-wide (enterprise) |
| 2 | `./CLAUDE.md` | Project (shared via git) |
| 3 | `./.claude/rules/*.md` | Project rules (modular) |
| 4 | `~/.claude/CLAUDE.md` | User (all projects) |
| 5 | `./CLAUDE.local.md` | Local (gitignored) |

### Modular rules with .claude/rules/

For larger projects, split instructions into separate files:

```text
.claude/
└── rules/
    ├── testing.md
    ├── security.md
    └── api/
        └── endpoints.md
```

Rules can target specific file patterns using frontmatter:

```markdown
---
paths:
  - "src/api/**/*.py"
  - "tests/api/**/*.py"
---

# API development rules

- All endpoints must validate input
- Return standard error format
- Include OpenAPI docstrings
```

### Importing other files

Reference other files with `@` syntax:

```markdown
For API conventions, see @docs/api-guide.md
For git workflow, see @~/.claude/git-instructions.md
```

[↑ Back to table of contents](#table-of-contents)

---

## Part 2: Hooks - automatic event-driven actions

Hooks execute shell commands automatically when specific events occur. They provide deterministic, automatic control over Claude's behavior.

### Available hook events

| Event | When it fires | Common uses |
|-------|---------------|-------------|
| PreToolUse | Before a tool runs | Block dangerous commands, log usage |
| PostToolUse | After a tool completes | Auto-format, run linters |
| Notification | When Claude notifies | Custom desktop alerts |
| Stop | When Claude finishes | Cleanup, summaries |
| SessionStart | Session begins | Load environment variables |

### Configuring hooks

Use the interactive interface:

```bash
claude
> /hooks
```

Or edit settings directly in `~/.claude/settings.json` (user) or `.claude/settings.json` (project):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'File modified'"
          }
        ]
      }
    ]
  }
}
```

### Example: Auto-format Python files

Format Python files automatically after Claude edits them:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs -I{} sh -c 'if [[ \"{}\" == *.py ]]; then ruff format \"{}\"; fi'"
          }
        ]
      }
    ]
  }
}
```

### Example: Block edits to sensitive files

Prevent modifications to `.env` files:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep -q '\\.env' && exit 2 || exit 0"
          }
        ]
      }
    ]
  }
}
```

Exit code `2` blocks the action. Any other exit code allows it.

### Hook input and output

Hooks receive JSON via stdin:

```json
{
  "tool": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "old_string": "...",
    "new_string": "..."
  }
}
```

Return JSON to control behavior:

```json
{
  "action": "block",
  "reason": "Cannot modify production config",
  "feedback": "Use staging config instead"
}
```

[↑ Back to table of contents](#table-of-contents)

---

## Part 3: MCP - external tool integration

MCP (Model Context Protocol) connects Claude to external services like databases, GitHub, and APIs.

### Adding MCP servers

**HTTP servers** (for cloud services):

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

**Stdio servers** (for local tools):

```bash
# Database connection
claude mcp add --transport stdio postgres -- npx -y @bytebase/dbhub \
  --dsn "postgresql://user:pass@localhost/mydb"

# With environment variables
claude mcp add --transport stdio myapi --env API_KEY=secret \
  -- python ./mcp_server.py
```

### Managing servers

```bash
# List configured servers
claude mcp list

# Get details
claude mcp get github

# Remove a server
claude mcp remove github

# Check status in Claude Code
> /mcp
```

### Scopes

| Scope | Storage | Visibility |
|-------|---------|------------|
| local | `~/.claude.json` | You only, current project |
| project | `.mcp.json` | Team (via git) |
| user | `~/.claude.json` | You, all projects |

```bash
# Project scope (shared with team)
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/
```

### Authentication

Many MCP servers require OAuth authentication:

```bash
# 1. Add the server
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 2. Authenticate in Claude Code
> /mcp
# Select the server and choose "Authenticate"
# Complete the browser login flow
```

### Using MCP tools

Once configured, MCP tools are available automatically:

```bash
# With GitHub MCP
> Show me all open PRs assigned to me
> Create an issue for the login bug

# With database MCP
> What's the schema for the users table?
> Show me orders from the last 7 days
```

[↑ Back to table of contents](#table-of-contents)

---

## Part 4: Skills and slash commands

Skills and commands extend Claude's capabilities with reusable prompts.

### Slash commands (manual invocation)

Slash commands are markdown files you invoke with `/name`.

**Create a command:**

```bash
mkdir -p .claude/commands
```

Create `.claude/commands/review.md`:

```markdown
Review this code for:
- Security vulnerabilities
- Performance issues
- Code style violations
```

**Use it:**

```bash
> /review
```

### Commands with arguments

Use `$ARGUMENTS` or positional `$1`, `$2`:

Create `.claude/commands/fix-issue.md`:

```markdown
Fix GitHub issue #$ARGUMENTS

Follow our coding standards and include tests.
```

Usage: `> /fix-issue 123`

### Commands with bash execution

Use `!` prefix to include command output:

Create `.claude/commands/commit.md`:

```markdown
---
allowed-tools: Bash(git:*)
---

## Context

Current changes:
!`git diff --staged`

Recent commits:
!`git log --oneline -5`

## Task

Create a clear, concise commit message for these changes.
```

### Skills (automatic discovery)

Skills are directories that Claude automatically discovers and applies based on your request.

**Create a skill:**

```bash
mkdir -p .claude/skills/code-review
```

Create `.claude/skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: Performs thorough code reviews with security and performance analysis
---

# Code review skill

When reviewing code, check for:

1. **Security**: SQL injection, XSS, auth bypasses
2. **Performance**: N+1 queries, unnecessary loops
3. **Maintainability**: Clear names, single responsibility
4. **Testing**: Edge cases covered, mocks appropriate

For security checklist, see [SECURITY.md](SECURITY.md).
```

Add supporting files as needed:

```text
.claude/skills/code-review/
├── SKILL.md
├── SECURITY.md
└── PERFORMANCE.md
```

### Skill activation

When you make a request, Claude follows a progressive disclosure pattern:

1. **Discovery phase**: Scan skill directories, load metadata (name + description)
2. **Matching phase**: Check if request matches skill description
3. **Execution phase**: Load full SKILL.md, follow instructions, execute scripts if needed

This keeps interactions fast while giving you access to powerful capabilities on demand.

### Restricting tool access

Limit what tools a skill or command can use:

```markdown
---
allowed-tools: Read, Grep, Glob
---

# Read-only analysis skill

This skill can only read files, not modify them.
```

### Commands vs skills comparison

| Aspect | Slash commands | Skills |
|--------|----------------|--------|
| Invocation | Manual: `/command` | Automatic |
| Structure | Single file | Directory with support files |
| Best for | Quick templates | Complex workflows |

[↑ Back to table of contents](#table-of-contents)

---

## Part 5: Building a project memory skill

This section walks you through building a project memory skill that tracks bugs, decisions, and key facts across sessions.

### The project memory concept

The project-memory skill creates a structured knowledge system in `docs/project_notes/` with four specialized files:

| File | Purpose | Example content |
|------|---------|-----------------|
| `bugs.md` | Bug log with solutions | "BUG-018: Pulumi state drift - run `pulumi refresh --yes`" |
| `decisions.md` | Architectural Decision Records (ADRs) | "ADR-012: Use D3.js for all charts (team expertise)" |
| `key_facts.md` | Project configuration, ports, URLs | "Staging API: https://api.staging.example.com:8443" |
| `issues.md` | Work log with ticket references | "TICKET-456: Implemented user auth - 2024-01-15" |

> [!NOTE]
> **Directory naming rationale:** Using `docs/project_notes/` instead of `memory/` makes it look like standard engineering documentation, not AI-specific tooling. Developers will view it as documentation and won't shy away from maintaining it.

### Creating the skill structure

```bash
mkdir -p ~/.claude/skills/project-memory
```

Create `~/.claude/skills/project-memory/SKILL.md`:

```markdown
---
name: project-memory
description: Set up and maintain a structured project memory system in docs/project_notes/ that tracks bugs with solutions, architectural decisions, key project facts, and work history. Use this skill when asked to "set up project memory", "track our decisions", "log a bug fix", "update project memory", or "initialize memory system".
---

# Project memory

## Table of contents

- [Overview](#overview)
- [When to use this skill](#when-to-use-this-skill)
- [Core capabilities](#core-capabilities)
- [Templates and references](#templates-and-references)
- [Example workflows](#example-workflows)

## Overview

Maintain institutional knowledge for projects by establishing a structured memory system.

## When to use this skill

Invoke this skill when:

- Starting a new project that will accumulate knowledge over time
- The project already has recurring bugs or decisions that should be documented
- The user asks to "set up project memory" or "track our decisions"
- Encountering a problem that feels familiar ("didn't we solve this before?")
- Before proposing an architectural change (check existing decisions first)

## Core capabilities

### 1. Initial setup - create memory infrastructure

When invoked for the first time in a project, create the following structure:

```text
docs/
└── project_notes/
    ├── bugs.md          # Bug log with solutions
    ├── decisions.md     # Architectural Decision Records
    ├── key_facts.md     # Project configuration and constants
    └── issues.md        # Work log with ticket references
```

### 2. Configure CLAUDE.md - memory-aware behavior

Add or update the following section in the project's `CLAUDE.md` file:

```markdown
## Project memory system

This project maintains institutional knowledge in `docs/project_notes/` for consistent context.

### Memory files

- **bugs.md** - Bug log with dates, solutions, and prevention notes
- **decisions.md** - Architectural Decision Records (ADRs) with context and trade-offs
- **key_facts.md** - Project configuration, credentials, ports, important URLs
- **issues.md** - Work log with ticket IDs, descriptions, and URLs

### Memory-aware protocols

**Before proposing architectural changes:**
- Check `docs/project_notes/decisions.md` for existing decisions
- Verify the proposed approach doesn't conflict with past choices

**When encountering errors or bugs:**
- Search `docs/project_notes/bugs.md` for similar issues
- Apply known solutions if found
- Document new bugs and solutions when resolved

**When looking up project configuration:**
- Check `docs/project_notes/key_facts.md` for credentials, ports, URLs, service accounts
- Prefer documented facts over assumptions
```

### 3. Memory entry formats

**Adding a bug entry:**
```markdown
### YYYY-MM-DD - Brief Bug Description
- **Issue**: What went wrong
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid it in the future
```

**Adding a decision:**
```markdown
### ADR-XXX: Decision Title (YYYY-MM-DD)

**Context:**
- Why the decision was needed
- What problem it solves

**Decision:**
- What was chosen

**Alternatives Considered:**
- Option 1 -> Why rejected
- Option 2 -> Why rejected

**Consequences:**
- Benefits
- Trade-offs
```

**Adding key facts:**
- Organize by category (GCP Project, Database, API, Local Development, etc.)
- Use bullet lists for clarity
- Include both production and development details
- Add URLs for easy navigation

**Adding work log entry:**
```markdown
### YYYY-MM-DD - TICKET-ID: Brief Description
- **Status**: Completed / In Progress / Blocked
- **Description**: 1-2 line summary
- **URL**: https://jira.company.com/browse/TICKET-ID
- **Notes**: Any important context
```

## Templates and references

This skill includes template files in `references/` that demonstrate proper format:

- **references/bugs_template.md** - Bug entry format with examples
- **references/decisions_template.md** - ADR format with examples
- **references/key_facts_template.md** - Key facts organization with examples (includes security guidelines)
- **references/issues_template.md** - Work log format with examples

When creating initial memory files, copy these templates to `docs/project_notes/`.

## Example workflows

### Scenario 1: Encountering a familiar bug

```text
User: "I'm getting a 'connection refused' error from the database"
-> Search docs/project_notes/bugs.md for "connection"
-> Find previous solution: "Use AlloyDB Auth Proxy on port 5432"
-> Apply known fix
```

### Scenario 2: Proposing an architectural change

```text
Internal: "User might benefit from using SQLAlchemy for migrations"
-> Check docs/project_notes/decisions.md
-> Find ADR-002: Already decided to use Alembic
-> Use Alembic instead, maintaining consistency
```

### Scenario 3: User requests memory update

```text
User: "Add that CORS fix to our bug log"
-> Read docs/project_notes/bugs.md
-> Add new entry with date, issue, solution, prevention
-> Confirm addition to user
```
```

### Adding template files

Create `~/.claude/skills/project-memory/references/bugs_template.md`:

```markdown
# Bug log

Track bugs, their solutions, and prevention strategies.

## 2024-10-20 - BUG-018: Pulumi state drift during deploy

- **Issue**: Deploy failed with cryptic "update failed" error after manual GCP console changes
- **Root Cause**: Pulumi state file out of sync with actual infrastructure after teammate made console changes
- **Solution**: Run `pulumi refresh --yes` before deploy to sync state
- **Prevention**: Add `pulumi refresh --yes` to CI/CD pipeline before deploys; document that manual console changes require refresh
```

Create `~/.claude/skills/project-memory/references/key_facts_template.md`:

```markdown
# Key facts

Project configuration, ports, URLs, and important constants.

## Security guidelines

> [!WARNING]
> **Never store in this file:**
> - Passwords, API keys, tokens
> - GCP/AWS JSON key files, private keys
> - OAuth secrets, refresh tokens
> - Database connection strings with passwords
> - SSH private keys, VPN credentials
>
> Use `.env` files (gitignored), cloud secrets managers, or CI/CD variables instead.

**Safe to store:**
- Hostnames and URLs (e.g., `api.staging.example.com`)
- Port numbers (e.g., `PostgreSQL: 5432`)
- Project identifiers (e.g., `gcp-project-id: my-app-prod`)
- Service account email addresses (identity, not authentication)
- Environment names (staging, production, dev)

## Database configuration

- PostgreSQL port: 5432
- Redis port: 6379
- Development database: `localhost:5432/app_dev`

## API endpoints

- Production: https://api.example.com/v1
- Staging: https://api.staging.example.com:8443/v1

## Environment identifiers

- GCP Project (prod): `my-app-prod`
- GCP Project (staging): `my-app-staging`
```

### Testing your skill

1. Open Claude Code in any project
2. Say: "Set up project memory for this project"
3. Claude recognizes the trigger phrase and activates the skill
4. The skill creates the directory structure and updates CLAUDE.md

### The compound interest effect

Once you have project memory set up, knowledge compounds:

| Encounter | Time spent | Result |
|-----------|------------|--------|
| First | 2 hours debugging | Document solution in bugs.md |
| Second | 5 minutes lookup | Apply known fix |
| Third | 2 minutes familiar | Recognize pattern instantly |
| Fourth | Preventative | Claude warns before you hit the issue |

By the fourth encounter, Claude doesn't just fix the bug. It prevents it. "I notice you're about to make a change that caused state drift issues before. Should I run `pulumi refresh` first?"

[↑ Back to table of contents](#table-of-contents)

---

## Putting it together

Here's a complete setup for a Python project:

### 1. Create CLAUDE.md

```markdown
# CLAUDE.md

## Commands

```bash
make test      # pytest
make lint      # ruff check
make format    # ruff format
```

## Architecture

- `src/` - Application code
- `tests/` - Test files
- FastAPI for API endpoints
- SQLAlchemy for database

## Style

- Ruff for linting (line-length 120)
- Google-style docstrings
- Type hints required

## Project memory system

This project maintains institutional knowledge in `docs/project_notes/`.

### Memory-aware protocols

**Before proposing architectural changes:**
- Check `docs/project_notes/decisions.md` for existing decisions

**When encountering errors:**
- Search `docs/project_notes/bugs.md` for similar issues
```

### 2. Add formatting hook

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs -I{} sh -c '[[ \"{}\" == *.py ]] && ruff format \"{}\" || true'"
          }
        ]
      }
    ]
  }
}
```

### 3. Add database MCP

```bash
claude mcp add --scope project --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://dev:pass@localhost/app_dev"
```

### 4. Create commit command

Create `.claude/commands/commit.md`:

```markdown
---
allowed-tools: Bash(git:*)
---

!`git status`
!`git diff --staged`

Create a commit with a clear message following conventional commits format.
```

### 5. Set up project memory

```bash
> Set up project memory for this project
```

[↑ Back to table of contents](#table-of-contents)

---

## Common pitfalls and how to avoid them

### Pitfall 1: The documentation ghost town

**The problem:** You set up project memory with enthusiasm, add three entries, then never touch it again. Six months later, the files are outdated and useless.

**The solution:** Add memory updates to your workflow, not your todo list. After every bug fix, ask Claude: "Log this in bugs.md." After every architectural discussion, say: "Add an ADR for this decision." Make it reflexive, not deliberate.

### Pitfall 2: The novel-length entry

**The problem:** Bug entries become multi-page essays. Decision records include the entire discussion history. Nobody reads them because they're too long.

**The solution:** Each entry should be scannable in 30 seconds. Use the structured format (Issue, Root Cause, Solution, Prevention). If you need more detail, link to a separate document.

### Pitfall 3: The everything file

**The problem:** All information goes into `key_facts.md`, which grows to 500 lines with no organization.

**The solution:** Use all four files for their intended purposes:
- Bugs go in `bugs.md`
- Decisions go in `decisions.md`
- Configuration goes in `key_facts.md`
- Work history goes in `issues.md`

If `key_facts.md` exceeds 100 lines, it probably contains decisions disguised as facts.

### Pitfall 4: The secret stash

**The problem:** Developers store API keys in `key_facts.md` "just for convenience." The keys end up in git history forever. Use `.env` and add it to your `.gitignore`.

**The solution:** See the Security section above. If you've already committed secrets, rotate them immediately. Removing from git history isn't enough because the secret may already be cloned elsewhere.

### Pitfall 5: The stale decisions

**The problem:** ADR-003 says "Use REST for all APIs" but the team migrated to GraphQL two years ago. The memory file now contains misleading information.

**The solution:** Review decision records quarterly. Mark outdated decisions as superseded: `**Status**: Superseded by ADR-027`. Don't delete. Future developers might wonder why old code uses REST.

[↑ Back to table of contents](#table-of-contents)

---

## Next steps

1. Run `/init` to create your first CLAUDE.md
2. Run `/hooks` to set up auto-formatting
3. Set up project memory with "Set up project memory for this project"
4. Explore available MCP servers for your tools
5. Create a `/commit` command for your workflow

### Cross-platform skills with skilz CLI

Skills can work across multiple AI coding assistants (Claude Code, Codex, Gemini, Cursor, and more) using the Agent Skill Standard. Install skills from GitHub:

```bash
# Install skilz CLI
pip install skilz

# Install project-memory skill globally
skilz install https://github.com/SpillwaveSolutions/project-memory

# Install for specific agents
skilz install https://github.com/SpillwaveSolutions/project-memory --agent codex
skilz install https://github.com/SpillwaveSolutions/project-memory --agent gemini
```

### Resources

- Project Memory Agent Skill: https://github.com/SpillwaveSolutions/project-memory
- Agent Skill Standard: https://agentskills.io
- SkillzWave Marketplace: https://skillzwave.ai

[↑ Back to table of contents](#table-of-contents)

---

## Summary

| Feature | File location | Purpose |
|---------|---------------|---------|
| CLAUDE.md | `./CLAUDE.md` | Project context and instructions |
| Hooks | `.claude/settings.json` | Automatic actions |
| MCP | `.mcp.json` | External tool connections |
| Commands | `.claude/commands/*.md` | Manual prompts |
| Skills | `.claude/skills/*/SKILL.md` | Auto-discovered capabilities |
| Project memory | `docs/project_notes/*.md` | Persistent knowledge across sessions |

[↑ Back to table of contents](#table-of-contents)

---

## Sources

### Official documentation

- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) - Anthropic's official Claude Code documentation
- [Agent Skill Standard](https://agentskills.io) - Open specification for cross-platform AI agent skills
- [Agent Skill Standard specification](https://agentskills.io/specification) - Detailed specification document

### Example skill repositories

- [Anthropic Skills](https://github.com/anthropics/skills) - Official example skills from Anthropic
- [Vercel Labs Agent Skills](https://github.com/vercel-labs/agent-skills) - Skills for React best practices, web design guidelines, and Vercel deployment
- [SpillwaveSolutions Project Memory](https://github.com/SpillwaveSolutions/project-memory) - Project memory skill referenced in this tutorial

### Skill marketplaces

- [SkillzWave](https://skillzwave.ai) - Community skill marketplace

### Reference materials

- [skilz CLI](https://github.com/agentskills/agentskills) - Cross-platform skill installation tool
- "Build Your First Claude Code Skill" by Rick Hightower - Project memory skill tutorial (PDF)

[↑ Back to table of contents](#table-of-contents)

---

## Appendix: Template collections

### Claude Code Templates

The [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) repository provides 100+ ready-to-use configurations:

| Category | Examples |
|----------|----------|
| Agents | Security auditing, performance optimization specialists |
| Commands | `/generate-tests`, `/optimize-bundle` |
| MCPs | GitHub, PostgreSQL, AWS integrations |
| Hooks | Pre-commit validation triggers |
| Skills | PDF processing, Excel automation |

**Installation:**

```bash
# Browse templates interactively
npx claude-code-templates

# Or visit the web interface
# https://aitmpl.com
```

**Additional tools included:**
- Analytics dashboard for monitoring AI sessions
- Conversation monitor with mobile interface
- Health check diagnostics
- Plugin management dashboard

[↑ Back to table of contents](#table-of-contents)
