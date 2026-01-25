# Chapter 22: Document processing

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 24, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Module](https://img.shields.io/badge/Module-5_RAG-blue)

## Learning objectives

By the end of this chapter, you will be able to:

1. Extract text from various document formats
2. Implement effective chunking strategies
3. Preserve document structure and metadata
4. Handle edge cases in document processing

## Table of contents

- [Introduction](#introduction)
- [Document extraction](#document-extraction)
- [Chunking strategies](#chunking-strategies)
- [Metadata extraction](#metadata-extraction)
- [Handling edge cases](#handling-edge-cases)
- [Summary](#summary)
- [Next steps](#next-steps)

## Introduction

Before documents can be retrieved, they must be processed into chunks suitable for embedding. Poor document processing leads to poor retrieval—garbage in, garbage out. This chapter covers techniques for extracting, chunking, and enriching documents.

[↑ Back to Table of Contents](#table-of-contents)

## Document extraction

### Common formats and tools

| Format | Tool | Notes |
|:-------|:-----|:------|
| PDF | PyMuPDF, pdfplumber | PyMuPDF faster, pdfplumber better for tables |
| Word (.docx) | python-docx | Preserves structure |
| HTML | BeautifulSoup | Handle boilerplate removal |
| Markdown | markdown-it | Parse to AST for structure |
| Plain text | Built-in | Handle encoding |

### PDF extraction

```python
import fitz  # PyMuPDF


def extract_pdf(path: str) -> list[dict]:
    """Extract text and metadata from PDF."""
    doc = fitz.open(path)
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page_number": page_num + 1,
            "text": text,
            "width": page.rect.width,
            "height": page.rect.height
        })

    return pages


def extract_pdf_with_tables(path: str) -> list[dict]:
    """Extract text preserving table structure."""
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables()

            # Format tables as markdown
            table_text = ""
            for table in tables:
                table_text += format_table_as_markdown(table) + "\n\n"

            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "tables": table_text
            })

    return pages


def format_table_as_markdown(table: list[list]) -> str:
    """Convert table to markdown format."""
    if not table or not table[0]:
        return ""

    # Header row
    header = "| " + " | ".join(str(cell) or "" for cell in table[0]) + " |"
    separator = "| " + " | ".join("---" for _ in table[0]) + " |"

    # Data rows
    rows = []
    for row in table[1:]:
        rows.append("| " + " | ".join(str(cell) or "" for cell in row) + " |")

    return "\n".join([header, separator] + rows)
```

### HTML extraction

```python
from bs4 import BeautifulSoup
import requests


def extract_html(url: str) -> dict:
    """Extract main content from HTML page."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove boilerplate
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()

    # Try to find main content
    main_content = (
        soup.find('main') or
        soup.find('article') or
        soup.find(class_='content') or
        soup.body
    )

    text = main_content.get_text(separator='\n', strip=True)

    return {
        "url": url,
        "title": soup.title.string if soup.title else "",
        "text": text
    }
```

[↑ Back to Table of Contents](#table-of-contents)

## Chunking strategies

### Why chunking matters

```text
CHUNKING TRADE-OFFS
═══════════════════

Chunk size too small:
├── Loses context
├── Fragments sentences
├── More embeddings to store
└── Retrieval may miss related info

Chunk size too large:
├── Dilutes relevance signal
├── Exceeds model context
├── Wastes tokens on irrelevant text
└── Less precise retrieval
```

### Fixed-size chunking

Simple but may split sentences mid-thought:

```python
def fixed_size_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # Overlap for context continuity

    return chunks
```

### Sentence-aware chunking

Respects sentence boundaries:

```python
import re


def sentence_chunks(text: str, max_chunk_size: int = 500) -> list[str]:
    """Split text at sentence boundaries."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence)

        if current_size + sentence_size > max_chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(sentence)
        current_size += sentence_size

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
```

### Semantic chunking

Group by meaning, not size:

```python
from sentence_transformers import SentenceTransformer
import numpy as np


def semantic_chunks(text: str, similarity_threshold: float = 0.7) -> list[str]:
    """Split text based on semantic similarity."""
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) < 2:
        return [text]

    # Get embeddings
    embeddings = model.encode(sentences)

    # Find break points where similarity drops
    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        # Compare with previous sentence
        similarity = np.dot(embeddings[i], embeddings[i-1]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i-1])
        )

        if similarity < similarity_threshold:
            # New topic - start new chunk
            chunks.append(' '.join(current_chunk))
            current_chunk = []

        current_chunk.append(sentences[i])

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
```

### Structure-aware chunking

Respect document structure:

```python
def markdown_chunks(markdown_text: str, max_chunk_size: int = 1000) -> list[dict]:
    """Split markdown by headers while respecting size limits."""
    chunks = []
    current_chunk = {"headers": [], "content": ""}

    lines = markdown_text.split('\n')

    for line in lines:
        # Check for headers
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2)

            # Save current chunk if it has content
            if current_chunk["content"].strip():
                chunks.append(current_chunk.copy())
                current_chunk["content"] = ""

            # Update header hierarchy
            current_chunk["headers"] = current_chunk["headers"][:level-1] + [header_text]

        else:
            # Check if adding this line exceeds limit
            if len(current_chunk["content"]) + len(line) > max_chunk_size:
                if current_chunk["content"].strip():
                    chunks.append(current_chunk.copy())
                current_chunk["content"] = line + "\n"
            else:
                current_chunk["content"] += line + "\n"

    if current_chunk["content"].strip():
        chunks.append(current_chunk)

    return chunks
```

### Chunking strategy comparison

| Strategy | Pros | Cons | Best For |
|:---------|:-----|:-----|:---------|
| Fixed-size | Simple, predictable | May split mid-sentence | Unstructured text |
| Sentence | Preserves meaning | Variable chunk sizes | Prose documents |
| Semantic | Topic-coherent | Computationally expensive | Technical documents |
| Structure-aware | Preserves hierarchy | Requires structured input | Markdown, HTML |

[↑ Back to Table of Contents](#table-of-contents)

## Metadata extraction

### Why metadata matters

Metadata enables:
- Filtering during retrieval
- Citation and attribution
- Temporal relevance
- Access control

### Extracting document metadata

```python
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class DocumentMetadata:
    source: str
    title: str
    created_at: datetime | None = None
    modified_at: datetime | None = None
    author: str | None = None
    page_number: int | None = None
    section: str | None = None
    tags: list[str] = field(default_factory=list)


def extract_metadata(path: str) -> DocumentMetadata:
    """Extract metadata from file."""
    p = Path(path)

    metadata = DocumentMetadata(
        source=str(p),
        title=p.stem,
        modified_at=datetime.fromtimestamp(p.stat().st_mtime)
    )

    # Format-specific extraction
    if p.suffix == '.pdf':
        metadata = enrich_from_pdf(path, metadata)
    elif p.suffix == '.docx':
        metadata = enrich_from_docx(path, metadata)

    return metadata


def enrich_from_pdf(path: str, metadata: DocumentMetadata) -> DocumentMetadata:
    """Extract PDF-specific metadata."""
    import fitz

    doc = fitz.open(path)
    pdf_metadata = doc.metadata

    if pdf_metadata.get('title'):
        metadata.title = pdf_metadata['title']
    if pdf_metadata.get('author'):
        metadata.author = pdf_metadata['author']
    if pdf_metadata.get('creationDate'):
        metadata.created_at = parse_pdf_date(pdf_metadata['creationDate'])

    return metadata


def parse_pdf_date(date_str: str) -> datetime | None:
    """Parse PDF date format (D:YYYYMMDDHHmmss)."""
    try:
        if date_str.startswith('D:'):
            date_str = date_str[2:16]
        return datetime.strptime(date_str, '%Y%m%d%H%M%S')
    except (ValueError, IndexError):
        return None
```

### Chunk-level metadata

```python
@dataclass
class ChunkWithMetadata:
    content: str
    document_metadata: DocumentMetadata
    chunk_index: int
    start_char: int
    end_char: int
    parent_headers: list[str] = field(default_factory=list)


def chunk_with_metadata(
    text: str,
    document_metadata: DocumentMetadata,
    chunk_size: int = 500
) -> list[ChunkWithMetadata]:
    """Create chunks with full metadata."""
    raw_chunks = sentence_chunks(text, chunk_size)

    chunks = []
    char_position = 0

    for i, chunk_text in enumerate(raw_chunks):
        start = text.find(chunk_text, char_position)
        end = start + len(chunk_text)

        chunks.append(ChunkWithMetadata(
            content=chunk_text,
            document_metadata=document_metadata,
            chunk_index=i,
            start_char=start,
            end_char=end
        ))

        char_position = end

    return chunks
```

[↑ Back to Table of Contents](#table-of-contents)

## Handling edge cases

### Tables

```python
def handle_tables(page_content: dict) -> str:
    """Combine text and tables appropriately."""
    text = page_content.get("text", "")
    tables = page_content.get("tables", "")

    if tables:
        # Add tables at the end with clear separation
        return f"{text}\n\n---\nTables on this page:\n{tables}"

    return text
```

### Code blocks

```python
def preserve_code_blocks(text: str) -> list[str]:
    """Chunk while preserving code blocks intact."""
    # Split on code block boundaries
    parts = re.split(r'(```[\s\S]*?```)', text)

    chunks = []
    for part in parts:
        if part.startswith('```'):
            # Keep code block whole
            chunks.append(part)
        else:
            # Chunk normal text
            chunks.extend(sentence_chunks(part))

    return chunks
```

### Images and diagrams

```python
def extract_with_images(pdf_path: str) -> list[dict]:
    """Extract text and describe images."""
    import fitz

    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        images = page.get_images()

        image_descriptions = []
        for img_index, img in enumerate(images):
            # Extract image for description (would use vision model in production)
            image_descriptions.append(f"[Image {img_index + 1} on page {page_num + 1}]")

        pages.append({
            "page_number": page_num + 1,
            "text": text,
            "images": image_descriptions
        })

    return pages
```

### Multi-language documents

```python
from langdetect import detect


def detect_and_chunk(text: str) -> list[dict]:
    """Detect language and chunk appropriately."""
    try:
        language = detect(text)
    except Exception:
        language = "unknown"

    # Use language-appropriate sentence splitting
    if language == 'zh':
        # Chinese: split on Chinese punctuation
        sentences = re.split(r'[。！？]', text)
    elif language == 'ja':
        # Japanese: similar to Chinese
        sentences = re.split(r'[。！？]', text)
    else:
        # Default: Western punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)

    return [{"text": s, "language": language} for s in sentences if s.strip()]
```

[↑ Back to Table of Contents](#table-of-contents)

## Summary

In this chapter, you learned:

- Extract text from PDFs, HTML, and other formats using appropriate libraries
- Choose chunking strategies based on document type and retrieval needs
- Preserve and enrich metadata for filtering and attribution
- Handle edge cases like tables, code blocks, and multi-language content

## Next steps

Continue to **[Chapter 23: Embeddings](./23_embeddings.md)** to learn how to convert text chunks into vector representations.

[↑ Back to Table of Contents](#table-of-contents)
