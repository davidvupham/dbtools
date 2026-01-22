# Your First Kafka Cluster

**[← Back to Environment Setup](./03_setup_environment.md)** | **[Next: Module 1 Quiz →](./quiz_module_1.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)

## Table of contents

- [Learning objectives](#learning-objectives)
- [Working with topics](#working-with-topics)
- [Producing messages](#producing-messages)
- [Consuming messages](#consuming-messages)
- [Exploring partitions](#exploring-partitions)
- [Consumer groups in action](#consumer-groups-in-action)
- [Monitoring with Kafka UI](#monitoring-with-kafka-ui)
- [Cleanup](#cleanup)
- [Key takeaways](#key-takeaways)
- [Knowledge check](#knowledge-check)

---

## Learning objectives

By the end of this lesson, you will be able to:

1. Create, list, describe, and delete Kafka topics
2. Produce messages with and without keys
3. Consume messages from different starting positions
4. Understand partition distribution in practice
5. Observe consumer group behavior
6. Use Kafka UI for monitoring

---

## Working with topics

### Listing topics

```bash
# List all topics in the cluster
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

### Creating topics

Let's create several topics for our exercises:

```bash
# Create a simple topic
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic user-events \
  --partitions 3 \
  --replication-factor 1

# Create a topic for orders
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic orders \
  --partitions 6 \
  --replication-factor 1

# Create a topic with custom retention (1 hour)
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic temp-events \
  --partitions 2 \
  --replication-factor 1 \
  --config retention.ms=3600000
```

### Describing topics

```bash
# Describe all topics
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe

# Describe a specific topic
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic orders
```

Expected output for the orders topic:

```
Topic: orders	TopicId: abc123	PartitionCount: 6	ReplicationFactor: 1	Configs:
	Topic: orders	Partition: 0	Leader: 1	Replicas: 1	Isr: 1
	Topic: orders	Partition: 1	Leader: 1	Replicas: 1	Isr: 1
	Topic: orders	Partition: 2	Leader: 1	Replicas: 1	Isr: 1
	Topic: orders	Partition: 3	Leader: 1	Replicas: 1	Isr: 1
	Topic: orders	Partition: 4	Leader: 1	Replicas: 1	Isr: 1
	Topic: orders	Partition: 5	Leader: 1	Replicas: 1	Isr: 1
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOPIC DESCRIPTION EXPLAINED                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topic: orders                                                              │
│  ─────────────────────────────────────────────────────────────────────      │
│  • PartitionCount: 6      → Topic divided into 6 partitions                 │
│  • ReplicationFactor: 1   → Each partition exists on 1 broker only          │
│                                                                             │
│  Each partition line shows:                                                 │
│  ─────────────────────────                                                  │
│  • Partition: 0           → Partition number (0-5)                          │
│  • Leader: 1              → Broker 1 is the leader                          │
│  • Replicas: 1            → List of brokers with copies                     │
│  • Isr: 1                 → In-sync replicas (same as Replicas here)        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Altering topics

```bash
# Increase partitions (cannot decrease!)
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --alter \
  --topic user-events \
  --partitions 6

# View the change
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic user-events
```

> [!WARNING]
> You cannot decrease partition count. Plan your partition strategy carefully. Adding partitions may affect key-based message ordering.

### Deleting topics

```bash
# Delete a topic
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic temp-events

# Verify deletion
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Producing messages

### Basic producer (interactive)

```bash
# Start an interactive producer
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic user-events
```

Type messages and press Enter to send:

```
>First message
>Second message
>Hello from Kafka!
```

Press `Ctrl+C` to exit.

### Producer with keys

Keys determine which partition a message goes to. Messages with the same key always go to the same partition.

```bash
# Start a producer that accepts keys
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --property parse.key=true \
  --property key.separator=:
```

Send keyed messages (format: `key:value`):

```
>user-001:{"orderId":"A1","item":"book","qty":1}
>user-002:{"orderId":"A2","item":"pen","qty":5}
>user-001:{"orderId":"A3","item":"notebook","qty":2}
>user-003:{"orderId":"A4","item":"eraser","qty":10}
>user-001:{"orderId":"A5","item":"pencil","qty":3}
```

Press `Ctrl+C` to exit.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KEY-BASED PARTITIONING                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Key: user-001 → hash → Partition 2                                         │
│       user-001 → hash → Partition 2  (same key = same partition)            │
│       user-001 → hash → Partition 2                                         │
│                                                                             │
│  Key: user-002 → hash → Partition 5                                         │
│                                                                             │
│  Key: user-003 → hash → Partition 0                                         │
│                                                                             │
│  Result:                                                                    │
│  ─────────────────────────────────────────────────────────────────────      │
│  • All user-001 orders are in partition 2 (in order!)                       │
│  • user-002 orders are in partition 5                                       │
│  • user-003 orders are in partition 0                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Producer from file

Create a test file with messages:

```bash
# Create a file with messages
cat > /tmp/messages.txt << 'EOF'
Message from file 1
Message from file 2
Message from file 3
EOF

# Produce from file
docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic user-events < /tmp/messages.txt
```

### Produce multiple messages programmatically

```bash
# Generate and send 100 messages
for i in {1..100}; do
  echo "Message number $i"
done | docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic user-events
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Consuming messages

### Basic consumer

```bash
# Consume new messages only (default)
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-events
```

This waits for new messages. Press `Ctrl+C` to exit.

### Consume from beginning

```bash
# Read all messages from the beginning
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --from-beginning
```

### Consume with keys and timestamps

```bash
# Show key, value, timestamp, and partition
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --from-beginning \
  --property print.key=true \
  --property print.timestamp=true \
  --property print.partition=true \
  --property key.separator=" | "
```

Expected output format:

```
CreateTime:1705849200000	Partition:2	user-001 | {"orderId":"A1","item":"book","qty":1}
CreateTime:1705849201000	Partition:5	user-002 | {"orderId":"A2","item":"pen","qty":5}
CreateTime:1705849202000	Partition:2	user-001 | {"orderId":"A3","item":"notebook","qty":2}
```

### Consume specific number of messages

```bash
# Read only 5 messages then exit
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --from-beginning \
  --max-messages 5
```

### Consume from specific partition

```bash
# Read from partition 0 only
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --partition 0 \
  --from-beginning
```

### Consume from specific offset

```bash
# Read from partition 0, starting at offset 2
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --partition 0 \
  --offset 2
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Exploring partitions

Let's see how messages are distributed across partitions:

### Create a topic and send keyed messages

```bash
# Create a topic with 4 partitions
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic partition-demo \
  --partitions 4 \
  --replication-factor 1

# Send messages with keys
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic partition-demo \
  --property parse.key=true \
  --property key.separator=: << 'EOF'
alice:Alice's first message
bob:Bob's first message
charlie:Charlie's first message
alice:Alice's second message
bob:Bob's second message
alice:Alice's third message
david:David's message
EOF
```

### Check message distribution

```bash
# Consume showing partition info
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic partition-demo \
  --from-beginning \
  --property print.key=true \
  --property print.partition=true
```

You'll see that messages with the same key are in the same partition:

```
Partition:1	alice	Alice's first message
Partition:3	bob	Bob's first message
Partition:0	charlie	Charlie's first message
Partition:1	alice	Alice's second message
Partition:3	bob	Bob's second message
Partition:1	alice	Alice's third message
Partition:2	david	David's message
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARTITION DISTRIBUTION                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Partition 0: [charlie]                                                     │
│  Partition 1: [alice, alice, alice]  ← All Alice messages together (order!) │
│  Partition 2: [david]                                                       │
│  Partition 3: [bob, bob]             ← All Bob messages together (order!)   │
│                                                                             │
│  KEY INSIGHT:                                                               │
│  • Same key = Same partition = Guaranteed order                             │
│  • Different keys = May be different partitions = No order guarantee        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Check partition offsets

```bash
# See offset information for each partition
docker exec -it kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic partition-demo
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Consumer groups in action

Consumer groups enable parallel consumption and provide fault tolerance.

### Create a consumer group

```bash
# First, let's produce more messages
for i in {1..20}; do
  echo "order-$((i % 5)):Order $i details"
done | docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --property parse.key=true \
  --property key.separator=:
```

### Start multiple consumers in the same group

Open **three terminal windows** and run one consumer in each:

**Terminal 1:**
```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --group order-processor \
  --property print.partition=true
```

**Terminal 2:**
```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --group order-processor \
  --property print.partition=true
```

**Terminal 3:**
```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --group order-processor \
  --property print.partition=true
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER GROUP: order-processor                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Topic: orders (6 partitions)                                               │
│                                                                             │
│  Consumer 1 (Terminal 1)        Consumer 2 (Terminal 2)                     │
│  ────────────────────           ────────────────────                        │
│  Assigned: P0, P1               Assigned: P2, P3                            │
│                                                                             │
│              Consumer 3 (Terminal 3)                                        │
│              ────────────────────                                           │
│              Assigned: P4, P5                                               │
│                                                                             │
│  Each consumer processes DIFFERENT partitions!                              │
│  Combined, they process the ENTIRE topic.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Watch consumer group rebalancing

Stop one consumer (`Ctrl+C` in Terminal 3). Watch the other terminals - you'll see a rebalance message, and the remaining consumers will take over the orphaned partitions.

### View consumer group status

```bash
# List all consumer groups
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list

# Describe the consumer group
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group order-processor
```

Output shows partition assignment and lag:

```
GROUP           TOPIC   PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG     CONSUMER-ID
order-processor orders  0          15              15              0       consumer-1-xxx
order-processor orders  1          12              12              0       consumer-1-xxx
order-processor orders  2          18              18              0       consumer-2-xxx
order-processor orders  3          14              14              0       consumer-2-xxx
order-processor orders  4          16              16              0       consumer-3-xxx
order-processor orders  5          13              13              0       consumer-3-xxx
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONSUMER GROUP STATUS EXPLAINED                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CURRENT-OFFSET: Where the consumer is currently reading                    │
│  LOG-END-OFFSET: Latest message in the partition                            │
│  LAG:            LOG-END-OFFSET - CURRENT-OFFSET                            │
│                                                                             │
│  LAG = 0 means consumer is caught up                                        │
│  LAG > 0 means consumer is behind (needs monitoring!)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Reset consumer group offsets

```bash
# Reset to earliest (start over)
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group order-processor \
  --topic orders \
  --reset-offsets \
  --to-earliest \
  --execute

# Now consume again - you'll see all messages from the beginning
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic orders \
  --group order-processor \
  --max-messages 5
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Monitoring with Kafka UI

Open `http://localhost:8080` in your browser.

### Exploring the dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KAFKA UI FEATURES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CLUSTER OVERVIEW                                                        │
│     • Broker count and status                                               │
│     • Total topics and partitions                                           │
│     • Cluster health indicators                                             │
│                                                                             │
│  2. TOPICS                                                                  │
│     • List all topics with message counts                                   │
│     • View partition distribution                                           │
│     • Browse messages (read individual records)                             │
│     • Create/delete topics via UI                                           │
│                                                                             │
│  3. CONSUMERS                                                               │
│     • List consumer groups                                                  │
│     • View consumer lag per partition                                       │
│     • See consumer assignments                                              │
│                                                                             │
│  4. BROKERS                                                                 │
│     • Broker configuration                                                  │
│     • Disk usage                                                            │
│     • Partition distribution                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Try these exercises in Kafka UI:

1. **View topic messages:**
   - Click on "Topics" → "orders"
   - Click "Messages" tab
   - See individual messages with keys, values, and metadata

2. **Check consumer lag:**
   - Click on "Consumers" → "order-processor"
   - View lag for each partition

3. **Create a topic:**
   - Click "Create Topic" button
   - Name: `ui-created-topic`
   - Partitions: 3
   - Click Create

[↑ Back to Table of Contents](#table-of-contents)

---

## Cleanup

### Delete test topics

```bash
# Delete individual topics
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic partition-demo

docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic ui-created-topic

# Verify
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

### Stop the environment (when done for the day)

```bash
cd ~/kafka-tutorial/docker

# Stop containers (data preserved)
docker compose down

# Or stop and remove all data (fresh start)
docker compose down -v
```

### Restart the environment

```bash
cd ~/kafka-tutorial/docker
docker compose up -d
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KEY TAKEAWAYS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. TOPIC MANAGEMENT                                                        │
│     • Create topics with appropriate partition count                        │
│     • You cannot decrease partitions - plan ahead                           │
│     • Use describe to verify configuration                                  │
│                                                                             │
│  2. MESSAGE KEYS                                                            │
│     • Same key → Same partition → Guaranteed order                          │
│     • Use keys when message ordering matters                                │
│     • No key → Round-robin distribution                                     │
│                                                                             │
│  3. CONSUMER GROUPS                                                         │
│     • Enable parallel consumption                                           │
│     • Partitions assigned automatically                                     │
│     • Rebalancing happens when consumers join/leave                         │
│     • Monitor consumer lag for health                                       │
│                                                                             │
│  4. OFFSETS                                                                 │
│     • Track consumer progress per partition                                 │
│     • Can be reset to replay messages                                       │
│     • Committed offsets survive consumer restarts                           │
│                                                                             │
│  5. MONITORING                                                              │
│     • Use Kafka UI for visual inspection                                    │
│     • Watch consumer lag for performance issues                             │
│     • CLI tools for automation and scripting                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Knowledge check

Test your understanding before moving on:

1. What happens when you produce messages without a key?
2. If you have 6 partitions and 3 consumers in a group, how are partitions assigned?
3. What does "consumer lag" indicate?
4. Can you decrease the number of partitions on an existing topic?
5. What happens to a consumer group when one consumer dies?

<details>
<summary>Click to reveal answers</summary>

1. **Messages without keys:** Messages are distributed across partitions using round-robin. This provides even distribution but no ordering guarantee for related messages.

2. **6 partitions, 3 consumers:** Each consumer gets 2 partitions assigned (6 / 3 = 2). Kafka distributes partitions evenly.

3. **Consumer lag:** The difference between the latest message offset and the consumer's current position. High lag means the consumer is falling behind and can't keep up with the producer.

4. **Decrease partitions:** No, you cannot decrease partition count. Partitions can only be increased. Plan your partition strategy carefully.

5. **Consumer death:** The consumer group rebalances. Remaining consumers take over the partitions that were assigned to the dead consumer. No messages are lost.

</details>

---

**Congratulations!** You've completed Module 1: Foundations!

**Next Steps:**
1. Complete the [Module 1 Exercises](./exercises/)
2. Take the [Module 1 Quiz](./quiz_module_1.md)
3. Build [Project 1: Kafka CLI Tool](./project_1_cli_tool.md)
4. Proceed to [Module 2: Core Concepts](../module_2_core_concepts/05_topics_partitions.md)
