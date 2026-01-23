# AI concepts and terminology glossary

**[← Back to local-ai-hub Index](./README.md)**

> **Document Version:** 4.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Explanation-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](./architecture.md) | [LLM Model Selection](./llm-model-selection.md) | [Hardware Requirements](./hardware-requirements.md)

## Table of contents

- [Introduction](#introduction)
- [What are Large Language Models (LLMs)?](#what-are-large-language-models-llms)
- [Parameters vs tokens: Understanding the difference](#parameters-vs-tokens-understanding-the-difference)
- [Model size recommendations](#model-size-recommendations)
  - [405B model hardware requirements](#405b-model-hardware-requirements)
- [Available open-source models](#available-open-source-models)
  - [Security and compliance considerations](#security-and-compliance-considerations-for-model-selection)
- [Local LLM vs cloud LLM comparison](#local-llm-vs-cloud-llm-comparison)
- [Do models need special training?](#do-models-need-special-training)
- [Adding proprietary documentation to local LLMs](#adding-proprietary-documentation-to-local-llms)
- [Recommendations for infrastructure teams](#recommendations-for-infrastructure-teams)
- [The inference layer explained](#the-inference-layer-explained)
- [Can Claude Code use local LLMs?](#can-claude-code-use-local-llms)
- [Model Context Protocol (MCP) explained](#model-context-protocol-mcp-explained)
- [Why we need a FastAPI server](#why-we-need-a-fastapi-server)
- [Architecture deep dive](#architecture-deep-dive)
- [Core concepts reference](#core-concepts-reference)
- [Hardware terminology](#hardware-terminology)
- [Glossary quick reference](#glossary-quick-reference)

## Introduction

This document explains the artificial intelligence (AI) concepts and terminology used throughout the local-ai-hub project. If you're new to AI or Large Language Models (LLMs), start here before diving into the technical documentation.

**Who this is for:**
- Database administrators new to AI tooling
- Infrastructure engineers using Python, PowerShell, Ansible, Terraform
- Developers integrating with local-ai-hub
- Operations teams deploying the infrastructure
- Anyone curious about how AI assistants work

[↑ Back to Table of Contents](#table-of-contents)

## What are Large Language Models (LLMs)?

### The basics

A **Large Language Model (LLM)** is a type of artificial intelligence that has been trained to understand and generate human language. Think of it as a very sophisticated autocomplete system that can write paragraphs instead of just words.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WHAT IS AN LLM?                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   TRAINING PHASE (done by model creators like Meta, Alibaba, etc.)          │
│   ─────────────────────────────────────────────────────────────────         │
│                                                                              │
│   ┌─────────────────┐                      ┌─────────────────┐              │
│   │  Training Data  │                      │    LLM Model    │              │
│   │                 │      Training        │                 │              │
│   │ • Books         │  ────────────────►   │  Billions of    │              │
│   │ • Websites      │  (weeks/months       │  learned        │              │
│   │ • Code          │   on GPU clusters)   │  patterns       │              │
│   │ • Articles      │                      │  (parameters)   │              │
│   │ • Conversations │                      │                 │              │
│   └─────────────────┘                      └─────────────────┘              │
│         │                                          │                         │
│         │ Terabytes of text                        │ Model file (4-200 GB)   │
│                                                                              │
│   INFERENCE PHASE (what we do locally)                                       │
│   ─────────────────────────────────────────────────────────────────         │
│                                                                              │
│   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐     │
│   │   Your Input    │      │    LLM Model    │      │    Response     │     │
│   │                 │      │                 │      │                 │     │
│   │ "Analyze this   │ ───► │  Pattern        │ ───► │ "The log shows  │     │
│   │  database log"  │      │  matching &     │      │  a connection   │     │
│   │                 │      │  generation     │      │  timeout..."    │     │
│   └─────────────────┘      └─────────────────┘      └─────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How LLMs actually work

LLMs don't "think" or "understand" like humans. They predict the most probable next word (token) based on patterns learned during training:

```text
Step-by-step text generation:

Input: "The database crashed because"
                                    │
                                    ▼
    ┌───────────────────────────────────────────────────────┐
    │  Model calculates probability of next word:           │
    │                                                       │
    │  "the"      → 35%  ←── Most likely, so model picks   │
    │  "of"       → 20%      this one                       │
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
    │  Model calculates probability of next word:           │
    │                                                       │
    │  "server"   → 40%  ←── Most likely                   │
    │  "disk"     → 25%                                     │
    │  "memory"   → 20%                                     │
    │  [others]   → 15%                                     │
    └───────────────────────────────────────────────────────┘
                                    │
                                    ▼
Output so far: "The database crashed because the server"

... this continues until the model generates a complete response
```

### Key characteristics

| Characteristic | Description |
|:---------------|:------------|
| **Parameters** | The learned values (weights) in the neural network. More parameters = more knowledge capacity. Measured in billions (7B, 70B, etc.) |
| **Context window** | How much text the model can "see" at once. Like short-term memory. Measured in tokens (8K, 32K, 128K) |
| **Training data** | What the model learned from. Determines its knowledge and biases |
| **Architecture** | The neural network design (most modern LLMs use "Transformer" architecture) |

### What LLMs can and cannot do

| LLMs CAN | LLMs CANNOT |
|:---------|:------------|
| Generate human-like text | Actually understand meaning |
| Answer questions based on training | Access the internet (unless given tools) |
| Summarize and explain content | Remember previous conversations (without context) |
| Write and explain code | Perform calculations reliably |
| Follow instructions | Know current events (knowledge cutoff) |
| Use tools when properly configured | Guarantee factual accuracy |

> [!WARNING]
> **Hallucinations**: LLMs can generate plausible-sounding but incorrect information. Always verify critical outputs, especially for database operations.

[↑ Back to Table of Contents](#table-of-contents)

## Parameters vs tokens: Understanding the difference

A common point of confusion is the difference between **model parameters** (1B, 8B, 70B) and **context tokens** (8K, 32K, 128K). These are two completely different concepts.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARAMETERS vs TOKENS - DIFFERENT CONCEPTS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MODEL PARAMETERS (1B, 8B, 70B)          CONTEXT TOKENS (8K, 32K, 128K)     │
│  ══════════════════════════════          ═══════════════════════════════    │
│                                                                              │
│  What it is:                             What it is:                         │
│  • The model's "brain size"              • The model's "working memory"      │
│  • Learned weights in neural network     • How much text it can see at once  │
│  • Fixed when model is created           • Can vary per request              │
│                                                                              │
│  Affects:                                Affects:                            │
│  • Model intelligence/capability         • Document length you can process   │
│  • Storage on disk                       • VRAM usage during inference       │
│  • VRAM needed to load model             • Response quality for long docs    │
│                                                                              │
│  Analogy:                                Analogy:                            │
│  • Size of a person's brain              • Size of their desk/workspace      │
│  • More neurons = smarter                • Bigger desk = more papers visible │
│                                                                              │
│  Example:                                Example:                            │
│  Llama 3.1 8B = 8 billion parameters    Llama 3.1 8B has 128K context       │
│  Llama 3.1 70B = 70 billion parameters  (same context, different brain)     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What are tokens?

**Tokens** are chunks of text that LLMs process. They're not exactly words—they're pieces determined by the model's "vocabulary."

```text
TOKEN EXAMPLES:

"Hello"           → 1 token   (common word = 1 token)
"PostgreSQL"      → 3 tokens  (Post + gres + QL)
"The quick brown" → 3 tokens  (The + quick + brown)
"authentication"  → 3 tokens  (auth + ent + ication)
"123456"          → 2 tokens  (numbers split up)
"\n\n"            → 1 token   (special characters)

ROUGH ESTIMATE: 1 token ≈ 4 characters ≈ 0.75 words
1,000 tokens ≈ 750 words ≈ 1.5 pages of text
```

### Is more tokens better?

**Context window** (how many tokens a model can process) and **model quality** are different things:

| Aspect | More Means | Trade-offs |
|:-------|:-----------|:-----------|
| **Context window (tokens)** | Can read longer documents | Uses more VRAM, slower |
| **Output length** | Longer responses | May ramble, higher cost |
| **Parameters (7B, 70B)** | More "knowledge" | Needs more hardware |

### Recommended token limits by use case

| Use Case | Input Tokens | Output Tokens | Context Needed | Notes |
|:---------|:-------------|:--------------|:---------------|:------|
| **Documentation rewriting** | 2,000-8,000 | 2,000-8,000 | 16K-32K | Need full doc + rewritten version |
| **Log analysis** | 500-2,000 | 500-1,000 | 8K | Logs are dense |
| **Query explanation** | 200-1,000 | 500-1,500 | 8K | SQL + explanation |
| **Code review** | 1,000-4,000 | 500-2,000 | 16K | Code + comments |
| **Config tuning** | 500-2,000 | 500-1,000 | 8K | Config + recommendations |
| **Chat/Q&A** | 100-500 | 200-500 | 4K-8K | Short exchanges |

[↑ Back to Table of Contents](#table-of-contents)

## Model size recommendations

### Model size → Storage and VRAM requirements

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LLAMA 3 MODEL SIZES AND REQUIREMENTS                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Model      Parameters    Disk Storage         VRAM (GPU Memory)            │
│  ─────      ──────────    ────────────         ─────────────────            │
│                           FP16    Q4           FP16      Q4                  │
│                                                                              │
│  Llama 3.2                                                                   │
│  ─────────                                                                   │
│  1B         1 billion     2 GB    0.7 GB      2 GB      1 GB                │
│  3B         3 billion     6 GB    2 GB        6 GB      2-3 GB              │
│                                                                              │
│  Llama 3.1                                                                   │
│  ─────────                                                                   │
│  8B         8 billion     16 GB   4.5 GB      16 GB     5-6 GB              │
│  70B        70 billion    140 GB  40 GB       140 GB    40-42 GB            │
│  405B       405 billion   810 GB  230 GB      810 GB    ~240 GB             │
│                                                                              │
│                                                                              │
│  VISUAL COMPARISON (Q4 quantized - most common for local use)               │
│  ═══════════════════════════════════════════════════════════                │
│                                                                              │
│  1B:    █                           (1 GB VRAM)   ← Runs on anything        │
│  3B:    ███                         (3 GB VRAM)   ← Basic GPU               │
│  8B:    █████                       (5 GB VRAM)   ← RTX 3060 minimum        │
│  70B:   ████████████████████████████████████████  (40 GB VRAM) ← A100/H100  │
│  405B:  [requires multi-GPU cluster]              (240 GB VRAM)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Which size is recommended?

#### Quick recommendation by hardware

| Your Hardware | Recommended Size | Model Command |
|:--------------|:-----------------|:--------------|
| **No GPU / Laptop** | 1B-3B | `ollama pull llama3.2:3b` |
| **GTX 1060/1070 (6-8GB)** | 3B-7B | `ollama pull llama3.2:3b` |
| **RTX 3060/4060 (12GB)** | 8B | `ollama pull llama3.1:8b` |
| **RTX 3090/4090 (24GB)** | 8B-14B | `ollama pull llama3.1:8b` or `qwen2.5:14b` |
| **A100 40GB** | 70B | `ollama pull llama3.1:70b` |
| **A100 80GB / H100** | 70B comfortably | `ollama pull llama3.1:70b` |
| **Multi-GPU cluster** | 405B | Requires special setup |

#### Detailed recommendation by use case

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDED MODEL SIZE BY USE CASE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USE CASE                        MINIMUM    RECOMMENDED    BEST             │
│  ════════                        ═══════    ═══════════    ════             │
│                                                                              │
│  DOCUMENTATION                                                               │
│  ─────────────                                                               │
│  Simple rewriting                3B         8B             14B              │
│  Complex restructuring           8B         14B            70B              │
│  Technical accuracy critical     8B         70B            70B              │
│                                                                              │
│  DATABASE OPERATIONS                                                         │
│  ───────────────────                                                         │
│  Log analysis (simple)           3B         8B             14B              │
│  Log analysis (complex)          8B         14B            70B              │
│  Query explanation               8B         8B             70B              │
│  Performance tuning advice       8B         70B            70B              │
│  Multi-step troubleshooting      14B        70B            70B              │
│                                                                              │
│  CODING                                                                      │
│  ──────                                                                      │
│  Code review                     8B         14B            70B              │
│  Bug fixing                      8B         14B            70B              │
│  Refactoring                     8B         14B            70B              │
│  Architecture suggestions        14B        70B            70B              │
│                                                                              │
│  GENERAL                                                                     │
│  ───────                                                                     │
│  Q&A / Chat                      3B         8B             14B              │
│  Summarization                   3B         8B             14B              │
│  Translation                     8B         8B             14B              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 405B model hardware requirements

For organizations considering the largest open-source model (Llama 3.1 405B), here are the detailed hardware requirements:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LLAMA 3.1 405B HARDWARE REQUIREMENTS                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MODEL SPECIFICATIONS:                                                       │
│  ═════════════════════                                                       │
│  Parameters:     405 billion                                                 │
│  Disk Storage:   810 GB (FP16) / 230 GB (Q4)                                │
│  VRAM Required:  ~810 GB (FP16) / ~240 GB (Q4)                              │
│  Context:        128K tokens                                                 │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  MINIMUM VIABLE CONFIGURATIONS:                                              │
│  ══════════════════════════════                                              │
│                                                                              │
│  OPTION A: Multi-GPU Server (Q4 quantized - production viable)              │
│  ─────────────────────────────────────────────────────────────              │
│  • GPUs:     8x NVIDIA A100 80GB (640 GB total VRAM)                        │
│  • RAM:      512 GB system RAM minimum                                       │
│  • Storage:  1 TB NVMe SSD (for model + cache)                              │
│  • Network:  NVLink or high-speed GPU interconnect                          │
│  • Cost:     ~$150,000-200,000 (hardware only)                              │
│  • Power:    ~5-8 kW                                                         │
│                                                                              │
│  OPTION B: H100 Cluster (FP16 full precision - best quality)                │
│  ─────────────────────────────────────────────────────────────              │
│  • GPUs:     8x NVIDIA H100 80GB (640 GB total VRAM)                        │
│              or 4x H100 with NVLink for Q4                                  │
│  • RAM:      1 TB system RAM recommended                                     │
│  • Storage:  2 TB NVMe SSD                                                   │
│  • Network:  NVLink required for multi-GPU                                   │
│  • Cost:     ~$300,000-400,000 (hardware only)                              │
│  • Power:    ~8-12 kW                                                        │
│                                                                              │
│  OPTION C: Cloud Instance (most practical for testing)                      │
│  ─────────────────────────────────────────────────────────────              │
│  • AWS:      p5.48xlarge (8x H100) - ~$98/hour                              │
│  • Azure:    ND96isr H100 v5 - ~$90/hour                                   │
│  • GCP:      a3-highgpu-8g - ~$85/hour                                      │
│  • Lambda:   8x H100 instance - ~$50/hour                                   │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  PERFORMANCE EXPECTATIONS:                                                   │
│  ═════════════════════════                                                   │
│                                                                              │
│  Configuration              Tokens/sec    Latency (first token)             │
│  ─────────────              ──────────    ─────────────────────             │
│  8x A100 80GB (Q4)          15-25 t/s     2-5 seconds                       │
│  8x H100 80GB (FP16)        30-50 t/s     1-3 seconds                       │
│  4x H100 (Q4 quantized)     20-35 t/s     1-4 seconds                       │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  ALTERNATIVE APPROACHES:                                                     │
│  ═══════════════════════                                                     │
│                                                                              │
│  For most use cases, consider these more practical alternatives:            │
│                                                                              │
│  70B on single A100 80GB   → 85-90% of 405B quality                        │
│  70B on 2x RTX 4090        → Viable with tensor parallelism                │
│  32B Qwen Coder            → Better for code than 405B general             │
│                                                                              │
│  405B is primarily useful for:                                               │
│  • Research and benchmarking                                                 │
│  • Complex multi-step reasoning                                              │
│  • Tasks requiring maximum accuracy                                          │
│  • When cost is not a constraint                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

> [!WARNING]
> **Practical Advice:** For most local-ai-hub use cases, 405B is overkill. A well-prompted 70B model achieves 85-90% of the quality at 1/5th the hardware cost. Consider 405B only if you have existing datacenter infrastructure or specific requirements for maximum accuracy.

### Why 8B is the sweet spot

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHY 8B IS THE SWEET SPOT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                     Quality                                                  │
│                        ▲                                                     │
│                        │                     ┌───────────────┐              │
│                   100% │                   ┌─┤  Cloud LLMs   │              │
│                        │                 ╱  └───────────────┘              │
│                    90% │               ╱    ┌───────────────┐              │
│                        │             ╱    ┌─┤     70B       │              │
│                    80% │           ╱      │ └───────────────┘              │
│                        │         ╱        │                                 │
│                    70% │  ═════╱══════════╪═══  ┌───────────────┐          │
│                        │     ╱            │   ┌─┤   8B SWEET    │          │
│                    60% │   ╱              │   │ │    SPOT       │          │
│                        │ ╱                │   │ └───────────────┘          │
│                    50% │╱                 │   │                             │
│                        ├──────────────────┴───┴──────────────────►         │
│                        1B    3B    8B    14B   70B   405B                   │
│                                                                              │
│                                   Parameters                                 │
│                                                                              │
│  8B models offer:                                                            │
│  • 70-80% of 70B quality for most tasks                                     │
│  • Runs on consumer GPU (RTX 3060+)                                         │
│  • Fast inference (50+ tokens/sec)                                          │
│  • Low cost to deploy                                                        │
│                                                                              │
│  Jump to 70B when:                                                           │
│  • Complex multi-step reasoning needed                                       │
│  • Nuanced technical accuracy required                                       │
│  • User-facing outputs that must be polished                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Available open-source models

### Are only Llama, Qwen, and Mistral available?

**No.** There are dozens of open-source LLM families available for local deployment. We highlight Llama, Qwen, and Mistral because they offer the best balance of quality, licensing, and tool support for our use cases. Here's the complete landscape:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPEN-SOURCE LLM LANDSCAPE (2025-2026)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TIER 1: RECOMMENDED FOR LOCAL-AI-HUB (best overall)                        │
│  ═══════════════════════════════════════════════════                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │    Llama     │  │    Qwen      │  │   Mistral    │                       │
│  │    (Meta)    │  │  (Alibaba)   │  │ (Mistral AI) │                       │
│  │              │  │              │  │              │                       │
│  │ • 8B-405B    │  │ • 0.5B-72B   │  │ • 7B-123B    │                       │
│  │ • Best       │  │ • Best tool  │  │ • Fastest    │                       │
│  │   community  │  │   calling    │  │   inference  │                       │
│  │ • Most docs  │  │ • Multilang  │  │ • Efficient  │                       │
│  └──────────────┘  └──────────────┘  └──────────────┘                       │
│                                                                              │
│  TIER 2: SPECIALIZED USE CASES                                               │
│  ═════════════════════════════════                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  DeepSeek    │  │   Gemma      │  │    Phi       │  │   Falcon     │    │
│  │  (DeepSeek)  │  │  (Google)    │  │ (Microsoft)  │  │    (TII)     │    │
│  │              │  │              │  │              │  │              │    │
│  │ • Code focus │  │ • Google's   │  │ • Tiny but   │  │ • Open       │    │
│  │ • Reasoning  │  │   open model │  │   capable    │  │   weights    │    │
│  │ • MIT lic.   │  │ • 2B-27B     │  │ • CPU-ready  │  │ • 7B-180B    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  TIER 3: OTHER NOTABLE OPTIONS                                               │
│  ═════════════════════════════════                                          │
│  • Vicuna (fine-tuned Llama)    • WizardLM (instruction-tuned)              │
│  • OpenChat (chat-optimized)    • Nous Hermes (fine-tuned)                  │
│  • Neural Chat (Intel)          • StableLM (Stability AI)                   │
│  • Yi (01.AI, Chinese)          • InternLM (Shanghai AI Lab)                │
│  • Baichuan (Baichuan Inc.)     • Command-R (Cohere, open weights)          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed model comparison: Llama vs Qwen vs Mistral

| Aspect | Llama 3 (Meta) | Qwen 2.5 (Alibaba) | Mistral (Mistral AI) |
|:-------|:---------------|:-------------------|:---------------------|
| **Creator** | Meta (Facebook) | Alibaba Cloud | Mistral AI (France) |
| **Sizes available** | 1B, 3B, 8B, 70B, 405B | 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B | 7B, 8x7B (MoE), 8x22B, 123B |
| **License** | Llama 3 Community | Apache 2.0 | Apache 2.0 |
| **Context window** | 128K tokens | 128K tokens | 32K-128K tokens |
| **Tool calling** | Good | Excellent | Good |
| **Code ability** | Good | Excellent (Coder variant) | Good (Codestral variant) |
| **Multilingual** | 8 languages | 29+ languages | European languages |
| **Best for** | General tasks, community support | Tool calling, Asian languages | Speed, efficiency |

### Why we chose these three

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHY LLAMA + QWEN + MISTRAL?                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LLAMA 3.x (Primary for general tasks)                                       │
│  ─────────────────────────────────────                                       │
│  ✓ Largest community and ecosystem                                           │
│  ✓ Most tutorials, fine-tunes, and documentation                            │
│  ✓ Proven production stability                                               │
│  ✓ Meta's continued investment                                               │
│  ✗ Llama license has some restrictions (>700M users)                        │
│                                                                              │
│  QWEN 2.5 (Primary for tool calling / MCP)                                   │
│  ─────────────────────────────────────────                                   │
│  ✓ Best-in-class tool calling accuracy                                       │
│  ✓ Fully open Apache 2.0 license                                            │
│  ✓ Excellent code understanding (Coder variant)                             │
│  ✓ Wide range of sizes (0.5B to 72B)                                        │
│  ✗ Smaller Western community                                                 │
│                                                                              │
│  MISTRAL (Primary for speed-critical tasks)                                  │
│  ──────────────────────────────────────────                                  │
│  ✓ Fastest inference at comparable quality                                   │
│  ✓ Innovative MoE (Mixture of Experts) architecture                         │
│  ✓ European company (GDPR-friendly)                                          │
│  ✓ Apache 2.0 license (open models)                                          │
│  ✗ Fewer size options than Llama/Qwen                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security and compliance considerations for model selection

When choosing models, some organizations have concerns about the origin of open-source models, particularly regarding data privacy and geopolitical considerations.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODEL ORIGIN AND SECURITY CONSIDERATIONS                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MODEL        COMPANY         COUNTRY     LICENSE      SECURITY NOTES       │
│  ═════        ═══════         ═══════     ═══════      ══════════════       │
│                                                                              │
│  Llama 3.x    Meta            USA         Llama 3      US company, widely   │
│                                           Community    audited, largest     │
│                                                        community            │
│                                                                              │
│  Mistral      Mistral AI      France      Apache 2.0   EU company (GDPR),   │
│                               (EU)                     European data regs   │
│                                                                              │
│  Qwen 2.5     Alibaba         China       Apache 2.0   Chinese company,     │
│                                                        see notes below      │
│                                                                              │
│  Gemma        Google          USA         Gemma        US company, Google   │
│                                           Terms        infrastructure       │
│                                                                              │
│  Phi          Microsoft       USA         MIT          US company, Azure    │
│                                                        backed               │
│                                                                              │
│  DeepSeek     DeepSeek        China       MIT          Chinese company,     │
│                                                        see notes below      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Qwen and Chinese-origin model concerns

**Common concerns about Qwen/Alibaba:**

1. **Data Privacy**: Some worry that using Chinese-developed models could create data exposure risks.

2. **Supply Chain**: Concerns about potential backdoors or hidden behaviors in the model weights.

3. **Regulatory Compliance**: Some industries (defense, government, finance) may have policies restricting foreign technology.

**Important clarifications:**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QWEN SECURITY FACTS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ✓ LOCAL EXECUTION: Model runs 100% locally on YOUR hardware                │
│    • No data is sent to Alibaba or China                                    │
│    • No phone-home or telemetry in the model weights                        │
│    • Network can be completely air-gapped                                   │
│                                                                              │
│  ✓ OPEN SOURCE: Weights and code are fully auditable                        │
│    • Published on Hugging Face with full transparency                       │
│    • Community has reviewed model architecture                              │
│    • No hidden network calls in inference code                              │
│                                                                              │
│  ✓ APACHE 2.0 LICENSE: No usage restrictions or reporting requirements      │
│    • Permissive commercial use                                              │
│    • No obligation to Alibaba                                               │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  REMAINING THEORETICAL CONCERNS:                                             │
│  ───────────────────────────────                                             │
│  ? Training data bias: Model may have subtle biases from Chinese training   │
│    data, though this is true of all models reflecting their training data   │
│                                                                              │
│  ? Steganographic backdoors: Theoretical concern about hidden behaviors     │
│    encoded in weights - extremely difficult to implement, no evidence       │
│    found in security audits                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Model recommendations by security posture

| Security Requirement | Recommended Models | Avoid |
|:---------------------|:-------------------|:------|
| **Standard enterprise** | Llama, Qwen, Mistral | None - all are safe for local use |
| **US government/defense** | Llama (Meta), Phi (Microsoft) | Qwen, DeepSeek (policy restriction) |
| **EU/GDPR focused** | Mistral, Llama | None specific |
| **Maximum caution** | Llama 3.x only | Qwen, DeepSeek |
| **Best code quality (pragmatic)** | Qwen 2.5 Coder | N/A - best option for code |

#### Our recommendation

For **local-ai-hub** where all processing is local and air-gapped:

- **Qwen 2.5 Coder is safe** for most enterprise use—data never leaves your network
- If organizational policy prohibits Chinese-developed software, use **Llama 3.x** as fallback
- For US government or defense work, verify your specific compliance requirements
- The model quality difference for code tasks (Qwen > Llama) may justify the pragmatic choice for most organizations

> [!NOTE]
> **Key Point:** Unlike cloud APIs where data is sent to remote servers, local LLMs run entirely on your hardware. The model's country of origin does not create data exposure risk when running locally.

### Complete list of models available in Ollama

You can run any of these locally with Ollama:

```bash
# View all available models
ollama list

# Popular general-purpose models:
ollama pull llama3.1:8b          # Meta Llama 3.1
ollama pull llama3.3:70b         # Meta Llama 3.3 (latest)
ollama pull qwen2.5:7b           # Alibaba Qwen 2.5
ollama pull mistral:7b           # Mistral 7B
ollama pull mixtral:8x7b         # Mistral MoE
ollama pull gemma2:9b            # Google Gemma 2
ollama pull phi3:mini            # Microsoft Phi-3

# Code-specialized models:
ollama pull qwen2.5-coder:7b     # Qwen for code (recommended)
ollama pull deepseek-coder:6.7b  # DeepSeek for code
ollama pull codellama:13b        # Meta's code model
ollama pull starcoder2:7b        # BigCode StarCoder
```

[↑ Back to Table of Contents](#table-of-contents)

## Local LLM vs cloud LLM comparison

### Overview comparison

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOCAL LLM vs CLOUD LLM COMPARISON                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    LOCAL LLM                    CLOUD LLM                    │
│                    (Ollama + Llama/Qwen)        (ChatGPT/Claude/Gemini)      │
│  ────────────────────────────────────────────────────────────────────────   │
│                                                                              │
│  QUALITY                                                                     │
│  ───────                                                                     │
│  7B models:        ████████░░░░░░░░  (60%)    ████████████████  (95-100%)   │
│  70B models:       ████████████░░░░  (80%)    (GPT-4, Claude, Gemini Pro)   │
│                                                                              │
│  PRIVACY                                                                     │
│  ───────                                                                     │
│  Local LLM:        ████████████████  100% - data never leaves your machine  │
│  Cloud LLM:        ████░░░░░░░░░░░░  Data sent to vendor servers            │
│                                                                              │
│  COST                                                                        │
│  ────                                                                        │
│  Local LLM:        Hardware upfront, then FREE unlimited usage              │
│  Cloud LLM:        $0.01-0.10 per 1K tokens (adds up fast!)                │
│                                                                              │
│  SPEED (tokens/sec)                                                          │
│  ─────────────────                                                           │
│  Local (GPU):      30-100 t/s (depends on hardware)                         │
│  Cloud:            50-150 t/s (consistent)                                  │
│                                                                              │
│  AVAILABILITY                                                                │
│  ────────────                                                                │
│  Local LLM:        Works offline, no internet needed                        │
│  Cloud LLM:        Requires internet, subject to outages                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cloud LLM providers compared

| Provider | Model | Strengths | Weaknesses |
|:---------|:------|:----------|:-----------|
| **OpenAI** | GPT-4, GPT-4o | Largest ecosystem, best general quality | Expensive, data concerns |
| **Anthropic** | Claude 3.5, Opus | Best for coding, safest | Premium pricing |
| **Google** | Gemini Pro/Ultra | Multimodal, large context | Quality varies |
| **xAI** | Grok | Real-time data, humor | Newer, less tested |
| **Local** | Llama, Qwen, Mistral | Privacy, free, offline | Lower quality, needs GPU |

### When to use each

| Scenario | Recommended |
|:---------|:------------|
| Sensitive internal data | **Local LLM** - data never leaves network |
| Air-gapped environment | **Local LLM** - no internet required |
| Best possible quality | **Cloud** (Claude/GPT-4) - if privacy allows |
| High volume usage | **Local LLM** - no per-token cost |
| Quick prototype | **Cloud** - instant setup |
| Production database ops | **Local LLM** - privacy + reliability |

[↑ Back to Table of Contents](#table-of-contents)

## Do models need special training?

### Short answer: No, but specialized variants help

General-purpose LLMs like Llama and Qwen were trained on massive datasets that include:
- Millions of Stack Overflow posts
- GitHub repositories (SQL, Python, configs)
- Technical documentation
- Database vendor manuals
- Troubleshooting forums

**They already know about:** SQL syntax, common database errors, configuration parameters, performance tuning concepts, and log formats.

### Specialization options

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODEL SPECIALIZATION OPTIONS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OPTION 1: USE BASE MODEL + GOOD PROMPTS (What we do)                       │
│  ═══════════════════════════════════════════════════                        │
│                                                                              │
│  ┌─────────────────┐      ┌─────────────────────────────────┐              │
│  │  Llama 3.1 8B   │  +   │  System Prompt:                 │              │
│  │  (general)      │      │  "You are an expert DBA with    │              │
│  │                 │      │   20 years of PostgreSQL and    │              │
│  │  Already knows: │      │   SQL Server experience..."     │              │
│  │  • SQL syntax   │      │                                 │              │
│  │  • Error types  │      │  This "steers" the model to     │              │
│  │  • Config files │      │  use its existing knowledge     │              │
│  └─────────────────┘      └─────────────────────────────────┘              │
│                                                                              │
│  QUALITY: ████████░░  Good for most tasks                                   │
│  EFFORT:  ██░░░░░░░░  Minimal - just write good prompts                    │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  OPTION 2: USE SPECIALIZED MODEL VARIANT                                     │
│  ════════════════════════════════════════                                    │
│                                                                              │
│  ┌─────────────────┐                                                        │
│  │ Qwen 2.5 Coder  │  Already fine-tuned on code                           │
│  │ DeepSeek Coder  │  Better at SQL, programming                           │
│  │ CodeLlama       │  Optimized for code tasks                             │
│  └─────────────────┘                                                        │
│                                                                              │
│  QUALITY: ██████████  Excellent for code/SQL                                │
│  EFFORT:  ██░░░░░░░░  Just use the right model                             │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  OPTION 3: FINE-TUNE YOUR OWN MODEL (Advanced)                              │
│  ═════════════════════════════════════════════                              │
│                                                                              │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐     │
│  │  Llama 3.1 8B   │  +   │  Your Data:     │  =   │  Custom Model   │     │
│  │  (base)         │      │  • Internal logs│      │  (specialized)  │     │
│  │                 │      │  • Your schemas │      │                 │     │
│  │                 │      │  • Runbooks     │      │  Knows YOUR     │     │
│  │                 │      │                 │      │  systems!       │     │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘     │
│                                                                              │
│  QUALITY: ████████████  Best for your specific use case                     │
│  EFFORT:  ████████░░░░  Significant - need training pipeline               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Our approach in local-ai-hub

We use **Option 1 + Option 2** combined:

| Task | Model Used | Why |
|:-----|:-----------|:----|
| General tasks | Llama 3.1 8B | Good all-rounder |
| SQL/Query analysis | Qwen 2.5 Coder 7B | Optimized for code |
| Tool calling (MCP) | Qwen 2.5 7B | Best tool support |
| Complex reasoning | Llama 3.1 70B | Larger = smarter |

Plus **specialized prompts** for each agent:

```text
Log Analyzer Agent prompt:
"You are an expert DBA with 20 years experience in SQL Server,
 PostgreSQL, and MongoDB. When analyzing logs, always identify:
 1. Error severity
 2. Root cause
 3. Affected components
 4. Remediation steps
 Be concise and actionable."
```

This approach gives 80-90% of fine-tuning benefits with 10% of the effort.

[↑ Back to Table of Contents](#table-of-contents)

## Adding proprietary documentation to local LLMs

A common question is whether local LLMs can be trained on proprietary documentation, PDFs, or internal knowledge bases. The answer is **yes**, with two main approaches.

### Approach comparison

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ADDING PROPRIETARY DATA TO LLMs                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  APPROACH 1: RAG (Retrieval-Augmented Generation) - RECOMMENDED             │
│  ═══════════════════════════════════════════════════════════════            │
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  Your Docs  │────►│  Vector DB  │     │             │                   │
│  │ • PDFs      │     │ (Embeddings)│     │             │                   │
│  │ • Markdown  │     │             │     │             │                   │
│  │ • Word docs │     └──────┬──────┘     │             │                   │
│  │ • Confluence│            │            │   LLM       │                   │
│  └─────────────┘            │ Search     │  (unchanged)│                   │
│                             │            │             │                   │
│  ┌─────────────┐     ┌──────▼──────┐     │             │                   │
│  │ User Query  │────►│  Relevant   │────►│  Generate   │──► Answer         │
│  │             │     │  Snippets   │     │  Response   │   (with sources)  │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                                                                              │
│  HOW IT WORKS:                                                               │
│  1. Documents are chunked and converted to vector embeddings                │
│  2. User query is also converted to embedding                                │
│  3. Most similar document chunks are retrieved                               │
│  4. Retrieved chunks are added to prompt as context                         │
│  5. LLM generates answer using the context                                  │
│                                                                              │
│  ✓ No model retraining needed                                               │
│  ✓ Documents can be added/updated instantly                                 │
│  ✓ Works with any document format (PDF, Word, HTML, etc.)                   │
│  ✓ Can cite sources in responses                                            │
│  ✓ Easy to implement with existing tools                                    │
│  ✗ Limited by context window size                                           │
│  ✗ Retrieval quality affects answer quality                                 │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  APPROACH 2: FINE-TUNING - For specialized needs                            │
│  ═══════════════════════════════════════════════════════════════            │
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  Base Model │ +   │  Your Data  │ ──► │ Fine-tuned  │                   │
│  │ (Llama 8B)  │     │ (formatted) │     │   Model     │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                          │                     │                             │
│                          │ Training            │ New model                   │
│                          │ (hours/days)        │ knows your                  │
│                          │ GPU required        │ content!                    │
│                                                                              │
│  ✓ Knowledge "baked in" to model                                            │
│  ✓ No retrieval needed at inference time                                    │
│  ✓ Can learn specific styles, terminology, patterns                         │
│  ✗ Requires ML expertise                                                     │
│  ✗ Needs significant GPU compute for training                               │
│  ✗ Hours or days to retrain when content changes                            │
│  ✗ Risk of catastrophic forgetting (losing base knowledge)                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### RAG implementation (recommended for local-ai-hub)

RAG is the practical choice for most organizations. Here's how to set it up:

**Required components:**
```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RAG STACK FOR LOCAL-AI-HUB                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COMPONENT          OPTIONS                 OUR RECOMMENDATION              │
│  ═════════          ═══════                 ══════════════════              │
│                                                                              │
│  Vector Database    • ChromaDB (simple)     ChromaDB for dev                │
│                     • Qdrant (production)   Qdrant for production           │
│                     • Milvus (enterprise)                                   │
│                     • pgvector (PostgreSQL)                                 │
│                                                                              │
│  Embedding Model    • nomic-embed-text      nomic-embed-text (Ollama)       │
│                     • all-MiniLM-L6-v2      Good balance of quality/speed   │
│                     • bge-large-en-v1.5                                     │
│                                                                              │
│  Document Loader    • LangChain             LangChain or LlamaIndex         │
│                     • LlamaIndex            Both support PDF, Word, HTML    │
│                     • Unstructured.io                                       │
│                                                                              │
│  Chunking Strategy  • Character-based       Semantic chunking with          │
│                     • Sentence-based        ~512 token chunks               │
│                     • Semantic                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example RAG setup with Ollama:**
```bash
# Pull embedding model
ollama pull nomic-embed-text

# Python dependencies
pip install chromadb langchain langchain-community

# Supported document types:
# - PDF (via pypdf or pdfplumber)
# - Word (.docx via python-docx)
# - Markdown
# - HTML
# - Plain text
# - PowerPoint (via python-pptx)
# - Confluence (via API export)
```

**Basic RAG workflow:**
```python
# Pseudocode example
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma

# 1. Load documents
loader = DirectoryLoader("./docs", glob="**/*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()

# 2. Create embeddings and store
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(documents, embeddings)

# 3. Query with RAG
query = "How do I configure database replication?"
relevant_docs = vectorstore.similarity_search(query, k=3)

# 4. Add to prompt and generate
context = "\n".join([doc.page_content for doc in relevant_docs])
prompt = f"Using this context:\n{context}\n\nAnswer: {query}"
# Send to Ollama for generation
```

### When to use fine-tuning instead

Fine-tuning is appropriate when:

| Use Case | Why Fine-Tuning |
|:---------|:----------------|
| **Specific output format** | Model should always respond in a particular structure (JSON schema, report format) |
| **Domain terminology** | Heavy use of internal jargon that needs consistent usage |
| **Behavioral patterns** | Model should follow specific workflows or reasoning patterns |
| **Style consistency** | Output must match a particular writing style across all responses |
| **Performance optimization** | Need to reduce prompt size by "baking in" common context |

**Fine-tuning tools:**
```text
• Ollama Modelfile (simple fine-tuning)
• Hugging Face PEFT/LoRA (efficient fine-tuning)
• Axolotl (full fine-tuning framework)
• Unsloth (fast LoRA fine-tuning)

Hardware needed for fine-tuning 8B model:
• Minimum: 24 GB VRAM (RTX 4090, A10)
• Recommended: 40-80 GB VRAM (A100)
• LoRA fine-tuning: 12-16 GB possible
```

### Recommendation for local-ai-hub

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDED APPROACH                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  START WITH:  RAG (Retrieval-Augmented Generation)                          │
│                                                                              │
│  • Fastest time to value                                                     │
│  • No ML expertise required                                                  │
│  • Documents update instantly                                                │
│  • Works with existing infrastructure                                        │
│                                                                              │
│  ADD FINE-TUNING LATER IF:                                                  │
│                                                                              │
│  • RAG retrieval quality is insufficient                                     │
│  • Need very specific output patterns                                        │
│  • Have ML engineering capacity                                              │
│  • Content is stable (doesn't change frequently)                            │
│                                                                              │
│  TYPICAL RESULTS:                                                            │
│  • RAG alone: 80-90% of use cases satisfied                                 │
│  • RAG + good prompts: 90-95% of use cases                                  │
│  • RAG + fine-tuning: 95%+ (only if truly needed)                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

> [!NOTE]
> **Privacy:** Both RAG and fine-tuning keep your proprietary data 100% local when using Ollama. No data is sent externally. This is a key advantage over cloud-based solutions where your documents would be processed on vendor servers.

[↑ Back to Table of Contents](#table-of-contents)

## Recommendations for infrastructure teams

This section provides specific model recommendations for teams working with Python, PowerShell, and infrastructure-as-code tools.

### Stack analysis

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE STACK COVERAGE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LANGUAGES                    LLM TRAINING DATA COVERAGE                     │
│  ═════════                    ══════════════════════════                     │
│  Python                       █████████████████████  Excellent              │
│  PowerShell                   ████████░░░░░░░░░░░░░  Moderate               │
│                                                                              │
│  INFRASTRUCTURE TOOLS         LLM TRAINING DATA COVERAGE                     │
│  ════════════════════         ══════════════════════                         │
│  Ansible (YAML)               █████████████████░░░░  Very Good              │
│  Terraform (HCL)              ████████████████░░░░░  Very Good              │
│  Docker (Dockerfile/Compose)  █████████████████████  Excellent              │
│  Vault (HCL/API)              ████████████░░░░░░░░░  Good                   │
│  JFrog (REST API/YAML)        ██████░░░░░░░░░░░░░░░  Limited               │
│                                                                              │
│  ASSESSMENT:                                                                 │
│  • Python/Docker/Ansible/Terraform: Well covered by most models             │
│  • PowerShell: Need models with good Windows/MS ecosystem training          │
│  • JFrog: May need prompt examples (less training data)                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Recommended model: Qwen 2.5 Coder

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRIMARY RECOMMENDATION: QWEN 2.5 CODER                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  WHY QWEN CODER:                                                             │
│  • Trained on 5.5 trillion tokens of code                                   │
│  • Supports 92 programming languages                                         │
│  • Excellent at infrastructure-as-code (Ansible, Terraform, Docker)         │
│  • Good PowerShell support (better than most open models)                   │
│  • Best-in-class tool calling (important for MCP integration)               │
│  • Apache 2.0 license (fully open)                                          │
│                                                                              │
│  SIZES AVAILABLE:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Size   │  VRAM (Q4)  │  Use Case                                   │    │
│  ├─────────┼─────────────┼─────────────────────────────────────────────┤    │
│  │  1.5B   │  1 GB       │  Quick completions, simple scripts          │    │
│  │  7B     │  4.5 GB     │  Daily coding, code review, Ansible/TF     │    │
│  │  14B    │  8 GB       │  Complex refactoring, architecture          │    │
│  │  32B    │  18 GB      │  Best quality, multi-file understanding     │    │
│  └─────────┴─────────────┴─────────────────────────────────────────────┘    │
│                                                                              │
│  INSTALL COMMANDS:                                                           │
│  ollama pull qwen2.5-coder:7b      # Development (RTX 3060)                 │
│  ollama pull qwen2.5-coder:14b     # Team (RTX 4090)                        │
│  ollama pull qwen2.5-coder:32b     # Production (A100)                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Model selection by tool

| Tool/Language | Best Model | Why | Fallback |
|:--------------|:-----------|:----|:---------|
| **Python** | Qwen 2.5 Coder 7B | Extensive Python training | DeepSeek Coder |
| **PowerShell** | Qwen 2.5 Coder 14B | Better Windows coverage at larger size | Llama 3.1 70B |
| **Ansible** | Qwen 2.5 Coder 7B | YAML + Jinja2 understanding | Llama 3.1 8B |
| **Terraform** | Qwen 2.5 Coder 7B | HCL well represented | DeepSeek Coder |
| **Docker** | Qwen 2.5 Coder 7B | Dockerfile/Compose excellent | Any 8B model |
| **Vault** | Qwen 2.5 Coder 7B | HCL + API patterns | Llama 3.1 8B |
| **JFrog** | Qwen 2.5 Coder 14B | Needs larger model for niche tool | Provide examples in prompt |

### Model selection by task

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHICH MODEL FOR WHICH TASK                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TASK                                    MODEL                SIZE           │
│  ════                                    ═════                ════           │
│                                                                              │
│  PYTHON                                                                      │
│  ──────                                                                      │
│  Write new functions                     Qwen 2.5 Coder      7B             │
│  Debug existing code                     Qwen 2.5 Coder      7B             │
│  Refactor large modules                  Qwen 2.5 Coder      14B            │
│  Architecture review                     Qwen 2.5 Coder      32B / 70B      │
│                                                                              │
│  POWERSHELL                                                                  │
│  ──────────                                                                  │
│  Simple scripts                          Qwen 2.5 Coder      7B             │
│  Complex modules                         Qwen 2.5 Coder      14B            │
│  DSC configurations                      Qwen 2.5 Coder      14B            │
│  Active Directory scripts                Llama 3.1           70B            │
│                                                                              │
│  ANSIBLE                                                                     │
│  ───────                                                                     │
│  Write playbooks                         Qwen 2.5 Coder      7B             │
│  Roles with Jinja2 templates             Qwen 2.5 Coder      7B             │
│  Complex inventories                     Qwen 2.5 Coder      14B            │
│  Troubleshoot failures                   Qwen 2.5 Coder      14B            │
│                                                                              │
│  TERRAFORM                                                                   │
│  ─────────                                                                   │
│  Write modules                           Qwen 2.5 Coder      7B             │
│  State troubleshooting                   Qwen 2.5 Coder      14B            │
│  Multi-cloud architectures               Qwen 2.5 Coder      32B            │
│                                                                              │
│  DOCKER                                                                      │
│  ──────                                                                      │
│  Dockerfile optimization                 Qwen 2.5 Coder      7B             │
│  Compose files                           Qwen 2.5 Coder      7B             │
│  Multi-stage builds                      Qwen 2.5 Coder      7B             │
│                                                                              │
│  VAULT                                                                       │
│  ─────                                                                       │
│  Policy writing (HCL)                    Qwen 2.5 Coder      7B             │
│  Secret engine configuration             Qwen 2.5 Coder      14B            │
│  Auth method setup                       Qwen 2.5 Coder      14B            │
│                                                                              │
│  JFROG                                                                       │
│  ─────                                                                       │
│  API integration scripts                 Qwen 2.5 Coder      14B            │
│  Pipeline YAML                           Qwen 2.5 Coder      7B             │
│  Artifactory configuration               Llama 3.1           8B + examples  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Recommended setup by hardware tier

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDED LOCAL-AI-HUB SETUP                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  DEVELOPMENT WORKSTATION (RTX 3060 12GB / RTX 4060 8GB)                     │
│  ══════════════════════════════════════════════════════                      │
│                                                                              │
│  # Primary model for all code tasks                                          │
│  ollama pull qwen2.5-coder:7b                                               │
│                                                                              │
│  # For tool calling / MCP integration                                        │
│  ollama pull qwen2.5:7b                                                      │
│                                                                              │
│  Total VRAM needed: ~5 GB (one model at a time)                             │
│  Total disk: ~10 GB                                                          │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  TEAM SERVER (RTX 4090 24GB)                                                │
│  ═══════════════════════════                                                 │
│                                                                              │
│  # Fast tier - quick code tasks                                              │
│  ollama pull qwen2.5-coder:7b                                               │
│                                                                              │
│  # Quality tier - complex refactoring, PowerShell                           │
│  ollama pull qwen2.5-coder:14b                                              │
│                                                                              │
│  # General/docs tier                                                         │
│  ollama pull llama3.1:8b                                                    │
│                                                                              │
│  Total VRAM needed: 8-14 GB (can run 7B + handle concurrent requests)       │
│  Total disk: ~25 GB                                                          │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  PRODUCTION (A100 40GB or 80GB)                                             │
│  ══════════════════════════════                                              │
│                                                                              │
│  # Fast tier                                                                 │
│  ollama pull qwen2.5-coder:7b                                               │
│                                                                              │
│  # Quality tier - best for complex infrastructure code                      │
│  ollama pull qwen2.5-coder:32b                                              │
│                                                                              │
│  # Heavy reasoning (architecture decisions, troubleshooting)                │
│  ollama pull llama3.1:70b                                                   │
│                                                                              │
│  Total VRAM needed: 18-40 GB                                                │
│  Total disk: ~80 GB                                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Quick start installation

```bash
# Essential for infrastructure teams
ollama pull qwen2.5-coder:7b     # Primary code model
ollama pull qwen2.5:7b           # Tool calling / MCP
ollama pull llama3.1:8b          # Documentation / general

# Add later if needed
ollama pull qwen2.5-coder:14b    # Better PowerShell/complex code
ollama pull deepseek-coder-v2:16b # Alternative code model
```

### Tips for PowerShell and JFrog (less common in training data)

For tools with less training data coverage, use larger models and provide context in prompts.

**PowerShell** - Use larger models + specific prompting:
```text
System prompt:
"You are a PowerShell expert specializing in Windows automation,
 Active Directory, and enterprise scripting. Follow PowerShell best
 practices: use approved verbs, proper error handling with
 try/catch, comment-based help, and PSScriptAnalyzer compliance."

Recommend: qwen2.5-coder:14b (smaller models struggle with PS)
```

**JFrog** - Provide examples in prompts (few-shot learning):
```text
System prompt:
"You are an expert in JFrog Artifactory and Xray. Here's an example
 of our repository configuration:
 ```yaml
 repositories:
   - key: libs-release-local
     type: local
     packageType: maven
 ```
 Follow this pattern for new configurations."

Recommend: qwen2.5-coder:14b + examples in prompt
```

[↑ Back to Table of Contents](#table-of-contents)

## The inference layer explained

### What is inference?

**Inference** is the process of running a trained AI model to generate outputs. If training is like a student learning from textbooks, inference is like that student taking a test.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRAINING vs INFERENCE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   TRAINING (Done by Meta, Alibaba, etc.)                                     │
│   ══════════════════════════════════════                                     │
│   • Happens once, takes weeks/months                                         │
│   • Requires massive GPU clusters ($millions)                                │
│   • Creates the model file                                                   │
│   • We DON'T do this                                                         │
│                                                                              │
│   INFERENCE (What we do with local-ai-hub)                                   │
│   ════════════════════════════════════════                                   │
│   • Happens every time you ask a question                                    │
│   • Requires a single GPU (or CPU)                                           │
│   • Uses the pre-trained model file                                          │
│   • This is what Ollama/vLLM do                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What is an inference engine/server?

An **inference engine** (like Ollama or vLLM) is software that:
1. Loads model files into GPU/CPU memory
2. Accepts text input from applications
3. Runs the model to generate output
4. Returns the response

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHAT OLLAMA DOES                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  YOUR APP                    OLLAMA SERVER                    GPU/CPU        │
│  ────────                    ─────────────                    ───────        │
│                                                                              │
│  ┌─────────┐                 ┌─────────────────────────────┐                │
│  │ Request │                 │                             │                │
│  │         │  ──────────►    │  1. RECEIVE REQUEST         │                │
│  │ "What   │  HTTP POST      │     Parse JSON, validate    │                │
│  │ causes  │  :11434         │                             │                │
│  │ this    │                 │  2. TOKENIZE                │                │
│  │ error?" │                 │     "What causes" → [123,   │                │
│  │         │                 │      456, 789, ...]         │                │
│  └─────────┘                 │                             │   ┌─────────┐  │
│                              │  3. LOAD MODEL (if needed)  │   │   GPU   │  │
│                              │     llama3.1:8b → GPU VRAM  │──►│  VRAM   │  │
│                              │                             │   │  (5GB)  │  │
│                              │  4. RUN INFERENCE           │   └─────────┘  │
│                              │     Forward pass through    │        │       │
│                              │     neural network          │◄───────┘       │
│                              │                             │                │
│  ┌─────────┐                 │  5. DETOKENIZE              │                │
│  │Response │  ◄──────────    │     [234, 567] → "The       │                │
│  │         │  HTTP Response  │     error indicates..."     │                │
│  │ "The    │                 │                             │                │
│  │ error   │                 │  6. STREAM RESPONSE         │                │
│  │ ..."    │                 │     Send tokens as          │                │
│  │         │                 │     generated               │                │
│  └─────────┘                 └─────────────────────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Ollama vs vLLM vs llama.cpp

| Aspect | Ollama | vLLM | llama.cpp |
|:-------|:-------|:-----|:----------|
| **Primary use** | Development, single user | Production, multi-user | Edge, embedded, CPU |
| **Ease of setup** | Very easy (one command) | Moderate | Complex |
| **Performance** | Good | Excellent | Good |
| **Concurrent users** | 1-4 | 10-100+ | 1-2 |
| **GPU support** | NVIDIA, AMD, Apple | NVIDIA, AMD | All (including CPU) |
| **API** | OpenAI-compatible | OpenAI-compatible | Custom |
| **Model management** | Built-in (pull/run) | Manual | Manual |
| **Best for** | local-ai-hub development | local-ai-hub production | Resource-constrained |

### Why we need an inference layer

Without an inference engine, you would need to:
- Write code to load model files (complex binary formats)
- Manage GPU memory allocation manually
- Implement the transformer forward pass
- Handle tokenization/detokenization
- Build an API server from scratch

**Ollama abstracts all of this into simple commands:**

```bash
# Without Ollama: hundreds of lines of CUDA code
# With Ollama:
ollama run llama3.1:8b "What causes database deadlocks?"
```

[↑ Back to Table of Contents](#table-of-contents)

## Can Claude Code use local LLMs?

### Short answer: Yes, with Ollama v0.14.0+

**As of Ollama v0.14.0 (2025)**, Claude Code CAN work with local LLMs through Ollama's Anthropic Messages API compatibility. This is a major development that allows 100% local operation.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE WITH LOCAL LLMs (NEW!)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OPTION 1: CLAUDE CODE + ANTHROPIC (Default)                                │
│  ════════════════════════════════════════════                                │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐           │
│  │  Your Code  │ ──────► │  Internet   │ ──────► │  Anthropic  │           │
│  │  & Prompts  │         │             │         │  Servers    │           │
│  └─────────────┘         └─────────────┘         └─────────────┘           │
│                                                         │                    │
│  ✓ Best AI coding quality          ✗ Data leaves network                   │
│  ✓ Easy setup (API key)            ✗ Requires internet                     │
│  ✓ Anthropic support               ✗ Pay per token                         │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  OPTION 2: CLAUDE CODE + OLLAMA LOCAL (New in Ollama v0.14.0+)              │
│  ═════════════════════════════════════════════════════════════               │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐           │
│  │ Claude Code │ ──────► │  Localhost  │ ──────► │   Ollama    │           │
│  │             │         │  :11434     │         │  (your GPU) │           │
│  └─────────────┘         └─────────────┘         └─────────────┘           │
│                                                         │                    │
│  ✓ 100% local/private              ! Requires capable GPU                  │
│  ✓ No internet needed              ! Lower quality than Claude Opus        │
│  ✓ No per-token cost               ! Requires Ollama v0.14.0+              │
│  ✓ Uses familiar Claude Code UI    ! Best with Qwen 2.5 Coder 32B+        │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  OPTION 3: OTHER LOCAL ALTERNATIVES (Cline, OpenCode, Aider)                │
│  ═══════════════════════════════════════════════════════════                 │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐           │
│  │ Cline/Aider │ ──────► │  Localhost  │ ──────► │   Ollama    │           │
│  │  OpenCode   │         │  :11434     │         │  (your GPU) │           │
│  └─────────────┘         └─────────────┘         └─────────────┘           │
│                                                         │                    │
│  ✓ 100% local/private              ✗ Different UI than Claude Code         │
│  ✓ No internet needed              ✗ Lower quality than Claude             │
│  ✓ No per-token cost               ✗ More setup required                   │
│  ✓ MCP compatible                  ✓ Can also use cloud APIs               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Setting up Claude Code with local Ollama

To use Claude Code with a local Ollama server (requires Ollama v0.14.0 or later):

```bash
# Step 1: Verify Ollama version (must be 0.14.0+)
ollama --version

# Step 2: Pull a capable model (32B+ recommended for Claude Code quality)
ollama pull qwen2.5-coder:32b
# Or for 70B+ systems:
ollama pull llama3.1:70b

# Step 3: Start Ollama server (if not already running)
ollama serve

# Step 4: Configure Claude Code environment variables
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_BASE_URL=http://localhost:11434

# Step 5: Run Claude Code as normal
claude
```

> [!WARNING]
> **Quality Note:** Local models, even large ones (70B), will not match Claude Opus/Sonnet quality. For complex coding tasks, expect reduced accuracy. Local models work best for:
> - Code completion and simple refactoring
> - Documentation tasks
> - Standard CRUD operations
> - Well-defined, straightforward tasks

> [!NOTE]
> **Model Recommendation for Claude Code:** Use `qwen2.5-coder:32b` or `llama3.1:70b` minimum. Smaller models (7B-14B) may struggle with complex Claude Code prompts.

### Coding assistant options for local use

| Tool | Type | MCP Support | Ollama Support | Best For |
|:-----|:-----|:------------|:---------------|:---------|
| **Claude Code + Ollama** | Terminal CLI | Yes | Yes (v0.14.0+) | Teams already using Claude Code |
| **Cline** | VS Code extension | Excellent | Yes | IDE users, feature-rich |
| **OpenCode** | Terminal TUI | Excellent | Yes | CLI-first developers |
| **Aider** | Terminal | Limited | Yes | Git-focused workflows |
| **Continue** | IDE extension | Good | Yes | Code completion |
| **Cursor** | Full IDE | Limited | Partial | Dedicated AI IDE |

### Recommended setup for local-ai-hub

For 100% local processing, you now have multiple options. **Claude Code + Ollama** is viable if you have powerful hardware (32B+ models recommended):

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDED LOCAL SETUP                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  VS CODE USERS                        TERMINAL USERS                         │
│  ══════════════                       ══════════════                         │
│                                                                              │
│  ┌─────────────────┐                  ┌─────────────────┐                   │
│  │    VS Code      │                  │    Terminal     │                   │
│  │  + Cline ext.   │                  │  + OpenCode     │                   │
│  └────────┬────────┘                  └────────┬────────┘                   │
│           │                                    │                             │
│           │ MCP Protocol                       │ MCP Protocol                │
│           │                                    │                             │
│           ▼                                    ▼                             │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │                    local-ai-hub                          │                │
│  │           (MCP Server + REST API + Agents)               │                │
│  └────────────────────────┬────────────────────────────────┘                │
│                           │                                                  │
│                           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │                      Ollama                              │                │
│  │              (Qwen 2.5 7B + Llama 3.1 8B)               │                │
│  └─────────────────────────────────────────────────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## Model Context Protocol (MCP) explained

### What is MCP?

**Model Context Protocol (MCP)** is an open standard created by Anthropic for connecting AI assistants to external tools and data sources. Think of it as **"USB for AI"**—a universal connector that lets any MCP-compatible AI client use any MCP-compatible tool.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE PROBLEM MCP SOLVES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BEFORE MCP: Every tool needed custom integration                            │
│  ═══════════════════════════════════════════════                             │
│                                                                              │
│  ┌──────────┐     Custom API     ┌──────────┐                               │
│  │  Claude  │◄──────────────────►│ Tool A   │                               │
│  └──────────┘                    └──────────┘                               │
│  ┌──────────┐     Different API  ┌──────────┐                               │
│  │  GPT     │◄──────────────────►│ Tool A   │  (Had to rebuild!)            │
│  └──────────┘                    └──────────┘                               │
│  ┌──────────┐     Another API    ┌──────────┐                               │
│  │  Llama   │◄──────────────────►│ Tool A   │  (Had to rebuild again!)      │
│  └──────────┘                    └──────────┘                               │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                              │
│  WITH MCP: One standard protocol for all                                     │
│  ═══════════════════════════════════════                                     │
│                                                                              │
│  ┌──────────┐                    ┌──────────┐                               │
│  │  Claude  │◄────┐              │ Tool A   │                               │
│  └──────────┘     │              └────┬─────┘                               │
│  ┌──────────┐     │    MCP           │                                      │
│  │  Cline   │◄────┼─────────────────►│  (Build once,                        │
│  └──────────┘     │   Protocol       │   works everywhere!)                 │
│  ┌──────────┐     │              ┌───┴──────┐                               │
│  │ OpenCode │◄────┘              │ Tool B   │                               │
│  └──────────┘                    └──────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MCP architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MCP ARCHITECTURE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                          MCP CLIENTS                                         │
│                    (AI Assistants/IDEs)                                      │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │   Cline     │  │  OpenCode   │  │ Claude Code │  │  Continue   │       │
│   │ (VS Code)   │  │ (Terminal)  │  │  (Anthropic)│  │   (IDE)     │       │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│          │                │                │                │               │
│          └────────────────┴────────────────┴────────────────┘               │
│                                    │                                         │
│                         MCP PROTOCOL LAYER                                   │
│          ┌─────────────────────────┴─────────────────────────┐              │
│          │  • JSON-RPC 2.0 over stdio/SSE                    │              │
│          │  • Standardized tool definitions                   │              │
│          │  • Resource discovery                              │              │
│          │  • Authentication support                          │              │
│          └─────────────────────────┬─────────────────────────┘              │
│                                    │                                         │
│          ┌─────────────────────────┴─────────────────────────┐              │
│                              MCP SERVERS                                     │
│                          (Tool Providers)                                    │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │local-ai-hub │  │ Filesystem  │  │    Git      │  │  Database   │       │
│   │             │  │   Server    │  │   Server    │  │   Server    │       │
│   │• DB tools   │  │• Read files │  │• Git status │  │• Run queries│       │
│   │• Doc tools  │  │• Write files│  │• Git diff   │  │• Get schema │       │
│   │• Code tools │  │• Search     │  │• Git commit │  │• Explain    │       │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why MCP matters for local-ai-hub

| Benefit | Description |
|:--------|:------------|
| **Write once, use everywhere** | Our tools work with Cline, OpenCode, Claude Code, and any future MCP client |
| **Standard interface** | No custom integrations needed |
| **Growing ecosystem** | Thousands of MCP servers available (GitHub, Slack, databases, etc.) |
| **Local-first** | MCP works entirely locally—no cloud required |

[↑ Back to Table of Contents](#table-of-contents)

## Why we need a FastAPI server

### The problem: Multiple ways to access AI

Different users want to access local-ai-hub in different ways:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    USER ACCESS PATTERNS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USER TYPE              ACCESS METHOD           WHAT THEY NEED               │
│  ═════════              ═════════════           ══════════════               │
│                                                                              │
│  DBA using CLI          curl/wget               REST API endpoint            │
│  Developer in VS Code   Cline extension         MCP server                   │
│  Python application     Python SDK              REST API or direct import   │
│  Web dashboard          JavaScript fetch        REST API with CORS           │
│  Other services         Service-to-service     REST API with auth           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What FastAPI provides

**FastAPI** is a modern Python web framework that gives us:

| Feature | Description |
|:--------|:------------|
| **REST API Endpoints** | `/api/v1/database/analyze-log`, `/api/v1/docs/validate`, etc. |
| **Automatic Documentation** | Swagger UI at `/docs`, ReDoc at `/redoc` |
| **Request Validation** | Automatic JSON schema validation with Pydantic |
| **Async Support** | Non-blocking I/O for concurrent requests |
| **Middleware** | CORS, authentication, logging, metrics |

### Why not just use Ollama directly?

You could call Ollama directly, but you'd lose important functionality:

| Feature | Ollama Direct | local-ai-hub + FastAPI |
|:--------|:--------------|:-----------------------|
| Raw LLM access | ✓ | ✓ |
| Specialized prompts for DB/docs | ✗ | ✓ |
| Data sanitization (remove PII) | ✗ | ✓ |
| Multi-agent workflows | ✗ | ✓ |
| MCP tool support | ✗ | ✓ |
| Domain-specific validation | ✗ | ✓ |
| Structured output formatting | ✗ | ✓ |
| Usage metrics and logging | Basic | Comprehensive |

[↑ Back to Table of Contents](#table-of-contents)

## Architecture deep dive

### Complete system architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOCAL-AI-HUB ARCHITECTURE OVERVIEW                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USER LAYER                                                                  │
│  ══════════                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ curl / CLI  │  │    Cline    │  │  Dashboard  │  │ Python App  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │ REST           │ MCP           │ REST          │ REST           │
│         └────────────────┴───────────────┴───────────────┘                 │
│                                    │                                         │
│  APPLICATION LAYER                 ▼                                         │
│  ═════════════════  ┌─────────────────────────────────────────────┐        │
│                     │            FASTAPI SERVER (:8080)           │        │
│                     │  • REST API endpoints                       │        │
│                     │  • MCP server                                │        │
│                     │  • Request validation                        │        │
│                     │  • Authentication                            │        │
│                     └────────────────────┬────────────────────────┘        │
│                                          │                                   │
│  AGENT LAYER       ┌─────────────────────┼─────────────────────┐           │
│  ════════════      │                     │                     │           │
│           ┌────────┴───────┐  ┌─────────┴────────┐  ┌─────────┴────────┐  │
│           │ DATABASE AGENTS│  │   DOC AGENTS     │  │  CODING AGENTS   │  │
│           │ • Log Analyzer │  │ • Converter      │  │ • Reviewer       │  │
│           │ • Query Expert │  │ • Validator      │  │ • Refactorer     │  │
│           │ • Config Tuner │  │ • Writer         │  │                  │  │
│           └────────┬───────┘  └─────────┬────────┘  └─────────┬────────┘  │
│                    └────────────────────┼────────────────────-┘           │
│                                         │                                   │
│  INFERENCE LAYER                        ▼                                   │
│  ═══════════════    ┌─────────────────────────────────────────────┐        │
│                     │           OLLAMA SERVER (:11434)            │        │
│                     │  • Model loading                            │        │
│                     │  • GPU/CPU inference                        │        │
│                     │  • OpenAI-compatible API                    │        │
│                     └────────────────────┬────────────────────────┘        │
│                                          │                                   │
│  MODEL LAYER                             ▼                                   │
│  ═══════════        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│                     │ Llama 3.1 8B │  │ Qwen 2.5 7B  │  │Qwen Coder 7B │  │
│                     │  (general)   │  │(tool calling)│  │    (code)    │  │
│                     └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                              │
│  HARDWARE LAYER                                                              │
│  ══════════════     ┌─────────────────────────────────────────────┐        │
│                     │  NVIDIA GPU (RTX 3060+ / A100)              │        │
│                     │  • 12-80 GB VRAM                            │        │
│                     │  • CUDA acceleration                        │        │
│                     └─────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Request flow example

```text
Example: Analyze a database log

1. User sends request
   curl -X POST http://localhost:8080/api/v1/database/analyze-log \
     -d '{"content": "ERROR: connection to 192.168.1.100 failed"}'

2. FastAPI validates and routes request

3. Sanitizer removes sensitive data
   "192.168.1.100" → "[REDACTED_IP]"

4. Log Analyzer Agent receives sanitized log + system prompt

5. Agent calls Ollama with llama3.1:8b

6. Ollama runs inference on GPU

7. Response flows back
   {
     "analysis": "Connection timeout to database server...",
     "severity": "High",
     "recommendations": ["Check network connectivity", ...]
   }
```

[↑ Back to Table of Contents](#table-of-contents)

## Core concepts reference

### Tokens

**Tokens** are the units of text that LLMs process. A token is typically a word or part of a word.

```text
"Hello world"     → ["Hello", " world"]           = 2 tokens
"PostgreSQL"      → ["Post", "gres", "QL"]        = 3 tokens
"authentication"  → ["auth", "ent", "ication"]    = 3 tokens
```

**Rule of thumb:** 1 token ≈ 4 characters or 0.75 words

### Context window

The maximum text an LLM can process at once. Larger windows allow longer documents but need more memory.

| Size | Characters | Use Case |
|:-----|:-----------|:---------|
| 8K tokens | ~32,000 | Standard conversations |
| 32K tokens | ~128,000 | Long documents |
| 128K tokens | ~512,000 | Entire codebases |

### Temperature

Controls randomness in output. Lower = more deterministic, higher = more creative.

- **0.0-0.3**: Use for factual tasks (database analysis)
- **0.5-0.7**: Balanced (general conversation)
- **0.8-1.0**: Creative tasks (writing)

### Quantization

Reduces model size by using lower precision numbers.

| Format | Size (7B model) | Quality | Speed |
|:-------|:----------------|:--------|:------|
| FP16 | 14 GB | Excellent | Fast |
| Q8 | 7 GB | Very Good | Faster |
| Q4 | 4 GB | Good | Fastest |

[↑ Back to Table of Contents](#table-of-contents)

## Hardware terminology

### VRAM (Video RAM)

GPU memory where models are loaded. LLMs must fit in VRAM for GPU acceleration.

| Model Size | VRAM (Q4) | Example GPUs |
|:-----------|:----------|:-------------|
| 7-8B | 4-5 GB | RTX 3060, 4060 |
| 14B | 8-9 GB | RTX 3080, 4070 |
| 70B | 40-42 GB | A100, 2x RTX 4090 |

### GPU tiers

| Tier | GPUs | VRAM | Best For |
|:-----|:-----|:-----|:---------|
| Consumer | RTX 3060/4060 | 8-12 GB | Development |
| Prosumer | RTX 3090/4090 | 24 GB | Team use |
| Datacenter | A100, H100 | 40-80 GB | Production |

[↑ Back to Table of Contents](#table-of-contents)

## Glossary quick reference

| Term | Definition |
|:-----|:-----------|
| **Agent** | AI system that can plan, use tools, and take actions |
| **Context Window** | Maximum tokens an LLM can process at once |
| **CrewAI** | Framework for building multi-agent AI systems |
| **CUDA** | NVIDIA's GPU computing platform |
| **Embedding** | Vector representation of text for similarity search |
| **FastAPI** | Python web framework for building APIs |
| **Fine-tuning** | Additional training to specialize a model |
| **Hallucination** | When AI generates plausible but incorrect information |
| **Inference** | Running a model to generate output |
| **LLM** | Large Language Model—AI trained on text data |
| **LoRA** | Low-Rank Adaptation—efficient fine-tuning technique |
| **MCP** | Model Context Protocol—standard for AI tool integration |
| **Ollama** | Tool for running LLMs locally |
| **Parameters** | Learned values in a model (7B = 7 billion) |
| **Prompt** | Input text provided to an LLM |
| **Quantization** | Reducing model precision to save memory (Q4, Q8) |
| **RAG** | Retrieval-Augmented Generation—adding documents as context |
| **Temperature** | Controls randomness in model output (0=deterministic) |
| **Token** | Unit of text (~4 characters) |
| **Tool Calling** | LLM ability to request function execution |
| **Vector Database** | Database optimized for similarity search (ChromaDB, Qdrant) |
| **vLLM** | High-performance inference engine |
| **VRAM** | GPU memory where models are loaded |

[↑ Back to Table of Contents](#table-of-contents)
