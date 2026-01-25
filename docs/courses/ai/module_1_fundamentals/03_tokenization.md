# Chapter 3: Tokenization

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-1_Fundamentals-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain what tokenization is and why it matters
2. Describe how Byte Pair Encoding (BPE) works
3. Estimate token counts for different types of text
4. Understand context windows and their implications

## Table of contents

- [Introduction](#introduction)
- [What is tokenization?](#what-is-tokenization)
- [Why not just use words?](#why-not-just-use-words)
- [Byte Pair Encoding (BPE)](#byte-pair-encoding-bpe)
- [Token estimation](#token-estimation)
- [Context windows](#context-windows)
- [Practical implications](#practical-implications)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

LLMs do not process text directly—they process numbers. **Tokenization** is the process of converting text into numerical tokens that the model can work with. Understanding tokenization helps you:

- Estimate costs (APIs charge per token)
- Work within context limits
- Understand why some text behaves unexpectedly
- Optimize prompts for efficiency

[↑ Back to Table of Contents](#table-of-contents)

## What is tokenization?

**Tokenization** splits text into smaller units called **tokens**. Each token is assigned a unique numerical ID from the model's vocabulary.

```text
TOKENIZATION EXAMPLE
════════════════════

Input text: "The PostgreSQL server crashed"

Tokenization:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   "The PostgreSQL server crashed"                                           │
│         │                                                                   │
│         ▼ (tokenize)                                                        │
│                                                                             │
│   ┌─────┬─────┬──────┬─────┬────────┬─────────┐                             │
│   │ The │Post │ gres │ QL  │ server │ crashed │                             │
│   └─────┴─────┴──────┴─────┴────────┴─────────┘                             │
│      │     │      │     │      │        │                                   │
│      ▼     ▼      ▼     ▼      ▼        ▼                                   │
│   ┌─────┬─────┬──────┬─────┬────────┬─────────┐                             │
│   │ 464 │8225 │ 4951 │7518 │  4382  │  28996  │                             │
│   └─────┴─────┴──────┴─────┴────────┴─────────┘                             │
│                                                                             │
│   6 tokens total                                                            │
│   Note: "PostgreSQL" → 3 tokens (Post + gres + QL)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key insight

Tokens are not always words. They can be:
- Whole words: "the", "server"
- Word pieces: "Post", "gres", "QL"
- Single characters: punctuation, rare letters
- Subwords: common prefixes/suffixes

[↑ Back to Table of Contents](#table-of-contents)

## Why not just use words?

Using whole words as tokens has significant problems:

### Problem 1: Vocabulary size

English has hundreds of thousands of words, plus:
- Technical terms (PostgreSQL, Kubernetes, JDBC)
- Proper nouns (names, places)
- Misspellings and variations
- Multiple languages

A word-based vocabulary would be enormous and include many rare words.

### Problem 2: Unknown words

What happens when the model encounters a word not in its vocabulary?

```text
Word-based approach:
"Configure the PostgreSQL server" → ["Configure", "the", "[UNKNOWN]", "server"]

The model has no information about "PostgreSQL"!
```

### Problem 3: Morphological variations

Related words would be separate vocabulary entries:

```text
"run", "runs", "running", "runner" → 4 separate tokens with no shared meaning
```

### The solution: Subword tokenization

Break words into meaningful pieces that can be recombined:

```text
Subword approach:
"PostgreSQL" → ["Post", "gres", "QL"]
"running"    → ["run", "ning"]
"unhelpful"  → ["un", "help", "ful"]

Benefits:
- Smaller vocabulary (typically 32K-100K tokens)
- Can represent ANY text (no unknown words)
- Related words share subword tokens
```

[↑ Back to Table of Contents](#table-of-contents)

## Byte Pair Encoding (BPE)

**Byte Pair Encoding (BPE)** is the most common tokenization algorithm used by modern LLMs (GPT, Llama, Claude).

### How BPE works

BPE builds a vocabulary by finding the most common character pairs and merging them:

```text
BPE ALGORITHM (Simplified)
══════════════════════════

Starting corpus: "low lower lowest"

Step 1: Start with character-level tokens
        ['l', 'o', 'w', ' ', 'l', 'o', 'w', 'e', 'r', ' ', 'l', 'o', 'w', 'e', 's', 't']

Step 2: Find most common pair → ('l', 'o') appears 3 times
        Merge: 'l' + 'o' → 'lo'
        ['lo', 'w', ' ', 'lo', 'w', 'e', 'r', ' ', 'lo', 'w', 'e', 's', 't']

Step 3: Find most common pair → ('lo', 'w') appears 3 times
        Merge: 'lo' + 'w' → 'low'
        ['low', ' ', 'low', 'e', 'r', ' ', 'low', 'e', 's', 't']

Step 4: Find most common pair → ('low', 'e') appears 2 times
        Merge: 'low' + 'e' → 'lowe'
        ['low', ' ', 'lowe', 'r', ' ', 'lowe', 's', 't']

... continue until vocabulary size is reached (typically 32K-100K merges)
```

### BPE properties

| Property | Implication |
|:---------|:------------|
| **Common words** | Become single tokens ("the", "and", "is") |
| **Rare words** | Split into multiple pieces |
| **Technical terms** | Often split ("PostgreSQL" → 3 tokens) |
| **Whitespace** | Usually attached to following word ("_the") |
| **Numbers** | Often tokenized digit-by-digit |

[↑ Back to Table of Contents](#table-of-contents)

## Token estimation

Understanding token counts helps you estimate costs and work within limits.

### General rules of thumb

```text
TOKEN ESTIMATION GUIDE
══════════════════════

English text:
  1 token    ≈ 4 characters
  1 token    ≈ 0.75 words (¾ of a word)
  100 tokens ≈ 75 words
  1,000 tokens ≈ 750 words ≈ 1.5 pages

Code:
  Generally more tokens than English prose
  Indentation, brackets, and syntax add tokens
  1,000 tokens ≈ 30-50 lines of code (varies by language)
```

### Token counts by content type

| Content Type | Tokens per 1000 chars | Notes |
|:-------------|:----------------------|:------|
| English prose | ~250 | Standard text |
| Technical documentation | ~280 | More jargon = more tokens |
| Python code | ~350 | Indentation, syntax |
| JSON data | ~400 | Brackets, quotes, keys |
| SQL queries | ~300 | Keywords, operators |
| Log files | ~350 | Timestamps, IDs |

### Examples with actual token counts

```text
TOKENIZATION EXAMPLES
═════════════════════

"Hello, world!"
→ 4 tokens: ["Hello", ",", " world", "!"]

"SELECT * FROM users WHERE id = 123;"
→ 10 tokens: ["SELECT", " *", " FROM", " users", " WHERE", " id", " =", " 123", ";"]

"The quick brown fox jumps over the lazy dog."
→ 10 tokens: ["The", " quick", " brown", " fox", " jumps", " over", " the", " lazy", " dog", "."]

"2026-01-24T15:30:00Z"
→ 9 tokens: ["202", "6", "-", "01", "-", "24", "T", "15", ":30:00Z"]
(Note: dates/times often tokenize poorly)

"PostgreSQL"
→ 3 tokens: ["Post", "gres", "QL"]

"error"
→ 1 token: ["error"]
```

[↑ Back to Table of Contents](#table-of-contents)

## Context windows

The **context window** is the maximum number of tokens a model can process at once—both input and output combined.

### Context window sizes

| Model | Context Window | Approximate |
|:------|:---------------|:------------|
| GPT-3.5 | 4K / 16K tokens | 3K-12K words |
| GPT-4 | 8K / 32K / 128K tokens | 6K-100K words |
| Claude 3 | 200K tokens | ~150K words |
| Llama 3.1 | 128K tokens | ~100K words |
| Local 7B models | 4K-32K tokens | 3K-25K words |

### How context is used

```text
CONTEXT WINDOW USAGE
════════════════════

Total context window: 8,000 tokens
                     ─────────────────────────────────────
                     │                                   │
                     ▼                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                     SYSTEM PROMPT                                   │    │
│   │                     (500 tokens)                                    │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                     CONVERSATION HISTORY                            │    │
│   │                     (Previous messages: 2,000 tokens)               │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                     RETRIEVED CONTEXT (RAG)                         │    │
│   │                     (Documents: 3,000 tokens)                       │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                     CURRENT USER MESSAGE                            │    │
│   │                     (500 tokens)                                    │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                     RESERVED FOR RESPONSE                           │    │
│   │                     (2,000 tokens)                                  │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   Total: 500 + 2,000 + 3,000 + 500 + 2,000 = 8,000 tokens               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### What happens when you exceed the context?

| Approach | Behavior |
|:---------|:---------|
| **Truncation** | Oldest messages are dropped |
| **Summarization** | Old context is summarized to save tokens |
| **Sliding window** | Only recent N tokens are kept |
| **Error** | Some APIs reject requests exceeding limits |

[↑ Back to Table of Contents](#table-of-contents)

## Practical implications

### 1. Cost estimation

Most API providers charge per token (input + output):

```text
Example cost calculation (hypothetical rates):
─────────────────────────────────────────────

Input:  2,000 tokens × $0.01/1K = $0.02
Output: 1,000 tokens × $0.03/1K = $0.03
Total:  $0.05 per request

1,000 requests/day × $0.05 = $50/day = $1,500/month
```

### 2. Optimize token usage

| Technique | Token Savings |
|:----------|:--------------|
| Remove unnecessary whitespace | 5-10% |
| Use abbreviations in prompts | 10-20% |
| Summarize long context | 50-80% |
| Use structured formats (JSON) | Varies |
| Avoid repetitive instructions | 10-30% |

### 3. Technical terms tokenize poorly

```text
Domain-specific terms often become many tokens:

"Kubernetes"  → 3 tokens: ["Kub", "ern", "etes"]
"PostgreSQL"  → 3 tokens: ["Post", "gres", "QL"]
"OAuth2"      → 3 tokens: ["O", "Auth", "2"]
"JDBC"        → 2 tokens: ["JD", "BC"]
```

This can matter for:
- Cost (more tokens = higher cost)
- Context limits (less room for content)
- Understanding (rare subwords may be less well-learned)

### 4. Numbers and dates

Numbers often tokenize digit-by-digit:

```text
"12345"           → 3 tokens: ["123", "45"]
"2026-01-24"      → 5+ tokens: ["202", "6", "-", "01", "-24"]
"192.168.1.100"   → 7 tokens: ["192", ".", "168", ".", "1", ".", "100"]
```

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **Token** | A unit of text processed by the model |
| **Tokenization** | Process of converting text to tokens |
| **Vocabulary** | Set of all possible tokens (typically 32K-100K) |
| **BPE** | Byte Pair Encoding - common tokenization algorithm |
| **Subword** | Token representing part of a word |
| **Context window** | Maximum tokens the model can process |
| **Token ID** | Numerical identifier for each token |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Tokenization converts text to numerical tokens for model processing
- BPE creates tokens from common character pairs
- 1 token ≈ 4 characters ≈ ¾ of a word in English
- Context windows limit total input + output tokens
- Technical terms and numbers often tokenize into many pieces
- Token counts directly impact costs and context limits

## Next steps

Continue to **[Chapter 4: Model Parameters](./04_model_parameters.md)** to understand what model sizes (7B, 70B) mean and how quantization affects performance.

## Additional resources

- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) - Visualize tokenization
- [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers/)
- [BPE Paper](https://arxiv.org/abs/1508.07909) - Original research

[↑ Back to Table of Contents](#table-of-contents)
