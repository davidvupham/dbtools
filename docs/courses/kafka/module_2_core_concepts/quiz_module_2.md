# Module 2 Quiz: Core Concepts

**[← Back to Module 2](./README.md)**

Test your understanding of Kafka core concepts: topics, partitions, producers, consumers, and consumer groups.

**Instructions:**
- 15 questions, approximately 20 minutes
- Mix of conceptual and practical questions
- Check your answers at the end
- Target: 80% (12/15) before proceeding to Module 3

---

## Section 1: Topics and partitions (5 questions)

### Question 1

A topic has 6 partitions. What is the maximum number of consumers that can actively process messages in a single consumer group?

a) 1
b) 3
c) 6
d) Unlimited

### Question 2

You need to ensure that all orders from the same customer are processed in order. What should you do?

a) Use a single partition
b) Use the customer ID as the message key
c) Use a consumer group with one consumer
d) Set `max.in.flight.requests.per.connection=1`

### Question 3

What happens when you try to decrease the number of partitions on an existing topic?

a) Kafka automatically rebalances messages
b) Old messages are deleted
c) The operation fails - you cannot decrease partitions
d) Consumers automatically adjust

### Question 4

Which cleanup policy retains only the latest value for each key?

a) delete
b) compact
c) retain
d) dedupe

### Question 5

A topic has `retention.ms=86400000` and `retention.bytes=1073741824`. When are messages deleted?

a) Only after 24 hours
b) Only after 1GB is reached
c) Whichever threshold is reached first
d) When both thresholds are reached

---

## Section 2: Producers (5 questions)

### Question 6

What does `acks=all` mean for a producer?

a) The producer doesn't wait for any acknowledgment
b) The producer waits for the leader to acknowledge
c) The producer waits for all in-sync replicas to acknowledge
d) The producer waits for all brokers in the cluster

### Question 7

You want maximum throughput and can tolerate some message loss. Which configuration is best?

a) `acks=all`, `linger.ms=0`
b) `acks=0`, `linger.ms=20`, `batch.size=65536`
c) `acks=1`, `enable.idempotence=true`
d) `acks=all`, `compression.type=gzip`

### Question 8

What is the purpose of enabling idempotence (`enable.idempotence=true`)?

a) Increase throughput
b) Reduce latency
c) Prevent duplicate messages during retries
d) Enable message compression

### Question 9

A producer sends a message, the broker writes it, but the ACK is lost in the network. With idempotence disabled, what happens when the producer retries?

a) The message is deduplicated
b) The message is written again (duplicate)
c) The retry fails
d) The original message is deleted

### Question 10

Which compression type offers the best balance of speed and compression ratio?

a) gzip
b) snappy
c) lz4
d) none

---

## Section 3: Consumers and consumer groups (5 questions)

### Question 11

A consumer group has 3 consumers and subscribes to a topic with 6 partitions. How are partitions typically assigned?

a) All 6 partitions to consumer 1
b) 2 partitions to each consumer
c) Random assignment
d) Round-robin message delivery

### Question 12

What is "consumer lag"?

a) The time a message spends in the queue
b) The difference between the latest offset and the consumer's committed offset
c) The network latency between consumer and broker
d) The time it takes to process a message

### Question 13

What does `auto.offset.reset=earliest` do when a new consumer group starts?

a) Starts from the latest messages only
b) Starts from the beginning of the topic
c) Fails with an error
d) Waits for new messages

### Question 14

When should you use manual offset commits instead of auto-commit?

a) When you want simpler code
b) When you need exactly-once processing semantics
c) When you want maximum throughput
d) When using console consumer

### Question 15

What triggers a consumer group rebalance?

a) Only when a broker fails
b) When a consumer joins or leaves the group
c) When a new message is produced
d) Every 5 minutes automatically

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **c**
With 6 partitions, at most 6 consumers can be active in a group. Each partition is assigned to exactly one consumer. Extra consumers would be idle.

### Question 2: **b**
Using the customer ID as the message key ensures all messages for that customer go to the same partition, maintaining order. A single partition would work but limits parallelism.

### Question 3: **c**
You cannot decrease the number of partitions on an existing topic. Partitions can only be added. Plan partition count carefully.

### Question 4: **b**
`cleanup.policy=compact` performs log compaction, retaining only the latest value for each key. Older values are removed during compaction.

### Question 5: **c**
When both time and size retention are configured, messages are deleted when either threshold is reached first.

### Question 6: **c**
`acks=all` means the producer waits for all in-sync replicas (ISR) to acknowledge receipt before considering the write successful.

### Question 7: **b**
For maximum throughput with acceptable loss: `acks=0` (no waiting), `linger.ms=20` (batching), `batch.size=65536` (larger batches).

### Question 8: **c**
Idempotent producers use sequence numbers to prevent duplicate messages when retries occur due to network issues or timeouts.

### Question 9: **b**
Without idempotence, the broker doesn't know the message was already written. The retry results in a duplicate message.

### Question 10: **c**
lz4 offers the best balance of compression speed and ratio. It's faster than gzip with similar compression to snappy.

### Question 11: **b**
Kafka distributes partitions evenly among consumers. With 6 partitions and 3 consumers, each gets 2 partitions.

### Question 12: **b**
Consumer lag is the difference between the log-end offset (latest message) and the consumer's committed offset. It indicates how far behind the consumer is.

### Question 13: **b**
`auto.offset.reset=earliest` tells the consumer to start reading from the beginning of the topic when no committed offset exists.

### Question 14: **b**
Manual commits give control over when offsets are committed, enabling exactly-once semantics by committing only after successful processing.

### Question 15: **b**
Rebalancing occurs when a consumer joins or leaves the group, when partitions are added, or when the consumer fails to send heartbeats.

---

### Score interpretation

- **13-15 correct**: Excellent! You have a solid grasp of core concepts. Proceed to Module 3.
- **10-12 correct**: Good understanding. Review the topics you missed before continuing.
- **7-9 correct**: Fair. Re-read the relevant lessons and redo the exercises.
- **Below 7**: Review Module 2 thoroughly before attempting Module 3.

</details>

---

[← Back to Module 2](./README.md) | [Proceed to Module 3 →](../module_3_intermediate/README.md)
