# Chapter 23: Embeddings

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-5_RAG-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Explain how embeddings represent semantic meaning
2. Choose appropriate embedding models for your use case
3. Generate embeddings using local and API-based models
4. Optimize embedding performance and quality

## Table of contents

- [Introduction](#introduction)
- [How embeddings work](#how-embeddings-work)
- [Embedding models](#embedding-models)
- [Generating embeddings](#generating-embeddings)
- [Local embeddings with Ollama](#local-embeddings-with-ollama)
- [Embedding quality](#embedding-quality)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Embeddings are the bridge between human language and machine understanding. They transform text into dense numerical vectors where semantic similarity corresponds to geometric proximity. This chapter covers how embeddings work and how to use them effectively.

[↑ Back to Table of Contents](#table-of-contents)

## How embeddings work

### The concept

```text
EMBEDDING SPACE
═══════════════

Text chunks become points in high-dimensional space:

"PostgreSQL connection pool exhausted"     ●──────┐
                                                   │ Close in space
"Database connections at maximum"          ●──────┘ (semantically similar)


"The weather is sunny today"               ●  Far away
                                              (semantically different)

Similarity = cosine(vector_a, vector_b)
```

### Vector representation

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Text becomes a 384-dimensional vector
text = "Database performance is degrading"
embedding = model.encode(text)

print(f"Dimensions: {len(embedding)}")  # 384
print(f"Sample values: {embedding[:5]}")  # [-0.023, 0.156, ...]
```

### Similarity measurement

```python
import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate Euclidean distance between two vectors."""
    return np.linalg.norm(a - b)


# Example
query = "slow database queries"
doc1 = "SQL query performance issues"
doc2 = "Weather forecast for tomorrow"

query_emb = model.encode(query)
doc1_emb = model.encode(doc1)
doc2_emb = model.encode(doc2)

print(f"Query to Doc1: {cosine_similarity(query_emb, doc1_emb):.3f}")  # ~0.72
print(f"Query to Doc2: {cosine_similarity(query_emb, doc2_emb):.3f}")  # ~0.15
```

[↑ Back to Table of Contents](#table-of-contents)

## Embedding models

### Model comparison

| Model | Dimensions | Speed | Quality | Use Case |
|:------|:-----------|:------|:--------|:---------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose, local |
| nomic-embed-text | 768 | Fast | Very good | Local with Ollama |
| text-embedding-3-small | 1536 | API | Very good | OpenAI API |
| text-embedding-3-large | 3072 | API | Excellent | High-quality retrieval |
| mxbai-embed-large | 1024 | Medium | Excellent | Local, high quality |

### Choosing a model

```text
DECISION FLOWCHART
══════════════════

Need to run locally?
├── YES → Need highest quality?
│         ├── YES → mxbai-embed-large (1024d)
│         └── NO → nomic-embed-text (768d) or all-MiniLM-L6-v2 (384d)
│
└── NO → Budget constrained?
         ├── YES → text-embedding-3-small
         └── NO → text-embedding-3-large
```

### Dimension trade-offs

| Dimensions | Storage | Speed | Quality |
|:-----------|:--------|:------|:--------|
| 384 | ~1.5 KB/vector | Fastest | Good |
| 768 | ~3 KB/vector | Fast | Very good |
| 1536 | ~6 KB/vector | Medium | Excellent |
| 3072 | ~12 KB/vector | Slower | Best |

[↑ Back to Table of Contents](#table-of-contents)

## Generating embeddings

### Using Sentence Transformers

```python
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingGenerator:
    """Generate embeddings using Sentence Transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text."""
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Embed multiple texts efficiently."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True
        )
        return embeddings.tolist()


# Usage
generator = EmbeddingGenerator()

# Single embedding
emb = generator.embed_single("Database connection timeout")

# Batch embedding (much faster for multiple texts)
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = generator.embed_batch(texts)
```

### Using OpenAI API

```python
from openai import OpenAI


class OpenAIEmbeddings:
    """Generate embeddings using OpenAI API."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text."""
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts (API handles batching)."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]


# Usage
embedder = OpenAIEmbeddings()
embedding = embedder.embed_single("PostgreSQL optimization tips")
```

[↑ Back to Table of Contents](#table-of-contents)

## Local embeddings with Ollama

### Setup

```bash
# Pull an embedding model
ollama pull nomic-embed-text

# Verify
ollama list
```

### Using Ollama embeddings

```python
import requests


class OllamaEmbeddings:
    """Generate embeddings using Ollama."""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text."""
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts (sequential with Ollama)."""
        return [self.embed_single(text) for text in texts]


# Usage
embedder = OllamaEmbeddings()
embedding = embedder.embed_single("Index optimization for PostgreSQL")
print(f"Dimensions: {len(embedding)}")  # 768 for nomic-embed-text
```

### Async batch processing

```python
import asyncio
import aiohttp


class AsyncOllamaEmbeddings:
    """Async embedding generation for better throughput."""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
        concurrency: int = 4
    ):
        self.model = model
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(concurrency)

    async def embed_single(self, session: aiohttp.ClientSession, text: str) -> list[float]:
        """Embed single text with concurrency control."""
        async with self.semaphore:
            async with session.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            ) as response:
                data = await response.json()
                return data["embedding"]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.embed_single(session, text) for text in texts]
            return await asyncio.gather(*tasks)


# Usage
async def main():
    embedder = AsyncOllamaEmbeddings(concurrency=4)
    texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
    embeddings = await embedder.embed_batch(texts)
    print(f"Generated {len(embeddings)} embeddings")

asyncio.run(main())
```

[↑ Back to Table of Contents](#table-of-contents)

## Embedding quality

### Normalization

Some models output normalized vectors (length 1), others don't:

```python
import numpy as np


def normalize(embedding: list[float]) -> list[float]:
    """Normalize vector to unit length."""
    arr = np.array(embedding)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return embedding
    return (arr / norm).tolist()


# Check if already normalized
def is_normalized(embedding: list[float], tolerance: float = 1e-6) -> bool:
    """Check if vector is unit length."""
    length = np.linalg.norm(embedding)
    return abs(length - 1.0) < tolerance
```

### Handling long texts

Embedding models have input limits. Handle gracefully:

```python
def embed_long_text(
    text: str,
    embedder,
    max_tokens: int = 512
) -> list[float]:
    """Handle texts longer than model's context."""
    # Estimate token count (rough approximation)
    estimated_tokens = len(text) // 4

    if estimated_tokens <= max_tokens:
        return embedder.embed_single(text)

    # Split and average (simple approach)
    chunks = split_into_chunks(text, max_tokens * 4)  # chars
    embeddings = embedder.embed_batch(chunks)

    # Average the embeddings
    avg = np.mean(embeddings, axis=0)
    return normalize(avg.tolist())


def split_into_chunks(text: str, max_chars: int) -> list[str]:
    """Split text into chunks."""
    chunks = []
    for i in range(0, len(text), max_chars):
        chunks.append(text[i:i + max_chars])
    return chunks
```

### Query vs document embeddings

Some models use different prefixes for queries and documents:

```python
class PrefixedEmbeddings:
    """Handle models that need query/document prefixes."""

    QUERY_PREFIX = "search_query: "
    DOCUMENT_PREFIX = "search_document: "

    def __init__(self, base_embedder):
        self.embedder = base_embedder

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query."""
        return self.embedder.embed_single(f"{self.QUERY_PREFIX}{query}")

    def embed_document(self, document: str) -> list[float]:
        """Embed a document for indexing."""
        return self.embedder.embed_single(f"{self.DOCUMENT_PREFIX}{document}")

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        prefixed = [f"{self.DOCUMENT_PREFIX}{doc}" for doc in documents]
        return self.embedder.embed_batch(prefixed)
```

### Evaluation metrics

```python
def evaluate_embeddings(
    queries: list[str],
    relevant_docs: list[list[str]],
    all_docs: list[str],
    embedder
) -> dict:
    """Evaluate embedding quality for retrieval."""
    # Embed all documents
    doc_embeddings = embedder.embed_batch(all_docs)

    hits_at_1 = 0
    hits_at_5 = 0
    mrr_sum = 0

    for query, relevant in zip(queries, relevant_docs):
        query_emb = embedder.embed_single(query)

        # Calculate similarities
        similarities = [
            cosine_similarity(np.array(query_emb), np.array(doc_emb))
            for doc_emb in doc_embeddings
        ]

        # Rank documents
        ranked_indices = np.argsort(similarities)[::-1]
        ranked_docs = [all_docs[i] for i in ranked_indices]

        # Calculate metrics
        for rank, doc in enumerate(ranked_docs, 1):
            if doc in relevant:
                if rank == 1:
                    hits_at_1 += 1
                if rank <= 5:
                    hits_at_5 += 1
                mrr_sum += 1 / rank
                break

    n = len(queries)
    return {
        "hits@1": hits_at_1 / n,
        "hits@5": hits_at_5 / n,
        "mrr": mrr_sum / n
    }
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Embeddings transform text into vectors where similar meanings are geometrically close
- Choose embedding models based on quality needs, latency requirements, and deployment constraints
- Generate embeddings locally with Ollama or via APIs like OpenAI
- Handle edge cases like long texts and properly normalize vectors

## Next steps

Continue to **[Chapter 24: Vector Stores](./24_vector_stores.md)** to learn how to store and search embeddings efficiently.

[↑ Back to Table of Contents](#table-of-contents)
