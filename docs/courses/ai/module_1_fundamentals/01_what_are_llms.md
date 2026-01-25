# Chapter 1: What are Large Language Models?

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-1_Fundamentals-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain what a Large Language Model (LLM) is in simple terms
2. Distinguish between training and inference phases
3. Identify what LLMs can and cannot do
4. Understand why "large" matters in language models

## Table of contents

- [Introduction](#introduction)
- [The basics: What is an LLM?](#the-basics-what-is-an-llm)
- [Training vs inference](#training-vs-inference)
- [How LLMs generate text](#how-llms-generate-text)
- [What LLMs can and cannot do](#what-llms-can-and-cannot-do)
- [Why "large" matters](#why-large-matters)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Large Language Models (LLMs) power tools like ChatGPT, Claude, and the local AI systems you will build in this course. Before diving into prompt engineering or building agents, you need to understand what these models actually are and how they work at a conceptual level.

This chapter provides that foundation without requiring deep mathematical knowledge.

[↑ Back to Table of Contents](#table-of-contents)

## The basics: What is an LLM?

A **Large Language Model (LLM)** is a type of artificial intelligence trained to understand and generate human language. Think of it as an extremely sophisticated autocomplete system that can write paragraphs instead of just words.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WHAT IS AN LLM?                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                      ┌─────────────────┐              │
│   │   Your Input    │                      │    Response     │              │
│   │                 │                      │                 │              │
│   │ "Explain why    │    ┌───────────┐     │ "The database   │              │
│   │  the database   │───►│    LLM    │────►│  crashed due    │              │
│   │  crashed"       │    └───────────┘     │  to a memory    │              │
│   │                 │                      │  allocation..." │              │
│   └─────────────────┘                      └─────────────────┘              │
│                                                                             │
│   The LLM predicts the most likely sequence of words to follow your input   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key insight

LLMs do not "think" or "understand" in the human sense. They predict the most probable next word (token) based on patterns learned during training. This is both their strength (they can generate fluent, contextual text) and their limitation (they can confidently produce incorrect information).

[↑ Back to Table of Contents](#table-of-contents)

## Training vs inference

Understanding the difference between training and inference is crucial for working with LLMs effectively.

### Training phase (done by model creators)

Training is the process of teaching an LLM by exposing it to massive amounts of text data. This is done by companies like Meta (Llama), Alibaba (Qwen), and Mistral.

```text
TRAINING PHASE
══════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Training Data                        Neural Network                       │
│   ─────────────                        ──────────────                       │
│   • Books                                                                   │
│   • Websites             Training        Billions of                        │
│   • Code repositories    ─────────►      learned patterns                   │
│   • Scientific papers    (weeks on       (parameters)                       │
│   • Conversations        GPU clusters)                                      │
│                                                                             │
│   Size: Terabytes                        Output: Model file                 │
│   of text                                (4-400 GB)                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key points about training:**

- Requires massive compute resources (thousands of GPUs for weeks/months)
- Costs millions of dollars for large models
- You do not do this—you use pre-trained models
- The result is a model file containing learned patterns (parameters)

### Inference phase (what you do)

Inference is using a trained model to generate responses. This is what happens when you chat with an AI or call an API.

```text
INFERENCE PHASE
═══════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Your Prompt              Pre-trained Model              Generated Output  │
│   ───────────              ────────────────              ────────────────   │
│                                                                             │
│   "Analyze this     ───►   Pattern matching    ───►   "The log shows       │
│    database log"           & text generation          connection timeout   │
│                                                       errors. Check..."    │
│                                                                             │
│   Time: Milliseconds       Requires: GPU/CPU          Result: Text         │
│   to seconds               with model loaded                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key points about inference:**

- This is what you do when using LLMs
- Runs on your hardware (local) or cloud APIs
- Speed depends on model size and hardware
- Can run on consumer hardware for smaller models

[↑ Back to Table of Contents](#table-of-contents)

## How LLMs generate text

LLMs generate text one token at a time by predicting the most likely next token given all previous tokens.

```text
Step-by-step text generation:

Input: "The database crashed because"
                                    │
                                    ▼
    ┌───────────────────────────────────────────────────────┐
    │  Model calculates probability of next token:          │
    │                                                       │
    │  "the"      → 35%  ←── Highest probability            │
    │  "of"       → 20%                                     │
    │  "it"       → 15%                                     │
    │  "memory"   → 10%                                     │
    │  [others]   → 20%                                     │
    └───────────────────────────────────────────────────────┘
                                    │
                                    ▼
Output so far: "The database crashed because the"
                                              │
                                              ▼
    ┌───────────────────────────────────────────────────────┐
    │  Model calculates probability of next token:          │
    │                                                       │
    │  "server"   → 40%  ←── Highest probability            │
    │  "disk"     → 25%                                     │
    │  "memory"   → 20%                                     │
    │  [others]   → 15%                                     │
    └───────────────────────────────────────────────────────┘
                                    │
                                    ▼
Output so far: "The database crashed because the server"

... continues until complete response
```

### The role of randomness

LLMs do not always pick the highest-probability token. A parameter called **temperature** controls randomness:

| Temperature | Behavior | Use Case |
|:------------|:---------|:---------|
| 0.0 | Always pick highest probability (deterministic) | Factual tasks, code generation |
| 0.3-0.7 | Balanced creativity and coherence | General conversation |
| 1.0+ | More random, creative outputs | Creative writing, brainstorming |

[↑ Back to Table of Contents](#table-of-contents)

## What LLMs can and cannot do

Understanding LLM capabilities and limitations is essential for using them effectively.

### What LLMs can do

| Capability | Example |
|:-----------|:--------|
| Generate human-like text | Write documentation, emails, code |
| Answer questions | Explain concepts, provide information |
| Summarize content | Condense long documents |
| Translate languages | English to Spanish, code to pseudocode |
| Follow instructions | Format output, role-play scenarios |
| Analyze text | Sentiment analysis, log parsing |
| Write and explain code | Generate functions, debug errors |

### What LLMs cannot do

| Limitation | Explanation |
|:-----------|:------------|
| Access the internet | Cannot browse or fetch live data (unless given tools) |
| Remember past conversations | Each session starts fresh (unless given context) |
| Perform reliable math | Prone to calculation errors |
| Know current events | Knowledge limited to training data cutoff |
| Guarantee accuracy | Can generate plausible but incorrect information |
| Execute code | Can write code but cannot run it (unless given tools) |

> [!WARNING]
> **Hallucinations**: LLMs can confidently generate incorrect information that sounds plausible. Always verify critical outputs, especially for database operations, security configurations, or compliance-related tasks.

[↑ Back to Table of Contents](#table-of-contents)

## Why "large" matters

The "large" in Large Language Model refers to the number of parameters—the learned values in the neural network. More parameters generally mean:

```text
PARAMETER SCALING
═════════════════

Small Model (1-3B parameters)
├── Fast inference
├── Lower quality outputs
├── Runs on CPUs or small GPUs
└── Good for: Simple tasks, constrained environments

Medium Model (7-14B parameters)
├── Balanced speed and quality
├── Good reasoning capabilities
├── Runs on consumer GPUs (8-16GB VRAM)
└── Good for: Most development and production tasks

Large Model (30-70B+ parameters)
├── Slower inference
├── Highest quality outputs
├── Requires datacenter GPUs (40-80GB+ VRAM)
└── Good for: Complex reasoning, high-stakes applications
```

### The scaling relationship

| Model Size | Typical VRAM (Q4) | Quality Level | Speed |
|:-----------|:------------------|:--------------|:------|
| 3B | 2-3 GB | Basic | Very Fast |
| 7-8B | 4-5 GB | Good | Fast |
| 13-14B | 8-10 GB | Very Good | Medium |
| 30-34B | 18-20 GB | Excellent | Slow |
| 70B | 40+ GB | State-of-art | Very Slow |

> [!NOTE]
> **Quantization** (covered in Chapter 4) allows running larger models on smaller hardware by reducing precision. A 70B model quantized to 4-bit can run on ~40GB VRAM instead of ~140GB.

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **LLM** | Large Language Model - AI trained on massive text data to generate human-like text |
| **Parameters** | Learned values (weights) in the neural network; more = greater capacity |
| **Training** | Process of teaching a model using large datasets (done by model creators) |
| **Inference** | Using a trained model to generate responses (what you do) |
| **Token** | A chunk of text the model processes (roughly 3/4 of a word in English) |
| **Context window** | Maximum number of tokens the model can "see" at once |
| **Temperature** | Parameter controlling randomness in outputs (0=deterministic, 1+=creative) |
| **Hallucination** | When the model generates plausible but incorrect information |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- LLMs are neural networks trained on massive text data to predict the next token
- Training creates the model (done by companies); inference uses it (done by you)
- LLMs generate text by predicting one token at a time
- LLMs are powerful but have clear limitations (no internet, can hallucinate)
- Larger models generally produce better outputs but require more resources

## Next steps

Continue to **[Chapter 2: Transformer Architecture](./02_transformer_architecture.md)** to learn how LLMs actually process text using the attention mechanism.

## Additional resources

- [What is an LLM? - IBM](https://www.ibm.com/think/topics/large-language-models)
- [AI Concepts Glossary](../../../projects/local-ai-hub/ai-concepts-glossary.md) - Comprehensive terminology reference

[↑ Back to Table of Contents](#table-of-contents)
