# System Design: Operational Excellence & Staff Engineering

> "Prod-First Mentality: Knowing how your system behaves — not just how it should work."

Senior engineers build features. Staff engineers ensure the system survives the features.

---

## 1. SLO, SLA, and Error Budgets

**The Concept:** 100% uptime is impossible and infinite cost. Who decides "how broken is too broken?"

- **SLI (Indicator):** The metric. "Request Latency".
- **SLO (Objective):** The goal. "99% of requests < 300ms over 30 days."
- **SLA (Agreement):** The contract. "If we miss the SLO, we pay you money." (Lawyers care about this).
- **Error Budget:** The remaining wiggle room.
  - If you need 99.9% uptime (43 min downtime/month), and you had 10 min downtime yesterday, you have 33 mins left.
  - **Staff Move:** If you exhaust the Error Budget, **freeze all feature deployments.** Only stability work allowed.

---

## 2. Disaster Testing & Chaos Engineering

**The Concept:** "Hope is not a strategy."

- **Game Days:** Scheduled exercises where you kill a database, sever a network link, or simulate a region failure.
- **Chaos Monkey:** Automated random destruction.
- **The Insight:** Distributed Systems degrade in weird ways.
  - If the Recommendation Service is slow, does the Checkout page hang? (It shouldn't).
  - If Redis is empty, does the DB melt? (Cache Stampede).

---

## 3. Capacity Planning & Backpressure

**The Problem:** "Thundering Herd."

- **Backpressure:** The ability of a system to say "I am full, go away" instead of crashing.
  - **TCP Backpressure:** The receiver window closes. Sender slows down.
  - **Application Backpressure:** Returning HTTP 503 instantly is better than hanging for 30s and then failing.
- **Bulkheads:** Partitioning your system so a failure in the "Image Resizer" doesn't crash the "Login Service". (Like ship bulkheads - if one compartment floods, the ship floats).

---

## 4. Organizational Influence (The "Staff" Part)

**The Concept:** Getting 50 people to agree on a direction.

- **Design Docs (RFCs):** Writing is thinking. Force engineers to write down the plan *before* coding.
  - Sections: Context, Goals, Non-Goals, Alternatives Considered (Why NOT MongoDB?).
- **Cross-Team Alignment:**
  - "I want to change the API." -> You need to talk to Mobile, Web, and QA teams first.
- **Glue Work:** Doing the unglamorous work (updating documentation, fixing CI/CD, mentoring) that makes the whole org faster.
