# MongoDB replica set architecture

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 27, 2026
> **Maintainers:** Global Data Services
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Topic](https://img.shields.io/badge/Topic-MongoDB-green)

> [!IMPORTANT]
> **Related Docs:** [RHEL Configuration](./rhel-configuration.md) | [Instance Configuration](./instance-configuration.md) | [Storage Engine](./storage-engine.md)

## Table of contents

- [Introduction](#introduction)
- [Architecture standard](#architecture-standard)
- [Voting members and quorum](#voting-members-and-quorum)
- [Hidden and priority nodes](#hidden-and-priority-nodes)
- [Advanced configuration](#advanced-configuration)
- [Verification](#verification)

## Introduction

A replica set architecture is essential for **business continuity**, ensuring both High Availability (HA) and Disaster Recovery (DR).

> [!NOTE]
> **Terminology:** A **replica set** is a group of `mongod` processes maintaining the same data set. In MongoDB, a "cluster" technically refers to a sharded architecture (which contains multiple replica sets), though the term is often used loosely to describe any production deployment. This guide focuses on the replica set unit.

[↑ Back to Table of Contents](#table-of-contents)

## Architecture standard

### Distributed PSS (5-node / 3-DC)

> [!NOTE]
> **Definition:** **PSS** (Primary-Secondary-Secondary) is the standard industry term for a replica set where **all members are data-bearing**, regardless of the total node count (3, 5, 7, etc.). It contrasts with **PSA** (Primary-Secondary-Arbiter), where voting-only non-data-bearing members are used.

**Restriction:** Enterprise standard (minimum for high availability).

To achieve true enterprise resilience and survive a full data center failure while maintaining `w:majority` write availability, a 5-node architecture distributed across 3 data centers (2-2-1) is the required minimum standard.

*   **Topology and priority settings:**
    *   **DC1 (Primary site):** 2 nodes — `priority: 2`
        *   **Role:** Preferred for Primary. High priority ensures leadership usually stays here.
    *   **DC2 (Failover site):** 2 nodes — `priority: 1`
        *   **Role:** Failover target. Lower priority than DC1, so it only becomes Primary if DC1 fails.
    *   **DC3 (Quorum site):** 1 node — `priority: 0`, `hidden: true`
        *   **Role:** Quorum voter and data-bearing. `priority: 0` prevents it from ever becoming Primary. `hidden: true` prevents clients from reading from it (avoiding cross-DC latency).

> [!NOTE]
> **Note on priorities:** MongoDB election priorities are **scores**, not ranks. Higher numbers are preferred.
> *   `2` beats `1`.
> *   `0` means "never eligible for Primary."
> *   Valid range: `0` to `1000`. Default: `1`.

*   **Why 5 nodes?**
    *   Losing any single DC (even one with 2 nodes) leaves 3 voting members active.
    *   3 out of 5 is a majority, ensuring `w:majority` writes succeed and elections complete.
    *   A 3-node PSS system across 3 DCs (1-1-1) becomes read-only if any DC fails (1 node lost leaves 2 of 3 votes, which is not >50%, so no new Primary can be elected).

### Read routing strategy

To ensure applications only read from the local active DC (avoiding cross-DC latency):

*   **Default (`primary`):** Reads always go to the Primary.
    *   **Normal:** Primary is in DC1, so reads stay in DC1.
    *   **Failover:** Primary moves to DC2, so reads move to DC2.
    *   **Verdict:** This is the safest default and guarantees data consistency.
*   **Scaling (`nearest`):** If you need to distribute reads across secondaries, use `readPreference: nearest`.
    *   Drivers automatically calculate latency to each member.
    *   **Normal:** DC1 nodes are <1ms away, DC2 nodes are >10ms. The driver picks DC1.
    *   **Failover:** DC1 is down. DC2 nodes are now the "nearest" available. The driver picks DC2.

> [!NOTE]
> MongoDB provides five read preference modes: `primary` (default), `primaryPreferred`, `secondary`, `secondaryPreferred`, and `nearest`. All modes except `primary` may return stale data. Distributed transactions **must** use `primary` read preference.

**Official Reference:** [Read preference](https://www.mongodb.com/docs/manual/core/read-preference/) | [Geographically distributed replica sets](https://www.mongodb.com/docs/manual/core/replica-set-architecture-geographically-distributed/)

[↑ Back to Table of Contents](#table-of-contents)

## Voting members and quorum

**"Voting" is the mechanism of high availability.**

*   **High Availability (HA):** MongoDB uses a mechanism called **quorum** to maintain HA. To elect a Primary (and keep the database writable), a strict majority (>50%) of voting members must be online and communicating.
    *   **No votes = no quorum = no Primary = downtime.**
*   **Disaster Recovery (DR):** DR depends on the **distribution** of these votes.
    *   In a 3-DC setup (2-2-1), if DC1 (2 votes) fails, DC2 (2 votes) + DC3 (1 vote) = 3 votes. This is a majority of 5, so the replica set survives.
    *   Without the vote in DC3, you would only have 2 of 5 votes, and the replica set would go down.
*   **7-voter limit:** A replica set can have a maximum of **7 voting members**. This is a hard limit in MongoDB on how widely you can distribute quorum power. A replica set can have up to **50 total members**, but only 7 may vote. Non-voting members must have `votes: 0` and `priority: 0`.

**Official Reference:** [Replica set elections](https://www.mongodb.com/docs/manual/core/replica-set-elections/) | [Replica set members](https://www.mongodb.com/docs/manual/core/replica-set-members/)

### Critical risk: arbiters (PSA) vs data-bearing (PSS)

Using an arbiter (PSA architecture) causes cluster unavailability primarily through **write concern deadlocks** and **Primary cache exhaustion**. While an arbiter keeps a Primary elected, it cannot acknowledge data writes, causing operations to hang.

#### 1. The "majority write" deadlock

This is the most immediate cause of downtime.

*   **The flaw:** Arbiters allow a Primary to remain elected (voting majority) even when there are not enough data nodes to acknowledge writes (data minority).
*   **Scenario (5-node set):** In a set with 4 data nodes + 1 arbiter, if 2 data nodes fail:
    *   **State:** 2 data + 1 arbiter remain (3 votes = majority). The Primary stays elected.
    *   **Deadlock:** A `w: "majority"` write requires acknowledgment from a majority of **data-bearing** members. With only 2 of 4 data nodes available, the majority (3) cannot be reached. **The cluster elects a leader but blocks all data operations.**

#### 2. The "cache pressure" crash

This is often the "silent killer" in high-load systems.

*   **Mechanics:** WiredTiger uses a "majority commit point" to safely manage its cache.
*   **Failure:** When data nodes fail in a PSA set, the commit point cannot advance.
*   **The crash:** The Primary is forced to pin "dirty" pages in its cache, exhausting memory and I/O. The Primary eventually crashes, leading to a total outage.

> [!CAUTION]
> **Production prohibition:** Always use PSS (all data-bearing nodes). In a 5-node replica set, deploy 5 data-bearing nodes to ensure that any surviving majority can both vote **and** store data. Starting in MongoDB 5.3, support for multiple arbiters in a replica set is disabled by default.

**Official Reference:** [Replica set arbiter](https://www.mongodb.com/docs/manual/core/replica-set-arbiter/)

[↑ Back to Table of Contents](#table-of-contents)

## Hidden and priority nodes

Use specialized node configurations for specific workloads without impacting HA.

### Analytics nodes

Configure a node as hidden (`hidden: true`) and non-electable (`priority: 0`) to serve heavy analytics queries without taking client traffic.

**Crucial logic:** Setting `hidden: true` makes the node invisible to *default* driver discovery, but it does **not** automatically route analytics traffic there. You **must** use replica set tags.

1.  **Server config:** Tag the node.
    ```javascript
    tags: { "nodeType": "analytics" }
    ```
2.  **Client connection:** The application must specify this tag.
    *   **URI:** `mongodb://...?readPreference=secondary&readPreferenceTags=nodeType:analytics`
    *   **Result:** The driver sends reads *only* to nodes with this specific tag.

> [!NOTE]
> Hidden members must have `priority: 0`. They can still vote in elections. If you want the node to be non-voting as well, explicitly set `votes: 0`.

**Official Reference:** [Hidden replica set members](https://www.mongodb.com/docs/manual/core/replica-set-hidden-member/) | [Replica set tags](https://www.mongodb.com/docs/manual/core/read-preference-tags/)

[↑ Back to Table of Contents](#table-of-contents)

## Advanced configuration

For 5-node distributed replica sets (WAN), specific parameter tuning is required for stability.

### Heartbeats and timeouts

*   **Parameter:** `settings.electionTimeoutMillis`
*   **Recommendation:** `20000` (20 seconds) or higher.
*   **Reason:** The default is `10000` (10 seconds). Standard WAN links often experience transient latency spikes or minor packet loss. In a cross-DC scenario, a brief network hiccup could cause secondaries to believe the Primary is dead, triggering a false failover (flapping). Increasing to 20 seconds provides a safety buffer, prioritizing cluster stability over sub-second failover speed.

### Replication chaining

*   **Parameter:** `settings.chainingAllowed`
*   **Recommendation:** `true` (default).
*   **Reason:** Allows the 2 nodes in the failover DC to replicate from each other. If disabled, both must pull data across the WAN from the Primary, doubling inter-DC bandwidth usage. Starting in MongoDB 5.0.2, the `enableOverrideClusterChainingSetting` parameter can override this setting per-member.

### Oplog sizing

*   **Parameter:** `oplogSizeMB`
*   **Default:** 5% of free disk space (minimum 990 MB, maximum 50 GB).
*   **Recommendation:** Size for **24+ hours** of write traffic.
*   **Reason:** If the failover DC is disconnected for several hours, the Primary's oplog must hold enough operations to let the secondaries catch up. If the oplog rolls over, the remote nodes enter a "stale" state and require a full initial sync, which saturates the network.

> [!TIP]
> You can resize the oplog dynamically without restarting `mongod` by using the `replSetResizeOplog` command. You can also set a minimum retention period with `storage.oplogMinRetentionHours`.

**Official Reference:** [Replica set oplog](https://www.mongodb.com/docs/manual/core/replica-set-oplog/) | [Replica set configuration](https://www.mongodb.com/docs/manual/reference/replica-configuration/)

[↑ Back to Table of Contents](#table-of-contents)

## Verification

### Check member config

Connect to the primary and run:
```javascript
rs.conf().members.forEach(m => print(`Host: ${m.host}, Priority: ${m.priority}, Votes: ${m.votes}, Arbiter: ${m.arbiterOnly}`))
```
Ensure:
*   Total voting members is 7 or fewer.
*   Total voting members is an odd number.
*   Production systems use `arbiterOnly: false` (PSS).

### Verify DC2 failover (DR)

Ensure DC2 is configured to take over *only* if DC1 fails completely.

**Scenario 1: Local HA (stepdown)**
*   **Action:** Step down the Primary in DC1.
    ```javascript
    rs.stepDown()
    ```
*   **Expectation:** The **other priority 2 node in DC1** becomes Primary.
*   **Why:** `priority: 2` > `priority: 1`. The replica set prefers staying in DC1.

**Scenario 2: Site DR (full outage)**
*   **Action:** Shut down (or step down) **both** DC1 nodes.
    ```javascript
    // Run on BOTH DC1 nodes to simulate site failure
    rs.stepDown(300) // Force 5-minute freeze
    ```
*   **Expectation:** A **priority 1 node in DC2** becomes Primary.
*   **Read routing:** Since `readPreference` defaults to `primary`, traffic automatically follows the new Primary to DC2.

### Verify DC3 isolation

Ensure DC3 never serves reads.
```javascript
rs.conf().members.forEach(m => {
    if (m.priority == 0 && m.hidden == true) {
        print(`ISOLATED: ${m.host} is Hidden/Priority 0`);
    }
})
```
*   **Guarantee:** `hidden: true` makes the node invisible to drivers using default read preferences.
*   **Direct check:** Connect directly to the DC3 node and run:
    ```javascript
    db.hello().hidden // Should return true
    db.hello().isWritablePrimary // Should return false
    ```

[↑ Back to Table of Contents](#table-of-contents)
