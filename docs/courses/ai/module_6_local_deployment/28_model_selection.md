# Chapter 28: Model selection

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-6_Local_Deployment-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Compare popular open-source model families
2. Match models to specific use cases
3. Understand quantization trade-offs
4. Evaluate models for your requirements

## Table of contents

- [Introduction](#introduction)
- [Model families](#model-families)
- [Size and capability trade-offs](#size-and-capability-trade-offs)
- [Quantization](#quantization)
- [Use case recommendations](#use-case-recommendations)
- [Evaluation](#evaluation)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Choosing the right model is critical for balancing quality, speed, and resource usage. This chapter covers the major model families, their strengths, and how to select based on your needs.

[↑ Back to Table of Contents](#table-of-contents)

## Model families

### Overview of major families

| Family | Developer | Sizes | Strengths |
|:-------|:----------|:------|:----------|
| **Llama 3.1** | Meta | 8B, 70B, 405B | General purpose, multilingual |
| **Qwen 2.5** | Alibaba | 0.5B-72B | Tool use, coding, math |
| **Mistral** | Mistral AI | 7B, 8x7B | Efficient, fast |
| **Gemma 2** | Google | 2B, 9B, 27B | Efficient, instruction-following |
| **Phi-3** | Microsoft | 3.8B, 14B | Small but capable |
| **CodeLlama** | Meta | 7B, 13B, 34B | Code-specialized |

### Llama 3.1

```text
LLAMA 3.1 CHARACTERISTICS
═════════════════════════

Strengths:
✓ Strong general reasoning
✓ Good multilingual support (8 languages)
✓ 128K context window
✓ Well-documented, large community

Limitations:
✗ Larger memory footprint
✗ Slower than specialized models
✗ May be overkill for simple tasks

Best for:
- General chat applications
- Document analysis
- Multilingual needs
```

### Qwen 2.5

```text
QWEN 2.5 CHARACTERISTICS
════════════════════════

Strengths:
✓ Excellent tool/function calling
✓ Strong coding abilities
✓ Good mathematical reasoning
✓ Available in many sizes (0.5B to 72B)

Limitations:
✗ Smaller English training corpus
✗ Less community resources

Best for:
- Agent applications (tool use)
- Code generation
- Structured output (JSON)
```

### Mistral

```text
MISTRAL CHARACTERISTICS
═══════════════════════

Strengths:
✓ Very fast inference
✓ Efficient memory usage
✓ Strong for its size
✓ Good instruction following

Limitations:
✗ Smaller context (32K)
✗ Fewer size options

Best for:
- High-throughput applications
- Resource-constrained environments
- Chat applications
```

### Specialized models

| Model | Specialization | Use Case |
|:------|:---------------|:---------|
| CodeLlama | Programming | Code completion, review |
| DeepSeek-Coder | Programming | Multi-language coding |
| SQLCoder | SQL | Database queries |
| Meditron | Medical | Healthcare applications |
| Nous-Hermes | Chat | Conversational AI |

[↑ Back to Table of Contents](#table-of-contents)

## Size and capability trade-offs

### Size comparison

```text
MODEL SIZE VS CAPABILITY
════════════════════════

Quality
   ▲
   │                                    ● 70B
   │                          ● 30-40B
   │                 ● 13-14B
   │        ● 7-8B
   │  ● 3B
   │● 1B
   └────────────────────────────────────────► VRAM/Speed
        Fast/Low                    Slow/High
```

### Capability by size

| Size | VRAM (Q4) | Good For | Limitations |
|:-----|:----------|:---------|:------------|
| 1-3B | 2-4 GB | Simple tasks, classification | Limited reasoning |
| 7-8B | 6-8 GB | General use, coding | Complex multi-step tasks |
| 13-14B | 10-12 GB | Better reasoning | Slower inference |
| 30-40B | 20-24 GB | Strong reasoning | Requires good GPU |
| 70B+ | 40+ GB | Near-frontier | Multiple GPUs or expensive |

### When to use smaller models

```python
# Simple classification - 3B model sufficient
def classify_intent(text: str) -> str:
    """A 3B model can handle simple classification."""
    prompt = f"""Classify this database question into one category:
- PERFORMANCE
- BACKUP
- SECURITY
- CONFIGURATION
- OTHER

Question: {text}
Category:"""
    return client.generate(prompt, model="phi3:3.8b")


# Complex analysis - need larger model
def analyze_query_plan(plan: str) -> str:
    """Complex analysis needs 13B+ model."""
    prompt = f"""Analyze this PostgreSQL query plan and provide:
1. Performance bottlenecks
2. Suggested indexes
3. Query rewrites

Plan:
{plan}

Analysis:"""
    return client.generate(prompt, model="llama3.1:70b")
```

[↑ Back to Table of Contents](#table-of-contents)

## Quantization

### What is quantization?

```text
QUANTIZATION OVERVIEW
═════════════════════

Original (FP16): Each weight = 16 bits
                 7B model ≈ 14 GB

Quantized (Q4):  Each weight ≈ 4 bits
                 7B model ≈ 4 GB

Trade-off: Smaller size + faster, but slight quality loss
```

### Common quantization levels

| Quantization | Bits | Size Reduction | Quality Impact |
|:-------------|:-----|:---------------|:---------------|
| FP16 | 16 | None (baseline) | Best quality |
| Q8_0 | 8 | ~50% | Minimal loss |
| Q6_K | 6 | ~60% | Very slight loss |
| Q5_K_M | 5 | ~65% | Slight loss |
| Q4_K_M | 4 | ~70% | Noticeable on complex tasks |
| Q4_0 | 4 | ~75% | Good balance |
| Q3_K_M | 3 | ~80% | Moderate loss |
| Q2_K | 2 | ~85% | Significant loss |

### Choosing quantization

```text
QUANTIZATION DECISION
═════════════════════

Priority is quality?
├── YES → Q8_0 or Q6_K
│
└── NO → Priority is speed?
         ├── YES → Q4_0 or Q4_K_M
         │
         └── NO → Have limited VRAM?
                  ├── YES → Q3_K_M or Q4_0
                  │
                  └── NO → Q4_K_M (best balance)
```

### VRAM requirements by quantization

| Model | FP16 | Q8 | Q4 |
|:------|:-----|:---|:---|
| 7B | 14 GB | 8 GB | 5 GB |
| 13B | 26 GB | 14 GB | 8 GB |
| 34B | 68 GB | 36 GB | 20 GB |
| 70B | 140 GB | 75 GB | 40 GB |

[↑ Back to Table of Contents](#table-of-contents)

## Use case recommendations

### By task type

| Task | Recommended | Why |
|:-----|:------------|:----|
| Simple chat | Mistral 7B Q4 | Fast, good quality |
| Code completion | Qwen2.5-Coder 7B | Best tool calling |
| Document analysis | Llama 3.1 8B Q4 | Strong reasoning |
| SQL generation | SQLCoder 15B | Specialized |
| Embeddings | nomic-embed-text | Efficient, good quality |
| Classification | Phi-3 3.8B | Small, fast |

### By resource constraints

```text
RESOURCE-BASED SELECTION
════════════════════════

Available VRAM: 8 GB
├── General: Llama 3.1 8B Q4 or Mistral 7B Q4
├── Coding: Qwen2.5-Coder 7B Q4
└── Fast: Phi-3 3.8B Q4

Available VRAM: 16 GB
├── General: Llama 3.1 8B Q8 or 13B Q4
├── Coding: CodeLlama 13B Q4
└── Quality: Qwen2.5 14B Q4

Available VRAM: 24 GB
├── General: Llama 3.1 70B Q4 (partial offload)
├── Coding: DeepSeek-Coder 33B Q4
└── Quality: Mixtral 8x7B Q4

Available VRAM: 48+ GB
├── General: Llama 3.1 70B Q4-Q8
├── Coding: CodeLlama 70B
└── Quality: Any model, full precision
```

### Database operations specific

| Operation | Model | Reasoning |
|:----------|:------|:----------|
| Query optimization | Qwen2.5 14B | Good at structured analysis |
| Log analysis | Llama 3.1 8B | General text understanding |
| Schema design | Llama 3.1 70B | Complex reasoning needed |
| Simple monitoring | Phi-3 3.8B | Fast, simple classification |
| SQL generation | SQLCoder 15B | Specialized for SQL |

[↑ Back to Table of Contents](#table-of-contents)

## Evaluation

### Benchmarking your use case

```python
import time
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    model: str
    avg_latency_ms: float
    throughput_tokens_per_sec: float
    quality_score: float


def benchmark_model(
    client,
    model: str,
    test_prompts: list[str],
    expected_outputs: list[str] = None,
    num_runs: int = 3
) -> BenchmarkResult:
    """Benchmark a model on your specific tasks."""
    latencies = []
    total_tokens = 0

    for _ in range(num_runs):
        for prompt in test_prompts:
            start = time.time()
            response = client.generate(prompt, model=model)
            elapsed = time.time() - start

            latencies.append(elapsed * 1000)  # ms
            total_tokens += len(response.split())  # rough estimate

    avg_latency = sum(latencies) / len(latencies)
    throughput = total_tokens / (sum(latencies) / 1000)

    # Quality scoring (if expected outputs provided)
    quality_score = 0.0
    if expected_outputs:
        quality_score = evaluate_quality(
            client, model, test_prompts, expected_outputs
        )

    return BenchmarkResult(
        model=model,
        avg_latency_ms=avg_latency,
        throughput_tokens_per_sec=throughput,
        quality_score=quality_score
    )


def evaluate_quality(
    client,
    model: str,
    prompts: list[str],
    expected: list[str]
) -> float:
    """Simple quality evaluation."""
    scores = []

    for prompt, exp in zip(prompts, expected):
        response = client.generate(prompt, model=model)
        # Simple keyword overlap scoring
        response_words = set(response.lower().split())
        expected_words = set(exp.lower().split())
        overlap = len(response_words & expected_words) / len(expected_words)
        scores.append(overlap)

    return sum(scores) / len(scores)


# Usage
test_prompts = [
    "Explain PostgreSQL VACUUM in one paragraph",
    "Write a SQL query to find slow queries",
    "What causes database deadlocks?"
]

models_to_test = [
    "llama3.1:8b",
    "qwen2.5:7b",
    "mistral:7b"
]

results = []
for model in models_to_test:
    result = benchmark_model(client, model, test_prompts)
    results.append(result)
    print(f"{model}: {result.avg_latency_ms:.0f}ms, {result.throughput_tokens_per_sec:.0f} tok/s")
```

### Quality evaluation framework

```python
def comprehensive_evaluation(
    client,
    model: str,
    test_cases: list[dict]
) -> dict:
    """Evaluate model across multiple dimensions."""
    results = {
        "accuracy": [],
        "relevance": [],
        "completeness": [],
        "format_compliance": []
    }

    for test in test_cases:
        response = client.generate(test["prompt"], model=model)

        # Accuracy: Does it contain correct information?
        results["accuracy"].append(
            check_accuracy(response, test.get("facts", []))
        )

        # Relevance: Is the response on-topic?
        results["relevance"].append(
            check_relevance(response, test["prompt"])
        )

        # Completeness: Are all required elements present?
        results["completeness"].append(
            check_completeness(response, test.get("required_elements", []))
        )

        # Format: Does it follow the requested format?
        results["format_compliance"].append(
            check_format(response, test.get("expected_format"))
        )

    return {
        dimension: sum(scores) / len(scores)
        for dimension, scores in results.items()
    }
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Major model families (Llama, Qwen, Mistral) and their strengths
- How model size affects capability and resource requirements
- Quantization trade-offs between quality, speed, and memory
- Match models to specific use cases and constraints
- Evaluate models for your particular requirements

## Next steps

Continue to **[Chapter 29: Performance Tuning](./29_performance_tuning.md)** to learn how to optimize inference speed and throughput.

[↑ Back to Table of Contents](#table-of-contents)
