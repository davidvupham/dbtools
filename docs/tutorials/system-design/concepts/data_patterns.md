# System Design: Data Patterns & Tradeoffs

> "The best engineers I know can explain why they'd choose a boring SQL database over the latest distributed system."

This guide focuses on **decisions**, not just definitions. Every pattern adds complexity. Your job is to decide if the problem justifies the cost.

---

## 1. CAP Theorem & Eventual Consistency

**The Concept:** You cannot have it all. In a distributed system (which partitions when networks fail - **P**), you must choose between:

- **Consistency (C):** Every read receives the most recent write or an error. (System pauses during partition).
- **Availability (A):** Every request receives a (non-error) response, without the guarantee that it contains the most recent write. (System keeps serving old data).

### The Tradeoff

- **CP (Consistency):**
  - *Good for:* Money transfers, inventory management (cannot oversell).
  - *Cost:* Downtime. If a node is unreachable, the system must reject writes to avoid data divergence.
- **AP (Availability):**
  - *Good for:* Social media feeds, likes, comments (ok if they appear 2s later).
  - *Cost:* **Eventual Consistency**. Users might see stale data. Complexity moves to the application developer (conflict resolution, read repairs).

### Advanced: PACELC Theorem

CAP is too simple. It says "If partitioned, choose A or C." But what if the network is fine (Else - E)?

- **PACELC:** If Partition (P), choose A or C. **Else (E)**, choose Latency (L) or Consistency (C).
- *Insight:* Even without a failure, you trade Latency for Consistency. Waiting for a database quorum takes time. DynamoDB lets you choose: "Consistent Read" (Slower) vs "Eventual Read" (Faster).

### Advanced: Anti-Entropy & Merkle Trees

How do eventual consistent systems actually converge?

- **Read Repair:** When you read, the DB notices replica A has v1 and replica B has v2. It returns v2 and updates A in the background.
- **Merkle Trees:** A hash tree to efficiently compare huge datasets. "Do we have the same data?" -> Compare root hash. If different, go down one level. Saves bandwidth.

### 🛑 When NOT to use Eventual Consistency

- When strong data integrity is required by law or logic (e.g., Banking).
- "We need high availability for our internal Admin dashboard." -> No you don't. Administrators can wait 5 minutes if the DB is failing over. Don't add complexity for 5 users.

---

## 2. Database Sharding

**The Concept:** Splitting a large database into smaller chunks (shards) across many machines because a single machine cannot handle the write volume or storage size.

### The Tradeoff

- **Problem Solved:** Unlimited horizontal write scaling.
- **Problem Created:**
  - **Cross-shard joins are impossible/expensive.** You lose ACID transactions across shards.
  - **Re-sharding is a nightmare.** If one shard gets too big (data skew), moving data while live is terrifying.
  - **Operational complexity:** Backups, monitoring, and failover become 10x harder.

### 🛑 When AVOID Sharding

- **Vertical Scaling First:** Can you just buy a bigger server? (AWS r6g.24xlarge has 768GB RAM). If your DB fits on one huge machine, do that. It is cheaper than engineer salaries debugging sharding issues.
- **Read Replicas First:** If your problem is *reads*, simple replication solves it without sharding. Sharding is for *write* saturation.

---

## 3. Consistent Hashing

**The Concept:** A strategy for distributing data (sharding) so that when a node is added/removed, only `1/N` keys need to be remapped, rather than *all* keys.

### The Decision

- **Use when:** You have a dynamic set of cache nodes or database shards that scale up/down frequently.
- **Don't use when:** Your cluster size is static. If you have 4 fixed database servers that never change, `id % 4` is faster and simpler.

---

## 4. Redis Caching

**The Concept:** Storing data in RAM for sub-millisecond access.

### The Tradeoff

- **Problem Solved:** Latency. Protects the database from read spikes.
- **Problem Created:** **Cache Invalidation.**
  - "There are only two hard things in Computer Science: cache invalidation and naming things."
  - You now have two sources of truth. They *will* drift apart.
  - Bugs where users update profiles but see old data.

### 🛑 When NOT to use Redis

- **Premature Optimization:** "We might get big." -> Don't cache until your database CPU is actually high. Postgres is incredibly fast.
- **Highly Volatile Data:** If data changes every second and is read every second, you are just thrashing the cache.
- **Critical Data:** Validating a session token? Maybe okay. Checking a balance before a transaction? Never trust the cache.

---

## 5. CQRS (Command Query Responsibility Segregation)

**The Concept:** Splitting your code into two distinct models: one for updating information (Command) and one for reading information (Query).

### The Tradeoff

- **Problem Solved:**
  - Optimizing reads and writes independently (e.g., Write to normalized SQL, Read from denormalized ElasticSearch).
  - Complex domains where "updating" an order means 50 different side effects.
- **Problem Created:**
  - **Lag:** The Read model updates asynchronously. Users create an item, refresh the page, and it's not there yet.
  - **Code Duplication:** You often define the data shape twice.

### 🛑 When NOT to use CQRS

- **CRUD Apps:** If your app is just "Create User, Read User", CQRS is pure over-engineering. It adds massive friction to simple features.

---

## 6. Event Sourcing

**The Concept:** Storing state as a sequence of events ("OrderCreated", "ItemAdded"), rather than just the current state ("Order is Open").

### The Tradeoff

- **Problem Solved:**
  - Perfect audit trail.
  - "Time Travel" debugging (replay events to see what happened).
- **Problem Created:**
  - **Storage Size:** Grows forever. You need snapshotting.
  - **Schema Evolution:** Changing an event structure from 3 years ago is hard. You can't just `ALTER TABLE`.
  - **Querying is Hard:** You can't ask "Give me all users named Alice". You have to build a projection (Read Model) first.

### 🛑 When NOT to use Event Sourcing

- Most of the time.
- Unless you are a bank, insurance co, or git, the complexity of event versioning and projections usually outweighs the "cool factor" of time travel.
