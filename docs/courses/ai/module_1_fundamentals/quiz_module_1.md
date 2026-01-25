# Module 1 Quiz: LLM Fundamentals

**[← Back to Course Index](../README.md)**

Test your understanding of LLM fundamentals. Choose the best answer for each question.

---

## Questions

### 1. What is the primary mechanism that allows transformers to understand context?

- A) Recurrent connections
- B) Self-attention
- C) Convolutional filters
- D) Random sampling

<details>
<summary>Show Answer</summary>

**B) Self-attention**

Self-attention allows each token to attend to all other tokens in the sequence, enabling the model to understand context regardless of distance between words.
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

Q4 quantization uses approximately 4 bits per parameter. 7B × 4 bits = 28 billion bits = 3.5 GB for weights, plus overhead for activations and KV cache, totaling around 5-6 GB.
</details>

---

### 3. What does BPE stand for in tokenization?

- A) Binary Position Encoding
- B) Byte Pair Encoding
- C) Basic Pattern Extraction
- D) Batch Processing Engine

<details>
<summary>Show Answer</summary>

**B) Byte Pair Encoding**

BPE is a subword tokenization algorithm that iteratively merges the most frequent pairs of characters or tokens.
</details>

---

### 4. What happens when you set temperature to 0 during inference?

- A) The model generates random output
- B) The model always selects the highest probability token (greedy decoding)
- C) The model refuses to generate
- D) The model generates longer responses

<details>
<summary>Show Answer</summary>

**B) The model always selects the highest probability token (greedy decoding)**

Temperature=0 makes the probability distribution extremely peaked, always selecting the most likely token. This produces deterministic, consistent output.
</details>

---

### 5. In the transformer architecture, what are Q, K, and V?

- A) Quantization, Knowledge, Validation
- B) Query, Key, Value matrices in attention
- C) Quality, Kernel, Vector parameters
- D) Queue, Kick, Verify operations

<details>
<summary>Show Answer</summary>

**B) Query, Key, Value matrices in attention**

In self-attention, the input is projected into Query (what we're looking for), Key (what we're matching against), and Value (what we retrieve) matrices.
</details>

---

### 6. What is the approximate token-to-word ratio for English text?

- A) 1 token = 1 word
- B) 1 token ≈ 0.75 words (4 characters)
- C) 1 token ≈ 2 words
- D) 1 token ≈ 1 character

<details>
<summary>Show Answer</summary>

**B) 1 token ≈ 0.75 words (4 characters)**

For English, a rough estimate is that 100 tokens ≈ 75 words. This varies by model and content type.
</details>

---

### 7. What is the purpose of the KV cache in inference?

- A) Store training data
- B) Cache computed Key and Value vectors to avoid recomputation
- C) Store model weights
- D) Cache network requests

<details>
<summary>Show Answer</summary>

**B) Cache computed Key and Value vectors to avoid recomputation**

During autoregressive generation, the KV cache stores previously computed Key and Value vectors so they don't need to be recomputed for each new token.
</details>

---

### 8. Which statement about context windows is TRUE?

- A) Larger context windows are always better
- B) Context window size has no impact on VRAM usage
- C) Context window determines maximum input + output length
- D) All models have the same context window size

<details>
<summary>Show Answer</summary>

**C) Context window determines maximum input + output length**

The context window is the total number of tokens the model can process in a single forward pass, including both input and generated output.
</details>

---

### 9. What does top-p (nucleus) sampling do?

- A) Samples from the top P tokens only
- B) Samples from tokens that together make up probability P
- C) Sets the probability of the top token to P
- D) Limits output to P tokens

<details>
<summary>Show Answer</summary>

**B) Samples from tokens that together make up probability P**

Top-p sampling creates a dynamic set of candidate tokens whose cumulative probability equals p (e.g., 0.9), then samples from this set.
</details>

---

### 10. What is the main trade-off of quantization?

- A) Speed vs. cost
- B) Memory usage vs. model quality
- C) Latency vs. throughput
- D) Training time vs. inference time

<details>
<summary>Show Answer</summary>

**B) Memory usage vs. model quality**

Quantization reduces memory requirements by using fewer bits per weight, but this can result in some loss of model quality, especially for complex tasks.
</details>

---

## Scoring

- **9-10 correct**: Excellent! You have a strong understanding of LLM fundamentals.
- **7-8 correct**: Good understanding. Review the topics you missed.
- **5-6 correct**: Fair. Consider re-reading the relevant chapters.
- **Below 5**: Review Module 1 chapters before proceeding.

---

**[Continue to Module 2 →](../module_2_prompt_engineering/06_prompt_anatomy.md)**
