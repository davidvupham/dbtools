# Administrator Learning Path

**[← Back to Course Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Path](https://img.shields.io/badge/Path-Administrator-purple)

## Overview

This learning path is designed for **platform engineers, DevOps engineers, and system administrators** who need to deploy, configure, secure, and operate Kafka clusters in production environments.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ADMINISTRATOR LEARNING PATH                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 1              Week 2              Week 3              Week 4         │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐     │
│  │ Module  │        │ Module  │        │ Module  │        │ Module  │     │
│  │ 1 & 2   │───────►│ 3       │───────►│ 4       │───────►│   4     │     │
│  │         │        │ (basics)│        │ (15-16) │        │ (17)    │     │
│  │Architect│        │ Connect │        │ Security│        │ Prod Ops│     │
│  │ure &    │        │ Ops     │        │ Monitor │        │ Project │     │
│  │ Core    │        │         │        │         │        │         │     │
│  └─────────┘        └─────────┘        └─────────┘        └─────────┘     │
│                                                                             │
│  Focus: How Kafka    Focus: Data       Focus: Securing    Focus: Running   │
│         Works        Integration       & Observing        Production       │
│         Internals    Operations        Clusters           Clusters         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Target audience

- Platform engineers managing Kafka infrastructure
- DevOps engineers deploying Kafka
- System administrators responsible for Kafka operations
- Site reliability engineers (SREs)
- Infrastructure architects

## Prerequisites

- Linux system administration experience
- Familiarity with Docker and containers
- Basic networking knowledge (TCP/IP, DNS, TLS)
- Understanding of distributed systems concepts

## Learning objectives

By completing this path, you will be able to:

1. **Deploy** Kafka clusters in KRaft mode (no ZooKeeper)
2. **Configure** brokers, topics, and clients for various workloads
3. **Secure** clusters with TLS, SASL, and ACLs
4. **Monitor** Kafka with metrics, logging, and alerting
5. **Troubleshoot** common issues and performance problems
6. **Plan** capacity and perform maintenance operations

---

## Week 1: Architecture and operations fundamentals

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1 | Architecture deep dive | [02_architecture.md](../module_1_foundations/02_architecture.md) | 2 hours |
| 2 | Environment setup (container) | [03_setup_environment.md](../module_1_foundations/03_setup_environment.md) | 2 hours |
| 3 | Topic management | [05_topics_partitions.md](../module_2_core_concepts/05_topics_partitions.md) | 2 hours |
| 4 | Producer/Consumer internals | [06_producers.md](../module_2_core_concepts/06_producers.md) | 2 hours |
| 5 | Configuration reference | [Configuration Guide](../reference/configuration-guide.md) | 3 hours |

### Key administrator concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLUSTER SIZING GUIDELINES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WORKLOAD            BROKERS    PARTITIONS/TOPIC    REPLICATION    STORAGE │
│  ────────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  Development         1          1-3                 1              50GB     │
│  (Testing)                                                                  │
│                                                                             │
│  Small Production    3          6-12                3              500GB    │
│  (<10K msg/sec)                                                    SSD      │
│                                                                             │
│  Medium Production   5-10       12-30               3              1-5TB    │
│  (10K-100K msg/sec)                                                SSD      │
│                                                                             │
│  Large Production    10-30      30-100              3              5-20TB   │
│  (100K+ msg/sec)                                                   NVMe     │
│                                                                             │
│  NOTES:                                                                     │
│  • Always use odd broker count for quorum (3, 5, 7)                         │
│  • Partitions = max(throughput_need, consumer_parallelism)                  │
│  • Plan for 2x storage for replication overhead                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 1)

1. **Deploy a 3-broker cluster** in Docker with KRaft mode
2. **Create topics** with various partition and replication settings
3. **Benchmark throughput** using `kafka-producer-perf-test`
4. **Analyze broker logs** for common patterns
5. **Practice partition reassignment** between brokers

---

## Week 2: Kafka Connect operations

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1-2 | Kafka Connect architecture | [09_kafka_connect.md](../module_3_intermediate/09_kafka_connect.md) | 4 hours |
| 3 | Connector deployment | Hands-on lab | 3 hours |
| 4 | Connect monitoring | Hands-on lab | 2 hours |
| 5 | Schema Registry operations | [10_schema_registry.md](../module_3_intermediate/10_schema_registry.md) | 2 hours |

### Key administrator concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA CONNECT DEPLOYMENT MODES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STANDALONE MODE                         DISTRIBUTED MODE                   │
│  ─────────────────                       ────────────────                   │
│                                                                             │
│  ┌─────────────────┐                     ┌─────────────────┐               │
│  │ Single Worker   │                     │ Worker 1        │               │
│  │                 │                     │ ┌─────────────┐ │               │
│  │ Connector A     │                     │ │ Task A-1    │ │               │
│  │ Connector B     │                     │ │ Task B-1    │ │               │
│  └─────────────────┘                     │ └─────────────┘ │               │
│                                          └─────────────────┘               │
│  • Simple setup                          ┌─────────────────┐               │
│  • No fault tolerance                    │ Worker 2        │               │
│  • Development only                      │ ┌─────────────┐ │               │
│                                          │ │ Task A-2    │ │               │
│                                          │ │ Task B-2    │ │               │
│                                          │ └─────────────┘ │               │
│                                          └─────────────────┘               │
│                                                                             │
│                                          • Scalable                         │
│                                          • Fault tolerant                   │
│                                          • Production recommended           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 2)

1. **Deploy Kafka Connect** in distributed mode
2. **Install and configure** Debezium PostgreSQL connector
3. **Monitor connector status** via REST API
4. **Configure dead letter queues** for failed records
5. **Scale connectors** by adjusting task count

---

## Week 3: Security and monitoring

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1-2 | Kafka security | [15_security.md](../module_4_advanced/15_security.md) | 4 hours |
| 3-4 | Monitoring and observability | [16_monitoring.md](../module_4_advanced/16_monitoring.md) | 4 hours |
| 5 | Alerting setup | Hands-on lab | 3 hours |

### Key administrator concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA SECURITY LAYERS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: ENCRYPTION (TLS/SSL)                                              │
│  ─────────────────────────────                                              │
│  • Encrypt data in transit                                                  │
│  • Client-to-broker and broker-to-broker                                    │
│  • Generate certificates, configure keystores/truststores                   │
│                                                                             │
│  LAYER 2: AUTHENTICATION (SASL)                                             │
│  ──────────────────────────────                                             │
│  • SASL/PLAIN      - Username/password (use with TLS)                       │
│  • SASL/SCRAM      - Salted challenge-response (recommended)                │
│  • SASL/GSSAPI     - Kerberos (enterprise)                                  │
│  • SASL/OAUTHBEARER - OAuth 2.0 tokens                                      │
│                                                                             │
│  LAYER 3: AUTHORIZATION (ACLs)                                              │
│  ──────────────────────────────                                             │
│  • Control who can read/write topics                                        │
│  • Manage consumer group permissions                                        │
│  • Restrict admin operations                                                │
│                                                                             │
│  RECOMMENDED PRODUCTION SETUP:                                              │
│  • TLS encryption for all connections                                       │
│  • SASL/SCRAM for authentication                                            │
│  • ACLs with deny-by-default policy                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Critical metrics to monitor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ESSENTIAL KAFKA METRICS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  BROKER HEALTH                                                              │
│  ─────────────                                                              │
│  • UnderReplicatedPartitions    → Should be 0                               │
│  • OfflinePartitionsCount       → Should be 0                               │
│  • ActiveControllerCount        → Exactly 1 in cluster                      │
│  • LeaderElectionRateAndTimeMs  → Spikes indicate instability               │
│                                                                             │
│  THROUGHPUT                                                                 │
│  ──────────                                                                 │
│  • BytesInPerSec / BytesOutPerSec       → Network throughput                │
│  • MessagesInPerSec                     → Message rate                      │
│  • RequestsPerSec                       → Request load                      │
│                                                                             │
│  LATENCY                                                                    │
│  ───────                                                                    │
│  • RequestLatencyMs (Produce/Fetch)     → Request processing time           │
│  • TotalTimeMs                          → End-to-end request time           │
│                                                                             │
│  CONSUMER                                                                   │
│  ────────                                                                   │
│  • ConsumerLag                          → Messages behind (critical!)       │
│  • FetchRate                            → Consumer efficiency               │
│                                                                             │
│  RESOURCES                                                                  │
│  ─────────                                                                  │
│  • JVM Heap Usage                       → Target <70%                       │
│  • Disk Usage                           → Alert at 70%, critical at 85%     │
│  • Network I/O                          → Watch for saturation              │
│  • Open File Descriptors                → Increase ulimit if needed         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 3)

1. **Configure TLS encryption** for broker and clients
2. **Set up SASL/SCRAM authentication**
3. **Create ACLs** to restrict topic access
4. **Deploy Prometheus + Grafana** for monitoring
5. **Configure alerts** for critical metrics

---

## Week 4: Production operations

### Lessons

| Day | Topic | Module | Duration |
|-----|-------|--------|----------|
| 1-2 | Production operations | [17_production_ops.md](../module_4_advanced/17_production_ops.md) | 4 hours |
| 3 | Troubleshooting | [Troubleshooting Guide](../troubleshooting.md) | 3 hours |
| 4-5 | Production project | [Project 4](../module_4_advanced/project_4_production.md) | 6 hours |

### Key administrator concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION OPERATIONS CHECKLIST                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRE-DEPLOYMENT                                                             │
│  ──────────────                                                             │
│  ☐ Capacity planning completed (disk, network, memory)                      │
│  ☐ Replication factor = 3 for all topics                                    │
│  ☐ min.insync.replicas = 2 for critical topics                              │
│  ☐ TLS and SASL configured                                                  │
│  ☐ ACLs defined (deny-by-default)                                           │
│  ☐ Monitoring and alerting configured                                       │
│  ☐ Backup strategy defined                                                  │
│  ☐ Disaster recovery plan documented                                        │
│                                                                             │
│  ONGOING OPERATIONS                                                         │
│  ──────────────────                                                         │
│  ☐ Monitor consumer lag daily                                               │
│  ☐ Check under-replicated partitions                                        │
│  ☐ Review disk usage trends                                                 │
│  ☐ Verify backup integrity                                                  │
│  ☐ Test failover procedures quarterly                                       │
│  ☐ Keep Kafka version current (security patches)                            │
│                                                                             │
│  MAINTENANCE WINDOWS                                                        │
│  ────────────────────                                                       │
│  ☐ Rolling restart procedure documented                                     │
│  ☐ Partition reassignment plan ready                                        │
│  ☐ Upgrade runbook tested                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Common troubleshooting scenarios

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TROUBLESHOOTING DECISION TREE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SYMPTOM: High Consumer Lag                                                 │
│  ───────────────────────────                                                │
│                     │                                                       │
│           ┌────────┴────────┐                                               │
│           │Is consumer      │                                               │
│           │running?         │                                               │
│           └────────┬────────┘                                               │
│              No    │    Yes                                                 │
│              ↓     │     ↓                                                  │
│         Check      │   Is processing                                        │
│         logs       │   slow?                                                │
│                    │     │                                                  │
│              ┌─────┴─────┐                                                  │
│              │           │                                                  │
│             Yes         No                                                  │
│              ↓           ↓                                                  │
│         Optimize      Add more                                              │
│         processing    consumers                                             │
│         logic         (up to partition count)                               │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  SYMPTOM: Broker Not Available                                              │
│  ─────────────────────────────                                              │
│  1. Check if broker process is running                                      │
│  2. Check network connectivity (ping, telnet)                               │
│  3. Check disk space (Kafka stops if disk full)                             │
│  4. Check JVM heap (OOM can crash broker)                                   │
│  5. Review broker logs for errors                                           │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  SYMPTOM: Under-Replicated Partitions                                       │
│  ────────────────────────────────────                                       │
│  1. Check if all brokers are running                                        │
│  2. Check network between brokers                                           │
│  3. Check disk I/O (slow disk = slow replication)                           │
│  4. Check if replica.lag.time.max.ms is too low                             │
│  5. Look for broker GC pauses                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exercises (Week 4)

1. **Perform rolling restart** without downtime
2. **Simulate broker failure** and observe recovery
3. **Run partition reassignment** during maintenance
4. **Practice offset reset** for a consumer group
5. **Document runbook** for common operations

---

## Administrator best practices checklist

### Cluster configuration

- [ ] Use KRaft mode (ZooKeeper is deprecated)
- [ ] Deploy odd number of brokers (3, 5, 7) for quorum
- [ ] Set `broker.rack` for rack awareness
- [ ] Configure `unclean.leader.election.enable=false`
- [ ] Set appropriate `num.partitions` default
- [ ] Configure log retention based on requirements
- [ ] Tune JVM heap size (typically 6-8GB, max 32GB)

### Security

- [ ] Enable TLS for all client and inter-broker communication
- [ ] Use SASL/SCRAM or SASL/GSSAPI for authentication
- [ ] Implement deny-by-default ACL policy
- [ ] Rotate credentials and certificates regularly
- [ ] Audit access logs
- [ ] Keep Kafka updated (security patches)

### Monitoring

- [ ] Export JMX metrics to Prometheus
- [ ] Create Grafana dashboards for key metrics
- [ ] Set alerts for: under-replicated partitions, offline partitions, high lag
- [ ] Monitor disk usage with trending
- [ ] Track consumer lag per consumer group
- [ ] Log aggregation for all brokers

### Operations

- [ ] Document all topics and owners
- [ ] Establish change management process
- [ ] Test disaster recovery procedures
- [ ] Maintain runbooks for common tasks
- [ ] Plan capacity 3-6 months ahead
- [ ] Schedule regular maintenance windows

---

## Assessment

| Assessment | Passing Score | Description |
|------------|---------------|-------------|
| Module 1 Quiz | 80% (12/15) | Architecture fundamentals |
| Module 2 Quiz | 80% (12/15) | Core concepts |
| Module 3 Quiz | 80% (12/15) | Connect operations |
| Module 4 Quiz | 80% (12/15) | Security and monitoring |
| Production Project | Complete all tasks | Secure, monitored cluster |

---

## Resources

### Documentation
- [Kafka Operations](https://kafka.apache.org/documentation/#operations)
- [Confluent Platform Docs](https://docs.confluent.io/platform/current/)
- [Kafka KRaft Documentation](https://kafka.apache.org/documentation/#kraft)

### Tools
- [Kafka UI](https://github.com/provectus/kafka-ui)
- [AKHQ](https://akhq.io/)
- [Burrow (Consumer Lag)](https://github.com/linkedin/Burrow)
- [Cruise Control](https://github.com/linkedin/cruise-control)

### Books
- "Kafka: The Definitive Guide" (O'Reilly)
- "Kafka in Action" (Manning)

---

**Next:** [Developer Learning Path →](./developer-path.md)
