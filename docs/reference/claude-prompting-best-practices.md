# Claude prompting best practices

**[← Back to Reference Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Claude-blue)

> [!IMPORTANT]
> This guide covers Claude 4.x specific prompting techniques. Claude 4.x models (Sonnet 4.5, Haiku 4.5, Opus 4.5) are trained for more precise instruction following than previous generations.

## Table of contents

- [General principles](#general-principles)
- [Core techniques](#core-techniques)
- [Claude 4.x specific guidance](#claude-4x-specific-guidance)
- [Agentic and coding workflows](#agentic-and-coding-workflows)
- [Output formatting](#output-formatting)
- [Common pitfalls](#common-pitfalls)
- [Quick reference](#quick-reference)

---

## General principles

### Be explicit with your instructions

Claude 4.x models respond well to clear, explicit instructions. Being specific about your desired output enhances results. Previous Claude models would infer intent and expand on vague requests. Claude 4.x takes you literally and does exactly what you ask for.

**Less effective:**

```text
Create an analytics dashboard
```

**More effective:**

```text
Create an analytics dashboard. Include as many relevant features and
interactions as possible. Go beyond the basics to create a fully-featured
implementation.
```

### Add context to improve performance

Providing context or motivation behind your instructions helps Claude understand your goals and deliver more targeted responses.

**Less effective:**

```text
NEVER use ellipses
```

**More effective:**

```text
Your response will be read aloud by a text-to-speech engine, so never use
ellipses since the text-to-speech engine will not know how to pronounce them.
```

Claude is smart enough to generalize from the explanation.

### Be vigilant with examples and details

Claude 4.x models pay close attention to details and examples. Ensure your examples align with the behaviors you want to encourage and minimize behaviors you want to avoid.

[↑ Back to Table of Contents](#table-of-contents)

---

## Core techniques

### 1. Be clear and direct

State exactly what you want without assuming the model will infer your intent. Use direct action verbs and skip preambles.

| Approach | Example |
|:---------|:--------|
| **Vague** | "Can you help me with this code?" |
| **Direct** | "Refactor this function to use async/await" |

### 2. Use examples (few-shot prompting)

Demonstrate desired formats, tone, or style through examples.

**When to use:**
- Format is easier to show than describe
- Specific tone is needed
- Subtle patterns require clarification

**Guidance:** Start with one example (one-shot). Only add more examples (few-shot) if the output still doesn't match your needs.

### 3. Chain of thought prompting

Request step-by-step reasoning before answering, particularly valuable for complex analytical tasks.

**Three implementations:**

| Type | Description | Example |
|:-----|:------------|:--------|
| **Basic** | Add instruction | "Think step-by-step" |
| **Guided** | Provide stages | "First analyze X, then consider Y, finally conclude Z" |
| **Structured** | Use XML tags | `<thinking>...</thinking>` then `<answer>...</answer>` |

> [!NOTE]
> When using Extended Thinking mode (Claude 4.x), avoid adding "think step-by-step" instructions—the model manages its own reasoning budget. Adding your own instructions is redundant and wastes tokens.

### 4. Use XML tags for structure

Claude was trained on structured prompts and parses XML effectively.

```text
<context>
Database: PostgreSQL 15
Environment: Production
Issue: Slow queries during peak hours
</context>

<task>
Analyze the query and suggest optimizations.
</task>

<constraints>
- No downtime required
- Must maintain backward compatibility
</constraints>
```

### 5. Give Claude a role (system prompts)

Define the persona and expertise level.

```text
You are a senior PostgreSQL DBA with 15 years of experience in performance
tuning for high-traffic OLTP systems.
```

### 6. Prefill Claude's response

Start the response for the model to guide format, tone, or structure.

**Use cases:**
- Enforce JSON/XML output format
- Maintain specific voice
- Skip preambles

**Example (API):**

```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system="You are a database expert.",
    messages=[
        {"role": "user", "content": "Analyze this query"},
        {"role": "assistant", "content": "{"}  # Prefill to force JSON
    ]
)
```

### 7. Give permission to express uncertainty

Explicitly allow the AI to acknowledge limitations rather than guessing, reducing hallucinations.

```text
If you don't have enough information to answer accurately, say "I don't have
sufficient information about that" rather than guessing.
```

### 8. Data placement matters

Starting your prompt with your data and ending with your instructions can improve Claude's response quality by up to 30%.

```text
<data>
[Your data here - logs, code, documents]
</data>

<instructions>
[Your task here - what to do with the data]
</instructions>
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Claude 4.x specific guidance

### Long-horizon reasoning and state tracking

Claude 4.5 models excel at long-horizon reasoning tasks with exceptional state tracking capabilities. They maintain orientation across extended sessions by focusing on incremental progress.

**Best practices for multi-context window workflows:**

1. **Use structured formats for state data:** Track structured information (test results, task status) in JSON
2. **Use unstructured text for progress notes:** Freeform notes work well for tracking general progress
3. **Use git for state tracking:** Git provides a log of what's been done and checkpoints that can be restored
4. **Emphasize incremental progress:** Explicitly ask Claude to keep track of its progress

**Example state files:**

```json
// tests.json - Structured state
{
  "tests": [
    {"id": 1, "name": "authentication_flow", "status": "passing"},
    {"id": 2, "name": "user_management", "status": "failing"}
  ],
  "total": 200,
  "passing": 150,
  "failing": 50
}
```

```text
// progress.txt - Unstructured notes
Session 3 progress:
- Fixed authentication token validation
- Updated user model to handle edge cases
- Next: investigate user_management test failures (test #2)
```

### Communication style differences

Claude 4.5 models have a more concise and natural communication style:

- **More direct and grounded:** Provides fact-based progress reports rather than self-celebratory updates
- **More conversational:** Slightly more fluent and colloquial, less machine-like
- **Less verbose:** May skip detailed summaries for efficiency

If you want Claude to provide updates as it works:

```text
After completing a task that involves tool use, provide a quick summary of
the work you've done.
```

### Tool usage patterns

Claude 4.5 models benefit from explicit direction to use specific tools. If you say "can you suggest some changes," it may provide suggestions rather than implementing them.

**For action-oriented behavior:**

```text
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's
intent is unclear, infer the most useful likely action and proceed, using
tools to discover any missing details instead of guessing.
</default_to_action>
```

**For conservative behavior:**

```text
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed.
When the user's intent is ambiguous, default to providing information and
recommendations rather than taking action.
</do_not_act_before_instructions>
```

### Subagent orchestration

Claude 4.5 models demonstrate significantly improved native subagent orchestration capabilities. They recognize when tasks would benefit from delegating work to specialized subagents and do so proactively.

To adjust conservativeness:

```text
Only delegate to subagents when the task clearly benefits from a separate
agent with a new context window.
```

### Thinking sensitivity

When extended thinking is disabled, Claude Opus 4.5 is particularly sensitive to the word "think" and its variants. Replace "think" with alternative words:

| Instead of | Use |
|:-----------|:----|
| "think about" | "consider" |
| "I think" | "I believe" |
| "think through" | "evaluate" |

[↑ Back to Table of Contents](#table-of-contents)

---

## Agentic and coding workflows

### Encouraging code exploration

Claude can be overly conservative when exploring code. Add explicit instructions:

```text
ALWAYS read and understand relevant files before proposing code edits.
Do not speculate about code you have not inspected. If the user references
a specific file/path, you MUST open and inspect it before explaining or
proposing fixes.
```

### Minimizing hallucinations

```text
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a
specific file, you MUST read the file before answering. Give grounded and
hallucination-free answers.
</investigate_before_answering>
```

### Avoiding over-engineering

Claude 4.x models can sometimes over-engineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested.

```text
Avoid over-engineering. Only make changes that are directly requested or
clearly necessary. Keep solutions simple and focused.

Don't add features, refactor code, or make "improvements" beyond what was
asked. A bug fix doesn't need surrounding code cleaned up. A simple feature
doesn't need extra configurability.

Don't add error handling, fallbacks, or validation for scenarios that can't
happen. Trust internal code and framework guarantees. Only validate at system
boundaries (user input, external APIs).

Don't create helpers, utilities, or abstractions for one-time operations.
Don't design for hypothetical future requirements. The right amount of
complexity is the minimum needed for the current task.
```

### Parallel tool calling

Claude 4.x models excel at parallel tool execution. Sonnet 4.5 is particularly aggressive in firing off multiple operations simultaneously.

```text
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between
the tool calls, make all of the independent tool calls in parallel.
Prioritize calling tools simultaneously whenever the actions can be done
in parallel rather than sequentially. However, if some tool calls depend
on previous calls, do NOT call these tools in parallel.
</use_parallel_tool_calls>
```

### Avoiding hard-coded solutions

Claude can sometimes focus too heavily on making tests pass at the expense of general solutions.

```text
Please write a high-quality, general-purpose solution using the standard
tools available. Implement a solution that works correctly for all valid
inputs, not just the test cases. Do not hard-code values or create solutions
that only work for specific test inputs.

If the task is unreasonable or if any of the tests are incorrect, please
inform me rather than working around them.
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Output formatting

### Control response format

Several approaches work well for steering output formatting:

1. **Tell Claude what to do instead of what not to do**
   - Instead of: "Do not use markdown"
   - Try: "Your response should be composed of smoothly flowing prose paragraphs"

2. **Use XML format indicators**
   - Try: "Write the prose sections in `<flowing_prose>` tags"

3. **Match your prompt style to desired output**
   - Removing markdown from your prompt can reduce markdown in the output

### Minimize excessive formatting

```text
<avoid_excessive_markdown>
When writing reports or technical explanations, write in clear, flowing prose
using complete paragraphs and sentences. Use standard paragraph breaks for
organization and reserve markdown primarily for `inline code`, code blocks,
and simple headings.

DO NOT use ordered lists or unordered lists unless presenting truly discrete
items or the user explicitly requests a list. Instead of listing items with
bullets, incorporate them naturally into sentences.
</avoid_excessive_markdown>
```

### Structured output (JSON)

```text
Respond in JSON format with this exact structure:
{
  "severity": "critical|error|warning|info",
  "root_cause": "string explaining why this happened",
  "recommendation": "string with specific steps",
  "confidence": 0.0-1.0
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Common pitfalls

### Troubleshooting guide

| Problem | Solution |
|:--------|:---------|
| Too generic | Add specificity, examples, or ask to exceed basics |
| Off-topic | Be more explicit about goals; provide context |
| Inconsistent format | Add examples (few-shot) or use prefilling |
| Unreliable on complex tasks | Break into multiple chained prompts |
| Unnecessary preambles | Use prefilling or request direct answers |
| Made-up information | Permission to say "I don't know" |
| Suggestions vs implementation | Be explicit: "Change this" not "Suggest changes" |
| Over-engineering | Add explicit constraints about minimal changes |
| Tool undertriggering | Be explicit about which tools to use |
| Tool overtriggering | Dial back aggressive language ("MUST" → "Use when") |

### Common mistakes to avoid

- **Over-engineering prompts:** The best prompt achieves goals reliably with minimum necessary structure
- **Ignoring basics:** Always start with clear, explicit instructions
- **Assuming inference:** Don't assume Claude will infer your intent—specify clearly
- **Using every technique:** Start simple and add complexity only when testing shows improvement
- **Skipping iteration:** Test prompts and refine based on results
- **Outdated approaches:** Claude 4.x follows instructions more literally than previous versions

[↑ Back to Table of Contents](#table-of-contents)

---

## Quick reference

### Prompt template

```text
<context>
[Background information, environment details]
</context>

<task>
[Clear, specific instruction - what to do]
</task>

<format>
[Expected output structure]
</format>

<constraints>
[Boundaries, limitations, requirements]
</constraints>
```

### Key principles

| Principle | Description |
|:----------|:------------|
| **Be explicit** | State exactly what you want; Claude 4.x follows literally |
| **Provide context** | Explain why something matters for better results |
| **Use examples** | Show desired format/style with one or few examples |
| **Structure with XML** | Use tags for clear section separation |
| **Allow uncertainty** | Let Claude say "I don't know" to reduce hallucinations |
| **Iterate** | Test and refine prompts based on results |

### Claude 4.x changes from previous versions

| Behavior | Previous Claude | Claude 4.x |
|:---------|:----------------|:-----------|
| **Instruction following** | Inferred intent, expanded on requests | Takes instructions literally |
| **Verbosity** | More detailed by default | More concise, efficient |
| **Tool usage** | More automatic | Requires explicit direction |
| **Parallel execution** | Conservative | Aggressive parallel tool calls |
| **Code exploration** | Proactive | More conservative, needs prompting |

### Resources

- [Claude Platform Docs: Prompt Engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Claude 4.x Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Claude Blog: Best Practices](https://claude.com/blog/best-practices-for-prompt-engineering)
- [Anthropic Prompt Engineering Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

[↑ Back to Table of Contents](#table-of-contents)
