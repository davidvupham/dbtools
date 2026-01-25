# Chapter 9: Prompt patterns

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-2_Prompt_Engineering-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Apply reusable prompt patterns for common tasks
2. Create templates for structured output generation
3. Use JSON mode for reliable data extraction
4. Build a library of effective prompts for your domain

## Table of contents

- [Introduction](#introduction)
- [Output structure patterns](#output-structure-patterns)
- [JSON mode](#json-mode)
- [Template patterns](#template-patterns)
- [Task-specific patterns](#task-specific-patterns)
- [Building a prompt library](#building-a-prompt-library)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Prompt patterns are reusable structures that solve common problems. Rather than crafting prompts from scratch, you can adapt proven patterns to your specific needs. This chapter covers the most useful patterns for infrastructure and database work.

[↑ Back to Table of Contents](#table-of-contents)

## Output structure patterns

### The explicit format pattern

Tell the model exactly how to structure its response:

```text
EXPLICIT FORMAT PATTERN
═══════════════════════

Analyze this database error and respond using exactly this format:

## Summary
[One sentence describing the issue]

## Root Cause
[2-3 sentences explaining why this happened]

## Severity
[CRITICAL | HIGH | MEDIUM | LOW]

## Immediate Actions
1. [First action]
2. [Second action]

## Prevention
[How to prevent this in the future]
```

### The fill-in-the-blanks pattern

Provide a template with placeholders:

```text
FILL-IN-THE-BLANKS PATTERN
══════════════════════════

Complete this incident report based on the error log provided:

INCIDENT REPORT
───────────────
Incident ID: INC-______
Date/Time: ______
Severity: ______
System: ______

Description:
______

Root Cause:
______

Resolution:
______
```

### The sectioned response pattern

For long-form responses with clear sections:

```text
SECTIONED RESPONSE PATTERN
══════════════════════════

Create a migration plan for upgrading PostgreSQL from 14 to 16.

Structure your response with these sections:
1. PREREQUISITES - What must be in place before starting
2. BACKUP PLAN - How to backup and verify
3. UPGRADE STEPS - Numbered step-by-step procedure
4. VALIDATION - How to verify success
5. ROLLBACK - Steps if something goes wrong
6. ESTIMATED TIME - Time for each phase
```

[↑ Back to Table of Contents](#table-of-contents)

## JSON mode

**JSON mode** ensures the model outputs valid JSON, which is critical for programmatic processing.

### Basic JSON output

```text
Extract the following information from this log entry and return as JSON:
- timestamp
- severity (error, warning, info)
- component
- message

Log: 2026-01-24 10:15:32 ERROR [PostgreSQL] FATAL: password authentication failed

Return only valid JSON with no additional text:
```

Response:
```json
{
  "timestamp": "2026-01-24T10:15:32",
  "severity": "error",
  "component": "PostgreSQL",
  "message": "FATAL: password authentication failed"
}
```

### JSON with schema definition

Provide the exact schema you expect:

```text
Parse the database metrics and return JSON matching this schema:

{
  "database_name": "string",
  "connections": {
    "active": "integer",
    "idle": "integer",
    "max": "integer"
  },
  "performance": {
    "cache_hit_ratio": "float (0-1)",
    "transactions_per_second": "float"
  },
  "alerts": ["array of strings"]
}

Metrics:
Database: production_db
Active connections: 45, Idle: 12, Max configured: 200
Cache hit ratio: 98.5%
TPS: 1,250
Warning: Connection pool at 28% capacity

Return only valid JSON:
```

### JSON array output

For multiple items:

```text
Parse these error messages into a JSON array of objects:

Errors:
1. 10:15 - Connection timeout to host 10.0.0.5
2. 10:18 - Permission denied for user 'app'
3. 10:22 - Query timeout after 30 seconds

Each object should have: time, type, description

Return a JSON array:
```

Response:
```json
[
  {"time": "10:15", "type": "connection", "description": "Connection timeout to host 10.0.0.5"},
  {"time": "10:18", "type": "permission", "description": "Permission denied for user 'app'"},
  {"time": "10:22", "type": "timeout", "description": "Query timeout after 30 seconds"}
]
```

### Ensuring valid JSON

Tips for reliable JSON output:

| Technique | Example |
|:----------|:--------|
| Explicit instruction | "Return only valid JSON, no markdown" |
| Schema example | Provide a complete example |
| Validation note | "Ensure all strings are quoted" |
| API setting | Use model's JSON mode if available |

[↑ Back to Table of Contents](#table-of-contents)

## Template patterns

### The persona template

Reusable role definition:

```text
PERSONA: DATABASE_ANALYST
═════════════════════════

You are a senior database analyst with expertise in:
- PostgreSQL, SQL Server, and MongoDB administration
- Performance tuning and query optimization
- High availability and disaster recovery
- Security best practices and compliance

Communication style:
- Clear and technical, appropriate for DBAs
- Evidence-based recommendations
- Include specific commands/queries when applicable
- Always mention potential risks

When analyzing issues:
1. State your understanding of the problem
2. List diagnostic steps you would take
3. Provide recommendations with rationale
4. Include rollback/safety considerations
```

### The analysis template

For consistent problem analysis:

```text
ANALYSIS TEMPLATE
═════════════════

## Problem Statement
[Restate the problem in your own words]

## Current State
[What we know about the situation]

## Analysis

### Hypothesis 1: [Title]
- Evidence for: [points]
- Evidence against: [points]
- Likelihood: [High/Medium/Low]

### Hypothesis 2: [Title]
- Evidence for: [points]
- Evidence against: [points]
- Likelihood: [High/Medium/Low]

## Recommendation
[Primary recommendation based on analysis]

## Next Steps
1. [Action item]
2. [Action item]

## Risks
[Potential risks and mitigations]
```

### The comparison template

For evaluating options:

```text
COMPARISON TEMPLATE
═══════════════════

Compare these options for [topic]:

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| [Criterion 1] | | | |
| [Criterion 2] | | | |
| [Criterion 3] | | | |

## Analysis
[Discussion of trade-offs]

## Recommendation
[Which option and why]

## When to choose differently
[Scenarios where another option might be better]
```

[↑ Back to Table of Contents](#table-of-contents)

## Task-specific patterns

### Log analysis pattern

```text
LOG ANALYSIS PATTERN
════════════════════

Analyze the following log segment. For each error or warning:

1. TIMESTAMP: When it occurred
2. SEVERITY: Error, Warning, or Info
3. COMPONENT: Which system component
4. DESCRIPTION: What happened
5. LIKELY CAUSE: Why this might have happened
6. CORRELATION: Related entries (if any)
7. ACTION: Recommended next step

Then provide:
- SUMMARY: Overall health assessment
- PRIORITY ISSUES: Top 3 issues to address
- PATTERNS: Any recurring problems

Log:
[paste log here]
```

### Query optimization pattern

```text
QUERY OPTIMIZATION PATTERN
══════════════════════════

Analyze this SQL query for performance issues:

```sql
[query]
```

Environment:
- Database: [PostgreSQL/MySQL/SQL Server]
- Table size: [approximate rows]
- Expected frequency: [times per hour/minute]

Analyze and provide:

1. ISSUES FOUND
   For each issue:
   - What: Description
   - Why: Why it's a problem
   - Impact: High/Medium/Low

2. OPTIMIZED QUERY
   ```sql
   [improved query]
   ```

3. INDEX RECOMMENDATIONS
   ```sql
   [CREATE INDEX statements if needed]
   ```

4. EXPECTED IMPROVEMENT
   - Estimated speedup: [X times faster]
   - Rationale: [why]
```

### Configuration review pattern

```text
CONFIGURATION REVIEW PATTERN
════════════════════════════

Review this database configuration for [PostgreSQL/MySQL/etc.]:

```
[configuration]
```

Context:
- Workload: [OLTP/OLAP/Mixed]
- Hardware: [RAM, CPU, Storage type]
- Expected connections: [number]

Evaluate each setting against best practices:

| Setting | Current | Recommended | Priority | Rationale |
|---------|---------|-------------|----------|-----------|
| [setting] | [value] | [value] | [H/M/L] | [why] |

## Critical Issues
[Any settings that could cause problems]

## Quick Wins
[Easy changes with significant impact]

## Advanced Tuning
[Optimizations requiring more testing]
```

[↑ Back to Table of Contents](#table-of-contents)

## Building a prompt library

### Organization structure

```text
PROMPT LIBRARY ORGANIZATION
═══════════════════════════

prompts/
├── personas/
│   ├── database-analyst.md
│   ├── security-reviewer.md
│   └── sre-oncall.md
├── analysis/
│   ├── log-analysis.md
│   ├── query-optimization.md
│   └── performance-review.md
├── generation/
│   ├── runbook-template.md
│   ├── incident-report.md
│   └── documentation.md
└── extraction/
    ├── error-parsing.md
    ├── metrics-extraction.md
    └── config-parsing.md
```

### Prompt template file format

```markdown
# Query Optimization Analysis

## Purpose
Analyze SQL queries for performance issues and suggest improvements.

## Variables
- `{query}` - The SQL query to analyze
- `{database}` - Database type (PostgreSQL, MySQL, etc.)
- `{table_size}` - Approximate table sizes

## Prompt

You are a database performance specialist...

[full prompt text with {variables}]

## Example Usage

### Input
{query}: SELECT * FROM orders WHERE status = 'pending'
{database}: PostgreSQL
{table_size}: 10M rows

### Expected Output
[example of good output]

## Notes
- Works best with execution plans included
- For complex queries, use with chain-of-thought
```

### Version control prompts

Treat prompts like code:
- Store in Git repository
- Track changes with meaningful commits
- Review prompt changes in PRs
- Test prompts before deploying

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Output structure patterns ensure consistent, usable responses
- JSON mode enables programmatic processing of outputs
- Templates provide reusable starting points for common tasks
- Task-specific patterns encode domain expertise
- A prompt library saves time and ensures consistency

## Next steps

Continue to **[Chapter 10: Avoiding Pitfalls](./10_avoiding_pitfalls.md)** to learn about hallucinations, prompt injection, and other common problems.

[↑ Back to Table of Contents](#table-of-contents)
