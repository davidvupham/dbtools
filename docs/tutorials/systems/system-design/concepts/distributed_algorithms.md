# System Design: Distributed Algorithms

> "If you think you understand distributed systems, you probably don't understand distributed systems."

This section covers the mathematical and logical foundations that make distributed systems possible (and frustrating).

---

## 1. Time & Clocks

**The Problem:** "Time" is an illusion. You cannot trust `System.currentTimeMillis()`.

- **NTP Drift:** Servers can be off by hundreds of milliseconds.
- **Leap Seconds:** Can crash software that assumes strictly increasing time.

### The Solutions

- **Lamport Clocks:** Logical counters (`timestamp++` on every event). Tells you *causality* ("A happened before B"), but not "A happened at 12:00".
- **Vector Clocks:** An array of counters `[A:1, B:2, C:0]` to detect CONCURRENT updates (conflicts) in distributed systems. Essential for Dynamo-style databases.
- **TrueTime (Spanner):** Google uses atomic clocks + GPS to bound the error interval. "It is definitely between 12:00:00.001 and 12:00:00.005".

### 🛑 Staff-Level Decision

- Don't use wall-clock time for ordering events unless you have Spanner.
- Use **Monotonic Clocks** (`System.nanoTime`) for measuring *duration* (elapsed time).

---

## 2. Consensus (Raft, Paxos, Zab)

**The Concept:** How a cluster of machines agrees on a value (e.g., "The leader is Node 3") even if some nodes are dead or the network is partitioned.

### The Tradeoff

- **Raft:** "Understandable" Consensus. Strong Leader. Used by Etcd, Consul.
- **Paxos:** The original, brutally abstract proof. Used by Spanner (Multi-Paxos).
- **Zab:** ZooKeeper Atomic Broadcast. Specialized for high-throughput total ordering.

### 🛑 When NOT to use

- **Your Application Code:** profound advice: **Never write your own consensus in application logic.** Use Etcd or ZooKeeper.
- **High Throughput Data:** Consensus is slow (requires round trips to majority). Don't use Raft to write every single user click. Use it to store *configuration* or *leader pointers*.

---

## 3. Failure Detection

**The Problem:** "Is Node 3 dead, or just slow?" You can never know for sure (FLP Impossibility).

### The Solutions

- **Heartbeats:** "I am alive" every 1s.
- **Phi Accrual Failure Detector (Akka, Cassandra):** Instead of a hard timeout ("Dead after 5s"), it calculates a *probability* of suspicion. "There is a 99.9% chance Node 3 is dead because it usually responds in 100ms but hasn't for 2s."

---

## 4. Coordination & Locks

**The Concept:** "Only one server should process the payroll job."

### The "Fencing Token" (Critical!)

- **Distributed Locks are dangerous.**
- Scenario:
    1. Worker A gets Lock (Lease: 10s).
    2. Worker A sleeps (GC pause) for 15s. Lease expires.
    3. Worker B gets Lock. Starts processing.
    4. Worker A wakes up. **Believes it still holds the lock.** Finishes processing.
  - **Result:** Data Corruption (Double write).
- **Solution:** Fencing Tokens. The lock server returns a strictly increasing token (1, 2, 3). The Database rejects any write with a token lower than the latest seen.

### 🛑 Staff-Level Decision

- If you use Redis for locks (`SETNX`), you do not have Fencing Tokens. You are choosing "Efficiency" over "Correctness". That is fine for "Sending Emails" (duplicates ok), but fatal for "Money" (duplicates bad).
