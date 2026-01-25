# AI Engineering quick reference

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

A condensed reference for key AI concepts, commands, and patterns covered in the AI Engineering Course.

---

## LLM fundamentals

### Model size guide

| Size | VRAM (Q4) | Quality | Speed | Best For |
|:-----|:----------|:--------|:------|:---------|
| 3B | 2-3 GB | Basic | Very Fast | Simple tasks, edge devices |
| 7-8B | 4-5 GB | Good | Fast | Development, most tasks |
| 13-14B | 8-10 GB | Very Good | Medium | Production, complex reasoning |
| 30-34B | 18-20 GB | Excellent | Slow | High-quality outputs |
| 70B+ | 40+ GB | State-of-art | Very Slow | Critical applications |

### Temperature settings

| Temperature | Behavior | Use Case |
|:------------|:---------|:---------|
| 0.0 | Deterministic | Code, factual tasks |
| 0.3-0.5 | Balanced | General use |
| 0.7-1.0 | Creative | Brainstorming, writing |

### Token estimation

```text
1 token ≈ 4 characters in English
1 token ≈ ¾ of a word
100 tokens ≈ 75 words
1,000 tokens ≈ 750 words ≈ 1.5 pages
```

---

## Prompt engineering

### Prompt structure template

```text
[ROLE]
You are a [role] specializing in [domain].

[CONTEXT]
- Environment: [details]
- Current situation: [details]

[TASK]
[Clear, specific instruction]

[FORMAT]
Respond with:
1. [Expected output 1]
2. [Expected output 2]

[CONSTRAINTS]
- [Limitation 1]
- [Limitation 2]
```

### Key techniques

| Technique | When to Use | Example |
|:----------|:------------|:--------|
| **Zero-shot** | Simple, clear tasks | "Summarize this text" |
| **Few-shot** | Need specific format | "Here are 2 examples..." |
| **Chain-of-thought** | Complex reasoning | "Think step by step" |
| **Role prompting** | Domain expertise | "You are a DBA expert" |

### Reducing hallucinations

```text
If you don't know the answer or the information isn't in the provided
context, say "I don't have information about that" rather than guessing.
```

### Claude 4.x specific guidance

| Behavior | Previous Claude | Claude 4.x |
|:---------|:----------------|:-----------|
| **Instructions** | Inferred intent | Takes literally |
| **Verbosity** | More detailed | More concise |
| **Tool usage** | Automatic | Needs explicit direction |
| **Code exploration** | Proactive | More conservative |

**Key tips for Claude 4.x:**

```text
# Be explicit about going beyond basics
Create a dashboard. Include as many relevant features as possible.
Go beyond the basics to create a fully-featured implementation.

# Provide context for better results
Your response will be read by a text-to-speech engine, so avoid ellipses.

# For action-oriented behavior
<default_to_action>
By default, implement changes rather than only suggesting them.
</default_to_action>

# For conservative behavior
<do_not_act_before_instructions>
Do not change files unless clearly instructed to make changes.
</do_not_act_before_instructions>
```

---

## Model Context Protocol (MCP)

### MCP primitives

| Primitive | Controlled By | Use When |
|:----------|:--------------|:---------|
| **Tool** | AI Model | AI needs to take an action |
| **Resource** | Application | Providing context data |
| **Prompt** | User | User-initiated workflows |

### MCP server example (Python)

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_log",
            description="Analyze database logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"}
                },
                "required": ["content"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_log":
        result = analyze(arguments["content"])
        return [TextContent(type="text", text=result)]
```

### MCP client configuration (Cline)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["-m", "my_server"],
      "env": {
        "MY_VAR": "value"
      }
    }
  }
}
```

---

## Agentic AI

### Agent components

```text
┌─────────────────┐
│     PROMPT      │  ← Blueprint: role, goals, constraints
├─────────────────┤
│     MEMORY      │  ← Context: conversation, past actions
├─────────────────┤
│     TOOLS       │  ← Capabilities: APIs, functions
└─────────────────┘
```

### ReAct pattern

```text
Thought: I need to [reasoning about next step]
Action: tool_name(param="value")
Observation: [result from tool]
... repeat until goal achieved ...
Final Answer: [response to user]
```

### When to use agents vs simple LLM

| Use Agent When | Use Simple LLM When |
|:---------------|:--------------------|
| Multi-step tasks | Single-turn questions |
| Need external data | Context provided |
| Actions required | Text generation only |
| Iterative refinement | One-shot response |

---

## RAG (Retrieval-Augmented Generation)

### RAG pipeline

```text
INDEXING (offline):
Documents → Chunk → Embed → Store in Vector DB

QUERY (online):
Query → Embed → Search → Retrieve chunks → Generate response
```

### Chunking guidelines

| Setting | Recommended | Notes |
|:--------|:------------|:------|
| Chunk size | 512 tokens | Balance precision/context |
| Overlap | 50-100 tokens | Prevent context cutoff |
| Strategy | By paragraph/section | Preserve semantic units |

### RAG prompt template

```text
SYSTEM:
You are a helpful assistant. Answer questions using ONLY the provided
context. If the context doesn't contain the answer, say "I don't have
information about that in my knowledge base."

CONTEXT:
[Retrieved chunk 1]
[Retrieved chunk 2]
[Retrieved chunk 3]

USER: [question]
```

### Evaluation metrics (RAGAS)

| Metric | Measures |
|:-------|:---------|
| **Context Precision** | Relevance of retrieved chunks |
| **Context Recall** | Coverage of ground truth |
| **Faithfulness** | Response grounded in context |
| **Answer Relevancy** | Response addresses question |

---

## Local deployment (Ollama)

### Essential commands

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.1:8b
ollama pull qwen2.5:7b

# Run model
ollama run llama3.1:8b

# List models
ollama list

# Remove model
ollama rm model_name

# API call
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello"
}'
```

### Environment variables

```bash
export OLLAMA_HOST=0.0.0.0:11434      # Listen address
export OLLAMA_NUM_PARALLEL=4          # Concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2     # Models in memory
export OLLAMA_KEEP_ALIVE=5m           # Model unload timeout
```

### Model selection by task

| Task | Recommended Model | Notes |
|:-----|:------------------|:------|
| General | Llama 3.1 8B | Good balance |
| Tool calling | Qwen 2.5 7B | Native function calling |
| Coding | Qwen 2.5 Coder 7B | Code-optimized |
| Complex reasoning | Llama 3.1 70B | Higher quality |
| CPU-only | Phi-3 Mini 3.8B | Small footprint |

---

## Common patterns

### Structured output (JSON)

```text
Respond in JSON format:
{
  "severity": "critical|error|warning|info",
  "root_cause": "string",
  "recommendation": "string"
}
```

### Error handling in agents

```python
try:
    result = await call_tool(name, args)
except ToolNotFoundError:
    return "Tool not available"
except asyncio.TimeoutError:
    return "Operation timed out"
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return "An error occurred"
```

### Security checklist

- [ ] Sanitize inputs before passing to LLM
- [ ] Validate LLM outputs before executing
- [ ] Use least-privilege for tool permissions
- [ ] Log all tool calls for audit
- [ ] Implement rate limiting
- [ ] Add human-in-the-loop for critical actions

---

## Glossary

| Term | Definition |
|:-----|:-----------|
| **LLM** | Large Language Model |
| **Token** | Unit of text processing (~4 chars) |
| **Context window** | Max tokens model can see |
| **Temperature** | Randomness in outputs |
| **Hallucination** | Confident but incorrect output |
| **MCP** | Model Context Protocol |
| **RAG** | Retrieval-Augmented Generation |
| **Embedding** | Vector representation of text |
| **Agent** | Autonomous AI with tools |
| **ReAct** | Reasoning + Acting pattern |
| **VRAM** | GPU memory |
| **Quantization** | Model compression (Q4, Q8) |

---

## Additional resources

- [Claude Prompting Best Practices](../../reference/claude-prompting-best-practices.md) - Claude 4.x specific guidance
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP Course](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Ollama Documentation](https://ollama.com/docs)
- [local-ai-hub Project](../../projects/local-ai-hub/README.md)
