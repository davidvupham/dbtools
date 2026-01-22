# Environment Setup

**[← Back to Architecture](./02_architecture.md)** | **[Next: Your First Cluster →](./04_first_cluster.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)

## Table of contents

- [Learning objectives](#learning-objectives)
- [Prerequisites check](#prerequisites-check)
- [Docker setup](#docker-setup)
- [Kafka docker compose](#kafka-docker-compose)
- [Start the environment](#start-the-environment)
- [Verify the installation](#verify-the-installation)
- [Understanding the setup](#understanding-the-setup)
- [Troubleshooting](#troubleshooting)
- [Key takeaways](#key-takeaways)

---

## Learning objectives

By the end of this lesson, you will be able to:

1. Verify your environment meets the prerequisites
2. Set up a local Kafka cluster using Docker
3. Understand the Docker Compose configuration
4. Validate that Kafka is running correctly
5. Troubleshoot common setup issues

---

## Prerequisites check

Before proceeding, verify your system has the required software:

```bash
# Check Docker
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose
docker compose version
# Expected: Docker Compose version v2.0.0 or higher

# Check available disk space (need at least 5GB)
df -h .

# Check available memory (need at least 4GB)
free -h  # Linux
# or
sysctl hw.memsize  # macOS
```

### Minimum requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 2 cores | 4 cores |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 5 GB | 20 GB |
| **Docker** | 20.10+ | Latest |
| **Docker Compose** | 2.0+ | Latest |

> [!WARNING]
> If your system doesn't meet the minimum requirements, Kafka may be unstable or fail to start.

[↑ Back to Table of Contents](#table-of-contents)

---

## Docker setup

### Create the project directory

```bash
# Create a directory for the Kafka tutorial
mkdir -p ~/kafka-tutorial
cd ~/kafka-tutorial

# Create subdirectories
mkdir -p docker scripts data
```

### Directory structure

```
kafka-tutorial/
├── docker/
│   └── docker-compose.yml    # Kafka cluster configuration
├── scripts/
│   └── setup.sh              # Helper scripts
└── data/
    └── (Kafka data files)
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Kafka docker compose

Create the Docker Compose file that defines our Kafka environment:

```bash
cat > ~/kafka-tutorial/docker/docker-compose.yml << 'EOF'
# Kafka Tutorial - Docker Compose Configuration
# This file creates a single-node Kafka cluster in KRaft mode (no ZooKeeper)

version: '3.8'

services:
  # =============================================================================
  # KAFKA BROKER (KRaft Mode)
  # =============================================================================
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    hostname: kafka
    container_name: kafka
    ports:
      - "9092:9092"      # External client access
      - "9093:9093"      # Controller port (internal)
    environment:
      # -------------------------------------------------------------------------
      # KRaft Configuration (No ZooKeeper)
      # -------------------------------------------------------------------------
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@kafka:9093'
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'

      # -------------------------------------------------------------------------
      # Listener Configuration
      # -------------------------------------------------------------------------
      KAFKA_LISTENERS: 'PLAINTEXT://kafka:29092,CONTROLLER://kafka:9093,PLAINTEXT_HOST://0.0.0.0:9092'
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT'
      KAFKA_INTER_BROKER_LISTENER_NAME: 'PLAINTEXT'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'

      # -------------------------------------------------------------------------
      # Topic Defaults (for single-node development)
      # -------------------------------------------------------------------------
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1

      # -------------------------------------------------------------------------
      # Logging
      # -------------------------------------------------------------------------
      KAFKA_LOG4J_LOGGERS: 'kafka.controller=INFO,kafka.producer.async.DefaultEventHandler=INFO,state.change.logger=INFO'
      KAFKA_LOG4J_ROOT_LOGLEVEL: 'WARN'
    volumes:
      - kafka-data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s

  # =============================================================================
  # KAFKA UI (Optional - Web Interface)
  # =============================================================================
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: 'local'
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: 'kafka:29092'
    depends_on:
      kafka:
        condition: service_healthy

# =============================================================================
# VOLUMES
# =============================================================================
volumes:
  kafka-data:
    driver: local
EOF
```

### Configuration explained

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE CONFIGURATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LISTENERS                                                                  │
│  ─────────                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Port 9092 (PLAINTEXT_HOST)                                          │   │
│  │  └── External access from your machine (localhost:9092)              │   │
│  │                                                                      │   │
│  │  Port 29092 (PLAINTEXT)                                              │   │
│  │  └── Internal Docker network (kafka:29092)                           │   │
│  │                                                                      │   │
│  │  Port 9093 (CONTROLLER)                                              │   │
│  │  └── KRaft controller communication                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  WHY TWO LISTENERS?                                                         │
│  ──────────────────                                                         │
│  ┌───────────────────┐     ┌───────────────────┐                           │
│  │   Your Machine    │     │  Docker Network   │                           │
│  │                   │     │                   │                           │
│  │  localhost:9092 ──┼────►│ kafka:29092       │                           │
│  │  (PLAINTEXT_HOST) │     │ (PLAINTEXT)       │                           │
│  └───────────────────┘     └───────────────────┘                           │
│                                                                             │
│  • Apps on your machine use localhost:9092                                  │
│  • Apps in Docker use kafka:29092                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Start the environment

### Start Kafka

```bash
# Navigate to the docker directory
cd ~/kafka-tutorial/docker

# Start Kafka in the background
docker compose up -d

# Watch the logs to see startup progress
docker compose logs -f kafka
```

### Expected output

```
kafka  | [2026-01-21 10:00:00,000] INFO [KafkaRaftServer nodeId=1] Starting
kafka  | [2026-01-21 10:00:01,000] INFO [KafkaServer id=1] started
kafka  | [2026-01-21 10:00:02,000] INFO Kafka version: 7.6.0
```

Wait until you see "started" in the logs, then press `Ctrl+C` to stop following logs.

### Check container status

```bash
docker compose ps
```

Expected output:

```
NAME       IMAGE                    STATUS                   PORTS
kafka      confluentinc/cp-kafka   Up (healthy)             0.0.0.0:9092->9092/tcp
kafka-ui   provectuslabs/kafka-ui  Up                       0.0.0.0:8080->8080/tcp
```

> [!IMPORTANT]
> Wait for the `STATUS` column to show `Up (healthy)` before proceeding. This may take 30-60 seconds.

[↑ Back to Table of Contents](#table-of-contents)

---

## Verify the installation

### Test 1: List topics (CLI)

```bash
# Execute kafka-topics.sh inside the container
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list
```

Expected output: Empty (no topics yet) or internal topics starting with `_`.

### Test 2: Create a test topic

```bash
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic test-topic \
  --partitions 3 \
  --replication-factor 1
```

Expected output:

```
Created topic test-topic.
```

### Test 3: Describe the topic

```bash
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic test-topic
```

Expected output:

```
Topic: test-topic	TopicId: xxx	PartitionCount: 3	ReplicationFactor: 1
	Topic: test-topic	Partition: 0	Leader: 1	Replicas: 1	Isr: 1
	Topic: test-topic	Partition: 1	Leader: 1	Replicas: 1	Isr: 1
	Topic: test-topic	Partition: 2	Leader: 1	Replicas: 1	Isr: 1
```

### Test 4: Produce a message

```bash
# This opens an interactive producer
# Type messages and press Enter to send
echo "Hello, Kafka!" | docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic test-topic
```

### Test 5: Consume the message

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning
```

Expected output:

```
Hello, Kafka!
```

Press `Ctrl+C` to exit the consumer.

### Test 6: Kafka UI (Web Interface)

Open your browser and navigate to:

```
http://localhost:8080
```

You should see the Kafka UI dashboard showing your cluster and topics.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KAFKA UI DASHBOARD                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Cluster: local                                                             │
│  ─────────────────                                                          │
│  • Brokers: 1                                                               │
│  • Topics: 1 (+ internal)                                                   │
│  • Partitions: 3                                                            │
│                                                                             │
│  Topics                                                                     │
│  ──────                                                                     │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ Name          │ Partitions │ Replicas │ Messages │                 │    │
│  ├───────────────┼────────────┼──────────┼──────────┼─────────────────┤    │
│  │ test-topic    │     3      │    1     │    1     │ [View Messages] │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Understanding the setup

### Network architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT SETUP                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  YOUR MACHINE                        DOCKER NETWORK                         │
│  ────────────                        ──────────────                         │
│                                                                             │
│  ┌─────────────────┐                ┌─────────────────────────────────┐    │
│  │ Terminal        │                │                                 │    │
│  │                 │  localhost:9092│  ┌─────────────────────────┐   │    │
│  │ kafka-cli tools │───────────────►│  │       KAFKA            │   │    │
│  │ Python client   │                │  │  Internal: kafka:29092  │   │    │
│  │ Java client     │                │  │  Controller: :9093      │   │    │
│  └─────────────────┘                │  └─────────────────────────┘   │    │
│                                     │              │                  │    │
│  ┌─────────────────┐                │              │ kafka:29092      │    │
│  │ Browser         │  localhost:8080│              ▼                  │    │
│  │                 │───────────────►│  ┌─────────────────────────┐   │    │
│  │ Kafka UI        │                │  │      KAFKA-UI           │   │    │
│  │                 │                │  │  Web Interface          │   │    │
│  └─────────────────┘                │  └─────────────────────────┘   │    │
│                                     │                                 │    │
│                                     └─────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data persistence

Kafka data is persisted in a Docker volume:

```bash
# List Docker volumes
docker volume ls

# Inspect the Kafka data volume
docker volume inspect docker_kafka-data
```

Data includes:
- Topic partitions and messages
- Consumer group offsets
- Cluster metadata (KRaft)

> [!NOTE]
> Data persists across container restarts. Use `docker compose down -v` to remove volumes and start fresh.

[↑ Back to Table of Contents](#table-of-contents)

---

## Troubleshooting

### Issue: Container won't start

**Symptom:** `docker compose up` fails or container exits immediately.

**Check logs:**
```bash
docker compose logs kafka
```

**Common causes:**

1. **Port conflict (9092 in use)**
   ```bash
   # Check what's using port 9092
   lsof -i :9092
   # or
   netstat -tlnp | grep 9092

   # Solution: Stop the conflicting service or change the port
   ```

2. **Not enough memory**
   ```bash
   # Check Docker memory limit
   docker system info | grep Memory

   # Solution: Increase Docker memory to at least 4GB
   ```

3. **Invalid configuration**
   ```bash
   # Validate docker-compose.yml
   docker compose config
   ```

### Issue: Cannot connect to Kafka

**Symptom:** `Connection refused` or `Broker not available`

**Steps:**

1. **Check container is running:**
   ```bash
   docker compose ps
   ```

2. **Check container health:**
   ```bash
   docker inspect kafka | grep -A 10 "Health"
   ```

3. **Check logs for errors:**
   ```bash
   docker compose logs kafka | grep -i error
   ```

4. **Test connectivity from host:**
   ```bash
   # Test if port is accessible
   nc -zv localhost 9092
   ```

### Issue: Kafka UI not loading

**Symptom:** Browser shows "connection refused" on port 8080

**Steps:**

1. **Check kafka-ui container:**
   ```bash
   docker compose logs kafka-ui
   ```

2. **Verify Kafka is healthy first:**
   ```bash
   docker compose ps kafka
   # Must show "healthy" status
   ```

3. **Restart kafka-ui:**
   ```bash
   docker compose restart kafka-ui
   ```

### Issue: Messages not being consumed

**Symptom:** Consumer receives no messages

**Steps:**

1. **Check consumer group offsets:**
   ```bash
   docker exec -it kafka kafka-consumer-groups \
     --bootstrap-server localhost:9092 \
     --describe --all-groups
   ```

2. **Consume from beginning:**
   ```bash
   docker exec -it kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic test-topic \
     --from-beginning
   ```

3. **Verify messages exist:**
   ```bash
   docker exec -it kafka kafka-run-class kafka.tools.GetOffsetShell \
     --broker-list localhost:9092 \
     --topic test-topic
   ```

### Useful diagnostic commands

```bash
# Check cluster status
docker exec -it kafka kafka-metadata --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log --command "broker"

# Check broker configuration
docker exec -it kafka kafka-configs \
  --bootstrap-server localhost:9092 \
  --entity-type brokers \
  --entity-name 1 \
  --describe --all

# Check topic details
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe

# View consumer groups
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KEY TAKEAWAYS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DOCKER SETUP                                                            │
│     • Docker Compose provides a simple way to run Kafka locally             │
│     • KRaft mode eliminates ZooKeeper dependency                            │
│     • Data persists in Docker volumes                                       │
│                                                                             │
│  2. LISTENER CONFIGURATION                                                  │
│     • localhost:9092 for host machine access                                │
│     • kafka:29092 for Docker network access                                 │
│     • This dual-listener setup is standard for development                  │
│                                                                             │
│  3. VERIFICATION                                                            │
│     • Always test create/produce/consume cycle                              │
│     • Use kafka-ui for visual inspection                                    │
│     • Check container health before troubleshooting                         │
│                                                                             │
│  4. COMMON COMMANDS                                                         │
│     • docker compose up -d (start)                                          │
│     • docker compose logs -f kafka (view logs)                              │
│     • docker compose down (stop)                                            │
│     • docker compose down -v (stop and remove data)                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

### Quick command reference

```bash
# Start environment
cd ~/kafka-tutorial/docker && docker compose up -d

# Stop environment
docker compose down

# View logs
docker compose logs -f kafka

# List topics
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Create topic
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic my-topic --partitions 3 --replication-factor 1

# Produce messages
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 --topic my-topic

# Consume messages
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 --topic my-topic --from-beginning
```

---

**Next:** [Your First Kafka Cluster →](./04_first_cluster.md)
