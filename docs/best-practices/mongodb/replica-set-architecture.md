# MongoDB Replica Set Architecture

**[← Back to MongoDB Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Database Reliability Engineering
> **Status:** Draft

**Table of Contents**

- [Introduction](#introduction)
- [Architecture Patterns](#architecture-patterns)
    - [PSS (Primary-Secondary-Secondary)](#pss-primary-secondary-secondary)
    - [PSA (Primary-Secondary-Arbiter)](#psa-primary-secondary-arbiter)
- [Voting Members](#voting-members)
- [Hidden and Priority Nodes](#hidden-and-priority-nodes)
- [Verification](#verification)

## Introduction

A robust replica set architecture is essential for high availability (HA) and data durability. This guide outlines standard topology patterns.

## Architecture Patterns

### PSS (Primary-Secondary-Secondary)

**Restriction:** Production Standard.

This is the standard 3-node architecture containing data on all nodes.
*   **Availability:** High. Can sustain 1 node failure.
*   **Durability:** High. Supports `w:majority` with full data safety.

### PSA (Primary-Secondary-Arbiter)

*See Critical Risks section below.*

### Distributed PSS (5-Node / 3-DC)

**Restriction:** Enterprise Standard (Minimum for High Availability).

To achieve true enterprise resilience and survive a full data center failure while maintaining `w:majority` write availability, a 5-node architecture distributed across 3 data centers (2-2-1) is the required minimum standard.

*   **Topology:**
    *   **DC1:** 2 Nodes (Priority High)
    *   **DC2:** 2 Nodes (Priority Medium)
    *   **DC3:** 1 Node (Priority Low)
*   **Why 5 Nodes?**
    *   Losing any single DC (even one with 2 nodes) leaves 3 voting members active.
    *   3 out of 5 is a majority, ensuring `w:majority` writes succeed and elections are instant.
    *   A 3-node PSS system across 3 DCs (1-1-1) becomes read-only if any DC fails (1 node lost leaves 2, but `w:majority` requires 2, leaving zero margin for error or maintenance).

### PSA (Primary-Secondary-Arbiter)

**Restriction:** Development / Non-Critical Only. DO NOT USE IN PRODUCTION.

An architecture with 2 data nodes and 1 arbiter.

*   **Critical Risks:**
    *   **Write Availability:** If the single Secondary fails, the replica set has only 1 data node. A `w:majority` write requires 2 data nodes. **Writes will stall indefinitely**, causing total application downtime.
    *   **Data Safety:** You effectively have `w:1` reliability disguised as a replica set.
    *   **Operational Drag:** Arbiters cause cache pressure on the primary during secondary outages, typically crashing the primary when it is needed most.

> [!CAUTION]
> Arbiters are strictly prohibited for production systems requiring `w:majority` guarantees. Use the 5-node PSS standard instead.

**Official Reference:** [Replica Set Deployment Architectures](https://www.mongodb.com/docs/manual/core/replica-set-architectures/)

## Voting Members

*   **Limit:** A replica set can have up to 50 members, but **only 7 can be voting members**.
*   **Odd Number:** Always maintain an odd number of votes (3, 5, 7) to prevent split-brain scenarios.

**Official Reference:** [Replica Set 7-Voter Limit](https://www.mongodb.com/docs/manual/core/replica-set-elections/#replica-set-elections-voting-limit)

## Hidden and Priority Nodes

Use specialized node configurations for specific workloads without impacting HA.

### Analytics Nodes
Configure a node as hidden (`hidden: true`) and non-voting (`priority: 0`) to serve heavy analytics queries without taking client traffic or participating in elections.

**Official Reference:** [Hidden Replica Set Members](https://www.mongodb.com/docs/manual/core/replica-set-hidden-member/)

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
