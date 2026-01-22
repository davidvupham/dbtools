# Lesson 16: Monitoring and observability

**[← Back to Security](./15_security.md)** | **[Next: Production Operations →](./17_production_ops.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Monitoring-blue)

## Overview

Effective monitoring is essential for running Kafka in production. This lesson covers the key metrics to monitor, how to collect them, and how to set up alerting.

**Learning objectives:**
- Understand critical Kafka metrics for brokers, producers, and consumers
- Set up JMX metrics collection with Prometheus
- Build Grafana dashboards for Kafka monitoring
- Configure alerts for common issues

**Prerequisites:** Lesson 15 (Security), familiarity with Prometheus/Grafana

**Estimated time:** 50 minutes

---

## Table of contents

- [Monitoring overview](#monitoring-overview)
- [Critical metrics](#critical-metrics)
- [JMX metrics collection](#jmx-metrics-collection)
- [Prometheus setup](#prometheus-setup)
- [Grafana dashboards](#grafana-dashboards)
- [Alerting](#alerting)
- [Log analysis](#log-analysis)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Monitoring overview

### Monitoring stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA MONITORING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         KAFKA CLUSTER                                │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐                        │   │
│  │  │ Broker 1 │   │ Broker 2 │   │ Broker 3 │                        │   │
│  │  │ JMX:9999 │   │ JMX:9999 │   │ JMX:9999 │                        │   │
│  │  └────┬─────┘   └────┬─────┘   └────┬─────┘                        │   │
│  └───────┼──────────────┼──────────────┼────────────────────────────────┘   │
│          │              │              │                                     │
│          └──────────────┼──────────────┘                                     │
│                         │                                                    │
│                         ▼                                                    │
│          ┌─────────────────────────────┐                                    │
│          │     JMX Exporter / Agent    │                                    │
│          │     (converts JMX → HTTP)   │                                    │
│          └─────────────┬───────────────┘                                    │
│                        │                                                     │
│                        ▼                                                     │
│          ┌─────────────────────────────┐                                    │
│          │        PROMETHEUS           │                                    │
│          │   (scrapes & stores)        │                                    │
│          └─────────────┬───────────────┘                                    │
│                        │                                                     │
│           ┌────────────┴────────────┐                                       │
│           │                         │                                        │
│           ▼                         ▼                                        │
│  ┌─────────────────┐    ┌─────────────────┐                                │
│  │    GRAFANA      │    │  ALERTMANAGER   │                                │
│  │  (dashboards)   │    │   (alerts)      │                                │
│  └─────────────────┘    └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What to monitor

| Layer | What to Monitor | Why |
|-------|-----------------|-----|
| **Brokers** | CPU, memory, disk, network | Resource saturation |
| **Kafka** | Under-replicated partitions, ISR | Data durability |
| **Topics** | Log size, message rate | Capacity planning |
| **Producers** | Send rate, errors, latency | Application health |
| **Consumers** | Lag, commit rate | Processing health |
| **Connect** | Connector status, task count | Pipeline health |

---

## Critical metrics

### Broker metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CRITICAL BROKER METRICS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METRIC                               DESCRIPTION           ALERT THRESHOLD │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  UnderReplicatedPartitions            Partitions with       > 0             │
│  kafka.server:type=ReplicaManager     fewer ISRs than                       │
│                                       replication factor                    │
│                                                                             │
│  OfflinePartitionsCount               Partitions without    > 0             │
│  kafka.controller:type=KafkaController a leader                             │
│                                                                             │
│  ActiveControllerCount                Number of active      != 1            │
│  kafka.controller:type=KafkaController controllers (should                  │
│                                       be exactly 1)                         │
│                                                                             │
│  UncleanLeaderElectionsPerSec         Elections causing     > 0             │
│  kafka.controller:type=ControllerStats potential data loss                  │
│                                                                             │
│  IsrShrinksPerSec / IsrExpandsPerSec  ISR membership        High rate       │
│  kafka.server:type=ReplicaManager     changes                               │
│                                                                             │
│  RequestHandlerAvgIdlePercent         Handler thread        < 30%           │
│  kafka.server:type=KafkaRequestHandler idle time                            │
│  Processor                                                                  │
│                                                                             │
│  NetworkProcessorAvgIdlePercent       Network thread        < 30%           │
│  kafka.network:type=SocketServer      idle time                             │
│                                                                             │
│  TotalTimeMs (Produce/Fetch)          Request latency       p99 > 100ms     │
│  kafka.network:type=RequestMetrics                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Consumer metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER LAG MONITORING                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Consumer Lag = Log End Offset - Consumer Committed Offset                  │
│                                                                             │
│  Partition:                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  0    100   200   300   400   500   600   700   800   900  1000     │  │
│  │  │─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────│      │  │
│  │               ▲                                           ▲          │  │
│  │               │                                           │          │  │
│  │         Consumer                                    Log End          │  │
│  │         Offset: 250                                 Offset: 950      │  │
│  │                                                                      │  │
│  │         LAG = 950 - 250 = 700 messages                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  HEALTHY LAG:                                                               │
│  • Stable or decreasing                                                     │
│  • < few thousand messages (depends on throughput)                          │
│                                                                             │
│  UNHEALTHY LAG:                                                             │
│  • Continuously increasing                                                  │
│  • Growing faster than processing rate                                      │
│                                                                             │
│  ALERT THRESHOLDS:                                                          │
│  • Warning: Lag > 10,000 messages                                           │
│  • Critical: Lag > 100,000 messages or growing for > 15 minutes            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Producer metrics

| Metric | Description | Alert |
|--------|-------------|-------|
| `record-send-rate` | Records sent per second | Sudden drop |
| `record-error-rate` | Failed sends per second | > 0 |
| `request-latency-avg` | Average request time | > 100ms |
| `record-retry-rate` | Retries per second | High rate |
| `buffer-available-bytes` | Available buffer memory | < 20% |
| `batch-size-avg` | Average batch size | Too small |

---

## JMX metrics collection

### Enable JMX on Kafka

```bash
# In kafka startup script or environment
export KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote \
    -Dcom.sun.management.jmxremote.port=9999 \
    -Dcom.sun.management.jmxremote.authenticate=false \
    -Dcom.sun.management.jmxremote.ssl=false \
    -Djava.rmi.server.hostname=kafka"

# Or in Docker Compose
environment:
  KAFKA_JMX_PORT: 9999
  KAFKA_JMX_HOSTNAME: kafka
```

### JMX Exporter configuration

```yaml
# jmx-exporter-config.yml
---
startDelaySeconds: 0
ssl: false
lowercaseOutputName: true
lowercaseOutputLabelNames: true
whitelistObjectNames:
  - "kafka.server:type=BrokerTopicMetrics,*"
  - "kafka.server:type=ReplicaManager,*"
  - "kafka.controller:type=KafkaController,*"
  - "kafka.controller:type=ControllerStats,*"
  - "kafka.network:type=RequestMetrics,*"
  - "kafka.network:type=SocketServer,*"
  - "kafka.log:type=LogFlushStats,*"
  - "kafka.server:type=KafkaRequestHandlerPool,*"
  - "kafka.server:type=DelayedOperationPurgatory,*"
  - "kafka.server:type=SessionExpireListener,*"
  - "kafka.cluster:type=Partition,*"

rules:
  # Broker topic metrics
  - pattern: kafka.server<type=BrokerTopicMetrics, name=(.+), topic=(.+)><>Count
    name: kafka_server_brokertopicmetrics_$1_total
    type: COUNTER
    labels:
      topic: "$2"

  # Broker metrics (no topic)
  - pattern: kafka.server<type=BrokerTopicMetrics, name=(.+)><>Count
    name: kafka_server_brokertopicmetrics_$1_total
    type: COUNTER

  # Replica manager
  - pattern: kafka.server<type=ReplicaManager, name=(.+)><>Value
    name: kafka_server_replicamanager_$1
    type: GAUGE

  # Controller metrics
  - pattern: kafka.controller<type=KafkaController, name=(.+)><>Value
    name: kafka_controller_kafkacontroller_$1
    type: GAUGE

  # Request metrics
  - pattern: kafka.network<type=RequestMetrics, name=(.+), request=(.+)><>(.+)
    name: kafka_network_requestmetrics_$1_$3
    type: GAUGE
    labels:
      request: "$2"
```

### Run JMX Exporter

```bash
# As Java agent (recommended)
java -javaagent:/opt/jmx_exporter/jmx_prometheus_javaagent.jar=7071:/opt/jmx_exporter/kafka.yml \
     -jar /opt/kafka/libs/kafka.jar

# As standalone HTTP server
java -jar jmx_prometheus_httpserver.jar 7071 kafka.yml
```

---

## Prometheus setup

### Prometheus configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Kafka brokers
  - job_name: 'kafka'
    static_configs:
      - targets:
        - 'kafka-1:7071'
        - 'kafka-2:7071'
        - 'kafka-3:7071'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '(.+):7071'
        replacement: '${1}'

  # Kafka Connect
  - job_name: 'kafka-connect'
    static_configs:
      - targets: ['connect:7071']

  # ksqlDB
  - job_name: 'ksqldb'
    static_configs:
      - targets: ['ksqldb:7071']

  # Schema Registry
  - job_name: 'schema-registry'
    static_configs:
      - targets: ['schema-registry:7071']
```

### Consumer lag exporter

Use Kafka Lag Exporter for consumer lag metrics:

```yaml
# docker-compose addition
kafka-lag-exporter:
  image: seglo/kafka-lag-exporter:latest
  environment:
    - KAFKA_LAG_EXPORTER_CLUSTERS.0.name=main
    - KAFKA_LAG_EXPORTER_CLUSTERS.0.bootstrapBrokers=kafka:9092
  ports:
    - "8000:8000"
```

### Key Prometheus queries

```promql
# Broker - Under-replicated partitions
sum(kafka_server_replicamanager_underreplicatedpartitions)

# Broker - Offline partitions
kafka_controller_kafkacontroller_offlinepartitionscount

# Broker - Active controller count
sum(kafka_controller_kafkacontroller_activecontrollercount)

# Broker - Messages in per second (by topic)
sum by (topic) (rate(kafka_server_brokertopicmetrics_messagesin_total[5m]))

# Broker - Bytes in per second
sum(rate(kafka_server_brokertopicmetrics_bytesin_total[5m]))

# Broker - Request latency p99
histogram_quantile(0.99, sum by (le, request) (rate(kafka_network_requestmetrics_totaltimems_bucket[5m])))

# Consumer - Lag by group
sum by (group, topic) (kafka_consumergroup_lag)

# Consumer - Lag rate of change
deriv(kafka_consumergroup_lag[5m])

# Producer - Record send rate
sum by (client_id) (rate(kafka_producer_record_send_total[5m]))
```

---

## Grafana dashboards

### Sample dashboard panels

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA CLUSTER OVERVIEW DASHBOARD                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ BROKER STATUS       │  │ UNDER-REPLICATED    │  │ OFFLINE PARTITIONS  │ │
│  │                     │  │                     │  │                     │ │
│  │   3/3 ONLINE ✓      │  │        0 ✓          │  │        0 ✓          │ │
│  │                     │  │                     │  │                     │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ MESSAGES IN (per second by topic)                                     │  │
│  │                                                                       │  │
│  │  50k ┤                    ╭──╮                                        │  │
│  │  40k ┤             ╭─────╯  ╰──────╮                                  │  │
│  │  30k ┤      ╭─────╯               ╰─────╮                            │  │
│  │  20k ┤ ─────╯                           ╰──────                       │  │
│  │  10k ┤                                                                │  │
│  │    0 ┼────────────────────────────────────────────────►              │  │
│  │      00:00     04:00     08:00     12:00     16:00    20:00          │  │
│  │                                                                       │  │
│  │  ─── orders   ─── payments   ─── events                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ CONSUMER LAG (by consumer group)                                      │  │
│  │                                                                       │  │
│  │  │                                                                    │  │
│  │  │ order-processors     ████████████████████████  45,000             │  │
│  │  │ payment-handlers     ████████  12,000                             │  │
│  │  │ analytics-consumers  ███  3,500                                   │  │
│  │  │                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ REQUEST LATENCY p99 (ms)                                              │  │
│  │                                                                       │  │
│  │  20ms ┤      ╭╮                                                       │  │
│  │  15ms ┤  ╭──╯ ╰─╮                                                    │  │
│  │  10ms ┤──╯      ╰───────────────────────                             │  │
│  │   5ms ┤                                                               │  │
│  │   0ms ┼────────────────────────────────────────────────►             │  │
│  │                                                                       │  │
│  │  ─── Produce   ─── Fetch                                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Import pre-built dashboards

Popular Grafana dashboard IDs:
- **7589**: Kafka Overview (Confluent)
- **721**: Kafka Exporter Overview
- **10973**: Kafka Consumer Lag
- **12460**: Kafka Streams

---

## Alerting

### Prometheus alerting rules

```yaml
# kafka-alerts.yml
groups:
  - name: kafka-broker-alerts
    rules:
      # Under-replicated partitions
      - alert: KafkaUnderReplicatedPartitions
        expr: kafka_server_replicamanager_underreplicatedpartitions > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka has under-replicated partitions"
          description: "{{ $value }} partitions are under-replicated on {{ $labels.instance }}"

      # Offline partitions
      - alert: KafkaOfflinePartitions
        expr: kafka_controller_kafkacontroller_offlinepartitionscount > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka has offline partitions"
          description: "{{ $value }} partitions are offline"

      # No active controller
      - alert: KafkaNoActiveController
        expr: sum(kafka_controller_kafkacontroller_activecontrollercount) != 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka cluster has no active controller"

      # Broker down
      - alert: KafkaBrokerDown
        expr: up{job="kafka"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Kafka broker is down"
          description: "Broker {{ $labels.instance }} is not responding"

      # High request latency
      - alert: KafkaHighRequestLatency
        expr: histogram_quantile(0.99, sum by (le) (rate(kafka_network_requestmetrics_totaltimems_bucket{request="Produce"}[5m]))) > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Kafka produce latency is high"
          description: "P99 produce latency is {{ $value }}ms"

  - name: kafka-consumer-alerts
    rules:
      # High consumer lag
      - alert: KafkaConsumerLagHigh
        expr: kafka_consumergroup_lag > 100000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Kafka consumer lag is high"
          description: "Consumer group {{ $labels.group }} has lag of {{ $value }} on topic {{ $labels.topic }}"

      # Consumer lag growing
      - alert: KafkaConsumerLagGrowing
        expr: deriv(kafka_consumergroup_lag[15m]) > 100
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Kafka consumer lag is continuously growing"
          description: "Consumer group {{ $labels.group }} lag is growing at {{ $value }} per second"

  - name: kafka-disk-alerts
    rules:
      # Disk space low
      - alert: KafkaDiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/var/kafka"} / node_filesystem_size_bytes{mountpoint="/var/kafka"}) < 0.2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Kafka disk space is running low"
          description: "Less than 20% disk space remaining on {{ $labels.instance }}"
```

### Alertmanager configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'slack-notifications'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    - match:
        severity: warning
      receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/xxx'
        channel: '#kafka-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
        severity: critical
```

---

## Log analysis

### Key log patterns to monitor

```bash
# Under-replicated partitions
grep "UnderReplicatedPartitions" /var/log/kafka/server.log

# ISR changes
grep "Shrinking ISR\|Expanding ISR" /var/log/kafka/server.log

# Controller issues
grep "Controller\|controller" /var/log/kafka/controller.log

# Authentication failures
grep "Failed authentication\|AuthenticationException" /var/log/kafka/server.log

# Connection issues
grep "Connection\|Disconnected" /var/log/kafka/server.log | grep -i error
```

### Centralized logging

```yaml
# Filebeat configuration for Kafka logs
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/kafka/*.log
    fields:
      log_type: kafka
    multiline:
      pattern: '^\['
      negate: true
      match: after

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "kafka-logs-%{+yyyy.MM.dd}"
```

---

## Hands-on exercises

### Exercise 1: Set up monitoring stack

```bash
# 1. Start Kafka with JMX enabled
# 2. Deploy JMX Exporter
# 3. Configure Prometheus to scrape metrics
# 4. Import Grafana dashboard
```

### Exercise 2: Create custom dashboard

Create a Grafana dashboard showing:
- Messages per second by topic
- Consumer lag by group
- Produce/Fetch latency percentiles

### Exercise 3: Configure alerts

Set up alerts for:
- Under-replicated partitions
- Consumer lag > 50,000
- Broker offline

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING KEY TAKEAWAYS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Monitor under-replicated and offline partitions - they indicate issues  │
│                                                                             │
│  ✓ Consumer lag is the #1 metric for application health                    │
│                                                                             │
│  ✓ Use JMX Exporter + Prometheus + Grafana for comprehensive monitoring    │
│                                                                             │
│  ✓ Alert on conditions, not just thresholds (e.g., lag growing)            │
│                                                                             │
│  ✓ Monitor both Kafka infrastructure and client applications               │
│                                                                             │
│  ✓ Set up centralized logging for troubleshooting                          │
│                                                                             │
│  ✓ Key metrics: UnderReplicatedPartitions, OfflinePartitions,              │
│    ActiveControllerCount, ConsumerLag, RequestLatency                      │
│                                                                             │
│  ✓ Don't forget disk space monitoring - Kafka is disk-heavy                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Security](./15_security.md)** | **[Next: Production Operations →](./17_production_ops.md)**

[↑ Back to Top](#lesson-16-monitoring-and-observability)
