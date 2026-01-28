# MongoDB Replica Set Architecture

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

## Table of Contents

- [Introduction](#introduction)
- [Architecture Standard](#architecture-standard)
- [Distributed PSS (5-Node / 3-DC)](#distributed-pss-5-node--3-dc)
- [Voting Members & Quorum](#voting-members--quorum)
- [Hidden and Priority Nodes](#hidden-and-priority-nodes)
  - [Analytics Nodes](#analytics-nodes)
- [Advanced Configuration](#advanced-configuration)
- [Verification](#verification)
  - [Check Member Config](#check-member-config)
  - [Verify DC2 Failover](#verify-dc2-failover)
  - [Verify DC3 Isolation](#verify-dc3-isolation)

## Introduction

A replica set architecture is essential for **Business Continuity**, ensuring both High Availability (HA) and Disaster Recovery (DR).

> **Terminology:** A **Replica Set** is a group of `mongod` processes maintaining the same data set. In MongoDB, a "Cluster" technically refers to a sharded architecture (which contains multiple replica sets), though the term is often used loosely to describe any production deployment. This guide focuses on the Replica Set unit.

[Back to Table of Contents](#table-of-contents)

## Architecture Standard

### Distributed PSS (5-Node / 3-DC)

> **Definition:** **PSS** (Primary-Secondary-Secondary) is the standard industry term for a replica set where **all members are data-bearing**, regardless of the total node count (3, 5, 7, etc.). It contrasts with **PSA** (Primary-Secondary-Arbiter), where voting-only members are used.

**Restriction:** Enterprise Standard (Minimum for High Availability).

To achieve true enterprise resilience and survive a full data center failure while maintaining `w:majority` write availability, a 5-node architecture distributed across 3 data centers (2-2-1) is the required minimum standard.

*   **Topology & Priority Settings:**
    *   **DC1 (Primary Site):** 2 Nodes - `priority: 2`
        *   **Role:** Preferred for Primary. High priority ensures leadership usually stays here.
    *   **DC2 (Failover Site):** 2 Nodes - `priority: 1`
        *   **Role:** Failover target. Lower priority than DC1, so it only becomes Primary if DC1 fails.
    *   **DC3 (Quorum Site):** 1 Node - `priority: 0`, `hidden: true`
        *   **Role:** Voting only. `priority: 0` prevents it from *ever* becoming Primary. `hidden: true` prevents clients from reading from it (avoiding high latency).

> **Note on Priorities:** MongoDB Election Priorities are **scores**, not ranks. Higher numbers are preferred.
> *   `2` beats `1`.
> *   `0` means "Never".
*   **Why 5 Nodes?**
    *   Losing any single DC (even one with 2 nodes) leaves 3 voting members active.
    *   3 out of 5 is a majority, ensuring `w:majority` writes succeed and elections are instant.
    *   A 3-node PSS system across 3 DCs (1-1-1) becomes read-only if any DC fails (1 node lost leaves 2, but `w:majority` requires 2, leaving zero margin for error or maintenance).

### Read Routing Strategy

To ensure applications only read from the local active DC (avoiding cross-DC latency):

*   **Default (`primary`):** Reads always go to the Primary.
    *   **Normal:** Primary is in DC1 -> Reads stay in DC1.
    *   **Failover:** Primary moves to DC2 -> Reads move to DC2.
    *   **Verdict:** This is the safest default and guarantees data consistency.
*   **Scaling (`nearest`):** If you need to read from Secondaries, use `readPreference: nearest`.
    *   Drivers automatically calculate latency.
    *   **Normal:** DC1 nodes are <1ms, DC2 are >10ms. Driver picks DC1.
    *   **Failover:** DC1 is down. DC2 nodes are now the "nearest" available. Driver picks DC2.

**Official Reference:** [Distributed Clusters](https://www.mongodb.com/docs/manual/core/replica-set-architecture-geographically-distributed/)





## Voting Members & Quorum

**"Voting" is the mechanism of High Availability.**

*   **High Availability (HA):** MongoDB uses a mechanism called **Quorum** to maintain HA. To elect a Primary (and keep the database writable), a majority (>50%) of voting members must be online and communicating.
    *   **No Votes = No Quorum = No Primary = Downtime.**
*   **Disaster Recovery (DR):** DR depends on the **distribution** of these votes.
    *   In a 3-DC setup (2-2-1), if DC1 (2 votes) fails, DC2 (2 votes) + DC3 (1 vote) = 3 votes. This is a majority of 5, so the cluster survives.
    *   If you did not have the vote in DC3, you would only have 2/5 votes, and the cluster would go down.
*   **7-Voter Limit:** You can only have 7 voting members max. This is a hard limit on how widely you can distribute this "Quorum" power.

**Official Reference:** [Replica Set 7-Voter Limit](https://www.mongodb.com/docs/manual/core/replica-set-elections/#replica-set-elections-voting-limit)

### Critical Risk: Arbiters (PSA) vs Data-Bearing (PSS)

Using an arbiter (PSA architecture) causes cluster unavailability primarily through **Write Concern Deadlocks** and **Primary Cache Exhaustion**. While an arbiter keeps a Primary elected, it cannot acknowledge data writes, causing operations to hang.

#### 1. The "Majority Write" Deadlock
This is the most immediate cause of downtime.
*   **The Flaw:** Arbiters allow a Primary to remain elected (Voting Majority) even when there aren't enough data nodes to acknowledge writes (Data Minority).
*   **Scenario (5-Node Set):** In a set with 4 Data nodes + 1 Arbiter, if 2 Data nodes fail:
    *   **State:** 2 Data + 1 Arbiter remain (3 votes = Majority). The Primary stays elected.
    *   **Deadlock:** A `w: "majority"` write requires 3 data acknowledgments (majority of 5). Only 2 data nodes are available. **Writes allow the cluster to elect a leader but block all data operations.**

#### 2. The "Cache Pressure" Crash
This is often the "silent killer" in high-load systems.
*   **Mechanics:** WiredTiger uses a "majority commit point" to safely manage its cache.
*   **Failure:** When data nodes fail in a PSA set, the commit point cannot advance.
*   **The Crash:** The Primary is forced to pin "dirty" pages in its cache, exhausting memory and I/O. The Primary eventually crashes, leading to a total outage.

> [!CAUTION]
> **Production Prohibition:** Always use PSS (all data-bearing nodes). In a 5-node cluster, deploy 5 data-bearing nodes to ensure that any surviving majority can both vote AND store data.

[Back to Table of Contents](#table-of-contents)

## Hidden and Priority Nodes

Use specialized node configurations for specific workloads without impacting HA.

### Analytics Nodes
Configure a node as hidden (`hidden: true`) and non-voting (`priority: 0`) to serve heavy analytics queries without taking client traffic.

**Crucial Logic:** Simply setting `hidden: true` makes the node invisible to *default* discovery, but it does **not** automatically route analytics traffic there. You **MUST** use Replica Set Tags.

1.  **Server Config:** Tag the node.
    ```javascript
    tags: { "nodeType": "analytics" }
    ```
2.  **Client Connection:** The application must specify this tag.
    *   **URI:** `mongodb://...?readPreference=secondary&readPreferenceTags=nodeType:analytics`
    *   **Result:** The driver will send reads *only* to nodes with this specific tag.

**Official Reference:** [Hidden Replica Set Members](https://www.mongodb.com/docs/manual/core/replica-set-hidden-member/)

[Back to Table of Contents](#table-of-contents)

## Advanced Configuration

For 5-node distributed replica sets (WAN), specific parameter tuning is required for stability.

### Heartbeats & Timeouts
*   **Parameter:** `settings.electionTimeoutMillis`
*   **Recommendation:** `20000` (20 seconds) or higher.
*   **Reason:** Standard WAN links often experience transient latency spikes or minor packet loss. The default 10s timeout triggers an election after 10s of silence. In a cross-DC scenario, a brief network hiccup could cause the Secondaries to "think" the Primary is dead, triggering a false failover (flapping). Increasing to 20s provides a safety buffer, prioritizing cluster stability over sub-second failover speeds.

### Replication Chaining
*   **Parameter:** `settings.chainingAllowed`
*   **Recommendation:** `true` (Default).
*   **Reason:** Allows the 2 nodes in the Failover DC to replicate from each other. If disabled, both must pull data across the WAN from the Primary, doubling inter-DC bandwidth usage.

### Oplog Sizing
*   **Parameter:** `oplogSizeMB`
*   **Recommendation:** Size for **24+ hours** of write traffic.
*   **Reason:** If the Failover DC is disconnected for 4 hours, the Primary's oplog must hold enough operations to let the secondaries catch up. If the oplog rolls over, the remote nodes fall into "Stale" state and require a full Initial Sync, which saturates usage.

[Back to Table of Contents](#table-of-contents)

## Verification

### Check Member Config
Connect to the primary and run:
```javascript
rs.conf().members.forEach(m => print(`Host: ${m.host}, Priority: ${m.priority}, Votes: ${m.votes}, Arbiter: ${m.arbiterOnly}`))
```
Ensure:
*   Total voting members <= 7.
*   Total voting members is an odd number.
*   Production systems use `arbiterOnly: false` (PSS).

### Verify DC2 Failover (DR)
Ensure DC2 is configured to take over *only* if DC1 fails completely.

**Scenario 1: Local HA (Stepdown)**
*   **Action:** Step down the Primary in DC1.
    ```javascript
    rs.stepDown()
    ```
*   **Expectation:** The **other Priority 2 node in DC1** becomes Primary.
*   **Why:** `Priority 2` > `Priority 1`. The cluster prefers staying in DC1.

**Scenario 2: Site DR (Full Outage)**
*   **Action:** Shutdown (or step down) **BOTH** DC1 nodes.
    ```javascript
    // Run on BOTH DC1 nodes to simulate site failure
    rs.stepDown(300) // Force 5 minute freeze
    ```
*   **Expectation:** A **Priority 1 node in DC2** becomes Primary.
*   **Read Routing:** Since `readPreference` defaults to `primary`, traffic will automatically follow the new Primary to DC2.

### Verify DC3 Isolation
Ensure DC3 never serves reads.
```javascript
rs.conf().members.forEach(m => {
    if (m.priority == 0 && m.hidden == true) {
        print(`ISOLATED: ${m.host} is Hidden/Priority 0`);
    }
})
```
*   **Guarantee:** `hidden: true` makes the node invisible to drivers. It is technically impossible for an application to send reads to this node.
*   **Direct Check:** Connect strictly to the DC3 node and run:
    ```javascript
    db.hello().hidden // Should match true
    db.hello().isWritablePrimary // Should match false
    ```

[Back to Table of Contents](#table-of-contents)
