# Project 5: Database Documentation RAG

**[← Back to Course Index](../README.md)**

> **Difficulty:** Advanced
> **Estimated Time:** 6-8 hours
> **Prerequisites:** Modules 1-5 completed

## Overview

Build a RAG system that indexes your organization's database documentation and enables natural language Q&A. The system should handle technical documentation, runbooks, and schema information.

## Learning objectives

By completing this project, you will:

1. Implement a complete RAG pipeline from ingestion to retrieval
2. Handle multiple document formats (markdown, SQL, YAML)
3. Build hybrid search with metadata filtering
4. Create an evaluation framework for retrieval quality

## Requirements

### Functional requirements

1. **Document ingestion**: Process markdown docs, SQL files, YAML configs
2. **Intelligent chunking**: Structure-aware chunking preserving headers
3. **Hybrid search**: Combine semantic and keyword search
4. **Metadata filtering**: Filter by document type, date, tags
5. **Answer generation**: Generate answers with source citations

### Document types to support

| Type | Format | Chunking Strategy |
|:-----|:-------|:------------------|
| Runbooks | Markdown | Header-based |
| Schema docs | SQL + comments | Function/table boundaries |
| Configuration | YAML | Section-based |
| Troubleshooting | Markdown | Problem/solution pairs |

## Architecture

```text
RAG PIPELINE
════════════

┌─────────────────────────────────────────────────────────────────┐
│                         Ingestion                                │
├─────────────────────────────────────────────────────────────────┤
│  Documents → Parser → Chunker → Embedder → Vector Store         │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Retrieval                                │
├─────────────────────────────────────────────────────────────────┤
│  Query → Embed → Hybrid Search → Re-rank → Context Selection    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Generation                                │
├─────────────────────────────────────────────────────────────────┤
│  Context + Query → LLM → Answer with Citations                  │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation guide

### Step 1: Document processing

```python
# src/ingestion/processors.py
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class ProcessedDocument:
    source: str
    content: str
    metadata: dict
    doc_type: str


class MarkdownProcessor:
    """Process markdown documentation."""

    def process(self, path: Path) -> ProcessedDocument:
        content = path.read_text()

        # Extract frontmatter if present
        metadata = self._extract_frontmatter(content)
        metadata["source"] = str(path)
        metadata["doc_type"] = "markdown"

        return ProcessedDocument(
            source=str(path),
            content=content,
            metadata=metadata,
            doc_type="markdown"
        )

    def _extract_frontmatter(self, content: str) -> dict:
        """Extract YAML frontmatter."""
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if match:
            import yaml
            return yaml.safe_load(match.group(1)) or {}
        return {}


class SQLProcessor:
    """Process SQL files with comments."""

    def process(self, path: Path) -> ProcessedDocument:
        content = path.read_text()

        # Extract header comment as description
        description = self._extract_header_comment(content)

        return ProcessedDocument(
            source=str(path),
            content=content,
            metadata={
                "source": str(path),
                "description": description,
                "doc_type": "sql"
            },
            doc_type="sql"
        )

    def _extract_header_comment(self, content: str) -> str:
        """Extract leading comment block."""
        lines = []
        for line in content.split('\n'):
            if line.startswith('--'):
                lines.append(line[2:].strip())
            elif line.strip() and not line.startswith('--'):
                break
        return ' '.join(lines)
```

### Step 2: Intelligent chunking

```python
# src/ingestion/chunker.py
from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    metadata: dict
    chunk_index: int
    parent_headers: list[str]


class MarkdownChunker:
    """Chunk markdown by headers."""

    def __init__(self, max_chunk_size: int = 1000):
        self.max_chunk_size = max_chunk_size

    def chunk(self, doc: ProcessedDocument) -> list[Chunk]:
        chunks = []
        current_headers = []
        current_content = []
        chunk_index = 0

        for line in doc.content.split('\n'):
            # Check for header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # Save current chunk if has content
                if current_content:
                    chunks.append(self._create_chunk(
                        current_content, current_headers.copy(),
                        chunk_index, doc.metadata
                    ))
                    chunk_index += 1
                    current_content = []

                # Update header hierarchy
                level = len(header_match.group(1))
                header_text = header_match.group(2)
                current_headers = current_headers[:level-1] + [header_text]

            current_content.append(line)

            # Check chunk size
            if len('\n'.join(current_content)) > self.max_chunk_size:
                chunks.append(self._create_chunk(
                    current_content, current_headers.copy(),
                    chunk_index, doc.metadata
                ))
                chunk_index += 1
                current_content = []

        # Final chunk
        if current_content:
            chunks.append(self._create_chunk(
                current_content, current_headers,
                chunk_index, doc.metadata
            ))

        return chunks

    def _create_chunk(
        self, lines: list, headers: list,
        index: int, base_metadata: dict
    ) -> Chunk:
        return Chunk(
            content='\n'.join(lines),
            metadata={
                **base_metadata,
                "headers": headers,
                "section": " > ".join(headers) if headers else "Introduction"
            },
            chunk_index=index,
            parent_headers=headers
        )
```

### Step 3: Hybrid retriever

```python
# src/retrieval/hybrid.py
import numpy as np


class HybridRetriever:
    """Combine semantic and keyword search."""

    def __init__(
        self,
        vector_store,
        embedder,
        keyword_weight: float = 0.3
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.keyword_weight = keyword_weight
        self.semantic_weight = 1 - keyword_weight

    async def search(
        self,
        query: str,
        k: int = 10,
        filters: dict = None
    ) -> list[dict]:
        """Hybrid search with RRF fusion."""
        # Semantic search
        query_embedding = self.embedder.embed(query)
        semantic_results = await self.vector_store.search(
            query_embedding, k=k*2, filters=filters
        )

        # Keyword search (BM25 or similar)
        keyword_results = await self.vector_store.keyword_search(
            query, k=k*2, filters=filters
        )

        # Reciprocal Rank Fusion
        fused = self._rrf_fusion(
            [semantic_results, keyword_results],
            weights=[self.semantic_weight, self.keyword_weight]
        )

        return fused[:k]

    def _rrf_fusion(
        self,
        result_lists: list[list[dict]],
        weights: list[float],
        k: int = 60
    ) -> list[dict]:
        """Reciprocal Rank Fusion."""
        scores = {}
        docs = {}

        for results, weight in zip(result_lists, weights):
            for rank, doc in enumerate(results, 1):
                doc_id = doc["id"]
                if doc_id not in scores:
                    scores[doc_id] = 0
                    docs[doc_id] = doc
                scores[doc_id] += weight * (1 / (k + rank))

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [docs[doc_id] for doc_id in sorted_ids]
```

### Step 4: Answer generation

```python
# src/generation/generator.py

class RAGGenerator:
    """Generate answers with citations."""

    PROMPT = """Answer the question based on the provided context.
Include citations in [1], [2] format referring to the sources.
If the context doesn't contain relevant information, say so.

Context:
{context}

Sources:
{sources}

Question: {question}

Answer:"""

    def __init__(self, llm):
        self.llm = llm

    async def generate(
        self,
        question: str,
        retrieved_docs: list[dict]
    ) -> dict:
        """Generate answer with citations."""
        # Format context
        context_parts = []
        sources = []

        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"[{i}] {doc['content']}")
            sources.append(f"[{i}] {doc['metadata'].get('source', 'Unknown')}")

        context = "\n\n".join(context_parts)
        sources_text = "\n".join(sources)

        # Generate
        prompt = self.PROMPT.format(
            context=context,
            sources=sources_text,
            question=question
        )

        answer = await self.llm.generate(prompt)

        return {
            "answer": answer,
            "sources": retrieved_docs,
            "question": question
        }
```

## Implementation tasks

### Part 1: Ingestion pipeline (30%)

- [ ] Implement document processors (markdown, SQL, YAML)
- [ ] Implement structure-aware chunking
- [ ] Build metadata extraction
- [ ] Create ingestion CLI tool

### Part 2: Retrieval (35%)

- [ ] Set up vector store (ChromaDB or pgvector)
- [ ] Implement hybrid search
- [ ] Add metadata filtering
- [ ] Implement re-ranking

### Part 3: Generation (20%)

- [ ] Build RAG generator with citations
- [ ] Handle "no relevant information" cases
- [ ] Add confidence scoring

### Part 4: Evaluation (15%)

- [ ] Create test question set
- [ ] Implement retrieval metrics (precision, recall)
- [ ] Build answer quality evaluation

## Expected usage

```python
from rag import DocumentRAG

# Initialize
rag = DocumentRAG(
    vector_store="chromadb",
    embedding_model="nomic-embed-text",
    llm_model="llama3.1:8b"
)

# Ingest documents
await rag.ingest_directory("./docs/runbooks")
await rag.ingest_directory("./docs/schemas")

# Query
result = await rag.query(
    "How do I troubleshoot slow PostgreSQL queries?",
    filters={"doc_type": "runbook"}
)

print(result["answer"])
print("\nSources:")
for source in result["sources"]:
    print(f"  - {source['metadata']['source']}")
```

## Evaluation criteria

| Criterion | Points |
|:----------|:-------|
| Ingestion pipeline handles all doc types | 25 |
| Hybrid search implemented correctly | 25 |
| Answer generation with citations | 20 |
| Metadata filtering works | 15 |
| Evaluation metrics implemented | 15 |
| **Total** | **100** |

---

**[Next Module →](../module_6_local_deployment/26_why_local.md)**
