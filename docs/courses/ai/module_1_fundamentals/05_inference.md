# Chapter 5: Inference

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-1_Fundamentals-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain the inference process step by step
2. Configure temperature and other sampling parameters
3. Understand latency factors and optimization strategies
4. Choose appropriate inference parameters for different tasks

## Table of contents

- [Introduction](#introduction)
- [The inference process](#the-inference-process)
- [Sampling parameters](#sampling-parameters)
- [Temperature](#temperature)
- [Top-p and top-k](#top-p-and-top-k)
- [Other parameters](#other-parameters)
- [Latency and performance](#latency-and-performance)
- [Practical guidelines](#practical-guidelines)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

**Inference** is the process of using a trained model to generate outputs. While training takes weeks and millions of dollars, inference is what you do every time you chat with an AI or call an API.

Understanding inference helps you:
- Control output quality and creativity
- Optimize for speed or quality
- Troubleshoot unexpected behavior
- Configure models appropriately for different tasks

[↑ Back to Table of Contents](#table-of-contents)

## The inference process

When you send a prompt, here's what happens:

```text
INFERENCE PIPELINE
══════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. TOKENIZATION                                                           │
│   ────────────────                                                          │
│   "Analyze this log" → [15711, 420, 1699]                                   │
│                                                                             │
│   2. EMBEDDING                                                              │
│   ────────────                                                              │
│   [15711, 420, 1699] → [[0.12, -0.34, ...], [0.56, 0.23, ...], ...]        │
│                                                                             │
│   3. FORWARD PASS                                                           │
│   ─────────────────                                                         │
│   Embeddings flow through transformer layers                                │
│   (Attention, feed-forward, normalization)                                  │
│                                                                             │
│   4. OUTPUT PROJECTION                                                      │
│   ─────────────────────                                                     │
│   Final hidden state → logits for all vocabulary tokens                     │
│   [2.3, -0.5, 1.7, 0.2, ...] (32,000+ values)                               │
│                                                                             │
│   5. SAMPLING                                                               │
│   ────────────                                                              │
│   Apply temperature, top-p, top-k to select next token                      │
│   Selected: token 578 = "The"                                               │
│                                                                             │
│   6. REPEAT                                                                 │
│   ─────────                                                                 │
│   Append "The" to input, go back to step 1                                  │
│   Continue until: stop token, max length, or stop sequence                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Autoregressive generation

LLMs generate text **one token at a time**, appending each generated token to the input for the next prediction:

```text
AUTOREGRESSIVE GENERATION
═════════════════════════

Step 1: Input: "Analyze this log:"
        Output: "The"

Step 2: Input: "Analyze this log: The"
        Output: "error"

Step 3: Input: "Analyze this log: The error"
        Output: "indicates"

Step 4: Input: "Analyze this log: The error indicates"
        Output: "a"

... continues until stop condition
```

This is why LLM latency scales with output length—each token requires a full forward pass.

[↑ Back to Table of Contents](#table-of-contents)

## Sampling parameters

After the model computes probabilities for all possible next tokens, **sampling parameters** control which token is selected.

```text
SAMPLING DECISION
═════════════════

Model output (logits → probabilities):

Token        Probability
─────        ───────────
"The"        0.35  ████████████████
"This"       0.25  ████████████
"Error"      0.15  ███████
"A"          0.10  █████
"First"      0.05  ██
[others]     0.10  █████

Without sampling: Always pick "The" (deterministic, boring)
With sampling: Pick according to probabilities (varied, creative)
```

### Key sampling parameters

| Parameter | Effect | Range |
|:----------|:-------|:------|
| **Temperature** | Controls randomness | 0.0 - 2.0 |
| **Top-p** | Nucleus sampling | 0.0 - 1.0 |
| **Top-k** | Limits candidate tokens | 1 - vocabulary size |
| **Max tokens** | Output length limit | 1 - context window |
| **Stop sequences** | Strings that end generation | List of strings |

[↑ Back to Table of Contents](#table-of-contents)

## Temperature

**Temperature** is the most important sampling parameter. It controls how "creative" or "random" the model's outputs are.

### How temperature works

```text
TEMPERATURE EFFECT ON PROBABILITIES
═══════════════════════════════════

Original probabilities (before temperature):
"The"=0.35, "This"=0.25, "Error"=0.15, "A"=0.10, others=0.15

Temperature = 0.0 (deterministic)
─────────────────────────────────
"The"=1.00   ████████████████████
"This"=0.00
"Error"=0.00
Always picks the highest probability token.

Temperature = 0.5 (focused)
─────────────────────────────────
"The"=0.55   ████████████████████
"This"=0.30  ███████████
"Error"=0.10 ████
Probabilities become more peaked.

Temperature = 1.0 (balanced)
─────────────────────────────────
"The"=0.35   ████████████████
"This"=0.25  ████████████
"Error"=0.15 ███████
Original distribution preserved.

Temperature = 1.5 (creative)
─────────────────────────────────
"The"=0.25   ████████████
"This"=0.22  ██████████
"Error"=0.18 █████████
"A"=0.15     ███████
Probabilities become more uniform.
```

### Temperature guidelines

| Temperature | Behavior | Use Cases |
|:------------|:---------|:----------|
| 0.0 | Deterministic—always picks most likely | Testing, debugging |
| 0.1 - 0.3 | Very focused, consistent | Code generation, factual Q&A |
| 0.4 - 0.7 | Balanced | General conversation, analysis |
| 0.8 - 1.0 | Creative but coherent | Writing, brainstorming |
| 1.0 - 1.5 | Very creative, may be inconsistent | Creative writing, exploration |
| > 1.5 | Chaotic, often incoherent | Rarely useful |

### Example: Same prompt, different temperatures

```text
Prompt: "Write a one-sentence description of PostgreSQL."

Temperature 0.1:
"PostgreSQL is a powerful, open-source relational database management system."

Temperature 0.5:
"PostgreSQL is an advanced open-source database system known for its reliability and feature set."

Temperature 1.0:
"PostgreSQL stands as a robust guardian of data, offering developers a reliable and extensible foundation for their applications."

Temperature 1.5:
"PostgreSQL dances between reliability and innovation, a database that whispers promises of ACID compliance to anxious developers."
```

[↑ Back to Table of Contents](#table-of-contents)

## Top-p and top-k

**Top-p** and **top-k** are additional sampling parameters that limit which tokens are considered.

### Top-k sampling

Limit sampling to the K most likely tokens:

```text
TOP-K SAMPLING
══════════════

Full distribution:
"The"=0.35, "This"=0.25, "Error"=0.15, "A"=0.10, "First"=0.05, ...

Top-k=3: Only consider top 3 tokens
─────────────────────────────────────
"The"=0.47    (0.35/0.75)
"This"=0.33   (0.25/0.75)
"Error"=0.20  (0.15/0.75)
(renormalized to sum to 1.0)

Low top-k (1-10): More focused, predictable
High top-k (40-100): More diverse, creative
```

### Top-p (nucleus) sampling

Include tokens until their cumulative probability reaches P:

```text
TOP-P SAMPLING
══════════════

Sorted by probability:
"The"=0.35  (cumulative: 0.35)
"This"=0.25 (cumulative: 0.60)
"Error"=0.15 (cumulative: 0.75)
"A"=0.10    (cumulative: 0.85)
"First"=0.05 (cumulative: 0.90)
...

Top-p=0.75: Include tokens until cumulative reaches 0.75
─────────────────────────────────────────────────────────
"The"=0.47   (0.35/0.75)
"This"=0.33  (0.25/0.75)
"Error"=0.20 (0.15/0.75)

Top-p=0.90: Include more tokens
─────────────────────────────────
"The", "This", "Error", "A", "First" all included
```

### Combining temperature with top-p/top-k

```text
RECOMMENDED COMBINATIONS
════════════════════════

Factual/Code tasks:
  temperature=0.1-0.3, top_p=0.9

Balanced conversation:
  temperature=0.7, top_p=0.9

Creative tasks:
  temperature=0.9-1.0, top_p=0.95
```

> [!TIP]
> Most practitioners adjust temperature and leave top-p at 0.9-0.95. Adjusting all three simultaneously can lead to unexpected interactions.

[↑ Back to Table of Contents](#table-of-contents)

## Other parameters

### Max tokens

Limits the maximum number of tokens to generate:

```python
# Example API call
response = client.generate(
    prompt="Explain PostgreSQL indexes",
    max_tokens=500  # Stop after 500 tokens even if not complete
)
```

**Guidelines:**
- Set based on expected output length + buffer
- Longer outputs = higher latency and cost
- Consider context window limits (input + output)

### Stop sequences

Strings that trigger the end of generation:

```python
response = client.generate(
    prompt="Write a SQL query:",
    stop=[";", "\n\n", "```"]  # Stop at semicolon, double newline, or code fence
)
```

**Use cases:**
- Stop at end of code block
- Stop at end of paragraph
- Stop before generating unwanted content

### Presence and frequency penalties

Discourage repetition:

| Parameter | Effect |
|:----------|:-------|
| **Presence penalty** | Penalize tokens that have appeared at all |
| **Frequency penalty** | Penalize tokens based on how often they appeared |

```text
Without penalties:
"The database is a database that stores database records in the database."

With frequency_penalty=0.5:
"The database is a system that stores records in persistent storage."
```

[↑ Back to Table of Contents](#table-of-contents)

## Latency and performance

### Latency components

```text
INFERENCE LATENCY BREAKDOWN
═══════════════════════════

Total latency = Prefill time + Generation time

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   PREFILL PHASE (process all input tokens at once)                          │
│   ─────────────                                                             │
│   • Scales with input length                                                │
│   • Can be parallelized on GPU                                              │
│   • Usually 10-100ms for typical prompts                                    │
│                                                                             │
│   GENERATION PHASE (one token at a time)                                    │
│   ─────────────────                                                         │
│   • Scales linearly with output length                                      │
│   • Sequential (each token depends on previous)                             │
│   • Typically 20-100ms per token (varies by model/hardware)                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Example:
  1,000 token input, 200 token output
  Prefill: 50ms
  Generation: 200 tokens × 30ms = 6,000ms
  Total: ~6 seconds
```

### Factors affecting speed

| Factor | Impact | Optimization |
|:-------|:-------|:-------------|
| Model size | Larger = slower | Use appropriate size for task |
| Quantization | Lower precision = faster | Q4 is 2x faster than Q8 |
| GPU VRAM | More = less swapping | Keep model in VRAM |
| Batch size | Multiple requests together | Batch when possible |
| Context length | Longer = slower (quadratic) | Minimize unnecessary context |
| Output length | Linear scaling | Set reasonable max_tokens |

### Tokens per second benchmarks

| Model | Hardware | Tokens/sec |
|:------|:---------|:-----------|
| 7B Q4 | RTX 4090 | 80-120 |
| 7B Q4 | RTX 3060 | 40-60 |
| 7B Q4 | M2 Pro | 30-50 |
| 7B Q4 | CPU (32 core) | 10-20 |
| 70B Q4 | A100 80GB | 30-50 |
| 70B Q4 | RTX 4090 | 5-10 (partial offload) |

[↑ Back to Table of Contents](#table-of-contents)

## Practical guidelines

### By task type

| Task | Temperature | Top-p | Notes |
|:-----|:------------|:------|:------|
| **Code generation** | 0.1-0.3 | 0.9 | Consistency is key |
| **Code explanation** | 0.3-0.5 | 0.9 | Some variety OK |
| **Factual Q&A** | 0.1-0.3 | 0.9 | Minimize hallucination |
| **Log analysis** | 0.2-0.4 | 0.9 | Reproducibility matters |
| **Documentation** | 0.5-0.7 | 0.9 | Balance clarity and variety |
| **Brainstorming** | 0.8-1.0 | 0.95 | Encourage creativity |
| **Creative writing** | 0.9-1.2 | 0.95 | Maximum variety |

### Common configurations

```python
# Factual/code tasks
config_factual = {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 1000
}

# Balanced conversation
config_balanced = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000
}

# Creative tasks
config_creative = {
    "temperature": 1.0,
    "top_p": 0.95,
    "max_tokens": 4000,
    "frequency_penalty": 0.3
}
```

### Debugging unexpected outputs

| Problem | Possible Cause | Solution |
|:--------|:---------------|:---------|
| Repetitive output | Low temp, no penalties | Add frequency_penalty |
| Inconsistent answers | High temperature | Lower temperature |
| Cuts off mid-sentence | max_tokens too low | Increase max_tokens |
| Doesn't follow format | Model capability | Try different model or more examples |
| Random/incoherent | Temperature too high | Lower temperature |

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **Inference** | Using a trained model to generate outputs |
| **Autoregressive** | Generating one token at a time, using previous as input |
| **Logits** | Raw model outputs before probability conversion |
| **Temperature** | Controls randomness/creativity in sampling |
| **Top-p** | Nucleus sampling—consider tokens until cumulative P |
| **Top-k** | Consider only top K most likely tokens |
| **Prefill** | Processing all input tokens (parallelizable) |
| **Generation** | Producing output tokens (sequential) |
| **Tokens per second** | Metric for generation speed |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Inference generates text one token at a time (autoregressive)
- Temperature controls creativity (0=deterministic, 1+=creative)
- Top-p and top-k limit which tokens are considered
- Latency has two components: prefill (input) and generation (output)
- Choose parameters based on task type: low temp for code, higher for creativity

## Next steps

You have completed Module 1! Continue to **[Module 2: Prompt Engineering](../module_2_prompt_engineering/06_prompt_anatomy.md)** to learn how to write effective prompts.

Before continuing, complete:
- 📝 **[Module 1 Exercises](./exercises/)**
- 📋 **[Module 1 Quiz](./quiz_module_1.md)**

## Additional resources

- [Hugging Face Generation Strategies](https://huggingface.co/docs/transformers/generation_strategies)
- [OpenAI API Parameters](https://platform.openai.com/docs/api-reference/chat)
- [Ollama Modelfile Parameters](https://ollama.com/docs/modelfile)

[↑ Back to Table of Contents](#table-of-contents)
