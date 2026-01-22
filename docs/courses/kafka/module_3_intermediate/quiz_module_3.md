# Module 3 Quiz: Intermediate Kafka

**[← Back to Module 3](./README.md)**

> **Passing Score:** 80% (12/15 correct)
> **Time Limit:** 25 minutes

---

## Instructions

Answer all 15 questions. Each question has one correct answer unless otherwise specified. Check your answers at the end.

---

## Questions

### Kafka Connect

**1. What is the primary purpose of Kafka Connect?**

A) To monitor Kafka cluster health
B) To stream data between Kafka and external systems
C) To manage Kafka topic configurations
D) To compress Kafka messages

---

**2. In Kafka Connect, what is the difference between a Source and Sink connector?**

A) Source writes to Kafka, Sink reads from Kafka
B) Source reads from Kafka, Sink writes to Kafka
C) Source is for databases, Sink is for files
D) There is no difference, they are interchangeable

---

**3. What happens when `errors.tolerance` is set to `all` in a Kafka Connect sink connector?**

A) The connector stops on any error
B) Errors are logged and processing continues
C) Errors are automatically retried forever
D) All errors are sent to the input topic

---

**4. Which of the following is NOT a valid Kafka Connect deployment mode?**

A) Standalone
B) Distributed
C) Clustered
D) Both A and B are valid modes

---

### Schema Registry

**5. What does Schema Registry store along with schemas?**

A) The actual message data
B) A unique schema ID for each version
C) Consumer group offsets
D) Kafka topic configurations

---

**6. What is the default schema compatibility mode in Schema Registry?**

A) FORWARD
B) FULL
C) BACKWARD
D) NONE

---

**7. Which schema change is BACKWARD compatible in Avro?**

A) Renaming a field
B) Changing a field's type from int to string
C) Adding a new field with a default value
D) Removing a required field without a default

---

**8. In BACKWARD compatibility mode, which component should be upgraded first?**

A) Producers
B) Consumers
C) Brokers
D) Schema Registry

---

### Serialization

**9. Which serialization format typically produces the smallest message size?**

A) JSON
B) Avro
C) Plain text
D) XML

---

**10. What is included in an Avro-serialized Kafka message value?**

A) The complete schema and data
B) Only the data, schema is in the topic
C) A magic byte, schema ID, and data
D) Compressed JSON with schema reference

---

**11. Which Avro type would you use for an optional string field?**

A) `"type": "string?"`
B) `"type": "optional<string>"`
C) `"type": ["null", "string"]`
D) `"type": "string", "required": false`

---

**12. When should you prefer Protobuf over Avro?**

A) When you need the smallest message size
B) When integrating with gRPC services
C) When using Kafka Connect
D) When schema evolution is critical

---

### Exactly-Once Semantics

**13. What does an idempotent producer guarantee?**

A) Messages are delivered exactly once end-to-end
B) No duplicate messages within a single producer session
C) Transactions across multiple topics
D) Consumer offset management

---

**14. Which configuration is required for a transactional producer?**

A) `acks=1`
B) `transactional.id` set to a unique value
C) `enable.auto.commit=true`
D) `max.in.flight.requests.per.connection=1`

---

**15. What isolation level should a consumer use to only read committed transactional messages?**

A) `read_uncommitted`
B) `read_committed`
C) `serializable`
D) `repeatable_read`

---

## Answer Key

<details>
<summary>Click to reveal answers</summary>

### Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | **B** | Kafka Connect is specifically designed to stream data between Kafka and external systems like databases, file systems, and cloud services. |
| 2 | **A** | Source connectors read from external systems and write TO Kafka. Sink connectors read FROM Kafka and write to external systems. |
| 3 | **B** | With `errors.tolerance=all`, Connect logs errors and continues processing. Failed records can optionally be sent to a dead letter queue. |
| 4 | **C** | Kafka Connect has two modes: Standalone (single worker) and Distributed (multiple workers). "Clustered" is not a mode name. |
| 5 | **B** | Schema Registry assigns a unique ID to each schema version. This ID is embedded in messages instead of the full schema. |
| 6 | **C** | BACKWARD is the default, meaning new schemas can read old data. Consumers can be upgraded before producers. |
| 7 | **C** | Adding a field with a default value is backward compatible because old data (without the field) can use the default. |
| 8 | **B** | In BACKWARD compatibility, new schemas read old data, so consumers (readers) should be upgraded first. |
| 9 | **B** | Avro (binary format) produces the smallest messages, typically 75-80% smaller than JSON for the same data. |
| 10 | **C** | Avro messages contain: magic byte (1 byte), schema ID (4 bytes), and the binary-encoded data. The full schema is fetched from the registry. |
| 11 | **C** | Avro uses union types for optional fields. `["null", "string"]` means the field can be null or a string. |
| 12 | **B** | Protobuf is preferred when integrating with gRPC services since it's the native serialization format for gRPC. |
| 13 | **B** | Idempotent producers prevent duplicates within a single session using producer ID and sequence numbers. Cross-session requires transactions. |
| 14 | **B** | A unique `transactional.id` is required for transactional producers. This ID survives restarts and enables exactly-once. |
| 15 | **B** | `read_committed` isolation level ensures consumers only see messages from committed transactions. Uncommitted or aborted messages are skipped. |

### Scoring

| Score | Result |
|-------|--------|
| 15/15 | Excellent! Ready for Module 4 |
| 12-14 | Passed! Review missed topics |
| 9-11 | Almost there - review and retake |
| 0-8 | Review lessons before retaking |

</details>

---

## Next Steps

- **Passed?** Continue to [Module 4: Advanced →](../module_4_advanced/README.md)
- **Need review?** Revisit the lessons:
  - [Kafka Connect](./09_kafka_connect.md)
  - [Schema Registry](./10_schema_registry.md)
  - [Serialization Formats](./11_serialization.md)
  - [Exactly-Once Semantics](./12_exactly_once.md)

---

**[← Back to Module 3](./README.md)**
