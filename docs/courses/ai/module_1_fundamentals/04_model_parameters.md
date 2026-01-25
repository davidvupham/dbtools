# Chapter 4: Model parameters

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-1_Fundamentals-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain what model parameters are
2. Understand the relationship between size and capability
3. Calculate VRAM requirements for different models
4. Explain how quantization reduces memory needs

## Table of contents

- [Introduction](#introduction)
- [What are parameters?](#what-are-parameters)
- [Parameter size and capability](#parameter-size-and-capability)
- [Memory requirements](#memory-requirements)
- [Quantization](#quantization)
- [Choosing the right size](#choosing-the-right-size)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

When you see model names like "Llama 3.1 70B" or "Qwen 2.5 7B," the number refers to **parameters**—the learned values in the neural network. Understanding parameters helps you:

- Choose appropriate models for your hardware
- Balance quality vs. speed tradeoffs
- Estimate infrastructure costs
- Make informed deployment decisions

[↑ Back to Table of Contents](#table-of-contents)

## What are parameters?

**Parameters** are the numerical values (weights) in a neural network that are learned during training. They encode the model's "knowledge."

```text
WHAT ARE PARAMETERS?
════════════════════

Think of parameters as adjustable knobs in the neural network:

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Input: "The server"                                                       │
│              │                                                              │
│              ▼                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      NEURAL NETWORK LAYER                           │   │
│   │                                                                     │   │
│   │   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐        │   │
│   │   │w₁   │   │w₂   │   │w₃   │   │w₄   │   │w₅   │   │...  │        │   │
│   │   │0.42 │   │-0.17│   │0.89 │   │0.03 │   │-0.56│   │     │        │   │
│   │   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘        │   │
│   │                                                                     │   │
│   │   Each w is a "parameter" - a learned value                         │   │
│   │   A 7B model has 7,000,000,000 of these values                      │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│              │                                                              │
│              ▼                                                              │
│   Output: Prediction for next token                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

During training, these values are adjusted to minimize prediction errors.
During inference, these values are fixed and used to generate outputs.
```

### Scale of modern models

| Model | Parameters | Written Out |
|:------|:-----------|:------------|
| Phi-3 Mini | 3.8B | 3,800,000,000 |
| Llama 3.1 8B | 8B | 8,000,000,000 |
| Qwen 2.5 14B | 14B | 14,000,000,000 |
| Llama 3.1 70B | 70B | 70,000,000,000 |
| Llama 3.1 405B | 405B | 405,000,000,000 |

[↑ Back to Table of Contents](#table-of-contents)

## Parameter size and capability

Generally, more parameters = more capability, but with diminishing returns.

```text
PARAMETER SIZE VS CAPABILITY
════════════════════════════

                    Capability
                         ▲
                         │
                    High │                           ●─────── 405B
                         │                      ●────────── 70B
                         │                 ●───────────── 30B
                         │           ●─────────────────── 13B
                         │     ●─────────────────────────── 7B
                         │●──────────────────────────────── 3B
                    Low  │
                         └────────────────────────────────────►
                              Parameters (billions)

Notice: The curve flattens as size increases.
Going from 7B to 70B is not 10x better.
```

### What more parameters provide

| Capability | Small (3-7B) | Medium (13-30B) | Large (70B+) |
|:-----------|:-------------|:----------------|:-------------|
| Basic Q&A | ✅ Good | ✅ Very good | ✅ Excellent |
| Code generation | ⚠️ Adequate | ✅ Good | ✅ Excellent |
| Complex reasoning | ⚠️ Limited | ✅ Good | ✅ Very good |
| Long-form writing | ⚠️ Adequate | ✅ Good | ✅ Excellent |
| Multi-step tasks | ❌ Weak | ⚠️ Adequate | ✅ Good |
| Rare knowledge | ❌ Limited | ⚠️ Some | ✅ More |

### The diminishing returns problem

```text
Example: Summarization task quality (hypothetical scores)

Model Size    Quality Score    Improvement
───────────   ─────────────    ───────────
3B            72%              baseline
7B            81%              +9%
13B           86%              +5%
30B           89%              +3%
70B           91%              +2%
405B          93%              +2%

Each size doubling provides smaller improvements.
```

[↑ Back to Table of Contents](#table-of-contents)

## Memory requirements

Parameters must be loaded into memory (RAM or VRAM) for inference. This is the primary constraint for running LLMs locally.

### Calculating memory requirements

Each parameter requires memory based on its precision:

```text
MEMORY CALCULATION
══════════════════

Memory = Parameters × Bytes per Parameter

Precision formats:
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   FP32 (32-bit float)     = 4 bytes per parameter                          │
│   FP16 (16-bit float)     = 2 bytes per parameter                          │
│   INT8 (8-bit integer)    = 1 byte per parameter                           │
│   INT4 (4-bit integer)    = 0.5 bytes per parameter                        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

Example: Llama 3.1 70B at different precisions:

FP32: 70B × 4 bytes = 280 GB
FP16: 70B × 2 bytes = 140 GB
INT8: 70B × 1 byte  = 70 GB
INT4: 70B × 0.5 bytes = 35 GB
```

### VRAM requirements table

| Model | FP16 | Q8 (8-bit) | Q4 (4-bit) |
|:------|:-----|:-----------|:-----------|
| Phi-3 3.8B | 7.6 GB | 3.8 GB | 2.3 GB |
| Llama 3.1 8B | 16 GB | 8 GB | 5 GB |
| Qwen 2.5 14B | 28 GB | 14 GB | 8 GB |
| Llama 3.1 70B | 140 GB | 70 GB | 40 GB |
| Llama 3.1 405B | 810 GB | 405 GB | 235 GB |

> [!NOTE]
> Actual VRAM usage is higher than just model weights due to:
> - KV cache for context
> - Activation memory during computation
> - Framework overhead
>
> Add ~20-30% buffer to these estimates.

[↑ Back to Table of Contents](#table-of-contents)

## Quantization

**Quantization** reduces the precision of model weights to decrease memory requirements while trying to maintain quality.

```text
QUANTIZATION EXPLAINED
══════════════════════

Original weight (FP16): 0.42578125
                        ↓
            ┌───────────────────────────────────────────────────────┐
            │                QUANTIZATION                           │
            │                                                       │
            │  FP16 → INT8: Round to nearest 8-bit value            │
            │  0.42578125 → 109 (scaled integer)                    │
            │                                                       │
            │  FP16 → INT4: Round to nearest 4-bit value            │
            │  0.42578125 → 7 (even more compressed)                │
            │                                                       │
            └───────────────────────────────────────────────────────┘
                        ↓
Quantized weight (Q4): 7 (with scale factor to reconstruct)
```

### Common quantization formats

| Format | Bits | Memory | Quality | Use Case |
|:-------|:-----|:-------|:--------|:---------|
| FP16 | 16 | 100% | Baseline | Training, high-precision inference |
| Q8 | 8 | 50% | ~99% | Production, quality-sensitive |
| Q6_K | 6 | 37% | ~98% | Balanced quality/size |
| Q5_K_M | 5 | 31% | ~96% | Good quality, smaller |
| Q4_K_M | 4 | 25% | ~94% | Common for local deployment |
| Q3_K_M | 3 | 19% | ~90% | Constrained environments |
| Q2_K | 2 | 12% | ~80% | Experimental, quality loss |

### Quality vs memory tradeoff

```text
QUANTIZATION QUALITY IMPACT
═══════════════════════════

                    Quality
                       ▲
                  100% │●─── FP16 (baseline)
                       │  ●─ Q8
                   95% │    ●─ Q6
                       │      ●─ Q5
                   90% │        ●─ Q4 (sweet spot for most users)
                       │          ●─ Q3
                   85% │            ●─ Q2
                       │
                       └─────────────────────────────────────►
                           Memory Usage (% of FP16)
                        100%  50%  37%  31%  25%  19%  12%
```

### GGUF format

**GGUF** (GPT-Generated Unified Format) is the standard format for quantized models, used by Ollama and llama.cpp:

```bash
# Model naming convention
llama-3.1-8b-instruct-q4_k_m.gguf
│         │          │
│         │          └── Quantization type
│         └── Model size
└── Model family
```

[↑ Back to Table of Contents](#table-of-contents)

## Choosing the right size

### By hardware tier

```text
HARDWARE RECOMMENDATIONS
════════════════════════

┌────────────────────────────────────────────────────────────────────────────┐
│ CONSUMER GPUs (8-12GB VRAM)                                                │
│ Examples: RTX 3060 12GB, RTX 4070                                          │
├────────────────────────────────────────────────────────────────────────────┤
│ Recommended: 7-8B models (Q4-Q5)                                           │
│ ✅ Llama 3.1 8B                                                            │
│ ✅ Qwen 2.5 7B                                                             │
│ ✅ Mistral 7B                                                              │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ PROSUMER GPUs (24GB VRAM)                                                  │
│ Examples: RTX 4090, RTX 6000 Ada                                           │
├────────────────────────────────────────────────────────────────────────────┤
│ Recommended: 13-14B models (Q4-Q8) or 30B (Q4)                             │
│ ✅ Qwen 2.5 14B                                                            │
│ ✅ Codestral 22B                                                           │
│ ⚠️ Llama 3.1 70B (Q3 only, quality loss)                                   │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ DATACENTER GPUs (40-80GB VRAM)                                             │
│ Examples: A100 40GB/80GB, H100                                             │
├────────────────────────────────────────────────────────────────────────────┤
│ Recommended: 70B models (Q4-Q8)                                            │
│ ✅ Llama 3.1 70B                                                           │
│ ✅ Qwen 2.5 72B                                                            │
│ ⚠️ Llama 3.1 405B (needs multiple GPUs)                                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ CPU-ONLY                                                                   │
│ Requires: 16GB+ RAM                                                        │
├────────────────────────────────────────────────────────────────────────────┤
│ Recommended: 3-4B models (Q4)                                              │
│ ✅ Phi-3 Mini 3.8B                                                         │
│ ⚠️ 7B models work but are slow (10-20 tokens/sec)                          │
└────────────────────────────────────────────────────────────────────────────┘
```

### By use case

| Use Case | Minimum Size | Recommended |
|:---------|:-------------|:------------|
| Chat/Q&A | 3B | 7B+ |
| Code completion | 7B | 14B+ |
| Code review/analysis | 7B | 14B+ |
| Complex reasoning | 13B | 70B |
| Tool calling | 7B | 7B+ (Qwen recommended) |
| Log analysis | 7B | 7B+ |
| Documentation | 7B | 14B+ |

### Decision framework

```text
CHOOSING A MODEL SIZE
═════════════════════

Q1: What's your VRAM?
    └── < 8GB  → 3-4B models or CPU inference
    └── 8-12GB → 7-8B models (Q4-Q5)
    └── 24GB   → 13-14B models or 7B at higher precision
    └── 40GB+  → 70B models

Q2: What's your quality requirement?
    └── Experimental/testing → Start small (7B Q4)
    └── Development          → 7-14B Q4-Q5
    └── Production           → 14B+ Q5-Q8

Q3: What's your latency requirement?
    └── Real-time (<1s)      → Smaller model or multiple GPUs
    └── Interactive (<5s)    → Match GPU to model size
    └── Batch processing     → Can use larger models

Q4: What tasks?
    └── Simple Q&A          → 7B is sufficient
    └── Code/reasoning      → 13B+ recommended
    └── Complex multi-step  → 70B recommended
```

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **Parameters** | Learned weights in a neural network (billions = B) |
| **VRAM** | Video RAM on a GPU, where model weights are stored |
| **Quantization** | Reducing precision to decrease memory requirements |
| **FP16** | 16-bit floating point (2 bytes per parameter) |
| **Q4/Q8** | 4-bit or 8-bit quantization |
| **GGUF** | Standard file format for quantized models |
| **KV cache** | Memory for storing attention key-value pairs |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Parameters are learned weights encoding model knowledge
- More parameters generally = better capability (with diminishing returns)
- Memory requirements scale with parameters × precision
- Quantization (Q4, Q8) dramatically reduces memory with minimal quality loss
- Choose model size based on hardware, use case, and quality requirements

## Next steps

Continue to **[Chapter 5: Inference](./05_inference.md)** to learn how models generate text and the parameters that control output.

## Additional resources

- [Hugging Face Model Hub](https://huggingface.co/models) - Browse model sizes
- [Ollama Model Library](https://ollama.com/library) - Pre-quantized models
- [GGUF Quantization Guide](https://github.com/ggerganov/llama.cpp/discussions/2094)
- [local-ai-hub Hardware Requirements](../../../projects/local-ai-hub/hardware-requirements.md)

[↑ Back to Table of Contents](#table-of-contents)
