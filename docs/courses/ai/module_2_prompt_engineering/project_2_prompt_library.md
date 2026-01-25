# Project 2: Prompt Library

**[← Back to Course Index](../README.md)**

> **Difficulty:** Intermediate
> **Estimated Time:** 3-4 hours
> **Prerequisites:** Module 2 chapters completed

## Overview

Build a reusable prompt library with templates for common database operations tasks. The library should support variable substitution, prompt chaining, and output validation.

## Learning objectives

By completing this project, you will:

1. Design reusable prompt templates with variables
2. Implement prompt chaining for complex workflows
3. Add output validation and parsing
4. Create a testable prompt engineering system

## Requirements

### Functional requirements

1. **Template system**: Define prompts with `{variable}` placeholders
2. **Prompt chaining**: Connect prompts where output flows to next input
3. **Output parsing**: Extract structured data from responses
4. **Validation**: Validate outputs match expected schema
5. **Testing**: Unit tests for prompt behavior

### Prompt templates to implement

Create templates for these database operations:

1. **Query explanation**: Explain what a SQL query does
2. **Query optimization**: Suggest improvements for slow queries
3. **Schema analysis**: Analyze table structure and suggest improvements
4. **Error diagnosis**: Diagnose database error messages
5. **Documentation generation**: Generate documentation for tables/procedures

## Getting started

### Step 1: Template structure

```python
# prompts/base.py
from dataclasses import dataclass, field
from typing import Any
import re


@dataclass
class PromptTemplate:
    name: str
    system: str
    user: str
    variables: list[str] = field(default_factory=list)
    output_schema: dict | None = None

    def __post_init__(self):
        # Extract variables from template
        self.variables = list(set(
            re.findall(r'\{(\w+)\}', self.system + self.user)
        ))

    def render(self, **kwargs) -> dict:
        """Render template with variables."""
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing variables: {missing}")

        return {
            "system": self.system.format(**kwargs),
            "user": self.user.format(**kwargs)
        }
```

### Step 2: Define templates

```python
# prompts/database.py

QUERY_EXPLANATION = PromptTemplate(
    name="query_explanation",
    system="""You are a database expert. Explain SQL queries clearly and concisely.
Format your response as:
- Purpose: What the query does
- Tables: Tables involved
- Operations: Key operations performed
- Performance: Any performance concerns""",
    user="""Explain this {dialect} query:

```sql
{query}
```""",
    output_schema={
        "type": "object",
        "properties": {
            "purpose": {"type": "string"},
            "tables": {"type": "array", "items": {"type": "string"}},
            "operations": {"type": "array", "items": {"type": "string"}},
            "performance_concerns": {"type": "array", "items": {"type": "string"}}
        }
    }
)


QUERY_OPTIMIZATION = PromptTemplate(
    name="query_optimization",
    system="""You are a database performance expert. Analyze queries and suggest optimizations.
Always consider:
- Index usage
- Query structure
- Execution plan implications""",
    user="""Optimize this {dialect} query. Current execution time: {execution_time}

Query:
```sql
{query}
```

Table statistics:
{table_stats}

Suggest specific optimizations with explanations."""
)
```

### Step 3: Implement prompt chain

```python
# prompts/chains.py
from dataclasses import dataclass
from typing import Callable


@dataclass
class ChainStep:
    template: PromptTemplate
    output_parser: Callable[[str], dict] | None = None
    output_key: str = "output"


class PromptChain:
    """Chain multiple prompts together."""

    def __init__(self, steps: list[ChainStep]):
        self.steps = steps

    async def execute(self, llm, initial_vars: dict) -> dict:
        """Execute chain and return all outputs."""
        context = initial_vars.copy()

        for i, step in enumerate(self.steps):
            # Render prompt with current context
            rendered = step.template.render(**context)

            # Call LLM
            response = await llm.chat(
                system=rendered["system"],
                user=rendered["user"]
            )

            # Parse output if parser provided
            if step.output_parser:
                parsed = step.output_parser(response)
                context.update(parsed)
            else:
                context[step.output_key] = response

        return context


# Example: Query analysis chain
QUERY_ANALYSIS_CHAIN = PromptChain([
    ChainStep(
        template=QUERY_EXPLANATION,
        output_parser=parse_explanation,
        output_key="explanation"
    ),
    ChainStep(
        template=QUERY_OPTIMIZATION,
        output_key="optimization_suggestions"
    )
])
```

### Step 4: Output validation

```python
# prompts/validation.py
import json
from jsonschema import validate, ValidationError


class OutputValidator:
    """Validate LLM outputs against schemas."""

    @staticmethod
    def validate_json(response: str, schema: dict) -> dict:
        """Parse and validate JSON response."""
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        try:
            parsed = json.loads(json_str)
            validate(instance=parsed, schema=schema)
            return {"valid": True, "data": parsed}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"Invalid JSON: {e}"}
        except ValidationError as e:
            return {"valid": False, "error": f"Schema validation failed: {e.message}"}
```

## Implementation tasks

### Part 1: Core templates (40%)

- [ ] Implement `PromptTemplate` class with variable substitution
- [ ] Create 5 database operation templates
- [ ] Add output schemas for structured responses
- [ ] Implement template rendering with validation

### Part 2: Prompt chaining (30%)

- [ ] Implement `PromptChain` class
- [ ] Create query analysis chain (explain → optimize)
- [ ] Create error diagnosis chain (parse → diagnose → suggest)
- [ ] Handle chain failures gracefully

### Part 3: Testing (30%)

- [ ] Unit tests for template rendering
- [ ] Tests for output parsing and validation
- [ ] Integration tests with mock LLM
- [ ] Edge case handling (empty inputs, invalid variables)

## Expected usage

```python
from prompts import PromptLibrary, QUERY_EXPLANATION

# Simple template usage
library = PromptLibrary()
prompt = library.get("query_explanation")

rendered = prompt.render(
    dialect="PostgreSQL",
    query="SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'"
)

response = await llm.chat(**rendered)

# Chain usage
from prompts.chains import QUERY_ANALYSIS_CHAIN

results = await QUERY_ANALYSIS_CHAIN.execute(
    llm=llm,
    initial_vars={
        "dialect": "PostgreSQL",
        "query": slow_query,
        "execution_time": "5.2s",
        "table_stats": table_stats
    }
)

print(results["explanation"])
print(results["optimization_suggestions"])
```

## Evaluation criteria

| Criterion | Points |
|:----------|:-------|
| Template system with variables | 25 |
| Prompt chain implementation | 25 |
| Output validation and parsing | 20 |
| Test coverage | 20 |
| Code quality and documentation | 10 |
| **Total** | **100** |

---

**[Next Module →](../module_3_mcp/11_mcp_overview.md)**
