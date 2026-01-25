# Chapter 25: Retrieval strategies

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-5_RAG-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Implement hybrid search combining semantic and keyword retrieval
2. Apply re-ranking to improve result quality
3. Use query transformation techniques for better retrieval
4. Evaluate and tune retrieval performance

## Table of contents

- [Introduction](#introduction)
- [Hybrid search](#hybrid-search)
- [Query transformation](#query-transformation)
- [Re-ranking](#re-ranking)
- [Advanced retrieval patterns](#advanced-retrieval-patterns)
- [Evaluation](#evaluation)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Vector similarity search alone isn't always sufficient. Exact keyword matches, query reformulation, and re-ranking can significantly improve retrieval quality. This chapter covers advanced strategies for finding the most relevant documents.

[↑ Back to Table of Contents](#table-of-contents)

## Hybrid search

### Why hybrid?

```text
SEMANTIC VS KEYWORD SEARCH
══════════════════════════

Query: "PG connection pool timeout"

Semantic search finds:
✓ "Database connection management"
✓ "PostgreSQL client configuration"
✗ Misses exact "PG" abbreviation

Keyword search finds:
✓ "PG pool timeout settings"
✓ "PG connection errors"
✗ Misses paraphrased content

Hybrid combines both for better recall and precision.
```

### Implementation with pgvector

```sql
-- Create tables for hybrid search
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),
    content_tsvector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

-- Create both indexes
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON documents USING gin (content_tsvector);
```

```python
class HybridSearch:
    """Combine semantic and keyword search."""

    def __init__(self, pool, embedder):
        self.pool = pool
        self.embedder = embedder

    async def search(
        self,
        query: str,
        limit: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> list[dict]:
        """Perform hybrid search with weighted scores."""
        query_embedding = self.embedder.embed_single(query)
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                WITH semantic AS (
                    SELECT id, content,
                           1 - (embedding <=> $1::vector) as score
                    FROM documents
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2 * 2
                ),
                keyword AS (
                    SELECT id, content,
                           ts_rank(content_tsvector, plainto_tsquery('english', $3)) as score
                    FROM documents
                    WHERE content_tsvector @@ plainto_tsquery('english', $3)
                    LIMIT $2 * 2
                )
                SELECT
                    COALESCE(s.id, k.id) as id,
                    COALESCE(s.content, k.content) as content,
                    COALESCE(s.score, 0) * $4 + COALESCE(k.score, 0) * $5 as combined_score
                FROM semantic s
                FULL OUTER JOIN keyword k ON s.id = k.id
                ORDER BY combined_score DESC
                LIMIT $2
                """,
                embedding_str, limit, query, semantic_weight, keyword_weight
            )

            return [{"id": r["id"], "content": r["content"], "score": r["combined_score"]} for r in rows]
```

### Reciprocal Rank Fusion (RRF)

A popular method to combine rankings from different retrieval methods:

```python
def reciprocal_rank_fusion(
    rankings: list[list[str]],
    k: int = 60
) -> list[tuple[str, float]]:
    """Combine multiple rankings using RRF.

    Args:
        rankings: List of ranked document ID lists
        k: Constant to prevent high ranks from dominating

    Returns:
        Combined ranking with scores
    """
    scores = {}

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, 1):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank)

    # Sort by score descending
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs


# Usage
semantic_results = ["doc_3", "doc_1", "doc_5", "doc_2"]
keyword_results = ["doc_1", "doc_4", "doc_3", "doc_6"]

combined = reciprocal_rank_fusion([semantic_results, keyword_results])
# Result: [("doc_1", 0.032), ("doc_3", 0.032), ("doc_5", 0.016), ...]
```

[↑ Back to Table of Contents](#table-of-contents)

## Query transformation

### Query expansion

Add related terms to improve recall:

```python
async def expand_query(query: str, llm) -> str:
    """Expand query with related terms."""
    prompt = f"""Given this search query, add 2-3 related terms that might help find relevant documents.
Keep the original query and add terms in parentheses.

Query: {query}

Expanded query:"""

    expanded = await llm.generate(prompt)
    return expanded.strip()


# Example
# Input: "postgres slow queries"
# Output: "postgres slow queries (performance optimization indexes explain analyze)"
```

### Query decomposition

Break complex queries into sub-queries:

```python
async def decompose_query(query: str, llm) -> list[str]:
    """Break complex query into simpler sub-queries."""
    prompt = f"""Break this complex question into 2-4 simpler, focused questions that together would answer the original question.

Question: {query}

Sub-questions (one per line):"""

    response = await llm.generate(prompt)
    sub_queries = [q.strip() for q in response.strip().split('\n') if q.strip()]
    return sub_queries


async def multi_query_retrieval(
    query: str,
    retriever,
    llm
) -> list[dict]:
    """Retrieve using multiple sub-queries."""
    sub_queries = await decompose_query(query, llm)

    all_results = []
    seen_ids = set()

    for sub_query in sub_queries:
        results = await retriever.search(sub_query)
        for result in results:
            if result["id"] not in seen_ids:
                all_results.append(result)
                seen_ids.add(result["id"])

    return all_results


# Example
# Input: "How do I set up PostgreSQL replication and monitor it?"
# Sub-queries:
#   - "How to configure PostgreSQL replication"
#   - "PostgreSQL replication monitoring setup"
#   - "PostgreSQL replication health checks"
```

### Hypothetical Document Embedding (HyDE)

Generate a hypothetical answer, then search for similar real documents:

```python
async def hyde_search(
    query: str,
    retriever,
    llm,
    embedder
) -> list[dict]:
    """Use HyDE for improved retrieval."""
    # Generate hypothetical document
    prompt = f"""Write a short paragraph that would be a perfect answer to this question.
Write as if it's from a technical documentation.

Question: {query}

Answer:"""

    hypothetical_doc = await llm.generate(prompt)

    # Embed the hypothetical document
    hyde_embedding = embedder.embed_single(hypothetical_doc)

    # Search using the hypothetical document's embedding
    return await retriever.search_by_embedding(hyde_embedding)


# Example
# Query: "How to tune PostgreSQL for OLAP workloads?"
# HyDE generates: "For OLAP workloads, increase work_mem to 256MB or higher,
#                  set effective_cache_size to 75% of RAM, enable parallel queries..."
# Then searches for documents similar to this hypothetical answer
```

[↑ Back to Table of Contents](#table-of-contents)

## Re-ranking

### Why re-rank?

Initial retrieval prioritizes recall (finding all relevant docs). Re-ranking improves precision by reordering results using a more sophisticated model.

```text
RE-RANKING PIPELINE
═══════════════════

Query: "PostgreSQL index optimization"

Step 1: Initial retrieval (fast, high recall)
        Returns 20 candidates

Step 2: Re-rank (slower, high precision)
        Cross-encoder scores each (query, document) pair
        Reorders by relevance

Step 3: Return top 5 most relevant
```

### Cross-encoder re-ranking

```python
from sentence_transformers import CrossEncoder


class Reranker:
    """Re-rank results using a cross-encoder."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5
    ) -> list[dict]:
        """Re-rank documents by relevance to query."""
        if not documents:
            return []

        # Create query-document pairs
        pairs = [(query, doc["content"]) for doc in documents]

        # Score all pairs
        scores = self.model.predict(pairs)

        # Add scores to documents
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        # Sort by rerank score
        sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

        return sorted_docs[:top_k]


# Usage
reranker = Reranker()

# Get initial results (high recall)
initial_results = await retriever.search(query, limit=20)

# Re-rank for precision
final_results = reranker.rerank(query, initial_results, top_k=5)
```

### LLM-based re-ranking

```python
async def llm_rerank(
    query: str,
    documents: list[dict],
    llm,
    top_k: int = 5
) -> list[dict]:
    """Re-rank using LLM scoring."""
    scored_docs = []

    for doc in documents:
        prompt = f"""Rate how relevant this document is to the query on a scale of 1-10.
Only output the number.

Query: {query}

Document: {doc['content'][:500]}

Relevance score (1-10):"""

        response = await llm.generate(prompt)
        try:
            score = int(response.strip())
        except ValueError:
            score = 5  # Default

        scored_docs.append({**doc, "llm_score": score})

    sorted_docs = sorted(scored_docs, key=lambda x: x["llm_score"], reverse=True)
    return sorted_docs[:top_k]
```

### Cohere re-ranking

```python
import cohere


class CohereReranker:
    """Re-rank using Cohere's rerank API."""

    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5
    ) -> list[dict]:
        """Re-rank using Cohere."""
        response = self.client.rerank(
            query=query,
            documents=[doc["content"] for doc in documents],
            top_n=top_k,
            model="rerank-english-v2.0"
        )

        results = []
        for result in response.results:
            doc = documents[result.index].copy()
            doc["rerank_score"] = result.relevance_score
            results.append(doc)

        return results
```

[↑ Back to Table of Contents](#table-of-contents)

## Advanced retrieval patterns

### Parent document retrieval

Store small chunks for matching, but return larger parent chunks for context:

```python
class ParentDocumentRetriever:
    """Retrieve parent documents from child chunk matches."""

    def __init__(self, store, embedder):
        self.store = store
        self.embedder = embedder

    async def add_document(self, document: str, doc_id: str):
        """Add document with child chunks."""
        # Create small chunks for precise matching
        small_chunks = sentence_chunks(document, max_size=200)

        # Store each chunk with reference to parent
        for i, chunk in enumerate(small_chunks):
            embedding = self.embedder.embed_single(chunk)
            await self.store.add(
                content=chunk,
                embedding=embedding,
                metadata={
                    "parent_id": doc_id,
                    "chunk_index": i,
                    "parent_content": document  # Store full content
                }
            )

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search and return parent documents."""
        query_emb = self.embedder.embed_single(query)
        results = await self.store.search(query_emb, limit=limit * 2)

        # Deduplicate by parent and return parent content
        seen_parents = set()
        parent_docs = []

        for result in results:
            parent_id = result["metadata"]["parent_id"]
            if parent_id not in seen_parents:
                seen_parents.add(parent_id)
                parent_docs.append({
                    "id": parent_id,
                    "content": result["metadata"]["parent_content"],
                    "matched_chunk": result["content"]
                })

            if len(parent_docs) >= limit:
                break

        return parent_docs
```

### Self-query retrieval

Let the LLM generate metadata filters:

```python
async def self_query_retrieval(
    query: str,
    retriever,
    llm
) -> list[dict]:
    """Extract filters from natural language query."""
    prompt = f"""Given this search query, extract any filters and the core search query.

Available metadata filters:
- database: postgresql, mysql, mongodb
- type: tutorial, reference, troubleshooting
- difficulty: beginner, intermediate, advanced

Query: {query}

Output as JSON:
{{"filters": {{}}, "search_query": ""}}"""

    response = await llm.generate(prompt)

    try:
        parsed = json.loads(response)
        filters = parsed.get("filters", {})
        search_query = parsed.get("search_query", query)
    except json.JSONDecodeError:
        filters = {}
        search_query = query

    return await retriever.search(search_query, metadata_filter=filters)


# Example
# Input: "beginner PostgreSQL indexing tutorial"
# Extracted: filters={"database": "postgresql", "type": "tutorial", "difficulty": "beginner"}
#            search_query="indexing"
```

### Contextual compression

Compress retrieved documents to only the relevant parts:

```python
async def compress_for_context(
    query: str,
    documents: list[dict],
    llm,
    max_length: int = 500
) -> list[dict]:
    """Compress documents to relevant portions."""
    compressed = []

    for doc in documents:
        prompt = f"""Extract only the parts of this document that are directly relevant to the query.
Keep it concise, under {max_length} characters.

Query: {query}

Document:
{doc['content']}

Relevant excerpt:"""

        excerpt = await llm.generate(prompt)
        compressed.append({
            **doc,
            "original_content": doc["content"],
            "content": excerpt.strip()[:max_length]
        })

    return compressed
```

[↑ Back to Table of Contents](#table-of-contents)

## Evaluation

### Metrics

| Metric | Description | Formula |
|:-------|:------------|:--------|
| **Precision@k** | Fraction of relevant docs in top k | relevant_in_k / k |
| **Recall@k** | Fraction of relevant docs found in top k | relevant_in_k / total_relevant |
| **MRR** | Average reciprocal rank of first relevant | 1/rank |
| **NDCG** | Normalized discounted cumulative gain | Considers position and graded relevance |

### Evaluation implementation

```python
from dataclasses import dataclass


@dataclass
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg: float


def evaluate_retrieval(
    queries: list[str],
    relevant_docs: list[set[str]],
    retriever,
    k: int = 5
) -> RetrievalMetrics:
    """Evaluate retrieval quality."""
    precisions = []
    recalls = []
    mrrs = []

    for query, relevant in zip(queries, relevant_docs):
        results = retriever.search(query, limit=k)
        retrieved_ids = [r["id"] for r in results]

        # Precision@k
        relevant_retrieved = len(set(retrieved_ids) & relevant)
        precisions.append(relevant_retrieved / k)

        # Recall@k
        recalls.append(relevant_retrieved / len(relevant) if relevant else 0)

        # MRR
        mrr = 0
        for rank, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in relevant:
                mrr = 1 / rank
                break
        mrrs.append(mrr)

    return RetrievalMetrics(
        precision_at_k=sum(precisions) / len(precisions),
        recall_at_k=sum(recalls) / len(recalls),
        mrr=sum(mrrs) / len(mrrs),
        ndcg=0.0  # NDCG calculation omitted for brevity
    )
```

### A/B testing retrieval strategies

```python
class RetrievalExperiment:
    """Run A/B tests on retrieval strategies."""

    def __init__(self):
        self.results = {"A": [], "B": []}

    async def run_experiment(
        self,
        queries: list[str],
        retriever_a,
        retriever_b,
        evaluator
    ) -> dict:
        """Compare two retrieval strategies."""
        for query in queries:
            results_a = await retriever_a.search(query)
            results_b = await retriever_b.search(query)

            # Get user feedback or use ground truth
            score_a = await evaluator.score(query, results_a)
            score_b = await evaluator.score(query, results_b)

            self.results["A"].append(score_a)
            self.results["B"].append(score_b)

        return {
            "strategy_a_avg": sum(self.results["A"]) / len(self.results["A"]),
            "strategy_b_avg": sum(self.results["B"]) / len(self.results["B"]),
            "winner": "A" if sum(self.results["A"]) > sum(self.results["B"]) else "B"
        }
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Hybrid search combines semantic and keyword retrieval for better coverage
- Query transformation (expansion, decomposition, HyDE) improves retrieval
- Re-ranking with cross-encoders or LLMs improves result precision
- Advanced patterns like parent document retrieval provide better context
- Evaluation with precision, recall, and MRR guides optimization

## Next steps

You have completed Module 5! Continue to **[Module 6: Local LLM Deployment](../module_6_local_deployment/26_why_local.md)** to learn how to run models on your own infrastructure.

Before continuing, complete:
- **[Module 5 Exercises](./exercises/)**
- **[Module 5 Quiz](./quiz_module_5.md)**
- **[Project 5: Database Documentation RAG](./project_5_rag_system.md)**

[↑ Back to Table of Contents](#table-of-contents)
