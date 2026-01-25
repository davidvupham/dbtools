# Chapter 8: Advanced techniques

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-2_Prompt_Engineering-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Apply chain-of-thought prompting for complex reasoning
2. Use self-consistency to improve reliability
3. Implement prompt chaining for multi-step tasks
4. Choose between tree-of-thought and other advanced techniques

## Table of contents

- [Introduction](#introduction)
- [Chain-of-thought prompting](#chain-of-thought-prompting)
- [Self-consistency](#self-consistency)
- [Prompt chaining](#prompt-chaining)
- [Tree-of-thought](#tree-of-thought)
- [Reflection and self-critique](#reflection-and-self-critique)
- [Choosing the right technique](#choosing-the-right-technique)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Basic techniques handle simple tasks well, but complex reasoning requires more sophisticated approaches. This chapter covers advanced techniques that significantly improve accuracy on multi-step problems.

[↑ Back to Table of Contents](#table-of-contents)

## Chain-of-thought prompting

**Chain-of-thought (CoT)** prompting instructs the model to show its reasoning step by step before giving a final answer. This dramatically improves accuracy on reasoning tasks.

### The basic pattern

```text
CHAIN-OF-THOUGHT PATTERN
════════════════════════

Without CoT:
"How many concurrent connections can our server handle?"
→ "About 500" (may be wrong)

With CoT:
"How many concurrent connections can our server handle?
Think through this step by step."
→ "Let me work through this:
   1. Current max_connections is set to 200
   2. Each connection uses approximately 5MB of RAM
   3. The server has 16GB RAM, with 4GB used by the OS
   4. Available RAM: 16GB - 4GB = 12GB
   5. Maximum theoretical connections: 12GB / 5MB ≈ 2,400
   6. But max_connections is 200, so that's the actual limit
   7. With connection pooling overhead, practical limit is ~180

   Answer: The server can handle approximately 180 concurrent connections."
```

### Zero-shot CoT

Simply add "Think step by step" or "Let's work through this":

```text
Analyze why this query might be slow and suggest optimizations.
Think step by step.

Query: SELECT * FROM orders o
       JOIN customers c ON o.customer_id = c.id
       WHERE o.created_at > '2025-01-01'
       ORDER BY o.total DESC
       LIMIT 100;
```

### Few-shot CoT

Provide examples with reasoning chains:

```text
Diagnose database performance issues by analyzing the symptoms step by step.

Problem: Database CPU usage spikes to 100% every hour.
Analysis:
1. First, identify what's happening hourly - likely a scheduled job
2. Check cron jobs and scheduled tasks for hourly patterns
3. Common culprits: backup jobs, statistics updates, report generation
4. Verify with pg_stat_activity during the spike
5. Check if queries are using excessive CPU (missing indexes, full table scans)
Diagnosis: Likely a scheduled job running an inefficient query. Check crontab and
query logs during the spike window.

Problem: Response times increase from 50ms to 2 seconds during peak hours.
Analysis:
1. First, identify if it's query-related or connection-related
2. Check connection pool saturation - are we hitting max connections?
3. If connections OK, check for lock contention during high concurrency
4. Examine query plans - could be statistics out of date under load
5. Consider if shared_buffers are adequate for working set
Diagnosis: [Model continues reasoning]
```

### When CoT helps most

| Task Type | CoT Improvement | Example |
|:----------|:----------------|:--------|
| Math/calculations | Very high | Resource capacity planning |
| Multi-step logic | High | Root cause analysis |
| Comparisons | Medium | Choosing between options |
| Simple factual | Low | Basic Q&A |

[↑ Back to Table of Contents](#table-of-contents)

## Self-consistency

**Self-consistency** generates multiple independent reasoning paths and takes the majority answer. This reduces errors from individual reasoning chains.

### How it works

```text
SELF-CONSISTENCY PROCESS
════════════════════════

Problem: "Should we add an index on the orders.customer_id column?"

Generate 5 independent CoT responses:

Response 1: "Let me analyze...
             Orders table has 10M rows, customer_id is frequently in WHERE...
             → YES, add index"

Response 2: "Considering the query patterns...
             Most queries join on customer_id, table is write-heavy but reads dominate...
             → YES, add index"

Response 3: "Looking at this systematically...
             The column has high cardinality, queries would benefit...
             → YES, add index"

Response 4: "Analyzing trade-offs...
             Index maintenance cost vs query improvement...
             → YES, add index"

Response 5: "Evaluating the need...
             Current queries are fast, might add unnecessary overhead...
             → NO, don't add index"

Final answer (majority vote): YES, add index (4/5)
```

### Implementing self-consistency

```python
# Pseudo-code for self-consistency
def self_consistent_answer(prompt, n=5, temperature=0.7):
    answers = []
    for _ in range(n):
        response = model.generate(prompt, temperature=temperature)
        answer = extract_final_answer(response)
        answers.append(answer)

    return majority_vote(answers)
```

### When to use self-consistency

| Situation | Use Self-Consistency? |
|:----------|:----------------------|
| Critical decisions | Yes—higher confidence |
| Ambiguous questions | Yes—multiple perspectives |
| Simple tasks | No—overkill, wastes tokens |
| Deterministic tasks | No—all answers will be same |

[↑ Back to Table of Contents](#table-of-contents)

## Prompt chaining

**Prompt chaining** breaks complex tasks into sequential steps, where the output of one prompt becomes input for the next.

### Basic chaining

```text
PROMPT CHAINING
═══════════════

Complex task: "Analyze this error log, identify issues, and create a runbook"

                Instead of one giant prompt...

                        ┌───────────┐
                        │  Step 1   │
                        │ Parse log │
                        │ entries   │
                        └─────┬─────┘
                              │ [parsed entries]
                              ▼
                        ┌───────────┐
                        │  Step 2   │
                        │ Classify  │
                        │ errors    │
                        └─────┬─────┘
                              │ [classified errors]
                              ▼
                        ┌───────────┐
                        │  Step 3   │
                        │ Identify  │
                        │ root cause│
                        └─────┬─────┘
                              │ [root cause analysis]
                              ▼
                        ┌───────────┐
                        │  Step 4   │
                        │ Generate  │
                        │ runbook   │
                        └───────────┘
```

### Chaining example

**Step 1: Extract errors**
```text
Extract all error messages from this log, returning them as a numbered list:
[log content]
```

**Step 2: Classify (using Step 1 output)**
```text
For each error below, classify as CRITICAL, WARNING, or INFO:
1. "FATAL: the database system is shutting down"
2. "ERROR: deadlock detected"
3. "WARNING: archive command failed"
[Step 1 output]
```

**Step 3: Analyze (using Step 2 output)**
```text
Based on these classified errors, identify the root cause and recommended actions:
[Step 2 output]
```

### Chaining patterns

| Pattern | Use Case |
|:--------|:---------|
| **Sequential** | Each step depends on previous |
| **Parallel + Merge** | Independent analyses combined |
| **Conditional** | Next step depends on previous result |
| **Iterative** | Repeat until condition met |

### Trade-offs

| Advantage | Disadvantage |
|:----------|:-------------|
| Better accuracy per step | Higher latency (multiple calls) |
| Easier debugging | More complex orchestration |
| Focused context per step | More total tokens used |
| Reusable components | Potential error propagation |

[↑ Back to Table of Contents](#table-of-contents)

## Tree-of-thought

**Tree-of-thought (ToT)** explores multiple reasoning paths simultaneously, evaluating and pruning branches to find the best solution.

### Concept

```text
TREE-OF-THOUGHT
═══════════════

Problem: "What's causing intermittent database timeouts?"

                    ┌─────────────────┐
                    │    Problem      │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │Network  │        │Database │        │Application│
    │issues?  │        │issues?  │        │issues?    │
    └────┬────┘        └────┬────┘        └────┬──────┘
         │                  │                  │
    ┌────┴────┐        ┌────┴────┐        ┌───┴───┐
    │Evaluate:│        │Evaluate:│        │Evaluate:│
    │Score: 3 │        │Score: 8 │        │Score: 5 │
    └─────────┘        └────┬────┘        └─────────┘
                            │
                      Explore further
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         ┌────────┐   ┌──────────┐   ┌────────┐
         │Locks?  │   │Resources?│   │Queries?│
         │Score: 9│   │Score: 6  │   │Score: 7│
         └────────┘   └──────────┘   └────────┘
              │
              ▼
         Best path: Database → Lock contention
```

### Simple ToT implementation

```text
You are analyzing a database performance issue. For each potential cause,
rate it 1-10 based on likelihood given the symptoms.

Symptoms: Intermittent 30-second query timeouts, CPU normal, connections under limit.

Consider these branches:
1. Lock contention: [Your analysis and score]
2. Network latency: [Your analysis and score]
3. Resource exhaustion: [Your analysis and score]
4. Query plan regression: [Your analysis and score]

Based on scores, what's the most likely root cause and what should we investigate?
```

### When to use ToT

| Scenario | Recommended? |
|:---------|:-------------|
| Single clear solution | No—overkill |
| Multiple viable paths | Yes |
| High-stakes decisions | Yes |
| Quick tasks | No—too slow |

[↑ Back to Table of Contents](#table-of-contents)

## Reflection and self-critique

**Reflection** asks the model to review and improve its own output.

### Basic reflection pattern

```text
REFLECTION PATTERN
══════════════════

Step 1: Generate initial response
Step 2: Ask model to critique its response
Step 3: Ask model to improve based on critique
```

### Example

**Step 1: Initial generation**
```text
Prompt: Write a SQL query to find the top 10 customers by order value.

Response: SELECT customer_id, SUM(total) as total_value
          FROM orders
          GROUP BY customer_id
          ORDER BY total_value DESC
          LIMIT 10;
```

**Step 2: Self-critique**
```text
Review your SQL query above. Identify any:
1. Performance issues
2. Missing edge cases
3. Best practice violations

Critique:
1. Missing customer name—need to JOIN with customers table
2. No date filter—might want recent orders only
3. Should alias the table for clarity
4. Consider NULL handling for total column
```

**Step 3: Improved version**
```text
Based on your critique, write an improved version:

Response:
SELECT c.id, c.name, COALESCE(SUM(o.total), 0) as total_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.created_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY c.id, c.name
ORDER BY total_value DESC
LIMIT 10;
```

[↑ Back to Table of Contents](#table-of-contents)

## Choosing the right technique

### Decision matrix

| Task | Technique | Why |
|:-----|:----------|:----|
| Single-step reasoning | Zero/few-shot | Simple enough |
| Multi-step calculation | Chain-of-thought | Shows work, catches errors |
| Critical decision | Self-consistency | Multiple validations |
| Complex workflow | Prompt chaining | Break into manageable steps |
| Open-ended exploration | Tree-of-thought | Consider multiple paths |
| Quality-sensitive output | Reflection | Self-improvement |

### Complexity vs accuracy trade-off

```text
                        Accuracy
                           ▲
                      High │     ┌─ Self-consistency + CoT
                           │   ┌─┼─ Tree-of-thought
                           │  ┌┼─┼─ Prompt chaining
                           │ ┌┼─┼─┼─ Chain-of-thought
                           │┌┼─┼─┼─┼─ Few-shot
                       Low │┼─┼─┼─┼─┼─ Zero-shot
                           └─────────────────────────────►
                             Low                      High
                                    Complexity/Cost
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Chain-of-thought dramatically improves reasoning by showing work
- Self-consistency uses multiple attempts to increase reliability
- Prompt chaining breaks complex tasks into manageable steps
- Tree-of-thought explores multiple solution paths
- Reflection enables self-improvement of outputs
- Choose techniques based on task complexity and accuracy requirements

## Next steps

Continue to **[Chapter 9: Prompt Patterns](./09_prompt_patterns.md)** to learn reusable patterns and templates for common tasks.

[↑ Back to Table of Contents](#table-of-contents)
