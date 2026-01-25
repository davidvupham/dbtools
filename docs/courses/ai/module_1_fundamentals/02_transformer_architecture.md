# Chapter 2: Transformer architecture

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-1_Fundamentals-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain why transformers replaced previous architectures
2. Describe the attention mechanism conceptually
3. Understand how self-attention enables context understanding
4. Identify the key components of transformer architecture

## Table of contents

- [Introduction](#introduction)
- [Before transformers: The RNN problem](#before-transformers-the-rnn-problem)
- [The attention mechanism](#the-attention-mechanism)
- [Self-attention explained](#self-attention-explained)
- [Multi-head attention](#multi-head-attention)
- [The transformer architecture](#the-transformer-architecture)
- [Why this matters for you](#why-this-matters-for-you)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

In 2017, Google researchers published "Attention Is All You Need," introducing the transformer architecture. This paper revolutionized natural language processing and enabled the creation of modern LLMs like GPT, Claude, and Llama.

You do not need to understand the mathematics to use LLMs effectively, but understanding the core concepts helps you:
- Write better prompts by knowing how models "see" text
- Troubleshoot when models behave unexpectedly
- Make informed decisions about model selection

[↑ Back to Table of Contents](#table-of-contents)

## Before transformers: The RNN problem

Before transformers, language models used **Recurrent Neural Networks (RNNs)** and their variants (LSTMs, GRUs).

### How RNNs process text

RNNs process text sequentially—one word at a time, in order:

```text
RNN SEQUENTIAL PROCESSING
══════════════════════════

Input: "The database server crashed because of memory"

Processing order:
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│  The  │ → │  data │ → │ base  │ → │server │ → │crashed│ → │because│ → │  of   │ → ...
└───────┘   └───────┘   └───────┘   └───────┘   └───────┘   └───────┘   └───────┘
    ↓           ↓           ↓           ↓           ↓           ↓           ↓
  State₁  →  State₂  →  State₃  →  State₄  →  State₅  →  State₆  →  State₇  → ...

Each word updates the hidden state, carrying information forward.
```

### The problems with RNNs

| Problem | Description |
|:--------|:------------|
| **Sequential bottleneck** | Cannot parallelize—each step depends on the previous |
| **Vanishing gradients** | Information from early words "fades" over long sequences |
| **Long-range dependencies** | Hard to connect words far apart in a sentence |
| **Slow training** | Sequential nature limits GPU utilization |

**Example of the long-range dependency problem:**

```text
"The server that handles authentication, logging, and rate limiting crashed."
     ↑                                                                  ↑
     └──────────────────── 9 words apart ──────────────────────────────┘

By the time the RNN reaches "crashed," it may have "forgotten" that
the subject was "server."
```

[↑ Back to Table of Contents](#table-of-contents)

## The attention mechanism

**Attention** solves the long-range dependency problem by allowing the model to look at all words simultaneously and decide which ones are most relevant to each other.

### The core idea

Instead of processing sequentially, attention asks: "For each word, which other words should I pay attention to?"

```text
ATTENTION MECHANISM
═══════════════════

Sentence: "The server crashed because of memory pressure"

When processing "crashed," attention looks at ALL words:

                    ┌─────────────────────────────────────────────┐
                    │              ATTENTION WEIGHTS              │
                    ├─────────────────────────────────────────────┤
                    │                                             │
   "crashed" ───────┼──► "The"      ░░░░░░░░░░  (0.05) - low     │
         │          │──► "server"   ████████░░  (0.40) - HIGH    │
         │          │──► "crashed"  ████░░░░░░  (0.20)           │
         │          │──► "because"  ███░░░░░░░  (0.15)           │
         │          │──► "of"       ░░░░░░░░░░  (0.02)           │
         │          │──► "memory"   ███████░░░  (0.35) - HIGH    │
         │          │──► "pressure" █████░░░░░  (0.25)           │
         │          │                                             │
         │          └─────────────────────────────────────────────┘
         │
         └──► The model learns that "server" and "memory" are most
              relevant when understanding what "crashed" means.
```

### Key insight

Attention weights are **learned during training**. The model discovers which word relationships matter for understanding language—it is not programmed with grammar rules.

[↑ Back to Table of Contents](#table-of-contents)

## Self-attention explained

**Self-attention** (also called intra-attention) is attention applied within a single sequence. Each word attends to every other word in the same sentence.

### The Query-Key-Value (QKV) mechanism

Self-attention uses three learned transformations for each word:

```text
QKV MECHANISM
═════════════

For each word, we create three vectors:

┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   Word: "crashed"                                                            │
│                                                                              │
│   ┌─────────────┐                                                            │
│   │   Query (Q) │  "What am I looking for?"                                  │
│   │             │   → Used to search for relevant context                    │
│   └─────────────┘                                                            │
│                                                                              │
│   ┌─────────────┐                                                            │
│   │    Key (K)  │  "What do I contain?"                                      │
│   │             │   → Used to be found by other words' queries               │
│   └─────────────┘                                                            │
│                                                                              │
│   ┌─────────────┐                                                            │
│   │   Value (V) │  "What information do I provide?"                          │
│   │             │   → The actual content to use if this word is relevant     │
│   └─────────────┘                                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### How attention scores are computed

```text
ATTENTION COMPUTATION
═════════════════════

1. For word "crashed", compute its Query vector
2. For ALL words, compute their Key vectors
3. Calculate similarity: Query("crashed") · Key(each word)
4. Convert similarities to probabilities (softmax)
5. Use probabilities to weight each word's Value
6. Sum weighted Values = new representation of "crashed"

           Query("crashed")
                 │
                 ▼
    ┌─────────────────────────────────────────────────┐
    │  Dot product with each Key:                     │
    │                                                 │
    │  Q·K("The")     = 0.2                           │
    │  Q·K("server")  = 0.9   ← High similarity      │
    │  Q·K("crashed") = 0.7                           │
    │  Q·K("because") = 0.5                           │
    │  Q·K("memory")  = 0.8   ← High similarity      │
    └─────────────────────────────────────────────────┘
                 │
                 ▼ (softmax normalization)
    ┌─────────────────────────────────────────────────┐
    │  Attention weights (sum to 1.0):                │
    │                                                 │
    │  "The"     : 0.05                               │
    │  "server"  : 0.35   ← Gets most attention      │
    │  "crashed" : 0.20                               │
    │  "because" : 0.12                               │
    │  "memory"  : 0.28   ← Gets high attention      │
    └─────────────────────────────────────────────────┘
                 │
                 ▼
    New representation = 0.05×V("The") + 0.35×V("server") + ...
```

[↑ Back to Table of Contents](#table-of-contents)

## Multi-head attention

**Multi-head attention** runs multiple attention operations in parallel, each focusing on different aspects of the relationships.

```text
MULTI-HEAD ATTENTION
════════════════════

Instead of one attention operation, run several in parallel:

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Input: "The server crashed because of memory pressure"                    │
│                                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│   │    Head 1     │  │    Head 2     │  │    Head 3     │  ...              │
│   │               │  │               │  │               │                   │
│   │ Might learn:  │  │ Might learn:  │  │ Might learn:  │                   │
│   │ Subject-verb  │  │ Cause-effect  │  │ Adjective-    │                   │
│   │ relationships │  │ relationships │  │ noun pairs    │                   │
│   └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                   │
│           │                  │                  │                           │
│           └──────────────────┼──────────────────┘                           │
│                              │                                              │
│                              ▼                                              │
│                    ┌─────────────────┐                                      │
│                    │    Combine      │                                      │
│                    │    all heads    │                                      │
│                    └─────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Each head has its own Q, K, V weight matrices, learning different patterns.
```

### Why multiple heads?

| Benefit | Explanation |
|:--------|:------------|
| **Diverse perspectives** | Different heads capture different relationship types |
| **Redundancy** | Multiple chances to capture important patterns |
| **Specialization** | Some heads may focus on syntax, others on semantics |
| **Better gradients** | Multiple paths for learning during training |

Modern LLMs use 32-128 attention heads per layer.

[↑ Back to Table of Contents](#table-of-contents)

## The transformer architecture

A complete transformer combines attention with other components:

```text
TRANSFORMER ARCHITECTURE (Simplified)
═════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   INPUT: "The server crashed"                                               │
│           │                                                                 │
│           ▼                                                                 │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                    TOKEN EMBEDDINGS                               │     │
│   │    Convert words to vectors + add position information            │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│           │                                                                 │
│           ▼                                                                 │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                    TRANSFORMER BLOCK (×N)                         │     │
│   │   ┌─────────────────────────────────────────────────────────┐     │     │
│   │   │              Multi-Head Self-Attention                  │     │     │
│   │   │         (Each token attends to all tokens)              │     │     │
│   │   └─────────────────────────────────────────────────────────┘     │     │
│   │                           │                                       │     │
│   │                           ▼                                       │     │
│   │   ┌─────────────────────────────────────────────────────────┐     │     │
│   │   │              Add & Layer Normalize                      │     │     │
│   │   │          (Residual connection + normalization)          │     │     │
│   │   └─────────────────────────────────────────────────────────┘     │     │
│   │                           │                                       │     │
│   │                           ▼                                       │     │
│   │   ┌─────────────────────────────────────────────────────────┐     │     │
│   │   │              Feed-Forward Network                       │     │     │
│   │   │         (Process each position independently)           │     │     │
│   │   └─────────────────────────────────────────────────────────┘     │     │
│   │                           │                                       │     │
│   │                           ▼                                       │     │
│   │   ┌─────────────────────────────────────────────────────────┐     │     │
│   │   │              Add & Layer Normalize                      │     │     │
│   │   └─────────────────────────────────────────────────────────┘     │     │
│   │                                                                   │     │
│   │   (Repeat this block N times - typically 32-80 layers)            │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│           │                                                                 │
│           ▼                                                                 │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                    OUTPUT PROJECTION                              │     │
│   │       Convert to probability distribution over vocabulary         │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│           │                                                                 │
│           ▼                                                                 │
│   OUTPUT: Next token prediction                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key components explained

| Component | Purpose |
|:----------|:--------|
| **Token embeddings** | Convert words/tokens to numerical vectors |
| **Positional encoding** | Add position information (transformer has no inherent order) |
| **Multi-head attention** | Learn relationships between all tokens |
| **Feed-forward network** | Process each position with a neural network |
| **Layer normalization** | Stabilize training |
| **Residual connections** | Help gradients flow through deep networks |

[↑ Back to Table of Contents](#table-of-contents)

## Why this matters for you

Understanding transformer architecture helps you use LLMs more effectively:

### 1. Context window limitations

Attention computes relationships between ALL token pairs. This is why context windows have limits—the computation grows quadratically.

```text
Tokens    Attention Computations
1,000     1,000,000 (1M)
10,000    100,000,000 (100M)
100,000   10,000,000,000 (10B)
```

### 2. Position matters less than you think

Unlike RNNs, transformers can easily connect distant words. But they still benefit from clear structure in your prompts.

### 3. All tokens influence all tokens

When you provide context in a prompt, the model considers relationships with every other token. This is why:
- Irrelevant context can hurt performance
- Clear, focused prompts work better
- Order matters less than semantic clarity

### 4. Attention patterns reveal understanding

Some tools visualize attention patterns, showing which words the model considers related. This can help debug unexpected behavior.

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **Transformer** | Neural network architecture using self-attention |
| **Attention** | Mechanism for weighing importance of different inputs |
| **Self-attention** | Attention within a single sequence |
| **Query (Q)** | Vector representing what a token is looking for |
| **Key (K)** | Vector representing what a token contains |
| **Value (V)** | Vector containing actual information to retrieve |
| **Multi-head attention** | Multiple parallel attention operations |
| **Feed-forward network** | Neural network processing each position |
| **Residual connection** | Skip connection adding input to output |
| **Layer normalization** | Technique to stabilize training |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- RNNs processed text sequentially, causing long-range dependency problems
- Attention allows looking at all words simultaneously
- Self-attention uses Query, Key, Value to compute relevance scores
- Multi-head attention captures different types of relationships
- Transformers combine attention with feed-forward networks and normalization
- Understanding this architecture helps you write better prompts

## Next steps

Continue to **[Chapter 3: Tokenization](./03_tokenization.md)** to learn how text is converted into the numerical format that transformers process.

## Additional resources

- [Attention Is All You Need (Original Paper)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [DataCamp: How Transformers Work](https://www.datacamp.com/tutorial/how-transformers-work)
- [IBM: What is a Transformer Model?](https://www.ibm.com/think/topics/transformer-model)

[↑ Back to Table of Contents](#table-of-contents)
