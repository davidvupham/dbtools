# Module 4 Quiz: Advanced Topics

Test your understanding of Kafka Streams, ksqlDB, security, monitoring, and production operations.

**Passing Score:** 80% (12/15 correct)

---

## Instructions

1. Read each question carefully
2. Select the best answer for each question
3. Check your answers against the answer key at the bottom
4. Review explanations for any questions you missed

---

## Questions

### Question 1: Kafka Streams Architecture

What is the relationship between partitions and tasks in Kafka Streams?

A) Each task processes all partitions of a topic
B) Each task processes exactly one partition from each input topic
C) Tasks and partitions have no relationship
D) Multiple tasks always share the same partition

---

### Question 2: KStream vs KTable

Which statement correctly describes the difference between KStream and KTable?

A) KStream represents a changelog, KTable represents an event stream
B) KStream is for batch processing, KTable is for stream processing
C) KStream treats each record as an independent event, KTable treats records as updates to keys
D) KStream stores state, KTable is stateless

---

### Question 3: Kafka Streams State Stores

Where does Kafka Streams persist its state stores for fault tolerance?

A) In an external database like PostgreSQL
B) In a Kafka topic (changelog topic)
C) In ZooKeeper
D) Only in local memory (no persistence)

---

### Question 4: ksqlDB Query Types

What is the difference between a push query and a pull query in ksqlDB?

A) Push queries use SELECT, pull queries use EMIT
B) Push queries return a static result, pull queries return continuous updates
C) Push queries continuously stream results, pull queries return a point-in-time result
D) There is no difference; they are aliases

---

### Question 5: ksqlDB Stream-Table Join

When joining a stream to a table in ksqlDB, what happens if the table key doesn't exist at the time of the stream event?

A) The join fails with an error
B) The stream event is buffered until the table key appears
C) The result includes NULL values for the table fields
D) The stream event is dropped completely

---

### Question 6: Kafka Security Protocols

Which security protocol provides both encryption and authentication?

A) PLAINTEXT
B) SSL
C) SASL_PLAINTEXT
D) SASL_SSL

---

### Question 7: SASL Mechanisms

Which SASL mechanism is recommended for production environments without Kerberos infrastructure?

A) PLAIN (with TLS)
B) SCRAM-SHA-512
C) GSSAPI
D) ANONYMOUS

---

### Question 8: Kafka ACLs

Which ACL operation is required for a consumer to read from a topic?

A) Write
B) Read
C) Describe
D) Both B and C

---

### Question 9: Critical Monitoring Metrics

Which metric indicates a potential data loss risk that requires immediate attention?

A) MessagesInPerSec
B) UnderReplicatedPartitions
C) BytesOutPerSec
D) ActiveControllerCount

---

### Question 10: Consumer Lag Monitoring

What does high consumer lag typically indicate?

A) Producers are sending messages too fast
B) The topic has too many partitions
C) Consumers are processing messages slower than they're being produced
D) The broker has insufficient disk space

---

### Question 11: JMX Metrics Export

What is the standard approach for exporting Kafka JMX metrics to Prometheus?

A) Configure Kafka to write directly to Prometheus
B) Use the JMX Exporter as a Java agent
C) Prometheus natively supports JMX
D) Use Kafka Connect with a Prometheus sink

---

### Question 12: Capacity Planning

When calculating storage requirements for a Kafka cluster, which factor is NOT typically included?

A) Message throughput rate
B) Retention period
C) Replication factor
D) Consumer count

---

### Question 13: Rolling Upgrades

During a rolling upgrade, what should you verify before stopping each broker?

A) That all topics have auto.create.topics.enable=true
B) That there are no under-replicated partitions
C) That all consumers are stopped
D) That the broker has the highest broker.id

---

### Question 14: MirrorMaker 2

What does MirrorMaker 2 replicate by default (when configured for replication)?

A) Only topic data
B) Topic data, consumer offsets, and topic configurations
C) Only consumer offsets
D) Only topic configurations

---

### Question 15: Production Best Practices

Which configuration should be set to FALSE in production to prevent potential data loss?

A) auto.create.topics.enable
B) unclean.leader.election.enable
C) log.cleaner.enable
D) Both A and B

---

## Answer Key

<details>
<summary>Click to reveal answers</summary>

### Answers

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **B** | In Kafka Streams, each task is assigned exactly one partition from each input topic. Tasks are the unit of parallelism. |
| 2 | **C** | KStream represents an unbounded stream where each record is an independent event. KTable represents a changelog where records with the same key are updates (upserts). |
| 3 | **B** | Kafka Streams persists state to changelog topics in Kafka. This enables fault tolerance - if a task fails, it can rebuild its state from the changelog. |
| 4 | **C** | Push queries (with EMIT CHANGES) continuously stream results as data changes. Pull queries return the current state at a point in time, like a traditional database query. |
| 5 | **C** | In a left stream-table join, if the table key doesn't exist, the result includes NULL values for the table's columns. The stream event is not dropped. |
| 6 | **D** | SASL_SSL provides both authentication (via SASL) and encryption (via SSL/TLS). SSL alone provides encryption but uses certificates for auth. SASL_PLAINTEXT provides auth without encryption. |
| 7 | **B** | SCRAM-SHA-512 is the recommended mechanism for production. It provides strong authentication with salted challenge-response, doesn't require Kerberos, and credentials are stored securely. |
| 8 | **D** | Consumers need both Read (to fetch messages) and Describe (to get topic metadata like partition count) operations on the topic resource. |
| 9 | **B** | UnderReplicatedPartitions > 0 indicates replicas are falling behind, which can lead to data loss if the leader fails. This requires immediate investigation. |
| 10 | **C** | Consumer lag measures the difference between the latest produced offset and the consumer's current offset. High lag means consumers can't keep up with the production rate. |
| 11 | **B** | The JMX Exporter runs as a Java agent attached to the Kafka broker process. It exposes JMX metrics in Prometheus format on an HTTP endpoint. |
| 12 | **D** | Storage calculation: throughput × retention × replication factor. Consumer count affects read bandwidth but not storage requirements (consumers don't create data). |
| 13 | **B** | Before stopping a broker, verify no under-replicated partitions exist. This ensures all replicas are in sync, so stopping the broker won't risk data loss or availability. |
| 14 | **B** | MirrorMaker 2 replicates topic data, consumer group offsets (via checkpoints), and topic configurations. This enables full cluster failover with offset translation. |
| 15 | **D** | Both should be FALSE: auto.create.topics.enable prevents accidental topic creation; unclean.leader.election.enable=false prevents electing an out-of-sync replica as leader. |

### Scoring

| Score | Result |
|-------|--------|
| 15/15 | Excellent! You've mastered advanced Kafka topics |
| 12-14/15 | Good! You understand the key concepts |
| 9-11/15 | Review the topics you missed |
| Below 9 | Consider re-reading the module lessons |

</details>

---

## Topics to Review If Needed

If you struggled with certain questions, review these sections:

| Questions | Topic | Lesson |
|-----------|-------|--------|
| 1-3 | Kafka Streams architecture and state | [Lesson 13](./13_kafka_streams.md) |
| 4-5 | ksqlDB queries and joins | [Lesson 14](./14_ksqldb.md) |
| 6-8 | Security protocols and ACLs | [Lesson 15](./15_security.md) |
| 9-11 | Monitoring and metrics | [Lesson 16](./16_monitoring.md) |
| 12-15 | Production operations | [Lesson 17](./17_production_ops.md) |

---

## Navigation

- **Previous:** [Lesson 17: Production Operations](./17_production_ops.md)
- **Next:** [Module 4 Exercises](./exercises/)
- **Module Home:** [Module 4: Advanced Topics](./README.md)
