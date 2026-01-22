# Exercises — Module 1: Kafka Foundations

**[← Back to Module 1](../README.md)**

## Learning objectives

After completing these exercises, you will be able to:
- Create, describe, and manage Kafka topics
- Produce and consume messages using CLI tools
- Work with message keys and partitions
- Understand consumer group behavior
- Troubleshoot common issues

---

## Exercise 1: Topic management (Warm-up)

**Bloom Level:** Apply

Create and manage topics using the Kafka CLI.

**Tasks:**

1. Create a topic called `customer-events` with 4 partitions
2. Create a topic called `audit-logs` with 2 partitions and retention of 24 hours (86400000 ms)
3. List all topics in your cluster
4. Describe the `customer-events` topic
5. Increase `customer-events` to 6 partitions
6. Delete the `audit-logs` topic

**Hints:**
```bash
# Topic creation
kafka-topics --bootstrap-server localhost:9092 --create --topic <name> --partitions <n>

# With configuration
--config retention.ms=<value>

# Alter partitions
--alter --partitions <n>

# Delete topic
--delete --topic <name>
```

---

## Exercise 2: Basic produce and consume (Practice)

**Bloom Level:** Apply

Practice sending and receiving messages.

**Tasks:**

1. Start a consumer on `customer-events` that shows messages from the beginning
2. In another terminal, start a producer for `customer-events`
3. Send 5 messages: "Event 1", "Event 2", "Event 3", "Event 4", "Event 5"
4. Verify all messages appear in the consumer
5. Stop both producer and consumer
6. Start a new consumer WITHOUT `--from-beginning` and send 2 more messages
7. Verify only the new messages appear

**Expected observation:** Without `--from-beginning`, consumers only see new messages.

---

## Exercise 3: Keyed messages (Practice)

**Bloom Level:** Apply

Understand how keys affect partition assignment.

**Tasks:**

1. Create a topic `user-activity` with 3 partitions
2. Start a producer with key parsing enabled
3. Send these messages (format key:value):
   ```
   alice:login
   bob:login
   alice:view_page
   charlie:login
   bob:purchase
   alice:logout
   bob:logout
   ```
4. Consume all messages showing partition numbers
5. Verify that all messages for the same user are in the same partition

**Questions to answer:**
- Are all "alice" messages in the same partition?
- Are all "bob" messages in the same partition?
- What happens if you send a message without a key?

---

## Exercise 4: Consumer groups (Practice)

**Bloom Level:** Analyze

Explore consumer group behavior.

**Setup:**
```bash
# Create a topic with 4 partitions
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic group-test --partitions 4
```

**Tasks:**

1. Open 3 terminal windows
2. Start a consumer in each terminal, all using group `test-group`:
   ```bash
   docker exec -it kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic group-test \
     --group test-group \
     --property print.partition=true
   ```
3. In a 4th terminal, produce 20 messages
4. Observe which consumer receives which partitions

**Questions to answer:**
- How are partitions distributed among consumers?
- What happens when you stop one consumer?
- What happens if you add a 5th consumer?

---

## Exercise 5: Consumer lag investigation (Analyze)

**Bloom Level:** Analyze

Learn to monitor consumer health.

**Tasks:**

1. Create topic `lag-test` with 2 partitions
2. Start a consumer group `slow-consumer` and immediately stop it (Ctrl+C)
3. Produce 100 messages to `lag-test`
4. Check the consumer group lag:
   ```bash
   docker exec -it kafka kafka-consumer-groups \
     --bootstrap-server localhost:9092 \
     --describe --group slow-consumer
   ```
5. Start the consumer again and watch the lag decrease
6. Produce messages faster than the consumer can process (use a loop)
7. Monitor the lag growth

**Questions to answer:**
- What does a LAG of 100 mean?
- How can you tell if a consumer is keeping up?
- What might cause lag in production?

---

## Exercise 6: Offset manipulation (Analyze)

**Bloom Level:** Analyze

Practice resetting consumer offsets.

**Tasks:**

1. Using the `lag-test` topic from Exercise 5
2. Reset the `slow-consumer` group to the earliest offset:
   ```bash
   docker exec -it kafka kafka-consumer-groups \
     --bootstrap-server localhost:9092 \
     --group slow-consumer \
     --topic lag-test \
     --reset-offsets --to-earliest --execute
   ```
3. Consume some messages, then stop
4. Reset to offset 50:
   ```bash
   --reset-offsets --to-offset 50 --execute
   ```
5. Reset to the latest offset
6. Try resetting to a specific timestamp (use current time)

**Questions to answer:**
- When would you reset to earliest?
- When would you reset to a specific offset?
- What's the risk of resetting offsets in production?

---

## Exercise 7: Multi-topic consumption (Practice)

**Bloom Level:** Apply

Consume from multiple topics simultaneously.

**Tasks:**

1. Create topics: `orders`, `payments`, `shipments` (2 partitions each)
2. Produce different messages to each topic
3. Start a consumer that subscribes to all three topics:
   ```bash
   docker exec -it kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --whitelist "orders|payments|shipments" \
     --from-beginning \
     --property print.topic=true
   ```
4. Verify messages from all topics are received

---

## Exercise 8: Partition exploration (Analyze)

**Bloom Level:** Analyze

Deep dive into partition internals.

**Tasks:**

1. Create topic `partition-explore` with 3 partitions
2. Produce 10 keyed messages
3. Check the offset for each partition:
   ```bash
   docker exec -it kafka kafka-run-class kafka.tools.GetOffsetShell \
     --broker-list localhost:9092 \
     --topic partition-explore
   ```
4. Consume only from partition 0
5. Consume only from partition 1 starting at offset 2
6. Compare message counts across partitions

**Questions to answer:**
- Are messages evenly distributed?
- What affects distribution when using keys?

---

## Exercise 9: Topic configuration (Practice)

**Bloom Level:** Apply

Modify topic-level configurations.

**Tasks:**

1. Create topic `config-test` with default settings
2. View current configuration:
   ```bash
   docker exec -it kafka kafka-configs \
     --bootstrap-server localhost:9092 \
     --entity-type topics \
     --entity-name config-test \
     --describe
   ```
3. Set retention to 1 hour (3600000 ms)
4. Set max message size to 2MB (2097152 bytes)
5. Enable log compaction:
   ```bash
   --alter --add-config cleanup.policy=compact
   ```
6. Revert retention to default by deleting the override

---

## Exercise 10: Troubleshooting scenarios (Challenge)

**Bloom Level:** Evaluate

Diagnose and fix common issues.

### Scenario A: Missing messages
A consumer reports missing messages. Investigate:
1. Check consumer group offsets
2. Verify the consumer is using the correct group ID
3. Check if `auto.offset.reset` is set correctly
4. Verify messages exist in the topic

### Scenario B: Uneven consumption
One consumer is processing more messages than others:
1. Check partition distribution in the consumer group
2. Verify partition count vs consumer count
3. Look for consumer lag on specific partitions

### Scenario C: High latency
Messages are delayed:
1. Check consumer lag
2. Verify broker health (check logs)
3. Check if partitions are evenly distributed

---

## Solutions

<details>
<summary>Click to reveal Exercise 1 solution</summary>

```bash
# 1. Create customer-events
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic customer-events --partitions 4

# 2. Create audit-logs with retention
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic audit-logs --partitions 2 \
  --config retention.ms=86400000

# 3. List topics
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 --list

# 4. Describe customer-events
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe --topic customer-events

# 5. Increase partitions
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --alter --topic customer-events --partitions 6

# 6. Delete audit-logs
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete --topic audit-logs
```

</details>

<details>
<summary>Click to reveal Exercise 3 solution</summary>

```bash
# 1. Create topic
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic user-activity --partitions 3

# 2-3. Producer with keys
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic user-activity \
  --property parse.key=true \
  --property key.separator=:

# Type:
# alice:login
# bob:login
# alice:view_page
# charlie:login
# bob:purchase
# alice:logout
# bob:logout

# 4. Consume with partition info
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user-activity \
  --from-beginning \
  --property print.key=true \
  --property print.partition=true

# Answers:
# - Yes, all "alice" messages are in the same partition
# - Yes, all "bob" messages are in the same partition
# - Messages without keys use round-robin distribution
```

</details>

---

[← Back to Module 1](../README.md) | [View Project →](../project_1_cli_tool.md)
