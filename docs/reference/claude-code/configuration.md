# Claude Code configuration reference

**[← Back to Claude Code reference](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 18, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Claude_Code-blue)

## Table of contents

- [Memory files](#memory-files)
- [Settings files](#settings-files)
- [MCP configuration](#mcp-configuration)
- [Slash commands](#slash-commands)
- [Skills](#skills)
- [Hooks](#hooks)
- [Agent Skill Standard](#agent-skill-standard)
- [CLI options](#cli-options)
- [Built-in tools](#built-in-tools)
- [Permission configuration](#permission-configuration)
- [Sub-agents](#sub-agents)
- [Session management](#session-management)
- [Skill resources](#skill-resources)
- [Sources](#sources)

---

## Memory files

Claude Code reads memory files automatically at startup.

### CLAUDE.md

| Property | Value |
|----------|-------|
| Location | Project root or `.claude/CLAUDE.md` |
| Purpose | Project-specific instructions |
| Scope | Team (committed to git) |

### CLAUDE.local.md

| Property | Value |
|----------|-------|
| Location | Project root |
| Purpose | Local overrides |
| Scope | Personal (gitignored) |

### Memory hierarchy (in order of precedence)

| Priority | Location | Scope |
|----------|----------|-------|
| 1 | `/etc/claude-code/CLAUDE.md` (Linux) | Enterprise-wide |
| 2 | `./CLAUDE.md` | Project (team) |
| 3 | `./.claude/rules/*.md` | Project rules (modular) |
| 4 | `~/.claude/CLAUDE.md` | User (all projects) |
| 5 | `./CLAUDE.local.md` | Local (personal) |

### File imports

Reference other files using `@` syntax:

```markdown
See @docs/api-guide.md for API conventions.
See @~/.claude/personal-prefs.md for personal settings.
```

Supported paths:
- Relative: `@docs/guide.md`
- Absolute: `@/etc/standards/style.md`
- Home directory: `@~/.claude/personal.md`

Maximum import depth: 5 hops.

[↑ Back to table of contents](#table-of-contents)

---

## Settings files

### User settings

| Property | Value |
|----------|-------|
| Location | `~/.claude/settings.json` |
| Purpose | Personal preferences, hooks |
| Scope | All projects |

### Project settings

| Property | Value |
|----------|-------|
| Location | `.claude/settings.json` |
| Purpose | Project-specific hooks, settings |
| Scope | Team (can be committed) |

### Settings schema

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Notification": [...],
    "Stop": [...],
    "SessionStart": [...],
    "SessionEnd": [...]
  }
}
```

[↑ Back to table of contents](#table-of-contents)

---

## MCP configuration

### Storage locations

| Scope | Storage file |
|-------|-------------|
| local | `~/.claude.json` |
| project | `.mcp.json` |
| user | `~/.claude.json` |

### Adding servers

**HTTP transport:**

```bash
claude mcp add --transport http <name> <url>
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

**Stdio transport:**

```bash
claude mcp add --transport stdio <name> -- <command> [args...]
claude mcp add --transport stdio postgres -- npx -y @bytebase/dbhub --dsn "postgresql://..."
```

### MCP commands

| Command | Description |
|---------|-------------|
| `claude mcp add` | Add a new MCP server |
| `claude mcp list` | List configured servers |
| `claude mcp get <name>` | Show server details |
| `claude mcp remove <name>` | Remove a server |
| `/mcp` | Interactive MCP management |

### Common MCP servers

| Server | URL/Command | Purpose |
|--------|-------------|---------|
| GitHub | `https://api.githubcopilot.com/mcp/` | Issues, PRs, repos |
| Sentry | `https://mcp.sentry.dev/mcp` | Error monitoring |
| PostgreSQL | `npx -y @bytebase/dbhub --dsn "..."` | Database queries |

[↑ Back to table of contents](#table-of-contents)

---

## Slash commands

### Location

| Scope | Directory |
|-------|-----------|
| Project | `.claude/commands/` |
| User | `~/.claude/commands/` |

### File format

```markdown
---
allowed-tools: Bash(git:*), Read, Edit
description: Optional description for help text
---

Your prompt content here.

Use $ARGUMENTS for all arguments.
Use $1, $2, etc. for positional arguments.
Use !`command` to include bash output.
```

### Frontmatter options

| Field | Type | Description |
|-------|------|-------------|
| `allowed-tools` | string | Comma-separated tool restrictions |
| `description` | string | Help text description |
| `context` | string | `fork` to run in isolated context |

### Variable substitution

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments as single string |
| `$1`, `$2`, ... | Positional arguments |
| `!`command`` | Bash command output |
| `@path/to/file` | File contents |

### Namespacing

Subdirectories create namespaced commands:

```text
.claude/commands/
├── deploy/
│   ├── staging.md      # /deploy:staging
│   └── production.md   # /deploy:production
└── review.md           # /review
```

[↑ Back to table of contents](#table-of-contents)

---

## Skills

### Location

| Scope | Directory |
|-------|-----------|
| Project | `.claude/skills/<skill-name>/SKILL.md` |
| User | `~/.claude/skills/<skill-name>/SKILL.md` |

### SKILL.md format

```markdown
---
name: skill-name
description: When to activate this skill. Include trigger phrases users might say.
allowed-tools: Read, Grep, Glob
model: claude-sonnet-4-*
context: fork
user-invocable: true
---

# Skill title

## When to use this skill

- Trigger condition 1
- Trigger condition 2

## Core capabilities

Instructions for Claude when this skill is active.
```

### Frontmatter fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Skill identifier (lowercase, hyphens, max 64 chars) |
| `description` | Yes | string | Activation trigger description |
| `allowed-tools` | No | string | Tool restrictions |
| `model` | No | string | Specific model requirement |
| `context` | No | string | `fork` for isolated subagent |
| `user-invocable` | No | boolean | Show in `/menu` (default: true) |
| `paths` | No | array | File patterns to auto-apply |

### Supporting files

Skills can include additional files:

```text
.claude/skills/code-review/
├── SKILL.md              # Main skill definition
├── SECURITY.md           # Referenced by SKILL.md
├── PERFORMANCE.md        # Additional guidance
└── scripts/
    └── lint.sh           # Helper scripts
```

Reference with relative paths: `See [SECURITY.md](SECURITY.md) for details.`

[↑ Back to table of contents](#table-of-contents)

---

## Hooks

### Hook events

| Event | Trigger | Can block |
|-------|---------|-----------|
| `PreToolUse` | Before tool execution | Yes (exit 2) |
| `PostToolUse` | After tool completion | No |
| `Notification` | When Claude notifies | No |
| `Stop` | When Claude finishes | No |
| `SessionStart` | Session begins | No |
| `SessionEnd` | Session ends | No |
| `SubagentStop` | Subagent completes | No |
| `PreCompact` | Before context compaction | No |
| `PermissionRequest` | Permission dialog shown | No |
| `UserPromptSubmit` | User submits prompt | No |

### Hook configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here"
          }
        ]
      }
    ]
  }
}
```

### Matcher patterns

| Pattern | Matches |
|---------|---------|
| `*` | All tools |
| `Bash` | Bash tool only |
| `Edit\|Write` | Edit or Write tools |
| `Bash(git:*)` | Bash commands starting with `git` |

### Hook input (stdin JSON)

```json
{
  "tool": "Edit",
  "tool_input": {
    "file_path": "/path/to/file",
    "old_string": "...",
    "new_string": "..."
  },
  "session_id": "abc123"
}
```

### Hook output

**Exit codes:**
- `0` - Continue normally
- `2` - Block action (PreToolUse only)
- Other - Continue (treated as success)

**JSON output:**

```json
{
  "action": "block",
  "reason": "Explanation shown to Claude",
  "feedback": "Suggestion for alternative"
}
```

[↑ Back to table of contents](#table-of-contents)

---

## Agent Skill Standard

Skills follow the open Agent Skill Standard for cross-platform compatibility.

### Supported platforms

- Claude Code
- OpenAI Codex
- Gemini CLI
- Cursor
- OpenCode
- GitHub Copilot
- VS Code
- And more (14+ platforms)

### Standard specification

| Resource | URL |
|----------|-----|
| Standard homepage | https://agentskills.io |
| Specification | https://agentskills.io/specification |
| Example skills | https://github.com/anthropics/skills |
| Reference library | https://github.com/agentskills/agentskills |

### Installing cross-platform skills

```bash
# Install skilz CLI
pip install skilz

# Install skill globally (all projects)
skilz install https://github.com/SpillwaveSolutions/project-memory

# Install for specific project
skilz install https://github.com/SpillwaveSolutions/project-memory --project

# Install for specific agent
skilz install https://github.com/SpillwaveSolutions/project-memory --agent codex
skilz install https://github.com/SpillwaveSolutions/project-memory --agent gemini
```

[↑ Back to table of contents](#table-of-contents)

---

## CLI options

### Session control

| Flag | Description |
|------|-------------|
| `--continue`, `-c` | Continue most recent conversation |
| `--resume <session-id>` | Resume a specific session |
| `--fork-session <session-id>` | Fork from an existing session |
| `--print`, `-p` | Print response without interactive mode |
| `--output-format <format>` | Output format: `text`, `json`, `stream-json` |
| `--verbose` | Enable verbose output |

### Model and agent

| Flag | Description |
|------|-------------|
| `--model <model>` | Specify model to use |
| `--agent <agent>` | Use a specific agent configuration |
| `--agents` | List available agents |
| `--system-prompt <prompt>` | Custom system prompt |
| `--append-system-prompt <text>` | Append to default system prompt |

### Tool restrictions

| Flag | Description |
|------|-------------|
| `--tools` | List available tools |
| `--allowedTools <tools>` | Comma-separated list of allowed tools |
| `--disallowedTools <tools>` | Comma-separated list of disallowed tools |

### Limits and budgets

| Flag | Description |
|------|-------------|
| `--max-budget-usd <amount>` | Maximum spend limit in USD |
| `--max-turns <n>` | Maximum conversation turns |

### Configuration paths

| Flag | Description |
|------|-------------|
| `--settings <path>` | Path to settings file |
| `--mcp-config <path>` | Path to MCP configuration file |

### Remote and debugging

| Flag | Description |
|------|-------------|
| `--remote` | Enable remote session |
| `--teleport` | Teleport session to another device |
| `--debug [category]` | Enable debug output (optional category filter) |
| `--ide <ide>` | IDE integration (vscode, cursor, etc.) |
| `--chrome` | Enable Chrome integration |

[↑ Back to table of contents](#table-of-contents)

---

## Built-in tools

Claude Code provides these built-in tools:

### File operations

| Tool | Description |
|------|-------------|
| `Read` | Read files, images, PDFs with line numbers |
| `Write` | Create new files |
| `Edit` | Precise string-replacement modifications |
| `Glob` | File pattern matching |
| `Grep` | Regex-based content searching |

### Execution

| Tool | Description |
|------|-------------|
| `Bash` | Shell command execution with background support |
| `Task` | Launch sub-agents for complex tasks |
| `TodoWrite` | Task management and tracking |

### Network

| Tool | Description |
|------|-------------|
| `WebFetch` | Fetch and process web content |
| `WebSearch` | Search the web for information |

### Notebooks

| Tool | Description |
|------|-------------|
| `NotebookEdit` | Edit Jupyter notebook cells |
| `NotebookRead` | Read Jupyter notebooks |

[↑ Back to table of contents](#table-of-contents)

---

## Permission configuration

### Permission modes

| Mode | Description |
|------|-------------|
| `ask` | Prompt for permission (default) |
| `allow` | Allow without prompting |
| `deny` | Deny without prompting |

### Settings file configuration

Configure permissions in `.claude/settings.json` or `~/.claude/settings.json`:

```json
{
  "permissions": {
    "default": "ask",
    "tools": {
      "Read": "allow",
      "Write": "ask",
      "Bash": "ask",
      "Edit": "ask"
    },
    "bash": {
      "allow": [
        "git status",
        "git diff",
        "git log*",
        "npm test",
        "npm run *"
      ],
      "deny": [
        "rm -rf *",
        "sudo *"
      ]
    },
    "protectedFiles": [
      ".env",
      ".env.*",
      "*.pem",
      "*.key",
      ".git/"
    ]
  }
}
```

### Bash command patterns

| Pattern | Matches |
|---------|---------|
| `git status` | Exact command |
| `git log*` | Commands starting with `git log` |
| `npm run *` | Any npm run script |
| `*` | All commands (use carefully) |

[↑ Back to table of contents](#table-of-contents)

---

## Sub-agents

Sub-agents delegate work to specialized Claude instances.

### Launching sub-agents

Use the `Task` tool to launch sub-agents:

| Agent type | Purpose |
|------------|---------|
| `Bash` | Command execution specialist |
| `Explore` | Codebase exploration and searching |
| `Plan` | Implementation planning |
| `general-purpose` | Multi-step complex tasks |

### Sub-agent characteristics

- Run in isolated context
- Have access to specific tool subsets
- Return results to parent conversation
- Can run in background with `run_in_background: true`

[↑ Back to table of contents](#table-of-contents)

---

## Session management

### Built-in session commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/exit` | Exit Claude Code |
| `/compact` | Compact conversation context |
| `/clear` | Clear conversation history |

### Background task commands

| Command | Description |
|---------|-------------|
| `/bashes` | List background shell tasks |
| `/tasks` | List all running tasks |
| `/kill <id>` | Kill a background task |

### Discovery commands

| Command | Description |
|---------|-------------|
| `/commands` | List available slash commands |
| `/hooks` | List configured hooks |
| `/skills` | List available skills |
| `/mcp` | MCP server management |

### Session persistence

Sessions are stored in `~/.claude/sessions/` and can be:

- Continued with `--continue` or `-c`
- Resumed by ID with `--resume <session-id>`
- Forked with `--fork-session <session-id>`

[↑ Back to table of contents](#table-of-contents)

---

## Skill resources

For a comprehensive list of skills, templates, marketplaces, and tools, see **[Skill resources](./skill-resources.md)**.

[↑ Back to table of contents](#table-of-contents)

---

## Sources

- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) - Official documentation
- [Claude Code Guide](https://github.com/Cranot/claude-code-guide) - Auto-updated CLI reference
- [Agent Skill Standard](https://agentskills.io) - Cross-platform skill specification
- [Skill resources](./skill-resources.md) - Curated list of skills, templates, and tools

[↑ Back to table of contents](#table-of-contents)
