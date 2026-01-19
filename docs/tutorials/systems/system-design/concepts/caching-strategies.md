# System Design: Caching Strategies & Redis Best Practices

> "Redis makes *well-designed* systems faster. It does not make slow systems fast."

This guide goes beyond basic caching concepts to address **why Redis caching often fails in production** and how proper cache design actually unlocks the 90% speed improvements Redis promises.

For basic caching concepts (cache invalidation, eviction policies), see [Data Patterns](data_patterns.md#4-redis-caching).

---

## The caching paradox

Redis is supposed to make APIs blazing fast, yet many applications still feel slow in production. The contradiction is one of the most frustrating realities modern backend engineers face.

**The real problem is not Redis. The real problem is everything wrapped around it.**

```
┌─────────────────────────────────────────────────────────────┐
│                    Request Lifecycle                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Client → API Gateway → Auth Check → Cache Lookup           │
│                              ↓                              │
│                         Cache Miss                          │
│                              ↓                              │
│                   Database + Joins + Mapping                │
│                              ↓                              │
│                    Serialization + Network                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

By the time Redis is even queried, authentication filters, request validation, heavy object mapping, and logging layers have already consumed most of the response time. The damage is done before the cache is checked.

---

## Where speed is actually lost

```
                      ┌──────────────────────────────────────┐
                      │        Speed Lost Outside Redis      │
                      └──────────────────────────────────────┘

    ┌─────────┐         ┌──────────────────────────────────────────┐
    │   API   │         │              SLOW ARCHITECTURE           │
    │  Layer  │ ───────→│                                          │
    └─────────┘         │   ┌──────┐  ┌──────┐  ┌────────┐  ┌────┐ │
                        │   │ Cold │  │Cache │  │Overhead│  │ DB │ │
        FAST CACHE      │   │Start │  │ Miss │  │ Layers │  │Lat.│ │
        (3ms Redis)     │   └──────┘  └──────┘  └────────┘  └────┘ │
             ↓          │                                          │
        Cache Hit       │         ↓ ↓ ↓ ↓ (400ms total)           │
             ↓          └──────────────────────────────────────────┘
        Response
```

### Common bottlenecks that Redis cannot fix

| Bottleneck | Impact | Redis Helps? |
|------------|--------|--------------|
| Auth/validation before cache check | Adds 50-100ms before cache is hit | No |
| Object mapping/serialization | Consumes CPU after DB fetch | Partially |
| N+1 query patterns | Multiple DB round-trips | No |
| Cold starts (empty cache) | First requests hit DB | No (needs warming) |
| Poor cache key design | Low hit rate (<40%) | No |
| Network latency to cache | Adds 1-5ms per call | No |

---

## Cache hit vs cache miss

Understanding the dramatic difference between hits and misses is essential for cache design.

```
┌─────────────────────────────────────────────────────────────────────────┐
│               CACHE HIT                    CACHE MISS                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│    ┌──────┐                               ┌──────┐                      │
│    │ User │                               │ User │                      │
│    └──┬───┘                               └──┬───┘                      │
│       │ Get request                          │ Get request              │
│       ▼                                      ▼                          │
│  ┌─────────┐                            ┌─────────┐                     │
│  │  Cache  │                            │  Cache  │                     │
│  │ Servers │                            │ Servers │ Data not found      │
│  └────┬────┘                            └────┬────┘                     │
│       │ Return cached data                   │ Forward request          │
│       ▼                                      ▼                          │
│  ┌──────┐                              ┌──────────┐                     │
│  │ User │                              │  Origin  │                     │
│  └──────┘                              │  Server  │                     │
│                                        └────┬─────┘                     │
│  Response: ~3ms                             │ Data returned             │
│                                             ▼                           │
│                                        ┌─────────┐                      │
│                                        │  Cache  │ Save copy            │
│                                        └────┬────┘                      │
│                                             │                           │
│                                             ▼                           │
│                                        ┌──────┐                         │
│                                        │ User │                         │
│                                        └──────┘                         │
│                                                                         │
│                                        Response: ~400ms                 │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key insight:** Cache misses are far more expensive than most teams realize. Every unnecessary miss compounds:
- Database load
- Serialization cost
- Network latency

---

## Fix 1: Move cache access earlier

The first optimization is moving cache access earlier in the request lifecycle, before unnecessary transformations and validations.

### Before (cache access too late)

```
Request → Auth → Validation → Logging → Cache Lookup → ...
                                              ↓
                                        (200ms wasted)
```

### After (cache-first approach)

```
Request → Cache Lookup → (Hit? Return immediately)
              ↓
          Cache Miss
              ↓
      Auth → Validation → Database → Cache Write → Response
```

### Code example: Cache-first approach

```python
# Cache-first approach with response-ready payload
def get_user_profile(user_id: str) -> dict:
    cache_key = f"user:profile:{user_id}"

    # Check cache FIRST - before any other processing
    cached_response = redis.get(cache_key)
    if cached_response is not None:
        return json.loads(cached_response)  # Skip DB, mapping, serialization

    # Cache miss - do the expensive work
    user = user_repository.find_by_id(user_id)
    response = mapper.to_json(user)

    # Cache the RESPONSE, not the domain object
    redis.setex(cache_key, 300, response)  # TTL matters

    return json.loads(response)
```

**Key principle:** The closer the cached value is to the final API output, the more latency you eliminate.

---

## Fix 2: Design cache keys for access patterns

Poor cache key design is one of the most common caching mistakes. Keys should reflect **real access patterns**, not object structures.

### Bad: Vague object-based keys

```python
# Bad: Caching entire domain objects with vague keys
cache_key = f"user:{user_id}"
redis.set(cache_key, serialize(user_object))

# Problems:
# - What if you only need the profile view?
# - What if you need user + recent orders?
# - Different views need different data shapes
```

### Good: Query-specific, deterministic keys

```python
# Good: Cache response-ready payloads with deterministic keys
cache_key = f"user:profile:{user_id}"           # Profile API response
cache_key = f"user:orders:{user_id}:recent:10"  # Last 10 orders
cache_key = f"user:dashboard:{user_id}"         # Dashboard aggregate

# Each key maps to exactly one API response shape
```

### Cache key design principles

| Principle | Example | Why |
|-----------|---------|-----|
| Include query parameters | `products:category:electronics:page:2` | Different queries = different cache entries |
| Include version/shape | `user:profile:v2:{id}` | Schema changes don't serve stale shapes |
| Be deterministic | Sort parameters alphabetically | `?a=1&b=2` and `?b=2&a=1` should hit same key |
| Avoid user-specific when possible | `config:feature_flags` not `config:flags:{user_id}` | Higher hit rate for shared data |

---

## Fix 3: Solve the cold start problem

Cold starts occur when the cache is empty (after deployment, restart, or cache flush). The first wave of traffic hits the database directly, potentially causing "thundering herd" or "cache stampede" problems.

### Cache warming strategy

```python
# Warm critical cache keys at application startup
async def warm_cache():
    """Pre-populate cache with frequently accessed data."""

    # Identify critical keys from access patterns
    critical_keys = [
        ("config:feature_flags", get_feature_flags),
        ("products:popular:top100", get_popular_products),
        ("categories:all", get_all_categories),
    ]

    for cache_key, data_fetcher in critical_keys:
        if not redis.exists(cache_key):
            data = await data_fetcher()
            redis.setex(cache_key, 3600, json.dumps(data))
            logger.info(f"Warmed cache key: {cache_key}")

# Call during application startup
@app.on_event("startup")
async def startup():
    await warm_cache()
```

### Preventing cache stampede

When a popular key expires, many requests may simultaneously try to rebuild it.

```python
import asyncio
from typing import Callable, Any

async def get_with_lock(
    cache_key: str,
    ttl: int,
    fetch_func: Callable[[], Any],
    lock_timeout: int = 5
) -> Any:
    """Fetch with distributed lock to prevent stampede."""

    # Try cache first
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Acquire lock before rebuilding
    lock_key = f"lock:{cache_key}"
    lock_acquired = redis.set(lock_key, "1", nx=True, ex=lock_timeout)

    if lock_acquired:
        try:
            # We got the lock - rebuild cache
            data = await fetch_func()
            redis.setex(cache_key, ttl, json.dumps(data))
            return data
        finally:
            redis.delete(lock_key)
    else:
        # Another process is rebuilding - wait and retry
        await asyncio.sleep(0.1)
        return await get_with_lock(cache_key, ttl, fetch_func, lock_timeout)
```

---

## Performance benchmarks that matter

Real-world results after applying these fixes:

```
┌────────────────────────────────────────────────────────────┐
│                    API Latency Comparison                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Before Cache Redesign:                                    │
│  ████████████████████████████████████████  420ms average   │
│                                                            │
│  After Cache Redesign:                                     │
│  ██████  65ms average                                      │
│                                                            │
│  Redis GET operation:                                      │
│  █  <3ms                                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Key metrics after optimization:**
- Database load dropped by over 70%
- Redis cache hit rates stabilized above 92%
- User-facing latency became predictable (no more random spikes)

**The cache was always fast. The API was slow.** The surrounding architecture was the problem.

---

## Redis deployment patterns

### Simple (single instance)

```
┌─────────┐
│ Primary │
└─────────┘
```

Best for: Development, low-traffic applications.

### High availability (Primary + Replica)

```
┌─────────┐     ┌─────────┐
│ Primary │────→│ Replica │
└─────────┘     └─────────┘
```

Best for: Production with automatic failover needs.

### Clustered (Horizontal scaling)

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│   P1    │  │   P2    │  │   Pn    │
└─────────┘  └─────────┘  └─────────┘
```

Best for: Large datasets that exceed single-node memory.

### HA Clustered (Full production)

```
┌─────────┬─────────┐  ┌─────────┬─────────┐
│   P1    │   R1    │  │   P2    │   R2    │
└─────────┴─────────┘  └─────────┴─────────┘
         ...                  ...
┌─────────┬─────────┐
│   Pn    │   Rn    │
└─────────┴─────────┘
```

Best for: Mission-critical production with both scaling and HA.

---

## Caching patterns compared

| Pattern | Description | Use When |
|---------|-------------|----------|
| **Cache-Aside** | App checks cache, fetches from DB on miss, writes to cache | Default choice for most read-heavy workloads |
| **Read-Through** | Cache automatically fetches from DB on miss | When you want cache to manage loading |
| **Write-Through** | Writes go to cache AND DB synchronously | Strong consistency required |
| **Write-Behind** | Writes go to cache, async flush to DB | High write throughput, can tolerate some lag |
| **Refresh-Ahead** | Proactively refresh cache before TTL expires | Predictable access patterns, zero-latency reads critical |

### Cache-aside flow (most common)

```
┌────────────────────────────────────────────────────────┐
│                    Client Request                      │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  Exists in      │
              │    Redis?       │
              └────────┬────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
           Yes                    No
            │                     │
            ▼                     ▼
    ┌───────────────┐    ┌───────────────┐
    │ Return cached │    │ Make API      │
    │ data (Fetch)  │    │ Request       │
    └───────────────┘    └───────┬───────┘
                                 │
                                 ▼
                        ┌───────────────┐
                        │ Get fresh     │
                        │ Response      │
                        └───────┬───────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ Save copy     │
                        │ in Redis      │
                        └───────┬───────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ Return to     │
                        │ Client        │
                        └───────────────┘
```

---

## Common mistakes checklist

### Architectural mistakes

- [ ] Checking cache after auth/validation layers (cache should be checked first)
- [ ] Caching domain objects instead of response payloads
- [ ] Using vague cache keys that don't match query patterns
- [ ] No cache warming strategy (cold starts hit DB)
- [ ] No protection against cache stampede

### TTL mistakes

- [ ] TTL too short: Cache churns, low hit rate
- [ ] TTL too long: Stale data served to users
- [ ] No TTL at all: Memory fills up, eviction chaos
- [ ] Same TTL for everything: Hot keys and cold keys treated equally

### Monitoring mistakes

- [ ] Only monitoring Redis metrics (miss the real latency story)
- [ ] Not measuring end-to-end API latency
- [ ] Not tracking cache hit rate per key pattern
- [ ] Blaming Redis for problems it didn't cause

---

## Key lessons

1. **Caching is a design problem, not a configuration problem.** Redis cannot compensate for inefficient request flows or poorly scoped cache keys.

2. **Cache misses are far more expensive than most teams realize.** Every unnecessary miss compounds database load, serialization cost, and network latency.

3. **Performance optimization only works when measured end-to-end.** If you only look at Redis metrics, you miss the real story happening in your API layers.

4. **Redis performance is about architecture, not just speed.** Redis does not hide bad design. It exposes it faster.

---

## Final takeaway

> **Redis makes APIs faster only when the system around it is designed to let it win. Real performance comes from cache-aware architecture, not blind dependency on speed.**

Measure honestly, cache intentionally, and let Redis do what it does best.

---

## Related topics

- [Data Patterns](data_patterns.md) - CAP Theorem, Sharding, Event Sourcing
- [SQL vs NoSQL](sql_vs_nosql.md) - When to use Redis as part of polyglot persistence
- [Scalability & Reliability](scalability_reliability.md) - Load balancing, High availability
