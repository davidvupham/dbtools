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

**Restriction:** Cost-sensitive / Non-critical only.

An architecture with 2 data nodes and 1 arbiter (no data).
*   **Risks:**
    *   **Data Safety:** `w:majority` essentially becomes `w:2` (all data nodes). If one data node fails, writes may stall or durability is compromised.
    *   **Operational:** Arbiters put significant pressure on the remaining data node during failures.

> [!WARNING]
> Avoid PSA architectures for systems requiring strict `w:majority` guarantees.

### Distributed PSS (5-Node / 3-DC)

**Restriction:** High Availability / Disaster Recovery Standard.

For systems requiring resilience against a full data center failure, a 5-node architecture spread across 3 data centers (2-2-1) is recommended.

*   **Topology:**
    *   **DC1:** 2 Nodes
    *   **DC2:** 2 Nodes
    *   **DC3:** 1 Node
*   **Resilience:** Can sustain the loss of any single data center (losing 2 nodes leaves 3 voting members, ensuring a majority).
*   **Write Concern:** Supports `w:majority` even with one DC offline.

**Official Reference:** [Distributed Clusters](https://www.mongodb.com/docs/manual/core/replica-set-architecture-geographically-distributed/)

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
