# System Design: Messaging & Async Patterns

> "Do I actually need Kafka? Or would a simple queue work fine for my 1000 requests per day?"

Async communication decouples services, but it introduces the complexity of "checking if it actually happened".

---

## 1. Message Queues (RabbitMQ, SQS, ActiveMQ)

**The Concept:** A buffer between a producer and a consumer. "Fire and forget."

### The Problem it Solves

- **Decoupling:** The user shouldn't wait for the PDF generation to finish. Send a message, return "202 Accepted", and let a worker handle it.
- **Load Smoothing:** If 1000 requests come in at once, the queue absorbs them, and your 5 workers process them at their own pace.

### The Tradeoff

- **Operational Complexity:** You now have another piece of infrastructure to manage.
- **Visibility:** Troubleshooting "Why didn't the email send?" is harder. You have to check queue depths, dead letter queues (DLQ), and logs across two systems.

### 🛑 When NOT to use

- **Synchronous Requirements:** If the user *needs* the answer immediately (e.g., login), don't use a queue.
- **Simple Apps:** For small background jobs, a database table (`jobs` table) with a cron script is often fine until you hit scale.

---

## 2. Kafka (Event Streaming)

**The Concept:** A distributed log. Unlike a queue (where messages disappear after consumption), Kafka stores events on disk for a set time (retention). Many consumers can read the same message.

### The Tradeoff

- **Problem Solved:**
  - High throughput (millions of events/sec).
  - Multiple consumers (Analytics team *and* Billing team can both read "OrderCreated").
  - Replayability (Rewind to yesterday and re-process).
- **Problem Created:**
  - **Massive Complexity:** Managing Zookeeper/KRaft, partition rebalancing, consumer group offsets.
  - **Ordering Guarantees:** Ordering is only guaranteed *within a partition*. Global ordering is hard.

### 🛑 When NOT to use Kafka

- **"We need a queue":** If you just want one worker to process a job and delete it, Kafka is overkill. Use RabbitMQ or SQS.
- **Low Throughput:** If you have < 500 msg/sec, Kafka is a Ferrari in a traffic jam. It requires significant maintenance.

---

## 3. Saga Pattern

**The Concept:** How to handle "Transactions" across microservices. Since you can't use a database transaction (ACID) across 3 different services, you break the workflow into validatable steps.

**The Flow:**

1. Service A: Charge Card -> Success.
2. Service B: Update Inventory -> Fail (Out of stock).
3. **Compensation:** Service A MUST run a "Refund" action to undo step 1.

### The Tradeoff

- **Problem Solved:** Data consistency in Distributed Systems / Microservices.
- **Problem Created:**
  - **Complexity:** You must write "Compensation Logic" (undo code) for every single step.
  - **Debugging:** If the compensation fails (e.g., Refund API is down), the system is in an inconsistent state tailored for human intervention.

### 🛑 When NOT to use

- **Monoliths:** If you are in a monolith, just use a SQL Transaction (`BEGIN...COMMIT`). It is 1000x safer and simpler. Do not simulate Sagas inside a monolith.
