# Chapter 7: Basic techniques

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-2_Prompt_Engineering-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Apply zero-shot prompting for simple tasks
2. Use few-shot prompting with effective examples
3. Implement role prompting to guide model behavior
4. Choose the right technique for different situations

## Table of contents

- [Introduction](#introduction)
- [Zero-shot prompting](#zero-shot-prompting)
- [Few-shot prompting](#few-shot-prompting)
- [Role prompting](#role-prompting)
- [Combining techniques](#combining-techniques)
- [Choosing the right technique](#choosing-the-right-technique)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

This chapter covers the foundational prompting techniques that form the building blocks for all AI interactions. Mastering these basics will significantly improve your results before moving to advanced techniques.

[↑ Back to Table of Contents](#table-of-contents)

## Zero-shot prompting

**Zero-shot prompting** means asking the model to perform a task without providing any examples. You rely on the model's pre-trained knowledge.

### When to use zero-shot

- Simple, well-defined tasks
- Common tasks the model likely saw during training
- When you don't have good examples
- Initial testing before refining

### Zero-shot examples

**Simple classification:**
```text
Classify the following database error as either CONNECTION, QUERY, or PERMISSION:

Error: "FATAL: password authentication failed for user 'dbadmin'"

Classification: PERMISSION
```

**Summarization:**
```text
Summarize the following log entry in one sentence:

2026-01-24 10:15:32 ERROR PostgreSQL[1234]: could not connect to server:
Connection refused. Is the server running on host "db.example.com" (192.168.1.10)
and accepting TCP/IP connections on port 5432?

Summary: PostgreSQL connection failed because the server at db.example.com:5432
is not accepting connections.
```

**Extraction:**
```text
Extract the server name and port from this error message:

"Failed to connect to database server prod-db-01.internal:5432"

Server: prod-db-01.internal
Port: 5432
```

### Zero-shot limitations

| Limitation | Example |
|:-----------|:--------|
| **Ambiguous format** | Model might not match your expected output format |
| **Domain-specific tasks** | May not know your internal conventions |
| **Complex logic** | Multi-step reasoning often fails |
| **Unusual tasks** | Tasks not in training data perform poorly |

[↑ Back to Table of Contents](#table-of-contents)

## Few-shot prompting

**Few-shot prompting** provides examples of the task before asking the model to perform it. This significantly improves accuracy and format consistency.

### The few-shot pattern

```text
FEW-SHOT STRUCTURE
══════════════════

[Task description]

Example 1:
Input: [example input]
Output: [example output]

Example 2:
Input: [example input]
Output: [example output]

Now perform the task:
Input: [actual input]
Output:
```

### Few-shot examples

**Classification with examples:**
```text
Classify database errors by severity (CRITICAL, WARNING, INFO).

Error: "FATAL: the database system is shutting down"
Severity: CRITICAL

Error: "LOG: checkpoint starting: time"
Severity: INFO

Error: "WARNING: there is no transaction in progress"
Severity: WARNING

Error: "FATAL: too many connections for role 'app_user'"
Severity:
```

**Format standardization:**
```text
Convert error messages to our standard JSON format.

Input: Connection refused to host 10.0.0.5 port 5432
Output: {"type": "connection", "host": "10.0.0.5", "port": 5432, "message": "Connection refused"}

Input: Authentication failed for user admin
Output: {"type": "auth", "user": "admin", "message": "Authentication failed"}

Input: Query timeout after 30 seconds on table orders
Output:
```

### How many examples?

| Examples | Effect | Use When |
|:---------|:-------|:---------|
| 1 (one-shot) | Basic format guidance | Simple tasks, clear format |
| 2-3 | Good balance | Most cases |
| 4-5 | Strong pattern learning | Complex formats |
| 6+ | Diminishing returns | Rarely needed, uses tokens |

### Few-shot best practices

**Do:**
- Use diverse examples covering edge cases
- Keep examples consistent in format
- Order examples from simple to complex
- Match example difficulty to actual task

**Don't:**
- Use too many similar examples
- Include incorrect examples
- Make examples too long
- Mix different formats

[↑ Back to Table of Contents](#table-of-contents)

## Role prompting

**Role prompting** tells the model to act as a specific persona or expert. This leverages the model's knowledge about how that role would behave.

### Role prompting structure

```text
ROLE PROMPTING PATTERN
══════════════════════

You are a [role] with [qualifications/experience].

Your expertise includes:
- [Skill 1]
- [Skill 2]
- [Skill 3]

[Task or question]
```

### Effective role prompts

**Database expert:**
```text
You are a senior PostgreSQL database administrator with 15 years of experience
optimizing high-traffic OLTP systems.

Your expertise includes:
- Query optimization and execution plan analysis
- Index design and maintenance strategies
- Connection pooling and resource management
- Replication and high availability

Analyze this slow query and suggest optimizations:
[query]
```

**Security analyst:**
```text
You are a database security specialist who conducts security audits
for financial institutions.

Your focus areas include:
- Access control and privilege management
- Data encryption at rest and in transit
- Audit logging and compliance
- SQL injection prevention

Review this database configuration for security issues:
[config]
```

**Troubleshooting engineer:**
```text
You are an on-call database reliability engineer responding to a production incident.

Your approach:
- Systematic root cause analysis
- Clear communication of findings
- Prioritization of immediate fixes vs long-term solutions
- Documentation for post-incident review

We're experiencing intermittent connection timeouts. Here's what we know:
[symptoms]
```

### Role prompting guidelines

| Guideline | Reason |
|:----------|:-------|
| Be specific about expertise | Generic roles give generic answers |
| Match role to task | DBA for database, SRE for operations |
| Include constraints | "You prioritize security" shapes responses |
| Avoid unrealistic roles | "All-knowing oracle" doesn't help |

### Combining role with persona traits

```text
You are a database administrator who:
- Prioritizes data safety over performance
- Always suggests testing changes in non-prod first
- Explains technical concepts clearly for junior team members
- Includes rollback steps with any recommendation
```

[↑ Back to Table of Contents](#table-of-contents)

## Combining techniques

The most effective prompts often combine multiple techniques:

### Role + Few-shot

```text
You are a database log analyst specializing in PostgreSQL error classification.

Classify these errors by category (CONNECTION, QUERY, PERMISSION, RESOURCE):

Error: "could not connect to server: Connection refused"
Category: CONNECTION

Error: "permission denied for table users"
Category: PERMISSION

Error: "canceling statement due to statement timeout"
Category: QUERY

Now classify:
Error: "FATAL: sorry, too many clients already"
Category:
```

### Role + Zero-shot + Format

```text
You are a database performance analyst.

Analyze the following query and respond with:
1. ISSUE: One-line problem description
2. IMPACT: Estimated performance impact (Low/Medium/High)
3. FIX: Recommended solution

Query:
SELECT * FROM orders WHERE EXTRACT(YEAR FROM created_at) = 2026;
```

[↑ Back to Table of Contents](#table-of-contents)

## Choosing the right technique

### Decision framework

```text
TECHNIQUE SELECTION
═══════════════════

Q: Is the task simple and common?
│
├── YES → Try zero-shot first
│         └── If output format wrong → Add few-shot examples
│
└── NO → Is there a relevant expert role?
         │
         ├── YES → Use role prompting + few-shot
         │
         └── NO → Use detailed task description + few-shot
```

### Quick reference

| Task Type | Recommended Approach |
|:----------|:--------------------|
| Simple classification | Zero-shot or 1-shot |
| Format standardization | Few-shot (2-3 examples) |
| Technical analysis | Role + zero-shot |
| Domain-specific tasks | Role + few-shot |
| Creative generation | Role with persona traits |
| Complex multi-step | Role + chain-of-thought (next chapter) |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Zero-shot works for simple, common tasks without examples
- Few-shot (1-5 examples) dramatically improves format and accuracy
- Role prompting leverages the model's knowledge about expert behavior
- Combining techniques creates more effective prompts
- Choose technique based on task complexity and format requirements

## Next steps

Continue to **[Chapter 8: Advanced Techniques](./08_advanced_techniques.md)** to learn chain-of-thought, tree-of-thought, and other advanced prompting strategies.

[↑ Back to Table of Contents](#table-of-contents)
