# System Design: SQL vs NoSQL

> "The best database is the one that fits your use case, not the one that won the last benchmark war."

A database choice is not about "which is best"—it's about which fits your use case based on data shape, query patterns, correctness needs, and scale.

---

## 1. Quick Definitions

### SQL (Relational Databases)

**Examples:** PostgreSQL, MySQL, Oracle, SQL Server

- Data stored in tables (rows/columns)
- Fixed schema (columns defined upfront)
- Great for relationships and joins
- Strong transactions (ACID)

### NoSQL (Non-Relational Databases)

**Examples:** MongoDB, Cassandra, DynamoDB, Redis, Neo4j

- Data stored in formats like:
  - Document (JSON-like)
  - Key-value
  - Wide-column
  - Graph
- Often more flexible schema
- Often easier horizontal scaling
- Usually you model data around how you read it

---

## 2. ACID vs BASE

### ACID (Common in SQL)

| Property | Meaning |
|----------|---------|
| **Atomic** | All-or-nothing transaction |
| **Consistent** | Rules/constraints always hold |
| **Isolated** | Transactions don't corrupt each other |
| **Durable** | Once committed, it stays |

**Use ACID when mistakes are expensive:**
- Payments
- Orders
- Inventory
- Ledger systems

### BASE (Common in Many NoSQL Systems)

| Property | Meaning |
|----------|---------|
| **Basically Available** | System responds even during failures |
| **Soft state** | State may change over time without input |
| **Eventually consistent** | System will converge to consistency |

**Use BASE when you can tolerate small delays in correctness:**
- Likes count
- Timelines
- Analytics dashboards
- View counters

---

## 3. CAP Theorem Refresher

When you have distributed storage (multi-node), CAP says you can't guarantee all 3 perfectly:

- **Consistency:** Everyone sees the latest data
- **Availability:** System responds even if some nodes fail
- **Partition tolerance:** System works despite network splits

**Reality:**
- Partition tolerance is basically required at scale
- So you often choose: **CP** or **AP**

| Choice | Behavior | Example Use Case |
|--------|----------|------------------|
| **CP** | Strong correctness, may reject/slow during partition | Banking, Inventory |
| **AP** | Always responds, might serve slightly stale data | Social feeds, Analytics |

---

## 4. When to Choose What

### Choose SQL When

- You need transactions across multiple rows/tables
- You need joins and complex queries
- You need strict data correctness
- Your schema is fairly stable

**Good for:**
- Order management
- Payments
- Accounting
- User profiles with constraints
- Audit trails

### Choose NoSQL When

- Your data is flexible or changes a lot
- You want easy horizontal scaling (sharding)
- Your queries are mostly key-based lookups
- You can design around access patterns

**Good for:**
- Feeds/timelines
- Sessions
- Clickstream events
- Product catalog (often)
- Chat messages (often)
- IoT telemetry

---

## 5. A Practical Decision Framework

Ask these questions in interviews (and real projects):

### Question 1: What are the top 3 queries?

Example queries that hint at SQL:
- "Get orders for user for last 6 months" (joins, filtering)
- "Calculate total revenue by region" (aggregations)

Example queries that hint at NoSQL:
- "Get user by id" (simple lookup)
- "Get last 50 messages in a chat" (partition key + sort)

### Question 2: Do I need multi-record transactions?

If yes → SQL is usually safest.

### Question 3: Do I need joins across large datasets?

If yes → SQL shines.

### Question 4: How much scale? (QPS + storage growth)

- Data: 5+ TB/month growing
- You will likely need sharding, and NoSQL might be simpler

### Question 5: How wrong can the system be, and for how long?

- If "never wrong" → SQL/strong consistency
- If "ok if corrected in 2–5 seconds" → NoSQL/eventual consistency

---

## 6. Example: E-commerce Orders (SQL Wins)

### Requirements

- Create order, reserve inventory, process payment
- Strong correctness required
- Wrong data = money loss

### Typical Schema (Simplified)

```
Users(id, name, email)
Orders(id, user_id, status, total_amount, created_at)
OrderItems(id, order_id, product_id, qty, price)
Inventory(product_id, available_qty)
Payments(id, order_id, status, provider_ref)
```

### Why SQL?

You need a transaction like:
1. Create order
2. Reduce inventory
3. Mark payment state

All must be consistent.

### Scale Notes

- **Reads:** "my orders list" might be moderate (2k–10k QPS)
- **Writes:** orders + payments (spiky during sales)
- **Strategy:**
  - Indexes on `Orders(user_id, created_at)`
  - Read replicas for read-heavy endpoints
  - Partition Orders by time if table grows huge

---

## 7. Example: Social Media Feed (NoSQL Wins)

### Requirements

- Heavy reads (feed loads), moderate writes (posting)
- Timeline reads can be massive:
  - 50M DAU × 10 opens/day = 500M feed loads/day
  - 500M / 86400 ≈ ~5.8k QPS average, peak could be 10× or more

### Why NoSQL?

Feeds are usually "query by user_id, sort by time, limit 50"—a perfect fit for:

- Wide-column (Cassandra)
- Document store (MongoDB)
- Key-value patterns + precomputed lists

### Data Modeling Idea (Feed Table)

```
Key: user_id
Sort: timestamp
Value: post references/content pointers
```

**Important:** NoSQL performance depends heavily on choosing the right partition key.

---

## 8. NoSQL Types and When to Use Each

### Key-Value (Redis, DynamoDB Style)

- Fast lookups by key
- **Great for:** Session store, rate limiting counters, caching layer

### Document (MongoDB)

- JSON-like documents
- **Great when:** Schema changes often, you store nested data naturally (catalog, profiles)

### Wide-Column (Cassandra)

- Built for huge write volume + scale
- **Great for:** Time series, chat messages, feeds/events

### Graph (Neo4j)

- Relationships are the main feature
- **Great for:** Friend recommendations, fraud rings, dependency mapping

---

## 9. Scaling Patterns (Both Worlds)

### Read Scaling

- Read replicas (SQL)
- Cache in front (Redis)
- Materialized views / precomputed feeds

### Write Scaling

- Sharding / partitioning
- SQL: harder but possible (by tenant/user/time)
- NoSQL: usually built-in patterns

### Storage Scaling

- Partition by time (logs, events)
- Archival (cold storage)

---

## 10. Polyglot Persistence

Most big systems use BOTH SQL and NoSQL.

**Example "realistic" stack:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| Orders + Payments | PostgreSQL | ACID transactions, joins |
| Feeds/Messages | Cassandra/MongoDB | High write volume, flexible schema |
| Caching + Sessions | Redis | Sub-millisecond access |
| Search | Elasticsearch | Full-text search |

This is not overengineering—it's matching tools to jobs.

---

## 11. Interview Summary

If asked "SQL or NoSQL?" you can say:

1. **"For money/transactions → SQL for ACID + joins."**
2. **"For massive scale, flexible schema, feed-like access → NoSQL."**
3. **"At scale, we often use both, plus Redis cache."**

---

## Related Topics

- [Database Internals](database_internals.md) - B-Tree vs LSM, WAL, MVCC
- [Data Patterns](data_patterns.md) - CAP Theorem details, Sharding, Caching strategies
- [Distributed Algorithms](distributed_algorithms.md) - Consistency models, Consensus
