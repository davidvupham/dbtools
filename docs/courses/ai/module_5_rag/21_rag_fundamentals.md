# Chapter 21: RAG fundamentals

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-5_RAG-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain what RAG is and why it matters
2. Describe the RAG pipeline architecture
3. Identify when RAG is the right solution
4. Understand the key components: retrieval and generation

## Table of contents

- [Introduction](#introduction)
- [What is RAG?](#what-is-rag)
- [Why RAG matters](#why-rag-matters)
- [RAG architecture](#rag-architecture)
- [The RAG pipeline](#the-rag-pipeline)
- [When to use RAG](#when-to-use-rag)
- [RAG vs alternatives](#rag-vs-alternatives)
- [Key challenges](#key-challenges)
- [Key terminology](#key-terminology)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

LLMs have impressive knowledge, but they have critical limitations:

- **Knowledge cutoff**: They only know what was in their training data
- **No access to your data**: They cannot read your internal documentation
- **Hallucinations**: They may confidently provide incorrect information

**Retrieval-Augmented Generation (RAG)** solves these problems by grounding LLM responses in your own data. Instead of relying solely on the model's training, RAG retrieves relevant information from your documents and provides it as context for the response.

[↑ Back to Table of Contents](#table-of-contents)

## What is RAG?

**RAG (Retrieval-Augmented Generation)** combines two capabilities:

1. **Retrieval**: Find relevant documents from your knowledge base
2. **Generation**: Use those documents as context for the LLM response

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RETRIEVAL-AUGMENTED GENERATION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Without RAG                          With RAG                             │
│   ──────────                           ────────                             │
│                                                                             │
│   User ──► LLM ──► Response            User ──┬──────────────────────┐      │
│                                               │                      │      │
│   LLM uses only                               ▼                      ▼      │
│   training knowledge         ┌──────────────────────┐    ┌──────────────┐  │
│                              │  Retrieve relevant   │    │  Your Docs   │  │
│                              │  documents           │◄───│  (knowledge  │  │
│                              └──────────┬───────────┘    │   base)      │  │
│                                         │                └──────────────┘  │
│                                         ▼                                  │
│                              ┌──────────────────────┐                      │
│                              │  LLM generates       │                      │
│                              │  response using      │                      │
│                              │  retrieved context   │                      │
│                              └──────────┬───────────┘                      │
│                                         │                                  │
│                                         ▼                                  │
│                                     Response                               │
│                                  (grounded in                              │
│                                   your data)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Simple analogy

Think of RAG like an open-book exam:

- **Without RAG**: Student answers from memory (may be incomplete or wrong)
- **With RAG**: Student can look up answers in reference materials (more accurate)

[↑ Back to Table of Contents](#table-of-contents)

## Why RAG matters

### Problem 1: Knowledge cutoff

LLMs only know what was in their training data, which has a cutoff date.

```text
User: "What's our company's current database backup policy?"
LLM without RAG: "I don't have information about your specific company policies..."
LLM with RAG: "According to your runbook (retrieved), daily backups run at 02:00 UTC
              with 30-day retention. Weekly full backups are stored offsite..."
```

### Problem 2: No access to private data

LLMs cannot read your internal documentation, code, or databases.

```text
User: "How do I configure connection pooling for our PostgreSQL setup?"
LLM without RAG: "Here's a generic PgBouncer configuration..."
LLM with RAG: "Based on your internal docs, your team uses PgBouncer with
              transaction pooling. Here's the config from your standards doc..."
```

### Problem 3: Hallucinations

LLMs can confidently provide incorrect information.

```text
User: "What's the max_connections setting on our production database?"
LLM without RAG: "Typically, production databases use 200-500 connections..."
LLM with RAG: "According to your config repo, prod-db-01 has max_connections=350,
              last updated 2026-01-15 per ticket INFRA-1234..."
```

### Benefits of RAG

| Benefit | Description |
|:--------|:------------|
| **Accuracy** | Responses grounded in actual documents |
| **Up-to-date** | Access current information, not just training data |
| **Verifiable** | Can cite sources for responses |
| **Domain-specific** | Works with your organization's knowledge |
| **No retraining** | Add new knowledge without model fine-tuning |

[↑ Back to Table of Contents](#table-of-contents)

## RAG architecture

A typical RAG system has two main phases: **indexing** (offline) and **retrieval + generation** (online).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG ARCHITECTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INDEXING PHASE (Offline - done once or periodically)                      │
│   ═══════════════════════════════════════════════════                       │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│   │  Documents  │     │   Chunking  │     │  Embedding  │                   │
│   │             │────►│             │────►│   Model     │                   │
│   │ • Runbooks  │     │ Split into  │     │             │                   │
│   │ • Docs      │     │ smaller     │     │ Convert to  │                   │
│   │ • Code      │     │ pieces      │     │ vectors     │                   │
│   └─────────────┘     └─────────────┘     └──────┬──────┘                   │
│                                                  │                          │
│                                                  ▼                          │
│                                          ┌─────────────┐                    │
│                                          │   Vector    │                    │
│                                          │   Store     │                    │
│                                          │             │                    │
│                                          │ Store       │                    │
│                                          │ vectors +   │                    │
│                                          │ metadata    │                    │
│                                          └─────────────┘                    │
│                                                                             │
│   RETRIEVAL + GENERATION PHASE (Online - per query)                         │
│   ═════════════════════════════════════════════════                         │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│   │    User     │     │  Embedding  │     │   Vector    │                   │
│   │    Query    │────►│   Model     │────►│   Search    │                   │
│   │             │     │             │     │             │                   │
│   │ "How do I   │     │ Convert     │     │ Find        │                   │
│   │  configure  │     │ query to    │     │ similar     │                   │
│   │  backups?"  │     │ vector      │     │ chunks      │                   │
│   └─────────────┘     └─────────────┘     └──────┬──────┘                   │
│                                                  │                          │
│                                                  ▼                          │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        PROMPT CONSTRUCTION                          │   │
│   │                                                                     │   │
│   │   System: You are a helpful assistant. Answer based on the context. │   │
│   │                                                                     │   │
│   │   Context:                                                          │   │
│   │   [Retrieved chunk 1: "Backup configuration is in /etc/backup..."]  │   │
│   │   [Retrieved chunk 2: "Daily backups run at 02:00 UTC..."]          │   │
│   │   [Retrieved chunk 3: "Retention policy is 30 days..."]             │   │
│   │                                                                     │   │
│   │   User: How do I configure backups?                                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                            ┌─────────────┐                                  │
│                            │     LLM     │                                  │
│                            │             │                                  │
│                            │  Generate   │                                  │
│                            │  response   │                                  │
│                            └──────┬──────┘                                  │
│                                   │                                         │
│                                   ▼                                         │
│                               Response                                      │
│                         (grounded in retrieved docs)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

## The RAG pipeline

### Step 1: Document ingestion

Load your source documents.

```python
# Example document sources
documents = [
    "docs/runbooks/*.md",
    "docs/reference/*.md",
    "internal-wiki/database-team/*",
    "confluence-export/*.html"
]
```

### Step 2: Chunking

Split documents into smaller pieces that fit in the context window.

```text
Original document (5000 words)
            │
            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         CHUNKING                                      │
│                                                                       │
│   Strategy: Split by paragraphs/sections with overlap                 │
│   Chunk size: 512 tokens (recommended starting point)                 │
│   Overlap: 50 tokens (prevents cutting off context)                   │
│                                                                       │
│   Chunk 1: "Introduction to PostgreSQL backups... [tokens 1-512]"     │
│   Chunk 2: "...backups. Configuration options... [tokens 462-974]"    │
│   Chunk 3: "...options. Retention policies... [tokens 924-1436]"      │
│   ...                                                                 │
└───────────────────────────────────────────────────────────────────────┘
```

**Research finding**: A chunk size of 512 tokens generally delivers the best performance, balancing retrieval precision and efficiency.

### Step 3: Embedding

Convert text chunks into numerical vectors that capture semantic meaning.

```text
Chunk: "PostgreSQL backup configuration uses pg_dump..."
            │
            ▼
    ┌───────────────────┐
    │  Embedding Model  │
    │  (e.g., OpenAI    │
    │   text-embedding  │
    │   or local model) │
    └─────────┬─────────┘
              │
              ▼
Vector: [0.023, -0.156, 0.089, ..., 0.042]  (1536 dimensions)
```

### Step 4: Storage

Store vectors in a vector database for fast similarity search.

| Vector Store | Type | Best For |
|:-------------|:-----|:---------|
| **ChromaDB** | Embedded | Development, small datasets |
| **pgvector** | PostgreSQL extension | Existing PostgreSQL infrastructure |
| **FAISS** | Library | High performance, large scale |
| **Pinecone** | Managed service | Production, no ops overhead |

### Step 5: Retrieval

When a user asks a question, find the most relevant chunks.

```text
User query: "How do I configure database backups?"
            │
            ▼
    ┌───────────────────┐
    │  Embedding Model  │
    │  (same as indexing)│
    └─────────┬─────────┘
              │
              ▼
Query vector: [0.018, -0.142, 0.095, ..., 0.038]
              │
              ▼
    ┌───────────────────┐
    │  Vector Search    │
    │  (cosine similarity)│
    └─────────┬─────────┘
              │
              ▼
Top 3 similar chunks:
1. "Backup configuration uses pg_dump..." (similarity: 0.92)
2. "Daily backups run at 02:00 UTC..." (similarity: 0.87)
3. "Retention policy is 30 days..." (similarity: 0.84)
```

### Step 6: Generation

Construct a prompt with retrieved context and generate the response.

```text
SYSTEM: You are a database assistant. Answer questions using only the
        provided context. If the context doesn't contain the answer,
        say "I don't have information about that in my knowledge base."

CONTEXT:
[Chunk 1] Backup configuration uses pg_dump with the following options...
[Chunk 2] Daily backups run at 02:00 UTC with full backup on Sundays...
[Chunk 3] Retention policy is 30 days for daily, 1 year for weekly...

USER: How do I configure database backups?

ASSISTANT: Based on your documentation, database backups are configured using
           pg_dump. Daily incremental backups run at 02:00 UTC, with full
           backups on Sundays. The retention policy is 30 days for daily
           backups and 1 year for weekly full backups...
```

[↑ Back to Table of Contents](#table-of-contents)

## When to use RAG

### Good use cases for RAG

| Use Case | Example |
|:---------|:--------|
| **Internal documentation Q&A** | "How do I request a production deployment?" |
| **Technical support** | "What's the troubleshooting process for timeout errors?" |
| **Code assistance** | "How does our authentication module work?" |
| **Compliance queries** | "What's our data retention policy for PII?" |
| **Onboarding assistance** | "What tools does the DBA team use?" |

### When RAG might not be the best choice

| Scenario | Better Alternative |
|:---------|:-------------------|
| Real-time data (stock prices) | Direct API integration |
| Complex multi-hop reasoning | Agentic workflows |
| Highly structured data (tables) | SQL queries |
| Very small knowledge base | Include directly in prompt |
| Tasks requiring actions | MCP tools |

[↑ Back to Table of Contents](#table-of-contents)

## RAG vs alternatives

### RAG vs fine-tuning

| Aspect | RAG | Fine-tuning |
|:-------|:----|:------------|
| **Knowledge updates** | Easy—just add documents | Requires retraining |
| **Cost** | Lower—no training needed | Higher—GPU training costs |
| **Accuracy** | Cites sources, verifiable | May hallucinate |
| **Setup complexity** | Moderate—need vector store | High—need training pipeline |
| **Best for** | Factual Q&A, documentation | Style, format, behavior |

### RAG vs long context

| Aspect | RAG | Long Context (e.g., 200K tokens) |
|:-------|:----|:--------------------------------|
| **Token usage** | Lower—only relevant chunks | Higher—entire corpus |
| **Cost per query** | Lower | Higher |
| **Retrieval quality** | May miss relevant info | Sees everything |
| **Scalability** | Scales to millions of docs | Limited by context window |
| **Best for** | Large knowledge bases | Small, focused document sets |

### Recommendation

Start with RAG for most enterprise use cases. Consider long context for smaller, focused document sets where you need comprehensive coverage.

[↑ Back to Table of Contents](#table-of-contents)

## Key challenges

### Challenge 1: Retrieval quality

The model can only use what retrieval finds. Poor retrieval = poor answers.

**Mitigations:**
- Use hybrid search (semantic + keyword)
- Implement re-ranking
- Tune chunk size and overlap
- Add metadata filters

### Challenge 2: Chunking strategy

Wrong chunk size leads to either missing context or irrelevant noise.

| Issue | Symptom | Fix |
|:------|:--------|:----|
| Chunks too small | Missing context, incomplete answers | Increase chunk size |
| Chunks too large | Irrelevant information, higher cost | Decrease chunk size |
| No overlap | Answers cut off mid-thought | Add 10-20% overlap |

### Challenge 3: Hallucination despite RAG

LLMs can still hallucinate even with context.

**Mitigations:**
- Instruct model to only use provided context
- Ask model to cite sources
- Implement answer verification
- Add "I don't know" as valid response

### Challenge 4: Stale information

Documents change, but embeddings don't update automatically.

**Mitigations:**
- Implement incremental re-indexing
- Track document modification dates
- Set up scheduled full re-indexing

[↑ Back to Table of Contents](#table-of-contents)

## Key terminology

| Term | Definition |
|:-----|:-----------|
| **RAG** | Retrieval-Augmented Generation - combining retrieval with LLM generation |
| **Embedding** | Numerical vector representing semantic meaning of text |
| **Vector store** | Database optimized for storing and searching embeddings |
| **Chunk** | Segment of a document sized for retrieval and context |
| **Semantic search** | Finding documents by meaning, not just keywords |
| **Cosine similarity** | Metric for comparing vector similarity (0-1) |
| **Re-ranking** | Second pass to improve retrieval relevance |
| **Hybrid search** | Combining semantic and keyword search |

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- RAG grounds LLM responses in your own documents, reducing hallucinations
- The pipeline: ingest → chunk → embed → store → retrieve → generate
- RAG is ideal for documentation Q&A, knowledge bases, and domain-specific queries
- Key challenges include retrieval quality, chunk sizing, and keeping data fresh
- RAG is often preferable to fine-tuning for factual, updateable knowledge

## Next steps

Continue to **[Chapter 22: Document Processing](./22_document_processing.md)** to learn chunking strategies and metadata extraction.

## Additional resources

- [RAG Best Practices Study (arXiv)](https://arxiv.org/abs/2501.07391)
- [Prompt Engineering Guide: RAG](https://www.promptingguide.ai/research/rag)
- [Best RAG Tools and Frameworks](https://research.aimultiple.com/retrieval-augmented-generation/)
- [RAGAS Evaluation Framework](https://docs.ragas.io/)

[↑ Back to Table of Contents](#table-of-contents)
