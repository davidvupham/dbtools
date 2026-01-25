# Module 5 Quiz: Retrieval-Augmented Generation

**[← Back to Course Index](../README.md)**

Test your understanding of RAG systems. Choose the best answer for each question.

---

## Questions

### 1. What problem does RAG solve that fine-tuning cannot?

- A) Improving model speed
- B) Providing access to up-to-date or private information
- C) Reducing model size
- D) Simplifying prompts

<details>
<summary>Show Answer</summary>

**B) Providing access to up-to-date or private information**

RAG allows models to access current information and private data without retraining, which fine-tuning cannot provide.
</details>

---

### 2. What is the purpose of chunking in RAG?

- A) To compress documents
- B) To split documents into pieces suitable for embedding and retrieval
- C) To remove duplicates
- D) To encrypt content

<details>
<summary>Show Answer</summary>

**B) To split documents into pieces suitable for embedding and retrieval**

Chunking creates appropriately sized pieces that can be embedded and retrieved individually, balancing context and relevance.
</details>

---

### 3. Why might semantic chunking be preferred over fixed-size chunking?

- A) It's faster
- B) It preserves topic coherence within chunks
- C) It uses less storage
- D) It's easier to implement

<details>
<summary>Show Answer</summary>

**B) It preserves topic coherence within chunks**

Semantic chunking groups related content together based on meaning, rather than arbitrary size boundaries.
</details>

---

### 4. What is cosine similarity used for in RAG?

- A) To compress vectors
- B) To measure semantic similarity between embeddings
- C) To tokenize text
- D) To generate responses

<details>
<summary>Show Answer</summary>

**B) To measure semantic similarity between embeddings**

Cosine similarity measures the angle between vectors, indicating how semantically similar two pieces of text are.
</details>

---

### 5. When should you use pgvector over ChromaDB?

- A) For development only
- B) When you need to integrate with existing PostgreSQL infrastructure
- C) When you have less than 100 documents
- D) When you don't need filtering

<details>
<summary>Show Answer</summary>

**B) When you need to integrate with existing PostgreSQL infrastructure**

pgvector is ideal when you already use PostgreSQL and want to add vector search without introducing new infrastructure.
</details>

---

### 6. What is hybrid search in RAG?

- A) Using two different LLMs
- B) Combining semantic (vector) and keyword search
- C) Searching across multiple databases
- D) Using both cloud and local storage

<details>
<summary>Show Answer</summary>

**B) Combining semantic (vector) and keyword search**

Hybrid search combines vector similarity with keyword matching to improve retrieval quality, capturing both semantic meaning and exact terms.
</details>

---

### 7. What is the purpose of re-ranking in RAG?

- A) To sort documents by date
- B) To reorder initial results using a more precise model
- C) To remove duplicates
- D) To compress results

<details>
<summary>Show Answer</summary>

**B) To reorder initial results using a more precise model**

Re-ranking uses a cross-encoder or LLM to more precisely score relevance, improving precision after initial high-recall retrieval.
</details>

---

### 8. What is HyDE (Hypothetical Document Embedding)?

- A) A type of vector database
- B) Generating a hypothetical answer and searching for similar real documents
- C) A compression algorithm
- D) A caching strategy

<details>
<summary>Show Answer</summary>

**B) Generating a hypothetical answer and searching for similar real documents**

HyDE generates what an ideal answer might look like, then searches for documents similar to that hypothetical answer.
</details>

---

### 9. Which index type offers better recall at the cost of more memory?

- A) IVF
- B) HNSW
- C) B-tree
- D) Hash

<details>
<summary>Show Answer</summary>

**B) HNSW**

HNSW (Hierarchical Navigable Small World) provides excellent recall but requires more memory than IVF indexes.
</details>

---

### 10. What is parent document retrieval?

- A) Finding the oldest documents
- B) Matching on small chunks but returning larger parent documents for context
- C) Retrieving documents from parent directories
- D) Inheritance in object-oriented programming

<details>
<summary>Show Answer</summary>

**B) Matching on small chunks but returning larger parent documents for context**

Parent document retrieval uses small chunks for precise matching but returns the larger source document to provide more context.
</details>

---

## Scoring

- **9-10 correct**: Excellent! You're ready to build RAG systems.
- **7-8 correct**: Good understanding. Review retrieval strategies.
- **5-6 correct**: Fair. Re-read the embeddings and vector store chapters.
- **Below 5**: Review Module 5 before proceeding.

---

**[Continue to Module 6 →](../module_6_local_deployment/26_why_local.md)**
