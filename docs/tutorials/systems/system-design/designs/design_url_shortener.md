# Design 1: URL Shortener (TinyURL)

> "It sounds simple until you calculate the storage for 5 years."

## 1. Requirements & Tradeoffs

This system has a massive **Read Skew**.

- **Write:** Users create a link (1x).
- **Read:** People click the link (100x).
- **Implication:** We must optimize for *fast reads* (Caching is mandatory) and we can accept slower writes.

### Capacity Estimation (Back-of-Envelope)

- **Traffic:** 100M writes/month.
- **Ratio:** 100:1 -> 10B reads/month.
- **Storage:**
  - 100M *5 years* 12 months = 6 Billion links.
  - 1 link = 1kb (URL + Metadata).
  - **Total:** 6 TB.
- **Decision:** 6TB fits easily in a modern NoSQL cluster or even a large sharded SQL setup. We don't need exotic "Big Data" storage (Hadoop). A standard database is fine.

## 2. The Core Problem: Unique IDs

How do we turn `google.com` into `ab7d9`?

### Approach A: Hashing (MD5/SHA)

- `hash("google.com")` -> `a739...`
- **Problem:** Hash collisions. Two different URLs might hash to the same prefix.
- **Problem:** Fixed length. We only want 6-7 characters, but hashes are 32+ chars.

### Approach B: Centralized Counter (The Winner 🏆)

- We assign an Integer ID to every request: `100001`, `100002`...
- We convert that Base10 Integer to **Base62** (a-z, A-Z, 0-9).
- `100001` -> `sT9`
- **Why this wins:**
  - Zero collisions (numbers are unique).
  - Deterministic length (we know exactly how many chars we need).
- **The Tradeoff:** **Concurrency.**
  - A single database Auto-Increment ID is a bottleneck.
  - **Solution:** **Range Allocation.**
    - App Server A claims range [1M - 2M]. It manages integers in memory.
    - App Server B claims range [2M - 3M].
    - No database locking required for every request!

## 3. Database Choice: SQL vs NoSQL

### Option A: Relational (Postgres)

```sql
CREATE TABLE links (
    id BIGINT PK,
    short_url CHAR(7),
    long_url TEXT
);
```

- **Pros:** ACID. Easy to manage.
- **Cons:** Indexing 6 Billion rows is heavy. Sharding logic must be manual.

### Option B: NoSQL (DynamoDB / Cassandra) - **Recommended**

- **Structure:** Key-Value store. `Key: short_url`, `Value: long_url`.
- **Pros:**
  - **Scale:** Handles 6TB trivially.
  - **Speed:** O(1) lookups by Key.
- **Cons:** Eventual Consistency (if we had complex relationships, but we don't).

## 4. Final Architecture

1. **User** sends `POST /api/shorten` (`long_url`).
2. **App Server** asks **Range Service** for a unique ID range.
3. **App Server** generates `short_id` locally (e.g., `sT9`).
4. **App Server** saves `{sT9: long_url}` to **DynamoDB**.
5. **App Server** returns `tiny.url/sT9`.

### The Read Path (Optimization)

1. **User** visits `tiny.url/sT9`.
2. **LB** hits App Server.
3. **App Server** checks **Redis Cache**.
    - *Hit:* Return 301 Redirect. (0.5ms).
    - *Miss:* Fetch from DynamoDB, save to Redis, Return 301. (10ms).

## 5. Staff-Level Nuance: 301 vs 302 Redirect

- **301 (Permanent):** Browser caches the redirect. Next time, it goes straight to the long URL. **We save server load, but we lose Analytics (link tracking).**
- **302 (Temporary):** Browser asks us every time. **Higher load, but accurate analytics.**
- **Decision:** Use 302 if you sell analytics. Use 301 if you are poor.
