# Module 2 Quiz: Prompt Engineering

**[← Back to Course Index](../README.md)**

Test your understanding of prompt engineering techniques. Choose the best answer for each question.

---

## Questions

### 1. What is the primary advantage of few-shot prompting over zero-shot?

- A) It uses fewer tokens
- B) It provides examples that guide the model's output format and reasoning
- C) It always produces better results
- D) It is faster to execute

<details>
<summary>Show Answer</summary>

**B) It provides examples that guide the model's output format and reasoning**

Few-shot prompting includes examples that demonstrate the expected input-output pattern, helping the model understand the task better.
</details>

---

### 2. Chain-of-thought prompting is most useful for:

- A) Simple classification tasks
- B) Multi-step reasoning and math problems
- C) Generating creative writing
- D) Translation tasks

<details>
<summary>Show Answer</summary>

**B) Multi-step reasoning and math problems**

Chain-of-thought prompting helps models show their reasoning step-by-step, which significantly improves performance on tasks requiring logical reasoning.
</details>

---

### 3. What is prompt injection?

- A) Adding more context to a prompt
- B) A security vulnerability where user input manipulates the system prompt
- C) A technique to improve response quality
- D) Breaking a prompt into multiple parts

<details>
<summary>Show Answer</summary>

**B) A security vulnerability where user input manipulates the system prompt**

Prompt injection occurs when untrusted user input is able to override or manipulate the system instructions, potentially causing harmful behavior.
</details>

---

### 4. When should you use a system prompt vs. a user prompt?

- A) System prompts for instructions, user prompts for the actual task
- B) They are interchangeable
- C) System prompts for questions, user prompts for context
- D) System prompts should never be used

<details>
<summary>Show Answer</summary>

**A) System prompts for instructions, user prompts for the actual task**

System prompts set the behavior, role, and constraints for the model. User prompts contain the actual query or content to process.
</details>

---

### 5. Which technique helps ensure consistent JSON output?

- A) Higher temperature
- B) Specifying schema in the prompt and using JSON mode
- C) Longer prompts
- D) Removing all punctuation

<details>
<summary>Show Answer</summary>

**B) Specifying schema in the prompt and using JSON mode**

Providing an explicit JSON schema and enabling JSON mode (when available) helps ensure the model outputs valid, consistent JSON.
</details>

---

### 6. What is the "persona pattern" in prompt engineering?

- A) Making the prompt longer
- B) Assigning a specific role or expertise to the model
- C) Using multiple prompts in sequence
- D) Hiding the true intent of the prompt

<details>
<summary>Show Answer</summary>

**B) Assigning a specific role or expertise to the model**

The persona pattern instructs the model to act as a specific expert (e.g., "You are a PostgreSQL DBA with 15 years of experience") to improve response quality for domain-specific tasks.
</details>

---

### 7. What does "self-consistency" prompting involve?

- A) Using the same prompt repeatedly
- B) Generating multiple reasoning paths and taking the majority answer
- C) Making the model agree with itself
- D) Verifying prompt syntax

<details>
<summary>Show Answer</summary>

**B) Generating multiple reasoning paths and taking the majority answer**

Self-consistency generates multiple chain-of-thought responses and selects the most common final answer, improving reliability on complex reasoning tasks.
</details>

---

### 8. Which is a common cause of hallucinations?

- A) Using too few tokens
- B) Asking about information outside the model's training data
- C) Using system prompts
- D) Temperature set to 0

<details>
<summary>Show Answer</summary>

**B) Asking about information outside the model's training data**

Models hallucinate when they lack knowledge about a topic but still attempt to generate plausible-sounding responses.
</details>

---

### 9. What is prompt chaining?

- A) Connecting prompts with physical chains
- B) Using the output of one prompt as input for the next
- C) Repeating the same prompt multiple times
- D) Combining all prompts into one

<details>
<summary>Show Answer</summary>

**B) Using the output of one prompt as input for the next**

Prompt chaining breaks complex tasks into steps, where each step's output feeds into the next, improving reliability for multi-step workflows.
</details>

---

### 10. To reduce bias in model outputs, you should:

- A) Always use temperature = 1
- B) Use balanced examples and explicit instructions to be objective
- C) Avoid using examples
- D) Make prompts as short as possible

<details>
<summary>Show Answer</summary>

**B) Use balanced examples and explicit instructions to be objective**

Including diverse, balanced examples and explicitly instructing the model to be objective and consider multiple perspectives helps reduce bias.
</details>

---

## Scoring

- **9-10 correct**: Excellent! You're ready to write effective prompts.
- **7-8 correct**: Good understanding. Review the missed topics.
- **5-6 correct**: Fair. Re-read the advanced techniques chapter.
- **Below 5**: Review Module 2 chapters before proceeding.

---

**[Continue to Module 3 →](../module_3_mcp/11_mcp_overview.md)**
