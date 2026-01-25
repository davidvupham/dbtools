# Chapter 6: Prompt anatomy

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-2_Prompt_Engineering-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Identify the components of an effective prompt
2. Structure prompts for different use cases
3. Write clear system prompts that guide AI behavior
4. Use formatting to improve output quality

## Table of contents

- [Introduction](#introduction)
- [What is a prompt?](#what-is-a-prompt)
- [Prompt components](#prompt-components)
- [System prompts](#system-prompts)
- [User messages](#user-messages)
- [Structuring for clarity](#structuring-for-clarity)
- [Output formatting](#output-formatting)
- [Common mistakes](#common-mistakes)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

A prompt is more than just a question you ask an AI. It is the complete set of instructions that guide the model's behavior. Understanding prompt anatomy is the foundation for writing effective prompts that produce reliable, useful outputs.

In this chapter, you will learn to dissect prompts into their components and construct them deliberately for different tasks.

[↑ Back to Table of Contents](#table-of-contents)

## What is a prompt?

A **prompt** is the entire input you provide to an LLM. This includes:

- Instructions about how the model should behave
- Context or background information
- The specific task or question
- Examples of desired outputs
- Constraints or formatting requirements

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROMPT STRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   System Prompt          (Sets behavior, role, constraints)                 │
│   ─────────────                                                             │
│   "You are a database expert. Respond in JSON format.                       │
│    Only provide technical information."                                     │
│                                                                             │
│   ──────────────────────────────────────────────────────                    │
│                                                                             │
│   Context                (Background information)                           │
│   ───────                                                                   │
│   "We are running PostgreSQL 15 on RHEL 8.                                  │
│    The server has 64GB RAM and 16 cores."                                   │
│                                                                             │
│   ──────────────────────────────────────────────────────                    │
│                                                                             │
│   User Message           (The actual task/question)                         │
│   ────────────                                                              │
│   "Analyze this error log and suggest configuration                         │
│    changes to prevent future occurrences:                                   │
│    [log content here]"                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Prompt components

### The five components of effective prompts

| Component | Purpose | Example |
|:----------|:--------|:--------|
| **Role** | Define who the AI should be | "You are a PostgreSQL performance expert" |
| **Context** | Provide background information | "Our database handles 10K transactions/sec" |
| **Task** | Specify what to do | "Analyze this slow query" |
| **Format** | Define output structure | "Respond with JSON containing fields..." |
| **Constraints** | Set boundaries | "Do not suggest solutions requiring downtime" |

### Example: Complete prompt with all components

```text
[ROLE]
You are a senior database administrator specializing in PostgreSQL performance
tuning with 15 years of experience.

[CONTEXT]
- Database: PostgreSQL 15.4
- Server: 64GB RAM, 16 CPU cores, NVMe storage
- Workload: OLTP with 10,000 transactions per second
- Current issue: Slow queries during peak hours (9 AM - 11 AM)

[TASK]
Analyze the following slow query log entry and provide optimization
recommendations:

```sql
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.created_at > '2026-01-01'
AND c.region = 'EMEA'
ORDER BY o.created_at DESC
LIMIT 100;
```

Query took 4.2 seconds (expected: <100ms)

[FORMAT]
Respond with:
1. Root cause analysis (2-3 sentences)
2. Recommended indexes (if any)
3. Query rewrite suggestions
4. Configuration changes (if applicable)

[CONSTRAINTS]
- Solutions must not require database downtime
- Prioritize index-based solutions over query rewrites
- Do not suggest partitioning (already evaluated and rejected)
```

[↑ Back to Table of Contents](#table-of-contents)

## System prompts

The **system prompt** sets the overall behavior and personality of the AI for the entire conversation. It is the most persistent part of your prompt.

### Effective system prompt structure

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SYSTEM PROMPT TEMPLATE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. IDENTITY                                                               │
│      "You are [role] specializing in [domain]."                             │
│                                                                             │
│   2. CAPABILITIES                                                           │
│      "You can [ability 1], [ability 2], and [ability 3]."                   │
│                                                                             │
│   3. BEHAVIOR                                                               │
│      "Always [do this]. Never [do that]."                                   │
│                                                                             │
│   4. OUTPUT STYLE                                                           │
│      "Respond in [format]. Use [tone]."                                     │
│                                                                             │
│   5. KNOWLEDGE BOUNDARIES                                                   │
│      "If you don't know, say so. Don't guess about [topic]."                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Example: Database assistant system prompt

```text
You are a database operations assistant specializing in PostgreSQL, SQL Server,
and MongoDB administration.

CAPABILITIES:
- Analyze error logs and identify root causes
- Explain query execution plans in plain English
- Suggest performance optimizations and index strategies
- Review database configurations for best practices

BEHAVIOR:
- Always verify your assumptions before making recommendations
- Provide evidence-based suggestions with expected impact
- Warn about potential risks before suggesting changes
- If uncertain, explicitly state your confidence level

OUTPUT:
- Use clear, technical language appropriate for DBAs
- Structure responses with headings and bullet points
- Include runnable SQL commands when suggesting changes
- Provide rollback steps for any recommended modifications

BOUNDARIES:
- Never suggest changes that could cause data loss without explicit warnings
- Do not provide specific performance numbers without data—qualify as estimates
- If asked about topics outside database administration, redirect politely
```

### System prompt best practices

| Do | Don't |
|:---|:------|
| Be specific about role and capabilities | Use vague descriptions like "helpful assistant" |
| Define clear boundaries | Leave behavior open-ended |
| Specify output format requirements | Assume the model knows your preferred format |
| Include safety constraints | Ignore potential harmful outputs |
| Keep it concise but complete | Write novel-length system prompts |

[↑ Back to Table of Contents](#table-of-contents)

## User messages

User messages contain the specific task, question, or information for the current interaction. They work within the context established by the system prompt.

### User message structure

```text
1. CONTEXT (if new information is needed)
   "Here is the error log from today..."

2. TASK (clear, specific instruction)
   "Identify the root cause and suggest a fix."

3. CONSTRAINTS (optional, task-specific)
   "Focus on connection-related errors only."
```

### Example: Effective vs ineffective user messages

**Ineffective:**
```text
The database is slow, help me fix it.
```

**Effective:**
```text
Our PostgreSQL database is experiencing slow response times during peak hours.

Environment:
- PostgreSQL 15 on Ubuntu 22.04
- 32GB RAM, 8 CPU cores
- Current connections: 150 (max_connections=200)

Symptoms:
- Query response time increased from 50ms to 2s
- Started occurring after deploying new feature on Monday
- Only affects SELECT queries, INSERTs are normal

Please analyze and suggest:
1. Immediate actions to restore performance
2. Diagnostic queries to identify the bottleneck
3. Preventive measures for the future
```

[↑ Back to Table of Contents](#table-of-contents)

## Structuring for clarity

Clear structure improves output quality. Use formatting to make your intent unambiguous.

### Use delimiters

Delimiters separate different parts of your prompt, preventing confusion.

```text
GOOD: Using clear delimiters

Analyze the following SQL query:
---
SELECT * FROM users WHERE status = 'active';
---
And this execution plan:
---
Seq Scan on users (cost=0.00..1.05 rows=5 width=96)
  Filter: (status = 'active'::text)
---

BAD: No delimiters

Analyze SELECT * FROM users WHERE status = 'active' and the plan
Seq Scan on users cost 0.00 to 1.05 rows 5 width 96 Filter status active
```

### Common delimiter patterns

| Pattern | Use Case | Example |
|:--------|:---------|:--------|
| `---` or `===` | Separating sections | Content above and below |
| Triple backticks | Code blocks | ` ```sql ... ``` ` |
| XML-style tags | Structured data | `<query>...</query>` |
| Numbered sections | Sequential items | `1. ... 2. ... 3. ...` |
| Bullet points | Unordered items | `- item 1 - item 2` |

### Use markdown formatting

Most LLMs understand markdown and produce better-formatted output when you use it.

```text
## Task
Analyze the query below for performance issues.

## Query
```sql
SELECT * FROM orders WHERE customer_id = 123;
```

## Expected Output
- List of issues found
- Severity rating (Critical/High/Medium/Low)
- Suggested fixes with code examples
```

[↑ Back to Table of Contents](#table-of-contents)

## Output formatting

Explicitly specify the format you want. LLMs follow formatting instructions well when given clear examples.

### JSON output

```text
Analyze the following log entry and respond in JSON format:

[log content]

Required JSON structure:
{
  "severity": "critical|error|warning|info",
  "category": "string describing the issue type",
  "root_cause": "string explaining why this happened",
  "recommended_action": "string with specific steps",
  "estimated_impact": "string describing consequences if not addressed"
}
```

### Structured text output

```text
Analyze the query and respond using this exact format:

ISSUE: [one-line description]
SEVERITY: [Critical/High/Medium/Low]
ROOT CAUSE: [2-3 sentence explanation]
RECOMMENDATION:
  1. [First step]
  2. [Second step]
  3. [Third step]
EXAMPLE FIX:
```sql
[corrected query here]
```
```

### Table output

```text
Compare these three database options and respond as a markdown table:

| Feature | PostgreSQL | MySQL | MongoDB |
|---------|------------|-------|---------|
| [Feature 1] | [value] | [value] | [value] |
...
```

[↑ Back to Table of Contents](#table-of-contents)

## Common mistakes

### Mistake 1: Vague instructions

```text
BAD:  "Make this query better"
GOOD: "Optimize this query to reduce execution time from 4s to under 500ms
       by suggesting appropriate indexes and query rewrites"
```

### Mistake 2: Missing context

```text
BAD:  "Why is my query slow?"
GOOD: "This PostgreSQL query takes 4s on a table with 10M rows.
       Here is the query, execution plan, and current indexes: [...]"
```

### Mistake 3: Conflicting instructions

```text
BAD:  "Be brief but also explain everything in detail"
GOOD: "Provide a 2-sentence summary, then a detailed explanation"
```

### Mistake 4: No output format

```text
BAD:  "Analyze this log"
GOOD: "Analyze this log and respond with:
       1. Error summary (1 sentence)
       2. Root cause
       3. Fix steps as a numbered list"
```

### Mistake 5: Overloading a single prompt

```text
BAD:  "Analyze this log, fix the query, update the config, write tests,
       document the changes, and create a runbook"
GOOD: "Analyze this log and identify the root cause.
       We'll address fixes in the next step."
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Prompts have five key components: role, context, task, format, and constraints
- System prompts set persistent behavior; user messages provide specific tasks
- Clear structure (delimiters, markdown, sections) improves output quality
- Explicit format instructions (JSON, tables, structured text) produce consistent output
- Common mistakes include vague instructions, missing context, and overloaded prompts

## Next steps

Continue to **[Chapter 7: Basic Techniques](./07_basic_techniques.md)** to learn zero-shot, few-shot, and role prompting techniques.

## Additional resources

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering Best Practices](https://claude.com/blog/best-practices-for-prompt-engineering)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

[↑ Back to Table of Contents](#table-of-contents)
