# Claude Code skill resources

**[← Back to Claude Code reference](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 18, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Claude_Code-blue)

> [!IMPORTANT]
> A curated collection of skills, templates, and resources for Claude Code and cross-platform AI agents.

## Table of contents

- [Official resources](#official-resources)
- [Community guides](#community-guides)
- [Skill repositories](#skill-repositories)
- [Template collections](#template-collections)
- [Marketplaces](#marketplaces)
- [Tools and CLIs](#tools-and-clis)
- [Standards and specifications](#standards-and-specifications)

---

## Official resources

| Resource | URL | Description |
|----------|-----|-------------|
| Claude Code documentation | https://docs.anthropic.com/en/docs/claude-code | Official Anthropic documentation |
| Anthropic Skills | https://github.com/anthropics/skills | Official example skills from Anthropic |

---

## Community guides

| Resource | URL | Description |
|----------|-----|-------------|
| Claude Code Guide | https://github.com/Cranot/claude-code-guide | Auto-updated comprehensive CLI reference (syncs every 2 days) |
| Awesome Claude Skills | https://github.com/ComposioHQ/awesome-claude-skills | Curated list of skills across 9 categories (docs, dev, data, marketing, creative, security) |
| ClaudeKit Skills | https://github.com/mrgoonie/claudekit-skills | 30+ skills with plugin marketplace; AI/ML, cloud, databases, testing |

### Claude Code Guide highlights

The [Cranot/claude-code-guide](https://github.com/Cranot/claude-code-guide) repository provides:

- **CLI flags reference** - All command-line options with examples
- **Built-in tools documentation** - Read, Write, Edit, Bash, Grep, Glob, Task, WebFetch, etc.
- **Permission model** - Detailed allow/deny configuration patterns
- **Sub-agents** - Delegating work to specialized Claude instances
- **Session management** - `--continue`, `--resume`, `--fork-session`, remote sessions
- **CLAUDE.md templates** - Community patterns for project context

Content is tagged as `[OFFICIAL]`, `[COMMUNITY]`, or `[EXPERIMENTAL]` for source clarity.

[↑ Back to table of contents](#table-of-contents)

---

## Skill repositories

### Infrastructure and DevOps

| Skill | URL | Author | Description |
|-------|-----|--------|-------------|
| Terraform Skill | https://github.com/antonbabenko/terraform-skill | Anton Babenko (AWS Hero) | Terraform/OpenTofu best practices, testing strategies, CI/CD workflows, security scanning |
| Infrastructure Showcase | https://github.com/diet103/claude-code-infrastructure-showcase | diet103 | Production-tested patterns: auto-activation hooks, dev docs, 10 agents, TypeScript microservices |

### Browser automation

| Skill | URL | Author | Description |
|-------|-----|--------|-------------|
| Agent Browse | https://github.com/browserbase/agent-browse | Browserbase | AI-powered web browsing using Stagehand; natural language browser control |

### Web development

| Skill | URL | Author | Description |
|-------|-----|--------|-------------|
| Vercel Labs Agent Skills | https://github.com/vercel-labs/agent-skills | Vercel | React best practices, web design guidelines, Vercel deployment |

### Project management and memory

| Skill | URL | Author | Description |
|-------|-----|--------|-------------|
| Project Memory | https://github.com/SpillwaveSolutions/project-memory | SpillwaveSolutions | Track bugs, decisions, key facts, and work history across sessions |
| Claude-Mem | https://github.com/thedotmack/claude-mem | Alex Newman | Automated memory capture with compression, vector search, web UI at localhost:37777 |

[↑ Back to table of contents](#table-of-contents)

---

## Template collections

| Resource | URL | Description |
|----------|-----|-------------|
| Claude Code Templates | https://github.com/davila7/claude-code-templates | 100+ templates including agents, commands, MCPs, hooks, and skills |
| AI Templates Web | https://aitmpl.com | Web interface for browsing and installing Claude Code templates |

### Claude Code Templates categories

The davila7/claude-code-templates repository includes:

| Category | Examples |
|----------|----------|
| Agents | Security auditing, performance optimization specialists |
| Commands | `/generate-tests`, `/optimize-bundle` |
| MCPs | GitHub, PostgreSQL, AWS integrations |
| Hooks | Pre-commit validation triggers |
| Skills | PDF processing, Excel automation |

**Installation:**

```bash
npx claude-code-templates
```

[↑ Back to table of contents](#table-of-contents)

---

## Marketplaces

| Marketplace | URL | Description |
|-------------|-----|-------------|
| SkillzWave | https://skillzwave.ai | Community skill marketplace |

[↑ Back to table of contents](#table-of-contents)

---

## Tools and CLIs

| Tool | URL | Description |
|------|-----|-------------|
| skilz CLI | https://github.com/agentskills/agentskills | Cross-platform skill installation tool |
| add-skill | `npx add-skill` | Install skills from GitHub repositories |

### skilz CLI usage

```bash
# Install globally
pip install skilz

# Install skill for all projects
skilz install https://github.com/username/skill-repo

# Install for specific project
skilz install https://github.com/username/skill-repo --project

# Install for specific agent
skilz install https://github.com/username/skill-repo --agent codex
skilz install https://github.com/username/skill-repo --agent gemini
```

[↑ Back to table of contents](#table-of-contents)

---

## Standards and specifications

| Resource | URL | Description |
|----------|-----|-------------|
| Agent Skill Standard | https://agentskills.io | Open specification for cross-platform AI agent skills |
| Specification docs | https://agentskills.io/specification | Detailed specification document |

### Supported platforms

The Agent Skill Standard is supported by 14+ platforms including:

- Claude Code
- OpenAI Codex
- Gemini CLI
- Cursor
- OpenCode
- GitHub Copilot
- VS Code

[↑ Back to table of contents](#table-of-contents)
