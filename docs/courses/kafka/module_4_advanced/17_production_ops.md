# Lesson 17: Production Operations

## Overview

Operating Kafka in production requires careful planning, systematic procedures, and deep understanding of cluster behavior. This lesson covers the critical aspects of running Kafka at scale: capacity planning, upgrade strategies, disaster recovery, and troubleshooting. You'll learn battle-tested operational practices that ensure reliability and minimize downtime.

## Learning Objectives

By the end of this lesson, you will be able to:

- Plan cluster capacity based on throughput and retention requirements
- Execute rolling upgrades with zero downtime
- Implement disaster recovery and backup strategies
- Troubleshoot common production issues systematically
- Create operational runbooks for routine procedures

## Table of Contents

1. [Capacity Planning](#1-capacity-planning)
2. [Cluster Sizing](#2-cluster-sizing)
3. [Rolling Upgrades](#3-rolling-upgrades)
4. [Disaster Recovery](#4-disaster-recovery)
5. [Backup and Restore](#5-backup-and-restore)
6. [Troubleshooting Guide](#6-troubleshooting-guide)
7. [Operational Runbooks](#7-operational-runbooks)
8. [Performance Tuning](#8-performance-tuning)
9. [Common Pitfalls](#9-common-pitfalls)
10. [Key Takeaways](#10-key-takeaways)

---

## 1. Capacity Planning

### Understanding Workload Characteristics

Before sizing a cluster, understand your workload:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKLOAD ASSESSMENT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  WRITE PATTERNS  │    │  READ PATTERNS   │                  │
│  ├──────────────────┤    ├──────────────────┤                  │
│  │ • Messages/sec   │    │ • Consumer count │                  │
│  │ • Message size   │    │ • Consumer groups│                  │
│  │ • Peak vs avg    │    │ • Replay needs   │                  │
│  │ • Burst capacity │    │ • Real-time lag  │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  RETENTION NEEDS │    │  AVAILABILITY    │                  │
│  ├──────────────────┤    ├──────────────────┤                  │
│  │ • Time-based     │    │ • RPO/RTO targets│                  │
│  │ • Size-based     │    │ • Replication    │                  │
│  │ • Compaction     │    │ • Multi-DC       │                  │
│  │ • Compliance     │    │ • Failover time  │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Capacity Worksheet

| Metric | Formula | Example |
|--------|---------|---------|
| **Write throughput** | messages/sec × avg_size | 100K × 1KB = 100 MB/s |
| **Read throughput** | write × consumer_groups | 100 MB/s × 5 = 500 MB/s |
| **Storage (raw)** | write × retention_seconds | 100 MB/s × 604800 = 60 TB |
| **Storage (with RF)** | raw_storage × replication_factor | 60 TB × 3 = 180 TB |
| **Network egress** | read + replication | 500 + 200 = 700 MB/s |

### Growth Planning

```python
#!/usr/bin/env python3
"""Kafka capacity planning calculator."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WorkloadProfile:
    """Defines expected Kafka workload characteristics."""

    messages_per_second: int
    average_message_bytes: int
    peak_multiplier: float = 2.0
    consumer_groups: int = 1
    retention_days: int = 7
    replication_factor: int = 3


@dataclass
class CapacityRequirements:
    """Calculated capacity requirements."""

    write_throughput_mb_s: float
    read_throughput_mb_s: float
    peak_throughput_mb_s: float
    storage_tb: float
    network_mb_s: float
    recommended_brokers: int
    partitions_per_topic: int


def calculate_capacity(workload: WorkloadProfile) -> CapacityRequirements:
    """Calculate cluster capacity requirements from workload profile."""
    # Throughput calculations
    write_mb_s = (workload.messages_per_second * workload.average_message_bytes) / (1024 * 1024)
    read_mb_s = write_mb_s * workload.consumer_groups
    peak_mb_s = write_mb_s * workload.peak_multiplier

    # Storage calculation
    seconds_per_day = 86400
    retention_seconds = workload.retention_days * seconds_per_day
    raw_storage_tb = (write_mb_s * retention_seconds) / (1024 * 1024)
    total_storage_tb = raw_storage_tb * workload.replication_factor

    # Network calculation (reads + replication)
    replication_traffic = write_mb_s * (workload.replication_factor - 1)
    network_mb_s = read_mb_s + replication_traffic + write_mb_s

    # Broker sizing (assume 100 MB/s per broker capacity)
    broker_capacity_mb_s = 100
    recommended_brokers = max(
        workload.replication_factor,  # Minimum for replication
        int(peak_mb_s / broker_capacity_mb_s) + 1,  # Based on throughput
        3  # Minimum for HA
    )

    # Partition calculation (assume 10 MB/s per partition)
    partition_throughput = 10
    partitions_per_topic = max(
        recommended_brokers,
        int(write_mb_s / partition_throughput) + 1
    )

    return CapacityRequirements(
        write_throughput_mb_s=write_mb_s,
        read_throughput_mb_s=read_mb_s,
        peak_throughput_mb_s=peak_mb_s,
        storage_tb=total_storage_tb,
        network_mb_s=network_mb_s,
        recommended_brokers=recommended_brokers,
        partitions_per_topic=partitions_per_topic
    )


def print_capacity_report(workload: WorkloadProfile, capacity: CapacityRequirements):
    """Print formatted capacity report."""
    print("=" * 60)
    print("KAFKA CAPACITY PLANNING REPORT")
    print("=" * 60)
    print("\nWorkload Profile:")
    print(f"  Messages/sec:      {workload.messages_per_second:,}")
    print(f"  Avg message size:  {workload.average_message_bytes:,} bytes")
    print(f"  Consumer groups:   {workload.consumer_groups}")
    print(f"  Retention:         {workload.retention_days} days")
    print(f"  Replication:       {workload.replication_factor}x")

    print("\nCalculated Requirements:")
    print(f"  Write throughput:  {capacity.write_throughput_mb_s:.1f} MB/s")
    print(f"  Read throughput:   {capacity.read_throughput_mb_s:.1f} MB/s")
    print(f"  Peak throughput:   {capacity.peak_throughput_mb_s:.1f} MB/s")
    print(f"  Total storage:     {capacity.storage_tb:.1f} TB")
    print(f"  Network egress:    {capacity.network_mb_s:.1f} MB/s")

    print("\nRecommendations:")
    print(f"  Brokers:           {capacity.recommended_brokers}")
    print(f"  Partitions/topic:  {capacity.partitions_per_topic}")
    print("=" * 60)


# Example usage
if __name__ == "__main__":
    workload = WorkloadProfile(
        messages_per_second=100000,
        average_message_bytes=1024,
        peak_multiplier=2.5,
        consumer_groups=5,
        retention_days=7,
        replication_factor=3
    )

    capacity = calculate_capacity(workload)
    print_capacity_report(workload, capacity)
```

---

## 2. Cluster Sizing

### Hardware Recommendations

| Component | Development | Production | High-Throughput |
|-----------|-------------|------------|-----------------|
| **CPU** | 4 cores | 16 cores | 32+ cores |
| **Memory** | 8 GB | 64 GB | 128+ GB |
| **Storage** | SSD 500 GB | NVMe 2 TB × 4 | NVMe 4 TB × 8 |
| **Network** | 1 Gbps | 10 Gbps | 25+ Gbps |
| **Brokers** | 1 | 3-5 | 10+ |

### Disk Sizing Formula

```
                        ┌─────────────────────────────────────┐
                        │      DISK SIZING CALCULATION        │
                        └─────────────────────────────────────┘

Total Disk = (Write Rate × Retention Period × RF × Safety Margin)
           ─────────────────────────────────────────────────────
                           Number of Brokers

Example:
- Write rate: 100 MB/s
- Retention: 7 days (604,800 seconds)
- RF: 3
- Safety margin: 1.25 (25% buffer)
- Brokers: 5

Total = (100 × 604,800 × 3 × 1.25) / 5
      = 45,360,000 MB / 5
      = 9,072,000 MB per broker
      ≈ 8.6 TB per broker (use 10 TB for safety)
```

### Memory Allocation

```properties
# Broker memory allocation strategy
# Total memory: 64 GB example

# JVM Heap: 6 GB (keep small, let OS cache handle data)
KAFKA_HEAP_OPTS="-Xms6g -Xmx6g"

# OS Page Cache: ~58 GB (remaining memory)
# This is managed by the OS, not configured directly

# Key insight: Kafka relies heavily on page cache
# More page cache = better read performance
# Rule: Keep heap small (4-8 GB), maximize page cache
```

### Network Bandwidth Planning

```
┌────────────────────────────────────────────────────────────────┐
│                  NETWORK TRAFFIC FLOW                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INGRESS                          EGRESS                       │
│  ───────                          ──────                       │
│                                                                │
│  Producer writes ──┐          ┌── Consumer reads               │
│  100 MB/s          │          │   500 MB/s (5 groups)          │
│                    │          │                                │
│                    ▼          ▼                                │
│              ┌─────────────────────┐                           │
│              │      BROKER         │                           │
│              │                     │                           │
│              │  ┌───────────────┐  │                           │
│              │  │  Page Cache   │  │                           │
│              │  └───────────────┘  │                           │
│              └─────────────────────┘                           │
│                    │          │                                │
│                    ▼          ▼                                │
│  Follower fetch ──┘          └── Replication                   │
│  200 MB/s                        200 MB/s                      │
│  (2 followers)                   (to 2 followers)              │
│                                                                │
│  TOTAL INGRESS: 300 MB/s    TOTAL EGRESS: 700 MB/s            │
│                                                                │
│  Required NIC: 10 Gbps (1.25 GB/s) provides headroom          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Rolling Upgrades

### Upgrade Strategy Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   ROLLING UPGRADE PROCESS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: Preparation                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Review release notes and breaking changes             │   │
│  │ • Test upgrade in staging environment                   │   │
│  │ • Backup configurations and metadata                    │   │
│  │ • Set inter.broker.protocol.version to current          │   │
│  │ • Disable auto-creation of topics                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Phase 2: Rolling Restart (per broker)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Verify cluster health (ISR complete)                 │   │
│  │ 2. Stop broker gracefully                               │   │
│  │ 3. Upgrade software                                     │   │
│  │ 4. Start broker                                         │   │
│  │ 5. Wait for ISR recovery                                │   │
│  │ 6. Verify broker health                                 │   │
│  │ 7. Repeat for next broker                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  Phase 3: Protocol Upgrade                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Update inter.broker.protocol.version                  │   │
│  │ • Another rolling restart                               │   │
│  │ • Verify new features working                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pre-Upgrade Checklist

```bash
#!/bin/bash
# pre_upgrade_check.sh - Verify cluster readiness for upgrade

set -euo pipefail

BOOTSTRAP_SERVERS="${1:-localhost:9092}"

echo "=== Kafka Pre-Upgrade Checklist ==="
echo ""

# Check 1: Cluster health
echo "1. Checking cluster health..."
UNDER_REPLICATED=$(kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --describe --under-replicated-partitions 2>/dev/null | wc -l)

if [ "$UNDER_REPLICATED" -gt 0 ]; then
    echo "   [FAIL] Found under-replicated partitions"
    kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
        --describe --under-replicated-partitions
    exit 1
else
    echo "   [OK] No under-replicated partitions"
fi

# Check 2: Offline partitions
echo "2. Checking for offline partitions..."
OFFLINE=$(kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --describe --unavailable-partitions 2>/dev/null | wc -l)

if [ "$OFFLINE" -gt 0 ]; then
    echo "   [FAIL] Found offline partitions"
    exit 1
else
    echo "   [OK] No offline partitions"
fi

# Check 3: Active controller
echo "3. Checking controller status..."
CONTROLLER=$(kafka-metadata.sh --snapshot /var/kafka-logs/__cluster_metadata-0/00000000000000000000.log \
    --command "controller" 2>/dev/null || echo "Check manually for KRaft")
echo "   [INFO] Controller: $CONTROLLER"

# Check 4: Consumer lag
echo "4. Checking consumer lag..."
kafka-consumer-groups.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --all-groups --describe 2>/dev/null | grep -E "^[a-zA-Z]" | head -20

# Check 5: Disk space
echo "5. Checking disk space..."
df -h /var/kafka-logs 2>/dev/null || df -h .

# Check 6: Current version
echo "6. Current Kafka version..."
kafka-broker-api-versions.sh --bootstrap-server "$BOOTSTRAP_SERVERS" 2>/dev/null | head -5

echo ""
echo "=== Pre-upgrade checks complete ==="
```

### Rolling Upgrade Script

```bash
#!/bin/bash
# rolling_upgrade.sh - Perform rolling upgrade of Kafka broker

set -euo pipefail

BROKER_ID="${1:?Usage: $0 <broker_id>}"
KAFKA_HOME="${KAFKA_HOME:-/opt/kafka}"
NEW_VERSION="${2:?Usage: $0 <broker_id> <new_version>}"

echo "=== Rolling Upgrade for Broker $BROKER_ID ==="

# Step 1: Verify ISR health before stopping
echo "Step 1: Verifying ISR health..."
UNDER_REPLICATED=$(kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --under-replicated-partitions | wc -l)

if [ "$UNDER_REPLICATED" -gt 0 ]; then
    echo "ERROR: Under-replicated partitions exist. Fix before upgrading."
    exit 1
fi

# Step 2: Gracefully stop the broker
echo "Step 2: Stopping broker $BROKER_ID..."
kafka-server-stop.sh

# Wait for clean shutdown
sleep 30

# Step 3: Verify broker is stopped
if pgrep -f "kafka.Kafka" > /dev/null; then
    echo "ERROR: Broker still running"
    exit 1
fi

# Step 4: Backup current installation
echo "Step 3: Backing up current installation..."
BACKUP_DIR="/opt/kafka-backup-$(date +%Y%m%d-%H%M%S)"
cp -r "$KAFKA_HOME" "$BACKUP_DIR"
echo "Backup created at $BACKUP_DIR"

# Step 5: Upgrade software
echo "Step 4: Upgrading to version $NEW_VERSION..."
# This depends on your deployment method
# Example for tarball installation:
# tar -xzf kafka_$NEW_VERSION.tgz -C /opt/
# ln -sfn /opt/kafka_$NEW_VERSION $KAFKA_HOME

# Step 6: Start broker
echo "Step 5: Starting broker..."
kafka-server-start.sh -daemon "$KAFKA_HOME/config/server.properties"

# Step 7: Wait for broker to rejoin cluster
echo "Step 6: Waiting for broker to rejoin cluster..."
sleep 60

# Step 8: Verify ISR recovery
echo "Step 7: Verifying ISR recovery..."
MAX_WAIT=300
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    UNDER_REPLICATED=$(kafka-topics.sh --bootstrap-server localhost:9092 \
        --describe --under-replicated-partitions | wc -l)

    if [ "$UNDER_REPLICATED" -eq 0 ]; then
        echo "ISR fully recovered"
        break
    fi

    echo "Waiting for ISR recovery... ($UNDER_REPLICATED partitions remaining)"
    sleep 10
    WAITED=$((WAITED + 10))
done

if [ "$UNDER_REPLICATED" -gt 0 ]; then
    echo "WARNING: ISR not fully recovered after ${MAX_WAIT}s"
    echo "Manual investigation required"
    exit 1
fi

echo "=== Broker $BROKER_ID upgrade complete ==="
```

### Version Compatibility Matrix

| From Version | To Version | Protocol Version | Notes |
|--------------|------------|------------------|-------|
| 3.5.x | 3.6.x | 3.5 → 3.6 | Minor upgrade, direct |
| 3.4.x | 3.6.x | 3.4 → 3.5 → 3.6 | Step through versions |
| 2.8.x | 3.6.x | Complex | Plan ZK → KRaft migration |

---

## 4. Disaster Recovery

### DR Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│              DISASTER RECOVERY PATTERNS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Pattern 1: Active-Passive (MirrorMaker 2)                      │
│  ────────────────────────────────────────                       │
│                                                                 │
│    Primary DC                    DR DC                          │
│   ┌─────────────┐              ┌─────────────┐                 │
│   │   Kafka     │    MM2       │   Kafka     │                 │
│   │  Cluster    │ ─────────►   │  Cluster    │                 │
│   │  (Active)   │  replicate   │  (Standby)  │                 │
│   └─────────────┘              └─────────────┘                 │
│                                                                 │
│   RPO: Minutes (replication lag)                                │
│   RTO: Minutes-Hours (consumer offset sync)                     │
│                                                                 │
│                                                                 │
│  Pattern 2: Active-Active (Bidirectional)                       │
│  ───────────────────────────────────────                        │
│                                                                 │
│    DC-West                        DC-East                       │
│   ┌─────────────┐              ┌─────────────┐                 │
│   │   Kafka     │ ◄──────────► │   Kafka     │                 │
│   │  Cluster    │    MM2       │  Cluster    │                 │
│   │  (Active)   │  (bidir)     │  (Active)   │                 │
│   └─────────────┘              └─────────────┘                 │
│        ▲                              ▲                         │
│        │                              │                         │
│   Local Producers              Local Producers                  │
│                                                                 │
│   RPO: Near-zero (async replication)                            │
│   RTO: Seconds (automatic failover)                             │
│                                                                 │
│                                                                 │
│  Pattern 3: Stretch Cluster                                     │
│  ─────────────────────────                                      │
│                                                                 │
│    DC-1          DC-2          DC-3                             │
│   ┌─────┐       ┌─────┐       ┌─────┐                          │
│   │ B1  │       │ B2  │       │ B3  │                          │
│   │ B4  │       │ B5  │       │ B6  │                          │
│   └─────┘       └─────┘       └─────┘                          │
│       └────────────┴────────────┘                               │
│              Single Cluster                                     │
│                                                                 │
│   RPO: Zero (synchronous replication)                           │
│   RTO: Automatic (built-in failover)                            │
│   Note: Requires low-latency links between DCs                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### MirrorMaker 2 Configuration

```properties
# mm2.properties - MirrorMaker 2 configuration

# Cluster aliases
clusters = primary, dr

# Primary cluster connection
primary.bootstrap.servers = primary-kafka-1:9092,primary-kafka-2:9092,primary-kafka-3:9092
primary.security.protocol = SASL_SSL
primary.sasl.mechanism = SCRAM-SHA-512
primary.sasl.jaas.config = org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="mm2-user" password="secret";

# DR cluster connection
dr.bootstrap.servers = dr-kafka-1:9092,dr-kafka-2:9092,dr-kafka-3:9092
dr.security.protocol = SASL_SSL
dr.sasl.mechanism = SCRAM-SHA-512
dr.sasl.jaas.config = org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="mm2-user" password="secret";

# Replication configuration
primary->dr.enabled = true
primary->dr.topics = .*
primary->dr.topics.exclude = .*[-.]internal, .*\.replica, __.*
primary->dr.groups = .*
primary->dr.emit.heartbeats.enabled = true
primary->dr.emit.checkpoints.enabled = true
primary->dr.sync.group.offsets.enabled = true

# Replication settings
replication.factor = 3
refresh.topics.interval.seconds = 30
refresh.groups.interval.seconds = 30
sync.group.offsets.interval.seconds = 5

# Exactly-once support (Kafka 3.5+)
exactly.once.source.support = enabled
```

### Failover Procedure

```bash
#!/bin/bash
# failover_to_dr.sh - Execute failover to DR cluster

set -euo pipefail

echo "=== Initiating Failover to DR Cluster ==="
echo "WARNING: This will redirect all traffic to DR cluster"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Failover cancelled"
    exit 1
fi

# Step 1: Stop producers pointing to primary
echo "Step 1: Stopping producers..."
# This depends on your deployment - could be:
# - Updating DNS records
# - Modifying load balancer configuration
# - Restarting producer applications with new bootstrap servers

# Step 2: Wait for MirrorMaker to catch up
echo "Step 2: Waiting for replication to catch up..."
# Check MM2 lag metrics
# kafka-consumer-groups.sh --bootstrap-server dr-kafka:9092 \
#     --describe --group mm2-MirrorSourceConnector

# Step 3: Stop MirrorMaker (to prevent circular replication if bidirectional)
echo "Step 3: Stopping MirrorMaker..."
# systemctl stop kafka-mirrormaker2

# Step 4: Update consumer offsets
echo "Step 4: Syncing consumer group offsets..."
# MirrorMaker 2 creates translated offsets automatically
# Consumers need to be configured to use: auto.offset.reset=earliest
# Or manually set offsets using:
# kafka-consumer-groups.sh --bootstrap-server dr-kafka:9092 \
#     --group my-group --topic my-topic --reset-offsets \
#     --to-latest --execute

# Step 5: Update DNS/Load Balancer to point to DR
echo "Step 5: Updating DNS to point to DR cluster..."
# Update DNS CNAME or A records
# aws route53 change-resource-record-sets ...

# Step 6: Start consumers on DR
echo "Step 6: Starting consumers on DR cluster..."
# kubectl scale deployment kafka-consumer --replicas=3

# Step 7: Verify traffic flow
echo "Step 7: Verifying traffic..."
sleep 30

# Check consumer lag on DR cluster
kafka-consumer-groups.sh --bootstrap-server dr-kafka:9092 \
    --all-groups --describe

echo "=== Failover complete ==="
echo "Monitor consumer lag and application health"
```

---

## 5. Backup and Restore

### What to Back Up

```
┌─────────────────────────────────────────────────────────────────┐
│                    KAFKA BACKUP STRATEGY                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MUST BACKUP (Critical)                                         │
│  ──────────────────────                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Cluster metadata (KRaft: __cluster_metadata topic)    │   │
│  │ • Topic configurations (can recreate from describe)     │   │
│  │ • ACL definitions (security)                            │   │
│  │ • Consumer group offsets (__consumer_offsets)           │   │
│  │ • Schema Registry schemas                               │   │
│  │ • Connector configurations (Connect)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  SHOULD BACKUP (For faster recovery)                            │
│  ──────────────────────────────────                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Topic data (via MirrorMaker 2)                        │   │
│  │ • Broker configurations (server.properties)             │   │
│  │ • Client configurations                                 │   │
│  │ • Monitoring dashboards and alerts                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  TYPICALLY NOT BACKED UP (Recreatable)                          │
│  ────────────────────────────────────                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Log segments (use replication instead)                │   │
│  │ • Index files (rebuilt on startup)                      │   │
│  │ • Temporary state                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration Backup Script

```python
#!/usr/bin/env python3
"""Backup Kafka cluster configurations."""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class TopicConfig:
    """Topic configuration."""

    name: str
    partitions: int
    replication_factor: int
    configs: dict


@dataclass
class ConsumerGroupConfig:
    """Consumer group configuration."""

    group_id: str
    offsets: dict  # topic-partition: offset


@dataclass
class ClusterBackup:
    """Complete cluster backup."""

    timestamp: str
    cluster_id: str
    topics: list
    consumer_groups: list
    acls: list


def run_kafka_command(cmd: list) -> str:
    """Run kafka CLI command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {result.stderr}")
    return result.stdout


def backup_topics(bootstrap_servers: str) -> list:
    """Backup all topic configurations."""
    topics = []

    # List all topics
    output = run_kafka_command([
        "kafka-topics.sh",
        "--bootstrap-server", bootstrap_servers,
        "--list"
    ])

    for topic_name in output.strip().split("\n"):
        if not topic_name or topic_name.startswith("_"):
            continue

        # Describe topic
        describe_output = run_kafka_command([
            "kafka-topics.sh",
            "--bootstrap-server", bootstrap_servers,
            "--describe",
            "--topic", topic_name
        ])

        # Parse topic details
        lines = describe_output.strip().split("\n")
        topic_line = lines[0]

        # Extract partition count and replication factor
        partitions = int(topic_line.split("PartitionCount:")[1].split()[0])
        rf = int(topic_line.split("ReplicationFactor:")[1].split()[0])

        # Get topic configs
        config_output = run_kafka_command([
            "kafka-configs.sh",
            "--bootstrap-server", bootstrap_servers,
            "--entity-type", "topics",
            "--entity-name", topic_name,
            "--describe"
        ])

        configs = {}
        for line in config_output.split("\n"):
            if "=" in line and "Configs for" not in line:
                for config in line.split():
                    if "=" in config:
                        key, value = config.split("=", 1)
                        configs[key] = value

        topics.append(TopicConfig(
            name=topic_name,
            partitions=partitions,
            replication_factor=rf,
            configs=configs
        ))

    return topics


def backup_consumer_groups(bootstrap_servers: str) -> list:
    """Backup consumer group offsets."""
    groups = []

    # List all groups
    output = run_kafka_command([
        "kafka-consumer-groups.sh",
        "--bootstrap-server", bootstrap_servers,
        "--list"
    ])

    for group_id in output.strip().split("\n"):
        if not group_id:
            continue

        # Describe group offsets
        describe_output = run_kafka_command([
            "kafka-consumer-groups.sh",
            "--bootstrap-server", bootstrap_servers,
            "--describe",
            "--group", group_id
        ])

        offsets = {}
        for line in describe_output.split("\n"):
            parts = line.split()
            if len(parts) >= 4 and parts[0] != "GROUP":
                topic = parts[1]
                partition = parts[2]
                current_offset = parts[3]
                if current_offset != "-":
                    offsets[f"{topic}-{partition}"] = int(current_offset)

        if offsets:
            groups.append(ConsumerGroupConfig(
                group_id=group_id,
                offsets=offsets
            ))

    return groups


def backup_acls(bootstrap_servers: str) -> list:
    """Backup ACL definitions."""
    output = run_kafka_command([
        "kafka-acls.sh",
        "--bootstrap-server", bootstrap_servers,
        "--list"
    ])
    return output.strip().split("\n")


def create_backup(bootstrap_servers: str, output_dir: str) -> str:
    """Create complete cluster backup."""
    print(f"Creating backup from {bootstrap_servers}...")

    backup = ClusterBackup(
        timestamp=datetime.now().isoformat(),
        cluster_id=bootstrap_servers,
        topics=[asdict(t) for t in backup_topics(bootstrap_servers)],
        consumer_groups=[asdict(g) for g in backup_consumer_groups(bootstrap_servers)],
        acls=backup_acls(bootstrap_servers)
    )

    # Save backup
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"kafka-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    filepath = output_path / filename

    with open(filepath, "w") as f:
        json.dump(asdict(backup), f, indent=2)

    print(f"Backup saved to {filepath}")
    return str(filepath)


if __name__ == "__main__":
    import sys
    bootstrap = sys.argv[1] if len(sys.argv) > 1 else "localhost:9092"
    output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/kafka-backups"
    create_backup(bootstrap, output)
```

### Restore Script

```bash
#!/bin/bash
# restore_topics.sh - Restore topics from backup

set -euo pipefail

BACKUP_FILE="${1:?Usage: $0 <backup_file.json> <bootstrap_servers>}"
BOOTSTRAP_SERVERS="${2:-localhost:9092}"

echo "=== Restoring from $BACKUP_FILE ==="

# Parse and create topics
python3 << EOF
import json
import subprocess

with open("$BACKUP_FILE") as f:
    backup = json.load(f)

for topic in backup["topics"]:
    name = topic["name"]
    partitions = topic["partitions"]
    rf = topic["replication_factor"]
    configs = topic["configs"]

    # Build config string
    config_args = []
    for k, v in configs.items():
        config_args.extend(["--config", f"{k}={v}"])

    cmd = [
        "kafka-topics.sh",
        "--bootstrap-server", "$BOOTSTRAP_SERVERS",
        "--create",
        "--topic", name,
        "--partitions", str(partitions),
        "--replication-factor", str(rf)
    ] + config_args

    print(f"Creating topic: {name}")
    try:
        subprocess.run(cmd, check=True)
        print(f"  Created successfully")
    except subprocess.CalledProcessError:
        print(f"  Already exists or failed")
EOF

echo "=== Restore complete ==="
```

---

## 6. Troubleshooting Guide

### Common Issues and Solutions

```
┌─────────────────────────────────────────────────────────────────┐
│              TROUBLESHOOTING DECISION TREE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    Problem Reported                             │
│                          │                                      │
│            ┌─────────────┼─────────────┐                       │
│            ▼             ▼             ▼                        │
│     High Latency    Data Loss    Consumer Lag                   │
│            │             │             │                        │
│            ▼             ▼             ▼                        │
│    ┌───────────┐  ┌───────────┐  ┌───────────┐                 │
│    │Check:     │  │Check:     │  │Check:     │                 │
│    │• Network  │  │• ISR list │  │• Throughput│                 │
│    │• Disk I/O │  │• min.isr  │  │• Partitions│                 │
│    │• CPU      │  │• acks     │  │• Consumer  │                 │
│    │• GC pauses│  │• RF       │  │  threads   │                 │
│    └───────────┘  └───────────┘  └───────────┘                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Issue: Under-Replicated Partitions

**Symptoms:**
- `UnderReplicatedPartitions` metric > 0
- Alerts firing
- Potential data loss risk

**Diagnosis:**

```bash
# Check under-replicated partitions
kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --under-replicated-partitions

# Check broker logs for ISR shrink events
grep -i "shrinking ISR" /var/log/kafka/server.log

# Check disk space on brokers
df -h /var/kafka-logs

# Check network connectivity between brokers
for broker in kafka-1 kafka-2 kafka-3; do
    echo "Checking $broker..."
    nc -zv $broker 9092
done
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Disk full | Add storage, increase retention, delete old topics |
| Slow disk I/O | Move to SSDs, reduce partitions per disk |
| Network issues | Check NIC errors, network saturation |
| Broker overload | Add brokers, rebalance partitions |
| replica.lag.time.max.ms too low | Increase value (default 30s) |

### Issue: High Consumer Lag

**Symptoms:**
- Consumer lag growing continuously
- Processing delays
- Potential data backlog

**Diagnosis:**

```bash
# Check consumer lag for all groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --all-groups --describe | sort -t $'\t' -k5 -nr | head -20

# Check specific consumer group
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --group my-consumer-group --describe

# Check topic throughput
kafka-run-class.sh kafka.tools.JmxTool \
    --object-name 'kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec' \
    --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

**Solutions:**

```python
# Consumer optimization checklist

# 1. Increase consumer parallelism
# Add more consumer instances (up to partition count)
# Each partition can only be consumed by one consumer in a group

# 2. Optimize consumer configuration
consumer_config = {
    # Increase batch size for higher throughput
    'fetch.min.bytes': 1048576,  # 1MB minimum fetch
    'fetch.max.wait.ms': 500,    # Wait up to 500ms for batch

    # Increase max poll records if processing is fast
    'max.poll.records': 1000,    # Process up to 1000 records per poll

    # Increase session timeout if processing is slow
    'session.timeout.ms': 45000,
    'max.poll.interval.ms': 300000,  # 5 minutes

    # Enable parallel processing within consumer
    # (application-level change)
}

# 3. Scale consumers
# Add more consumer instances
# kubectl scale deployment my-consumer --replicas=10

# 4. Increase partitions (if consumers < partitions)
# kafka-topics.sh --bootstrap-server localhost:9092 \
#     --alter --topic my-topic --partitions 20
```

### Issue: Producer Timeouts

**Symptoms:**
- `TimeoutException` in producer logs
- Messages not acknowledged
- High latency

**Diagnosis:**

```bash
# Check broker responsiveness
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Check topic health
kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --topic my-topic

# Check request queue
kafka-run-class.sh kafka.tools.JmxTool \
    --object-name 'kafka.network:type=RequestChannel,name=RequestQueueSize' \
    --jmx-url service:jmx:rmi:///jndi/rmi://localhost:9999/jmxrmi
```

**Solutions:**

```properties
# Producer configuration tuning

# Increase timeout for slow networks
request.timeout.ms=60000
delivery.timeout.ms=180000

# Tune batching for throughput
batch.size=65536
linger.ms=10

# Reduce load with compression
compression.type=lz4

# Tune for reliability vs speed
acks=1  # or acks=all for durability
retries=3

# Buffer tuning
buffer.memory=67108864  # 64MB
max.block.ms=120000
```

### Issue: Out of Memory (OOM)

**Symptoms:**
- Broker crashes with OOM
- GC pauses in logs
- Slow response times

**Diagnosis:**

```bash
# Check GC logs
grep -E "GC|pause" /var/log/kafka/gc.log | tail -50

# Check heap usage
jstat -gcutil $(pgrep -f kafka.Kafka) 5000

# Check memory-mapped files
ls -la /var/kafka-logs/**/00000*.log | wc -l

# Check page cache
free -h
```

**Solutions:**

```bash
# JVM tuning for Kafka

# Keep heap small (4-8 GB), let OS handle caching
export KAFKA_HEAP_OPTS="-Xms6g -Xmx6g"

# Use G1GC for better latency
export KAFKA_JVM_PERFORMANCE_OPTS="-XX:+UseG1GC \
    -XX:MaxGCPauseMillis=20 \
    -XX:InitiatingHeapOccupancyPercent=35 \
    -XX:+ExplicitGCInvokesConcurrent"

# Reduce number of partitions per broker
# Each partition uses memory for indexes and buffers

# Limit log segment count
log.retention.hours=168
log.segment.bytes=1073741824
```

---

## 7. Operational Runbooks

### Runbook: Add New Broker

```markdown
# Runbook: Adding a New Broker to Cluster

## Prerequisites
- [ ] Hardware provisioned and accessible
- [ ] Network connectivity verified
- [ ] Kafka software installed
- [ ] Certificates/credentials prepared

## Procedure

### Step 1: Configure New Broker
1. Copy server.properties from existing broker
2. Update broker.id to unique value
3. Update listeners and advertised.listeners
4. Verify log.dirs points to correct storage

### Step 2: Start Broker
```bash
kafka-server-start.sh -daemon /etc/kafka/server.properties
```

### Step 3: Verify Broker Joined
```bash
kafka-metadata.sh --snapshot /path/to/__cluster_metadata-0/00000000000000000000.log \
    --command "broker-list"
```

### Step 4: Rebalance Partitions
```bash
# Generate reassignment plan
kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --topics-to-move-json-file topics.json \
    --broker-list "1,2,3,4" \
    --generate

# Execute reassignment
kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file reassignment.json \
    --execute

# Verify completion
kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
    --reassignment-json-file reassignment.json \
    --verify
```

### Step 5: Monitor
- Check UnderReplicatedPartitions metric
- Verify even partition distribution
- Monitor disk and network utilization

## Rollback
1. Stop new broker
2. Remove broker from cluster
3. Let existing brokers handle partitions
```

### Runbook: Emergency Partition Recovery

```markdown
# Runbook: Emergency Partition Recovery

## Symptoms
- OfflinePartitions > 0
- Topic not readable/writable
- Alerts firing for data unavailability

## Immediate Actions

### Step 1: Identify Affected Partitions
```bash
kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --unavailable-partitions
```

### Step 2: Check Broker Status
```bash
# List all brokers
kafka-metadata.sh --snapshot /path/to/__cluster_metadata-0/00000000000000000000.log \
    --command "broker-list"

# Check if offline broker can be restarted
ssh kafka-broker-X "systemctl status kafka"
```

### Step 3: Decision Point

IF broker can be recovered:
- Restart broker
- Wait for ISR to recover
- Verify partitions online

IF broker cannot be recovered:
```bash
# WARNING: This may cause data loss
# Trigger leader election with unclean.leader.election.enable

# Option 1: Enable for specific topic
kafka-configs.sh --bootstrap-server localhost:9092 \
    --entity-type topics --entity-name my-topic \
    --alter --add-config unclean.leader.election.enable=true

# Option 2: Trigger preferred leader election
kafka-leader-election.sh --bootstrap-server localhost:9092 \
    --election-type UNCLEAN \
    --topic my-topic --partition 0
```

### Step 4: Verify Recovery
```bash
# Confirm partitions are online
kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --topic my-topic

# Check for data loss
# Compare high watermark before and after
```

## Post-Incident
1. Root cause analysis
2. Update monitoring/alerting
3. Review replication factor
4. Document in incident log
```

---

## 8. Performance Tuning

### Broker Tuning Reference

```properties
# server.properties - Production tuning

############################# Server Basics #############################
broker.id=1
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

############################# Log Basics #############################
log.dirs=/data/kafka-logs
num.partitions=12
num.recovery.threads.per.data.dir=2
default.replication.factor=3
min.insync.replicas=2

############################# Internal Topic Settings #############################
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

############################# Log Retention Policy #############################
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000
log.cleaner.enable=true

############################# Replication #############################
replica.fetch.max.bytes=10485760
replica.fetch.wait.max.ms=500
replica.lag.time.max.ms=30000

############################# Group Coordinator Settings #############################
group.initial.rebalance.delay.ms=3000

############################# Quotas #############################
# Limit producers to 50 MB/s per client
# quota.producer.default=52428800
# Limit consumers to 100 MB/s per client
# quota.consumer.default=104857600
```

### Performance Benchmarking

```bash
#!/bin/bash
# benchmark_cluster.sh - Benchmark Kafka cluster performance

BOOTSTRAP_SERVERS="${1:-localhost:9092}"
TOPIC="benchmark-test"
NUM_RECORDS=1000000
RECORD_SIZE=1024
THROUGHPUT=-1  # Unlimited

echo "=== Kafka Performance Benchmark ==="
echo "Bootstrap: $BOOTSTRAP_SERVERS"
echo "Records: $NUM_RECORDS"
echo "Record size: $RECORD_SIZE bytes"

# Create test topic
echo ""
echo "Creating test topic..."
kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --create --topic "$TOPIC" \
    --partitions 12 --replication-factor 3 \
    --config min.insync.replicas=2 \
    2>/dev/null || true

# Producer benchmark
echo ""
echo "=== Producer Benchmark ==="
kafka-producer-perf-test.sh \
    --topic "$TOPIC" \
    --num-records "$NUM_RECORDS" \
    --record-size "$RECORD_SIZE" \
    --throughput "$THROUGHPUT" \
    --producer-props bootstrap.servers="$BOOTSTRAP_SERVERS" \
        acks=all \
        compression.type=lz4 \
        batch.size=65536 \
        linger.ms=10

# Consumer benchmark
echo ""
echo "=== Consumer Benchmark ==="
kafka-consumer-perf-test.sh \
    --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --topic "$TOPIC" \
    --messages "$NUM_RECORDS" \
    --threads 1

# End-to-end latency
echo ""
echo "=== End-to-End Latency ==="
kafka-run-class.sh kafka.tools.EndToEndLatency \
    "$BOOTSTRAP_SERVERS" "$TOPIC" 10000 all 1024

# Cleanup
echo ""
echo "Cleaning up..."
kafka-topics.sh --bootstrap-server "$BOOTSTRAP_SERVERS" \
    --delete --topic "$TOPIC" 2>/dev/null || true

echo ""
echo "=== Benchmark Complete ==="
```

---

## 9. Common Pitfalls

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Too many partitions** | Memory overhead, slow recovery | Use fewer, larger partitions |
| **RF=1 in production** | Single point of failure | Always use RF >= 3 |
| **acks=0** | Data loss risk | Use acks=all for durability |
| **No monitoring** | Blind to issues | Implement comprehensive monitoring |
| **Manual topic creation** | Configuration drift | Use GitOps, automate |
| **Huge messages** | Performance degradation | Keep messages < 1MB |
| **No quotas** | Noisy neighbor problems | Implement client quotas |
| **Direct log access** | Data corruption risk | Use Kafka APIs only |

### Production Checklist

```markdown
## Kafka Production Readiness Checklist

### Infrastructure
- [ ] Minimum 3 brokers for HA
- [ ] SSDs for log storage
- [ ] 10 Gbps network
- [ ] Separate disks for logs vs OS
- [ ] Proper JVM sizing (heap + GC tuning)

### Configuration
- [ ] Replication factor >= 3
- [ ] min.insync.replicas >= 2
- [ ] unclean.leader.election.enable = false
- [ ] auto.create.topics.enable = false
- [ ] log.retention configured appropriately

### Security
- [ ] TLS encryption enabled
- [ ] Authentication configured (SASL)
- [ ] ACLs defined for all principals
- [ ] Secrets management in place

### Monitoring
- [ ] JMX metrics exported
- [ ] Prometheus/Grafana dashboards
- [ ] Alerts for critical metrics
- [ ] Consumer lag monitoring
- [ ] Log aggregation

### Operations
- [ ] Backup procedures documented
- [ ] DR plan tested
- [ ] Runbooks created
- [ ] On-call rotation defined
- [ ] Capacity planning reviewed

### Documentation
- [ ] Architecture documented
- [ ] Topic inventory maintained
- [ ] Client inventory maintained
- [ ] Change management process
```

---

## 10. Key Takeaways

### Summary

| Topic | Key Points |
|-------|------------|
| **Capacity Planning** | Calculate based on throughput, retention, and replication |
| **Cluster Sizing** | Small heap, maximize page cache, use SSDs |
| **Rolling Upgrades** | Test in staging, maintain ISR, upgrade protocol last |
| **Disaster Recovery** | MirrorMaker 2 for replication, test failover regularly |
| **Backup** | Back up configs and metadata, use replication for data |
| **Troubleshooting** | Systematic approach, check metrics first |
| **Runbooks** | Document procedures, automate where possible |
| **Performance** | Benchmark regularly, tune based on workload |

### Production Operations Principles

1. **Measure Everything**: Comprehensive monitoring is essential
2. **Automate Repetitive Tasks**: Reduce human error
3. **Test Disaster Recovery**: Untested backups aren't backups
4. **Document Procedures**: Runbooks save time in emergencies
5. **Plan for Growth**: Capacity planning prevents surprises
6. **Practice Upgrades**: Rolling upgrades need rehearsal
7. **Security First**: Production clusters must be secured
8. **Learn from Incidents**: Post-mortems improve operations

---

## Practice Exercise

### Exercise: Capacity Planning Scenario

**Scenario:** Your company is launching a new event streaming platform with these requirements:
- 50,000 events per second at peak
- Average event size: 2 KB
- 5 consumer applications
- 14-day retention
- 99.99% availability SLA

**Tasks:**

1. Calculate required storage capacity
2. Determine broker count and specifications
3. Design the DR strategy
4. Create a monitoring plan
5. Document the upgrade procedure

<details>
<summary>Solution</summary>

**1. Storage Calculation:**
```
Write rate: 50,000 × 2 KB = 100 MB/s
Daily storage: 100 MB/s × 86,400 = 8.64 TB/day
14-day retention: 8.64 × 14 = 121 TB raw
With RF=3: 121 × 3 = 363 TB total
Per broker (6 brokers): ~60 TB each
Recommendation: 8 × 10 TB NVMe per broker
```

**2. Broker Specifications:**
```
- 6 brokers minimum (N+2 for maintenance)
- 32 cores per broker
- 128 GB RAM (8 GB heap, rest for page cache)
- 8 × 10 TB NVMe drives
- 25 Gbps networking
```

**3. DR Strategy:**
```
- Active-passive with MirrorMaker 2
- Secondary cluster in different region
- RPO: 1 minute (MM2 lag)
- RTO: 15 minutes (manual failover)
- Daily DR drills
```

**4. Monitoring Plan:**
```
Critical alerts:
- UnderReplicatedPartitions > 0
- OfflinePartitions > 0
- Consumer lag > 100,000
- Disk usage > 80%
- Request latency p99 > 100ms
```

**5. Upgrade Procedure:**
```
1. Test in staging (2 weeks before)
2. Schedule maintenance window
3. Drain broker 1
4. Upgrade broker 1
5. Wait for ISR recovery
6. Repeat for each broker
7. Upgrade protocol version
8. Verify all features
```

</details>

---

## Navigation

- **Previous:** [Lesson 16: Monitoring and Observability](./16_monitoring.md)
- **Next:** [Module 4 Quiz](./quiz_module_4.md)
- **Module Home:** [Module 4: Advanced Topics](./README.md)
