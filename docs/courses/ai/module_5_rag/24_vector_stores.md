# Chapter 24: Vector stores

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-5_RAG-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Choose the right vector store for your use case
2. Implement vector storage with ChromaDB and pgvector
3. Configure indexes for optimal search performance
4. Manage vector data at scale

## Table of contents

- [Introduction](#introduction)
- [Vector store comparison](#vector-store-comparison)
- [ChromaDB](#chromadb)
- [pgvector](#pgvector)
- [Index types](#index-types)
- [Scaling considerations](#scaling-considerations)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Vector stores are specialized databases optimized for storing and searching high-dimensional vectors. Unlike traditional databases that use exact matching, vector stores find the most similar vectors using approximate nearest neighbor (ANN) algorithms.

[↑ Back to Table of Contents](#table-of-contents)

## Vector store comparison

### Overview

| Store | Type | Best For | Deployment |
|:------|:-----|:---------|:-----------|
| **ChromaDB** | Embedded/Server | Development, small-medium | Local, Docker |
| **pgvector** | PostgreSQL extension | Existing Postgres, ACID needs | Postgres server |
| **FAISS** | Library | Maximum speed, in-memory | Python app |
| **Pinecone** | Managed service | Serverless, managed | Cloud API |
| **Weaviate** | Full-featured | Multi-modal, GraphQL | Self-hosted, Cloud |
| **Qdrant** | High-performance | Production, filtering | Self-hosted, Cloud |

### Decision guide

```text
VECTOR STORE SELECTION
══════════════════════

Starting a new project?
├── YES → ChromaDB (easy to start, migrate later)
│
└── NO → Already using PostgreSQL?
         ├── YES → pgvector (add to existing stack)
         │
         └── NO → Need managed service?
                  ├── YES → Pinecone or Weaviate Cloud
                  │
                  └── NO → Need maximum performance?
                           ├── YES → Qdrant or FAISS
                           └── NO → ChromaDB or Weaviate
```

[↑ Back to Table of Contents](#table-of-contents)

## ChromaDB

### Installation and setup

```bash
pip install chromadb
```

### Basic usage

```python
import chromadb
from chromadb.config import Settings


# Create client (in-memory for development)
client = chromadb.Client()

# Or persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

# Create a collection
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)
```

### Adding documents

```python
def add_documents(
    collection,
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict] = None,
    ids: list[str] = None
):
    """Add documents to ChromaDB collection."""
    if ids is None:
        ids = [f"doc_{i}" for i in range(len(texts))]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas or [{} for _ in texts],
        ids=ids
    )


# Example usage
texts = [
    "PostgreSQL connection pooling with PgBouncer",
    "MySQL replication setup guide",
    "MongoDB sharding configuration"
]

# Generate embeddings (using your preferred method)
embeddings = embedder.embed_batch(texts)

metadatas = [
    {"database": "postgresql", "topic": "performance"},
    {"database": "mysql", "topic": "replication"},
    {"database": "mongodb", "topic": "scaling"}
]

add_documents(collection, texts, embeddings, metadatas)
```

### Querying

```python
def search(
    collection,
    query_embedding: list[float],
    n_results: int = 5,
    where: dict = None,
    where_document: dict = None
) -> dict:
    """Search for similar documents."""
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,  # Metadata filter
        where_document=where_document,  # Document content filter
        include=["documents", "metadatas", "distances"]
    )


# Simple search
query_emb = embedder.embed_single("How to optimize PostgreSQL performance?")
results = search(collection, query_emb, n_results=3)

for doc, metadata, distance in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
):
    print(f"Distance: {distance:.3f}")
    print(f"Document: {doc}")
    print(f"Metadata: {metadata}\n")


# Filtered search
results = search(
    collection,
    query_emb,
    n_results=3,
    where={"database": "postgresql"}  # Only PostgreSQL docs
)
```

### ChromaDB with automatic embedding

```python
from chromadb.utils import embedding_functions

# Use built-in embedding function
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.create_collection(
    name="auto_embed",
    embedding_function=embedding_fn
)

# Now you can add documents without pre-computing embeddings
collection.add(
    documents=["Document 1", "Document 2"],
    ids=["id1", "id2"]
)

# Query with text (embedding computed automatically)
results = collection.query(
    query_texts=["search query"],
    n_results=5
)
```

[↑ Back to Table of Contents](#table-of-contents)

## pgvector

### Installation

```sql
-- Install extension (requires superuser)
CREATE EXTENSION vector;
```

### Schema setup

```sql
-- Create table for documents
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),  -- Dimension must match your model
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for fast similarity search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Or use HNSW index (better quality, more memory)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Python integration

```python
import asyncpg
import numpy as np
from dataclasses import dataclass


@dataclass
class Document:
    id: int
    content: str
    embedding: list[float]
    metadata: dict


class PgVectorStore:
    """Vector store using pgvector."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(self.dsn)

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    async def add_document(
        self,
        content: str,
        embedding: list[float],
        metadata: dict = None
    ) -> int:
        """Add a document and return its ID."""
        async with self.pool.acquire() as conn:
            # Convert embedding to pgvector format
            embedding_str = f"[{','.join(map(str, embedding))}]"

            row = await conn.fetchrow(
                """
                INSERT INTO documents (content, embedding, metadata)
                VALUES ($1, $2::vector, $3::jsonb)
                RETURNING id
                """,
                content,
                embedding_str,
                metadata or {}
            )
            return row["id"]

    async def add_documents_batch(
        self,
        contents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] = None
    ):
        """Add multiple documents efficiently."""
        if metadatas is None:
            metadatas = [{} for _ in contents]

        async with self.pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO documents (content, embedding, metadata)
                VALUES ($1, $2::vector, $3::jsonb)
                """,
                [
                    (
                        content,
                        f"[{','.join(map(str, emb))}]",
                        meta
                    )
                    for content, emb, meta in zip(contents, embeddings, metadatas)
                ]
            )

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        metadata_filter: dict = None
    ) -> list[Document]:
        """Search for similar documents."""
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        query = """
            SELECT id, content, embedding, metadata,
                   1 - (embedding <=> $1::vector) as similarity
            FROM documents
        """

        params = [embedding_str]

        if metadata_filter:
            # Add JSONB filter
            query += " WHERE metadata @> $2::jsonb"
            params.append(metadata_filter)

        query += f" ORDER BY embedding <=> $1::vector LIMIT {limit}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            return [
                Document(
                    id=row["id"],
                    content=row["content"],
                    embedding=list(row["embedding"]),
                    metadata=row["metadata"]
                )
                for row in rows
            ]


# Usage
async def main():
    store = PgVectorStore("postgresql://user:pass@localhost/db")
    await store.connect()

    # Add documents
    embeddings = embedder.embed_batch(["Doc 1", "Doc 2", "Doc 3"])
    await store.add_documents_batch(
        contents=["Doc 1", "Doc 2", "Doc 3"],
        embeddings=embeddings,
        metadatas=[{"type": "tutorial"}, {"type": "guide"}, {"type": "reference"}]
    )

    # Search
    query_emb = embedder.embed_single("How do I configure PostgreSQL?")
    results = await store.search(query_emb, limit=3)

    for doc in results:
        print(f"ID: {doc.id}, Content: {doc.content}")

    await store.close()
```

### Distance operators in pgvector

| Operator | Distance Type | Use Case |
|:---------|:--------------|:---------|
| `<->` | L2 (Euclidean) | General purpose |
| `<=>` | Cosine | Normalized vectors |
| `<#>` | Inner product | When vectors are normalized |

[↑ Back to Table of Contents](#table-of-contents)

## Index types

### IVF (Inverted File Index)

```text
IVF INDEX
═════════

Documents are clustered into buckets (lists).
Query searches only nearby buckets.

┌─────────┐  ┌─────────┐  ┌─────────┐
│ Cluster │  │ Cluster │  │ Cluster │
│    1    │  │    2    │  │    3    │
├─────────┤  ├─────────┤  ├─────────┤
│ doc_1   │  │ doc_4   │  │ doc_7   │
│ doc_2   │  │ doc_5   │  │ doc_8   │
│ doc_3   │  │ doc_6   │  │ doc_9   │
└─────────┘  └─────────┘  └─────────┘

Query lands near Cluster 2 → Only search doc_4, doc_5, doc_6

Pros: Fast, low memory
Cons: May miss results in edge cases
```

### HNSW (Hierarchical Navigable Small World)

```text
HNSW INDEX
══════════

Multi-layer graph for efficient navigation:

Layer 2 (sparse):    A ─────────────── B
                      \               /
Layer 1 (medium):     A ── C ── D ── B
                       \    │    │   /
Layer 0 (dense):      A ─ E ─ C ─ D ─ F ─ B

Search: Start at top layer, descend to find nearest neighbors

Pros: Best recall, no training needed
Cons: More memory, slower inserts
```

### Configuration guidelines

```sql
-- IVF: lists ≈ sqrt(num_vectors)
-- For 1M vectors: lists = 1000
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 1000);

-- HNSW: m = connections per node, ef_construction = build quality
-- Higher values = better recall, more memory
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Index comparison

| Aspect | IVF | HNSW |
|:-------|:----|:-----|
| Build time | Fast | Slow |
| Query time | Fast | Faster |
| Memory | Lower | Higher |
| Recall | Good | Excellent |
| Updates | Needs rebuild | Incremental |

[↑ Back to Table of Contents](#table-of-contents)

## Scaling considerations

### Partitioning strategies

```python
class PartitionedVectorStore:
    """Vector store with metadata-based partitioning."""

    def __init__(self):
        self.partitions: dict[str, chromadb.Collection] = {}

    def get_partition(self, partition_key: str):
        """Get or create a partition."""
        if partition_key not in self.partitions:
            self.partitions[partition_key] = client.create_collection(
                name=f"partition_{partition_key}"
            )
        return self.partitions[partition_key]

    def add(self, text: str, embedding: list[float], partition_key: str):
        """Add document to appropriate partition."""
        collection = self.get_partition(partition_key)
        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())]
        )

    def search(self, query_embedding: list[float], partition_keys: list[str], n: int = 5):
        """Search across specified partitions."""
        all_results = []
        for key in partition_keys:
            if key in self.partitions:
                results = self.partitions[key].query(
                    query_embeddings=[query_embedding],
                    n_results=n
                )
                all_results.extend(zip(
                    results["documents"][0],
                    results["distances"][0]
                ))

        # Sort by distance and return top n
        all_results.sort(key=lambda x: x[1])
        return all_results[:n]
```

### Batch processing

```python
async def bulk_insert(
    store: PgVectorStore,
    documents: list[dict],
    batch_size: int = 1000
):
    """Insert documents in batches."""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]

        contents = [d["content"] for d in batch]
        embeddings = embedder.embed_batch(contents)
        metadatas = [d.get("metadata", {}) for d in batch]

        await store.add_documents_batch(contents, embeddings, metadatas)

        print(f"Inserted {min(i + batch_size, len(documents))}/{len(documents)}")
```

### Memory management

```python
class CachedVectorStore:
    """Vector store with LRU cache for frequent queries."""

    def __init__(self, store, cache_size: int = 1000):
        self.store = store
        self.cache = {}
        self.cache_order = []
        self.cache_size = cache_size

    def _cache_key(self, embedding: list[float], limit: int) -> str:
        """Create cache key from embedding."""
        # Use first few dimensions as key (approximate)
        return f"{embedding[:10]}_{limit}"

    async def search(self, query_embedding: list[float], limit: int = 5):
        """Search with caching."""
        key = self._cache_key(query_embedding, limit)

        if key in self.cache:
            return self.cache[key]

        results = await self.store.search(query_embedding, limit)

        # Add to cache
        if len(self.cache_order) >= self.cache_size:
            oldest = self.cache_order.pop(0)
            del self.cache[oldest]

        self.cache[key] = results
        self.cache_order.append(key)

        return results
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Choose vector stores based on your deployment needs and existing infrastructure
- ChromaDB is excellent for development and small-to-medium deployments
- pgvector integrates vector search into existing PostgreSQL databases
- IVF indexes trade some recall for speed; HNSW provides better recall at higher memory cost
- Scale with partitioning, batching, and caching strategies

## Next steps

Continue to **[Chapter 25: Retrieval Strategies](./25_retrieval_strategies.md)** to learn advanced techniques for finding the most relevant documents.

[↑ Back to Table of Contents](#table-of-contents)
