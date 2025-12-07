# System Design: Scalability & Reliability Patterns

> "Scaling is solving problems you don't have yet, often by creating problems you didn't expect."

Making systems reliable usually involves adding more moving parts (redundancy), which paradoxically can decrease reliability if not managed well.

---

## 1. Load Balancers (L7 vs L4)

**The Concept:** A reverse proxy that distributes network traffic across multiple servers.

### The Tradeoff

- **Problem Solved:**
  - **Horizontal Scaling:** You can add 10 more servers to handle 10x traffic.
  - **High Availability:** If one server dies, the LB stops sending traffic to it.
- **Problem Created:**
  - **Single Point of Failure:** If the LB goes down, *everything* goes down. (Now you need two LBs with floating IPs).
  - **Session Stickiness:** If you store user sessions in local RAM, you must force the LB to send User A to Server 1 every time. This breaks load balancing. (Solution: Stateless servers + Redis).

### 🛑 When NOT to use

- **Tiny Internal Apps:** If you have 10 users, just point DNS to the server IP. An AWS ELB costs money and config time.
- **Stateful Legacy Apps:** If your app assumes it's the only server in the world, putting an LB in front will break it immediately.

---

## 2. Rate Limiting

**The Concept:** Controlling the amount of incoming or outgoing traffic. "User A can only make 10 requests per minute."

### The Reason It Exists

- **Preventing Abuse:** Stopping DDOS attacks or reckless scripts.
- **Protecting Downstream:** Your API Gateway might handle 10k RPS, but the legacy database behind it can only handle 100 RPS.

### The Tradeoff

- **Problem Solved:** Stability. It sheds load to save the system.
- **Problem Created:** **User Experience.** Legitimate users might get blocked (False Positives). "Why is my important API call failing with 429?"

### Advanced: Backpressure & Jitter

- **Backpressure:** The system screams "STOP" instead of crashing. TCP has it built-in (Window Size). HTTP does not (needs 503 Service Unavailable).
- **Jitter:** When 1000 clients fail, they all retry in 1s. Then they all fail again.
  - *Solution:* `sleep(retry_count * 1s + random(0, 500ms))`. The randomness desynchronizes the herd.

### 🛑 When NOT to use

- **Strictly Internal/Trusted Traffic:** If Service A calls Service B and you own both, fix the calling pattern in Service A. Don't add a rate limiter in Service B just to make Service A crash.

---

### Advanced: Backpressure & Jitter

- **Backpressure:** The system screams "STOP" instead of crashing. TCP has it built-in (Window Size). HTTP does not (needs 503 Service Unavailable).
- **Jitter:** When 1000 clients fail, they all retry in 1s. Then they all fail again.
  - *Solution:* `sleep(retry_count * 1s + random(0, 500ms))`. The randomness desynchronizes the herd.

## 3. Circuit Breakers

**The Concept:** If Service B is failing/slow, Service A should *stop trying* to call it for a while, rather than waiting for timeouts and piling up requests.

### The Tradeoff

- **Problem Solved:** **Cascading Failure.** Prevents one slow service from taking down the entire system by exhausting thread pools in callers.
- **Problem Created:**
  - **Testing Difficulty:** Hard to test "partial failure" states.
  - **Fallback Logic:** You need to write code for "What do I show the user when the Recommendation Service is dead?" (e.g., Show default items). This logic is rarely exercised and often buggy.

### 🛑 When NOT to use

- **Monoliths:** In-process function calls don't timeout the same way network calls do.
- **Critical Data:** If writing to the Payment Service fails, you *should* probably fail the transaction, not "fallback to a default payment."

---

## 4. Content Delivery Networks (CDNs)

**The Concept:** Caching static assets (images, CSS, JS) on servers geographically closer to the user (e.g., Cloudflare, Cloudfront).

### The Tradeoff

- **Problem Solved:**
  - **Latency:** Speed of light matters. Content comes from London instead of San Francisco.
  - **Server Load:** Offloads 90% of traffic (static files) from your application servers.
- **Problem Created:**
  - **Cache Invalidation (Again):** "I deployed the new CSS but users still see the broken layout."
  - **Cost:** High bandwidth bills if not configured correctly (e.g., caching 4K video).

### 🛑 When NOT to use

- **Dynamic API Responses:** Caching JSON API responses at the edge is risky (User A sees User B's data). Stick to static assets unless you are an expert.
- **Intranet Apps:** If all your users are in the same office building as the server, a CDN adds nothing.
