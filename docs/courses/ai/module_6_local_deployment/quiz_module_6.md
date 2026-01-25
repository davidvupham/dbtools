# Module 6 Quiz: Local LLM Deployment

**[← Back to Course Index](../README.md)**

Test your understanding of local LLM deployment. Choose the best answer for each question.

---

## Questions

### 1. What is the primary advantage of running LLMs locally?

- A) Always better quality
- B) Data privacy and cost predictability
- C) Faster than cloud APIs
- D) Easier to set up

<details>
<summary>Show Answer</summary>

**B) Data privacy and cost predictability**

Local deployment keeps data on your infrastructure (privacy) and has fixed costs regardless of query volume (predictability).
</details>

---

### 2. A 7B parameter model with Q4 quantization requires approximately how much VRAM?

- A) 2 GB
- B) 5-6 GB
- C) 14 GB
- D) 28 GB

<details>
<summary>Show Answer</summary>

**B) 5-6 GB**

Q4 quantization uses ~4 bits per parameter. 7B × 4 bits ≈ 3.5 GB for weights, plus overhead totals 5-6 GB.
</details>

---

### 3. Which Ollama environment variable keeps models loaded in memory?

- A) OLLAMA_MODEL_PERSIST
- B) OLLAMA_KEEP_ALIVE
- C) OLLAMA_CACHE_MODELS
- D) OLLAMA_PRELOAD

<details>
<summary>Show Answer</summary>

**B) OLLAMA_KEEP_ALIVE**

OLLAMA_KEEP_ALIVE controls how long models stay loaded in memory after the last request (e.g., "30m" for 30 minutes).
</details>

---

### 4. What is the trade-off of using Q4 vs Q8 quantization?

- A) Q4 is slower but higher quality
- B) Q4 uses less memory but may have lower quality on complex tasks
- C) Q8 uses less memory
- D) There is no difference

<details>
<summary>Show Answer</summary>

**B) Q4 uses less memory but may have lower quality on complex tasks**

Lower quantization (Q4) reduces memory requirements but can impact quality, especially for complex reasoning tasks.
</details>

---

### 5. Which model family is known for excellent tool/function calling?

- A) Llama
- B) Qwen
- C) Phi
- D) Gemma

<details>
<summary>Show Answer</summary>

**B) Qwen**

Qwen models are specifically trained for strong tool-use capabilities, making them excellent for agent applications.
</details>

---

### 6. What does TTFT stand for in LLM performance?

- A) Total Token Fetch Time
- B) Time To First Token
- C) Token Transfer Failure Threshold
- D) Text Tokenization Formatting Time

<details>
<summary>Show Answer</summary>

**B) Time To First Token**

TTFT measures the latency from sending a request until the first token of the response is generated.
</details>

---

### 7. What is the purpose of a kill switch in production LLM deployments?

- A) To restart models faster
- B) To immediately stop all LLM operations in emergencies
- C) To reduce power consumption
- D) To switch between models

<details>
<summary>Show Answer</summary>

**B) To immediately stop all LLM operations in emergencies**

A kill switch provides an emergency mechanism to halt all operations if something goes wrong.
</details>

---

### 8. Which index type provides better recall but uses more memory?

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

### 9. What is the recommended approach for high availability Ollama deployment?

- A) Single node with large GPU
- B) Multiple nodes behind a load balancer with health checks
- C) Running on CPU only
- D) Cloud-only deployment

<details>
<summary>Show Answer</summary>

**B) Multiple nodes behind a load balancer with health checks**

Multiple Ollama instances with load balancing and health checks provide redundancy and fault tolerance.
</details>

---

### 10. When does local deployment become cost-effective vs cloud APIs?

- A) Always
- B) Never
- C) At high, consistent query volumes (calculate break-even)
- D) Only for small deployments

<details>
<summary>Show Answer</summary>

**C) At high, consistent query volumes (calculate break-even)**

Local deployment has upfront costs but no per-token fees, becoming cost-effective above a certain query volume.
</details>

---

## Scoring

- **9-10 correct**: Excellent! You're ready to deploy LLMs in production.
- **7-8 correct**: Good understanding. Review operations and monitoring.
- **5-6 correct**: Fair. Re-read the performance and production chapters.
- **Below 5**: Review Module 6 before deployment.

---

**[Course Complete!](../README.md)**

Congratulations on completing the AI for Database Operations course!
