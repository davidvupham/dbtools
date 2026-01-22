# Module 1 Quiz: Kafka Foundations

**[← Back to Module 1](./README.md)**

Test your understanding of Kafka basics: architecture, topics, partitions, producers, consumers, and consumer groups.

**Instructions:**
- 15 questions, approximately 20 minutes
- Mix of conceptual and practical questions
- Check your answers at the end
- Target: 80% (12/15) before proceeding to Module 2

---

## Section 1: Conceptual questions (6 questions)

### Question 1

What is the primary difference between Apache Kafka and a traditional message queue like RabbitMQ?

a) Kafka can only handle text messages
b) Kafka deletes messages after they are consumed
c) Kafka retains messages and allows replay
d) Kafka doesn't support multiple consumers

### Question 2

Which component is responsible for storing messages and serving client requests?

a) ZooKeeper
b) Producer
c) Broker
d) Consumer Group

### Question 3

What determines which partition a message is sent to when a key is provided?

a) Random selection
b) Round-robin distribution
c) Hash of the key
d) The partition with the most space

### Question 4

What is the purpose of the ISR (In-Sync Replicas)?

a) To store consumer offsets
b) To ensure data durability by maintaining replicas that are up-to-date with the leader
c) To manage producer batching
d) To coordinate consumer group rebalancing

### Question 5

In KRaft mode, what does Kafka use instead of ZooKeeper?

a) etcd
b) Consul
c) Built-in Raft consensus protocol
d) Redis

### Question 6

Which statement about partitions is TRUE?

a) You can increase and decrease partition count at any time
b) Messages are ordered across all partitions in a topic
c) Messages are ordered within a single partition
d) Each partition can only have one consumer

---

## Section 2: Architecture questions (4 questions)

### Question 7

A Kafka topic has 6 partitions and replication factor of 3. How many partition replicas exist in total?

a) 6
b) 9
c) 18
d) 3

### Question 8

What happens when a partition leader fails?

a) The partition becomes permanently unavailable
b) A follower from the ISR is elected as the new leader
c) All messages in that partition are lost
d) Producers must manually select a new leader

### Question 9

In the following diagram, what is the relationship between Consumer 1 and Consumer 2?

```
Topic: orders (4 partitions)
Consumer Group: order-processor

P0 ──► Consumer 1
P1 ──► Consumer 1
P2 ──► Consumer 2
P3 ──► Consumer 2
```

a) They are competing for the same messages
b) They are in different consumer groups
c) They are in the same consumer group, processing different partitions
d) Consumer 2 is a backup for Consumer 1

### Question 10

What is the maximum number of active consumers in a consumer group that can process a topic with 4 partitions?

a) 1
b) 4
c) 8
d) Unlimited

---

## Section 3: Practical questions (5 questions)

### Question 11

Which command creates a Kafka topic named "events" with 3 partitions?

a)
```bash
kafka-topics --bootstrap-server localhost:9092 \
  --create --topic events --partitions 3
```

b)
```bash
kafka-topics --zookeeper localhost:2181 \
  --new-topic events --partitions 3
```

c)
```bash
kafka-create-topic --server localhost:9092 \
  --name events --partitions 3
```

d)
```bash
kafka-topics --bootstrap-server localhost:9092 \
  --add --topic events --partition-count 3
```

### Question 12

A consumer wants to read all messages from a topic, including those produced before the consumer started. Which option should be used?

a) `--from-latest`
b) `--from-beginning`
c) `--read-all`
d) `--offset 0`

### Question 13

You have a producer sending messages with keys "user-1", "user-2", and "user-1" to a topic with 3 partitions. What can you conclude?

a) All three messages will be in different partitions
b) Messages with key "user-1" will be in the same partition
c) The partition assignment is random
d) Keys are ignored when partitioning

### Question 14

What does this command output show?

```bash
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group my-group
```

```
GROUP     TOPIC   PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
my-group  orders  0          100             150             50
my-group  orders  1          200             200             0
```

a) Partition 0 has more messages than partition 1
b) The consumer is 50 messages behind on partition 0
c) Partition 1 is not receiving any messages
d) The consumer group has 50 active consumers

### Question 15

You want to send a message with key "order-123" to a topic. Which producer command is correct?

a)
```bash
kafka-console-producer --bootstrap-server localhost:9092 \
  --topic orders \
  --property parse.key=true \
  --property key.separator=:
# Then type: order-123:message-value
```

b)
```bash
kafka-console-producer --bootstrap-server localhost:9092 \
  --topic orders \
  --key order-123 \
  --value message-value
```

c)
```bash
kafka-console-producer --bootstrap-server localhost:9092 \
  --topic orders \
  --message "key=order-123,value=message-value"
```

d)
```bash
kafka-console-producer --bootstrap-server localhost:9092 \
  --topic orders:order-123
# Then type: message-value
```

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **c**
Kafka retains messages for a configurable period and allows consumers to replay messages by resetting offsets. Traditional message queues typically delete messages after consumption.

### Question 2: **c**
Brokers are Kafka servers that receive messages from producers, store them on disk, and serve them to consumers. ZooKeeper (or KRaft) handles coordination, not message storage.

### Question 3: **c**
When a key is provided, Kafka uses `hash(key) % numPartitions` to determine the target partition. This ensures messages with the same key always go to the same partition.

### Question 4: **b**
ISR (In-Sync Replicas) contains replicas that are fully caught up with the leader. Only ISR members can be elected as leader, ensuring no data loss during failover.

### Question 5: **c**
KRaft (Kafka Raft) uses a built-in implementation of the Raft consensus protocol to manage cluster metadata, eliminating the need for ZooKeeper.

### Question 6: **c**
Messages are ordered within a single partition, not across partitions. This is why using keys is important for related messages that need ordering.

### Question 7: **c**
Total replicas = Partitions × Replication Factor = 6 × 3 = 18. Each of the 6 partitions has 3 copies (1 leader + 2 followers).

### Question 8: **b**
When a leader fails, the controller automatically elects a new leader from the ISR. This ensures continued availability without data loss.

### Question 9: **c**
Consumer 1 and Consumer 2 are in the same consumer group ("order-processor"). Kafka assigns different partitions to each consumer so they process messages in parallel without duplication.

### Question 10: **b**
With 4 partitions, at most 4 consumers can be active (one per partition). Additional consumers would be idle. To utilize more consumers, you need more partitions.

### Question 11: **a**
The correct modern syntax uses `--bootstrap-server` and `--create` with `--partitions`. The replication factor defaults to 1 if not specified.

### Question 12: **b**
`--from-beginning` tells the consumer to start reading from the earliest available offset in each partition, allowing it to see historical messages.

### Question 13: **b**
Messages with the same key ("user-1") will always be hashed to the same partition. This guarantees ordering for messages related to the same entity.

### Question 14: **b**
LAG = LOG-END-OFFSET - CURRENT-OFFSET. For partition 0: 150 - 100 = 50. The consumer has 50 messages to catch up on. Partition 1 has LAG=0, meaning it's fully caught up.

### Question 15: **a**
The console producer requires `--property parse.key=true` and `--property key.separator=:` to accept keyed messages. Then you type messages in the format `key:value`.

---

### Score interpretation

- **13-15 correct**: Excellent! You have a solid foundation. Proceed to Module 2.
- **10-12 correct**: Good understanding. Review the topics you missed before continuing.
- **7-9 correct**: Fair. Re-read the relevant lessons and redo the exercises.
- **Below 7**: Review Module 1 thoroughly before attempting Module 2.

</details>

---

**Next:** [Project 1: Kafka CLI Tool →](./project_1_cli_tool.md)

[← Back to Module 1](./README.md) | [Proceed to Module 2 →](../module_2_core_concepts/README.md)
