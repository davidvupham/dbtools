# System Design: Database Internals

> "Show me a developer who understands B-Trees vs LSM Trees, and I'll show you a developer who knows why their write-heavy app is slow."

Understanding the storage engine helps you predict performance without even running a benchmark.

---

## 1. Storage Engines: B-Tree vs LSM Tree

**The Decision:** Are you optimizing for Reads (SQL) or Writes (NoSQL)?

### B-Trees (Postgres, MySQL, Oracle)

- **Structure:** Balanced tree stored on disk. Data is in 4kb pages.
- **Pros:** Fast Reads. Precise Lookups. Range Scans. Good for transactional data.
- **Cons:** **Random Writes are slow.** Inserting a random ID might require seeking to the middle of the disk and updating a page. "Write Amplification" (writing a 4kb page just to change 10 bytes).

### LSM Trees (Cassandra, RocksDB, Kafka, BigTable)

- **Structure:** Log-Structured Merge Tree.
    1. Writes go to **MemTable** (RAM). Fast!
    2. When RAM is full, flush to disk as an **SSTable** (Sorted String Table). (Sequential Write!).
    3. Background processes **Compact** (merge) old SSTables to delete duplicates.
- **Pros:** **Insanely Fast Writes.** Everything is an append.
- **Cons:** Slower Reads. You might have to check MemTable + 5 different SSTables on disk to find a key.

### 🛑 Staff-Level Decision

- **Write-Heavy Logging/History:** Use LSM (Cassandra/Scylla).
- **Complex Queries/Consistency:** Use B-Tree (Postgres).

---

## 2. WAL (Write Ahead Log)

**The Concept:** Durability.

- Before a database changes the data file (B-Tree), it appends the command to a simple append-only file (WAL).
- **Crash Recovery:** If electricity dies, the DB reads the WAL on startup to re-apply unsaved changes.
- **Implication:** Committing a transaction = `fsync` the WAL to disk. This is often the bottleneck.

---

## 3. Concurrency Control: Pessimistic vs Optimistic

**The Problem:** Two users change the same row at the same time.

### Pessimistic Locking (The "Safe" Way)

- `SELECT ... FOR UPDATE`
- You lock the row. No one else can read/write it until you are done.
- **Tradeoff:** Safety vs Performance. High contention = Deadlocks.

### Optimistic Locking (The "Fast" Way)

- You don't lock. You read a version number (`v1`).
- When writing, you say `UPDATE ... WHERE id=X AND version=1`.
- If the row is now `v2`, the DB returns "0 rows updated". You failed. **Retry.**
- **Tradeoff:** Fast (no locks) but requires Application-Level Retry logic.

---

## 4. MVCC (Multi-Version Concurrency Control)

**The Concept:** Readers don't block Writers. Writers don't block Readers.

- When you update a row, Postgres doesn't overwrite it. It writes a **new version** of the row and marks the old one "dead" (visible only to older transactions).
- **VACUUM:** The process of cleaning up dead rows.
- **Staff-Level Insight:** If you update a row 1000 times a second, you create 1000 "dead tuples". The VACUUM process might not keep up, causing "Table Bloat" and slowing down everything. This is why standard SQL DBs struggle with high-churn counters.
