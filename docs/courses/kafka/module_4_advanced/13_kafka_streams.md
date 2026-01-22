# Lesson 13: Kafka Streams

**[← Back to Module 4](./README.md)** | **[Next: ksqlDB →](./14_ksqldb.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Kafka_Streams-blue)

## Overview

Kafka Streams is a client library for building real-time streaming applications. Unlike external processing frameworks, Kafka Streams runs as part of your application with no separate cluster required.

**Learning objectives:**
- Understand Kafka Streams architecture and concepts
- Build stream processing applications with the DSL
- Implement stateful operations (aggregations, joins, windowing)
- Handle time semantics and late-arriving data

**Prerequisites:** Module 3 completed, Java basics

**Estimated time:** 60 minutes

---

## Table of contents

- [Why Kafka Streams](#why-kafka-streams)
- [Architecture](#architecture)
- [Core concepts](#core-concepts)
- [Streams DSL](#streams-dsl)
- [Stateful operations](#stateful-operations)
- [Windowing](#windowing)
- [Error handling](#error-handling)
- [Testing](#testing)
- [Hands-on exercises](#hands-on-exercises)
- [Key takeaways](#key-takeaways)

---

## Why Kafka Streams

### Comparison with other frameworks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAM PROCESSING OPTIONS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KAFKA STREAMS                                                              │
│  ─────────────                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Your Application (JVM)                                              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │              Kafka Streams Library                           │    │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │    │   │
│  │  │  │ Task 0  │  │ Task 1  │  │ Task 2  │  │ Task 3  │        │    │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • No separate cluster needed                                               │
│  • Scales by adding more application instances                              │
│  • Exactly-once processing built-in                                         │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  APACHE FLINK / SPARK STREAMING                                             │
│  ──────────────────────────────                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Separate Processing Cluster                                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker 4 │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  • Separate cluster to manage                                               │
│  • More powerful for complex analytics                                      │
│  • Better for batch + stream unified processing                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to use Kafka Streams

| Use Case | Kafka Streams | Flink/Spark |
|----------|---------------|-------------|
| Simple transformations | ✓ Best | Overkill |
| Enrichment/filtering | ✓ Best | Overkill |
| Real-time aggregations | ✓ Good | ✓ Good |
| Complex event processing | Possible | ✓ Better |
| ML model serving | Possible | ✓ Better |
| Batch + stream unified | Limited | ✓ Best |
| Operational simplicity | ✓ Best | More complex |

---

## Architecture

### Topology and tasks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA STREAMS ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TOPOLOGY (Processing Graph)                                                │
│  ───────────────────────────                                                │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   SOURCE    │────►│  PROCESSOR  │────►│    SINK     │                   │
│  │  (orders)   │     │  (enrich)   │     │ (enriched)  │                   │
│  └─────────────┘     └──────┬──────┘     └─────────────┘                   │
│                             │                                               │
│                             ▼                                               │
│                      ┌─────────────┐                                       │
│                      │   STATE     │                                       │
│                      │   STORE     │                                       │
│                      └─────────────┘                                       │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  TASKS (Parallelism Unit)                                                   │
│  ────────────────────────                                                   │
│                                                                             │
│  Input Topic: orders (4 partitions)                                         │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                              │
│  │  P0    │ │  P1    │ │  P2    │ │  P3    │                              │
│  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘                              │
│       │          │          │          │                                    │
│       ▼          ▼          ▼          ▼                                    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                              │
│  │ Task 0 │ │ Task 1 │ │ Task 2 │ │ Task 3 │  ← 4 tasks = 4 partitions   │
│  └────────┘ └────────┘ └────────┘ └────────┘                              │
│                                                                             │
│  Tasks distributed across application instances                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scaling model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HORIZONTAL SCALING                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1 Instance (handles all 4 tasks):                                          │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Instance 1: [Task 0] [Task 1] [Task 2] [Task 3]                   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  2 Instances (tasks redistributed):                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐          │
│  │  Instance 1: [Task 0] [Task 1]│  │  Instance 2: [Task 2] [Task 3]│       │
│  └─────────────────────────────┘  └─────────────────────────────┘          │
│                                                                             │
│  4 Instances (maximum parallelism):                                         │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐                  │
│  │Instance 1 │ │Instance 2 │ │Instance 3 │ │Instance 4 │                  │
│  │ [Task 0]  │ │ [Task 1]  │ │ [Task 2]  │ │ [Task 3]  │                  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘                  │
│                                                                             │
│  NOTE: Max parallelism = number of input partitions                         │
│  More instances than partitions = idle instances                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core concepts

### KStream vs KTable

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KSTREAM vs KTABLE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KSTREAM (Event Stream)                                                     │
│  ──────────────────────                                                     │
│  Each record is an independent event                                        │
│  All records matter (append-only log)                                       │
│                                                                             │
│  Time: ──────────────────────────────────────────────────────►              │
│  Key A: [+$10] ──────► [+$20] ──────► [+$5] ──────►                        │
│                                                                             │
│  Use for: Events, logs, transactions                                        │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  KTABLE (Changelog Stream)                                                  │
│  ─────────────────────────                                                  │
│  Each record is an update to a key                                          │
│  Only latest value per key matters                                          │
│                                                                             │
│  Time: ──────────────────────────────────────────────────────►              │
│  Key A: [balance=$10] ──► [balance=$30] ──► [balance=$35]                  │
│                                              ▲                              │
│                                              │                              │
│                                         Current state                       │
│                                                                             │
│  Use for: User profiles, account balances, inventory                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### GlobalKTable

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KTABLE vs GLOBALKTABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KTABLE (Partitioned)                                                       │
│  ─────────────────────                                                      │
│  Each task has subset of data                                               │
│                                                                             │
│  Task 0: [A, B, C]     Task 1: [D, E, F]     Task 2: [G, H, I]             │
│                                                                             │
│  Joins: Only works with co-partitioned data                                 │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  GLOBALKTABLE (Replicated)                                                  │
│  ─────────────────────────                                                  │
│  Each task has ALL data                                                     │
│                                                                             │
│  Task 0: [A-I]         Task 1: [A-I]         Task 2: [A-I]                 │
│                                                                             │
│  Joins: Works with any key (no co-partitioning needed)                      │
│  Tradeoff: More memory, slower startup                                      │
│                                                                             │
│  Use for: Small reference data (countries, product catalog)                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Streams DSL

### Basic application structure

```java
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;

import java.util.Properties;

public class OrderProcessingApp {

    public static void main(String[] args) {
        // 1. Configure the application
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-processing-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG,
                  Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG,
                  Serdes.String().getClass());

        // 2. Build the topology
        StreamsBuilder builder = new StreamsBuilder();

        KStream<String, String> orders = builder.stream("orders");

        orders
            .filter((key, value) -> value.contains("\"status\":\"confirmed\""))
            .mapValues(value -> enrichOrder(value))
            .to("enriched-orders");

        // 3. Create and start the streams application
        KafkaStreams streams = new KafkaStreams(builder.build(), props);

        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));

        streams.start();
    }

    private static String enrichOrder(String order) {
        // Add enrichment logic
        return order;
    }
}
```

### Common DSL operations

```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Order> orders = builder.stream("orders");

// FILTER - Keep only matching records
KStream<String, Order> confirmedOrders = orders
    .filter((key, order) -> order.getStatus().equals("CONFIRMED"));

// MAP - Transform key and/or value
KStream<String, OrderEvent> orderEvents = orders
    .map((key, order) -> KeyValue.pair(
        order.getCustomerId(),
        new OrderEvent(order, "RECEIVED")
    ));

// MAPVALUES - Transform value only (more efficient, preserves partitioning)
KStream<String, EnrichedOrder> enrichedOrders = orders
    .mapValues(order -> enrichWithCustomerData(order));

// FLATMAP - One input to zero or more outputs
KStream<String, OrderItem> orderItems = orders
    .flatMapValues(order -> order.getItems());

// BRANCH - Split stream based on predicates
KStream<String, Order>[] branches = orders.branch(
    (key, order) -> order.getAmount() > 1000,  // High value
    (key, order) -> order.getAmount() > 100,   // Medium value
    (key, order) -> true                        // Low value (default)
);
KStream<String, Order> highValueOrders = branches[0];
KStream<String, Order> mediumValueOrders = branches[1];
KStream<String, Order> lowValueOrders = branches[2];

// MERGE - Combine multiple streams
KStream<String, Order> allOrders = highValueOrders
    .merge(mediumValueOrders)
    .merge(lowValueOrders);

// SELECTKEY - Change the key
KStream<String, Order> byCustomer = orders
    .selectKey((key, order) -> order.getCustomerId());

// PEEK - Side effects (logging, metrics)
orders.peek((key, order) ->
    logger.info("Processing order: {}", order.getId()));

// THROUGH - Write to intermediate topic (repartition)
KStream<String, Order> repartitioned = orders
    .through("orders-by-customer");

// TO - Write to output topic (terminal operation)
enrichedOrders.to("enriched-orders");
```

### Serialization (Serdes)

```java
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import io.confluent.kafka.streams.serdes.avro.SpecificAvroSerde;

// Built-in Serdes
Serde<String> stringSerde = Serdes.String();
Serde<Long> longSerde = Serdes.Long();
Serde<byte[]> bytesSerde = Serdes.ByteArray();

// JSON Serde (custom)
Serde<Order> orderSerde = new JsonSerde<>(Order.class);

// Avro Serde (with Schema Registry)
Map<String, String> serdeConfig = Map.of(
    "schema.registry.url", "http://localhost:8081"
);
SpecificAvroSerde<Order> avroOrderSerde = new SpecificAvroSerde<>();
avroOrderSerde.configure(serdeConfig, false);

// Using Serdes in stream operations
KStream<String, Order> orders = builder.stream(
    "orders",
    Consumed.with(Serdes.String(), orderSerde)
);

orders.to(
    "processed-orders",
    Produced.with(Serdes.String(), orderSerde)
);
```

---

## Stateful operations

### Aggregations

```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Order> orders = builder.stream("orders");

// COUNT - Count records per key
KTable<String, Long> ordersPerCustomer = orders
    .groupByKey()
    .count(Materialized.as("orders-per-customer-store"));

// REDUCE - Combine values
KTable<String, Order> latestOrderPerCustomer = orders
    .groupByKey()
    .reduce(
        (order1, order2) -> order2,  // Keep latest
        Materialized.as("latest-order-store")
    );

// AGGREGATE - Custom aggregation
KTable<String, CustomerStats> customerStats = orders
    .groupBy((key, order) -> order.getCustomerId())
    .aggregate(
        // Initializer
        CustomerStats::new,
        // Aggregator
        (customerId, order, stats) -> {
            stats.incrementOrderCount();
            stats.addToTotalSpent(order.getAmount());
            return stats;
        },
        Materialized.<String, CustomerStats, KeyValueStore<Bytes, byte[]>>as("customer-stats")
            .withKeySerde(Serdes.String())
            .withValueSerde(customerStatsSerde)
    );

// Query the state store
ReadOnlyKeyValueStore<String, CustomerStats> store =
    streams.store(
        StoreQueryParameters.fromNameAndType(
            "customer-stats",
            QueryableStoreTypes.keyValueStore()
        )
    );
CustomerStats stats = store.get("customer-123");
```

### Joins

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    JOIN TYPES                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  KSTREAM-KSTREAM JOIN (Windowed)                                            │
│  ───────────────────────────────                                            │
│  Joins events within a time window                                          │
│                                                                             │
│  Orders Stream    Payments Stream                                           │
│  ─────────────    ───────────────                                           │
│  [order-1, t1]    [payment-1, t2]  → Joined if |t1-t2| < window            │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  KSTREAM-KTABLE JOIN                                                        │
│  ───────────────────                                                        │
│  Enriches stream events with table lookups                                  │
│                                                                             │
│  Orders Stream    Customers Table                                           │
│  ─────────────    ───────────────                                           │
│  [order-1]   ───► [customer lookup] → EnrichedOrder                        │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  KTABLE-KTABLE JOIN                                                         │
│  ─────────────────                                                          │
│  Joins two changelog streams by key                                         │
│                                                                             │
│  Users Table      Addresses Table                                           │
│  ───────────      ───────────────                                           │
│  [user-1]    ───► [address-1]      → UserWithAddress                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

```java
// KStream-KStream Join (windowed)
KStream<String, Order> orders = builder.stream("orders");
KStream<String, Payment> payments = builder.stream("payments");

KStream<String, OrderWithPayment> ordersWithPayments = orders.join(
    payments,
    (order, payment) -> new OrderWithPayment(order, payment),
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)),
    StreamJoined.with(Serdes.String(), orderSerde, paymentSerde)
);

// KStream-KTable Join (enrichment)
KStream<String, Order> orders = builder.stream("orders");
KTable<String, Customer> customers = builder.table("customers");

KStream<String, EnrichedOrder> enrichedOrders = orders
    .selectKey((key, order) -> order.getCustomerId())
    .join(
        customers,
        (order, customer) -> new EnrichedOrder(order, customer)
    );

// KStream-GlobalKTable Join (no repartitioning needed)
GlobalKTable<String, Product> products = builder.globalTable("products");

KStream<String, OrderWithProduct> ordersWithProducts = orders.join(
    products,
    (orderId, order) -> order.getProductId(),  // Key extractor
    (order, product) -> new OrderWithProduct(order, product)
);
```

---

## Windowing

### Window types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WINDOW TYPES                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TUMBLING WINDOW (Fixed, non-overlapping)                                   │
│  ─────────────────────────────────────────                                  │
│  │ Window 1  │ Window 2  │ Window 3  │                                     │
│  ├───────────┼───────────┼───────────┤                                     │
│  0          10          20          30  (seconds)                           │
│                                                                             │
│  Use: Hourly/daily aggregations, batch-like processing                      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  HOPPING WINDOW (Fixed, overlapping)                                        │
│  ───────────────────────────────────                                        │
│  │ Window 1      │                                                         │
│  ├───────────────┤                                                         │
│       │ Window 2      │                                                    │
│       ├───────────────┤                                                    │
│            │ Window 3      │                                               │
│  0    5   10   15   20   25   30  (seconds)                                │
│                                                                             │
│  Window size: 15s, Advance: 5s                                              │
│  Use: Moving averages, sliding metrics                                      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  SESSION WINDOW (Dynamic, activity-based)                                   │
│  ────────────────────────────────────────                                   │
│  │Session 1│         │Session 2        │      │Session 3│                  │
│  ├─────────┤         ├─────────────────┤      ├─────────┤                  │
│  ●  ●  ●             ●     ●  ●  ●            ●   ●                        │
│                                                                             │
│  Inactivity gap: 5 minutes                                                  │
│  Use: User sessions, clickstreams                                           │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  SLIDING WINDOW (For joins only)                                            │
│  ───────────────────────────────                                            │
│  Window starts at each event timestamp                                      │
│  Use: Stream-stream joins within time difference                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Windowed aggregations

```java
// Tumbling window - Orders per customer per hour
KTable<Windowed<String>, Long> hourlyOrderCounts = orders
    .groupBy((key, order) -> order.getCustomerId())
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
    .count(Materialized.as("hourly-order-counts"));

// Hopping window - 5-minute averages, updated every minute
KTable<Windowed<String>, Double> movingAverage = orders
    .groupBy((key, order) -> order.getProductId())
    .windowedBy(TimeWindows.ofSizeAndGrace(
        Duration.ofMinutes(5),
        Duration.ofMinutes(1)
    ).advanceBy(Duration.ofMinutes(1)))
    .aggregate(
        () -> new AverageAggregator(),
        (key, order, agg) -> agg.add(order.getAmount()),
        Materialized.as("moving-average")
    )
    .mapValues(AverageAggregator::getAverage);

// Session window - User session activity
KTable<Windowed<String>, Long> sessionActivity = clickEvents
    .groupBy((key, click) -> click.getUserId())
    .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(30)))
    .count(Materialized.as("session-activity"));

// Extract window information
hourlyOrderCounts.toStream().foreach((windowedKey, count) -> {
    String customerId = windowedKey.key();
    Window window = windowedKey.window();
    Instant start = Instant.ofEpochMilli(window.start());
    Instant end = Instant.ofEpochMilli(window.end());
    System.out.printf("Customer %s had %d orders between %s and %s%n",
        customerId, count, start, end);
});
```

### Grace period for late data

```java
// Allow late events up to 10 minutes after window closes
TimeWindows windowSpec = TimeWindows
    .ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(10));

KTable<Windowed<String>, Long> counts = orders
    .groupByKey()
    .windowedBy(windowSpec)
    .count();

// Without grace period - late events are dropped
TimeWindows strictWindow = TimeWindows
    .ofSizeWithNoGrace(Duration.ofHours(1));
```

---

## Error handling

### Deserialization errors

```java
// Configure deserialization exception handler
props.put(
    StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
    LogAndContinueExceptionHandler.class  // Log and skip bad records
);

// Or fail fast
props.put(
    StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
    LogAndFailExceptionHandler.class  // Fail the stream task
);

// Custom handler
public class CustomDeserializationHandler implements DeserializationExceptionHandler {
    @Override
    public DeserializationHandlerResponse handle(
            ProcessorContext context,
            ConsumerRecord<byte[], byte[]> record,
            Exception exception) {

        // Log the error
        logger.error("Deserialization error for record: {}", record, exception);

        // Send to dead letter topic
        producer.send(new ProducerRecord<>("deserialization-errors",
            record.key(), record.value()));

        return DeserializationHandlerResponse.CONTINUE;
    }
}
```

### Production errors

```java
// Configure production exception handler
props.put(
    StreamsConfig.DEFAULT_PRODUCTION_EXCEPTION_HANDLER_CLASS_CONFIG,
    DefaultProductionExceptionHandler.class
);

// Custom handler
public class CustomProductionHandler implements ProductionExceptionHandler {
    @Override
    public ProductionExceptionHandlerResponse handle(
            ProducerRecord<byte[], byte[]> record,
            Exception exception) {

        if (exception instanceof RecordTooLargeException) {
            // Skip oversized records
            return ProductionExceptionHandlerResponse.CONTINUE;
        }

        // Fail for other errors
        return ProductionExceptionHandlerResponse.FAIL;
    }
}
```

### Uncaught exceptions

```java
// Set uncaught exception handler
streams.setUncaughtExceptionHandler((thread, exception) -> {
    logger.error("Uncaught exception in thread {}", thread.getName(), exception);

    // Return action
    if (exception instanceof RetriableException) {
        return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.REPLACE_THREAD;
    }
    return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.SHUTDOWN_APPLICATION;
});
```

---

## Testing

### TopologyTestDriver

```java
import org.apache.kafka.streams.TopologyTestDriver;
import org.apache.kafka.streams.TestInputTopic;
import org.apache.kafka.streams.TestOutputTopic;

public class OrderProcessingTest {

    private TopologyTestDriver testDriver;
    private TestInputTopic<String, Order> inputTopic;
    private TestOutputTopic<String, EnrichedOrder> outputTopic;

    @BeforeEach
    void setup() {
        // Build the topology
        StreamsBuilder builder = new StreamsBuilder();
        buildTopology(builder);  // Your topology building code

        // Create test driver
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "test-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:9092");

        testDriver = new TopologyTestDriver(builder.build(), props);

        // Create test topics
        inputTopic = testDriver.createInputTopic(
            "orders",
            new StringSerializer(),
            new OrderSerializer()
        );

        outputTopic = testDriver.createOutputTopic(
            "enriched-orders",
            new StringDeserializer(),
            new EnrichedOrderDeserializer()
        );
    }

    @AfterEach
    void teardown() {
        testDriver.close();
    }

    @Test
    void testOrderEnrichment() {
        // Given
        Order order = new Order("ORD-1", "CUST-1", 99.99);

        // When
        inputTopic.pipeInput("ORD-1", order);

        // Then
        EnrichedOrder result = outputTopic.readValue();
        assertNotNull(result);
        assertEquals("ORD-1", result.getOrderId());
        assertNotNull(result.getCustomerName());
    }

    @Test
    void testWindowedAggregation() {
        // Pipe multiple events with timestamps
        inputTopic.pipeInput("key1", order1, Instant.parse("2026-01-01T10:00:00Z"));
        inputTopic.pipeInput("key1", order2, Instant.parse("2026-01-01T10:30:00Z"));
        inputTopic.pipeInput("key1", order3, Instant.parse("2026-01-01T11:30:00Z"));

        // Verify output
        List<KeyValue<Windowed<String>, Long>> results = outputTopic.readKeyValuesToList();
        assertEquals(2, results.size());  // Two hourly windows
    }
}
```

---

## Hands-on exercises

### Exercise 1: Word count

Build a classic word count application:

```java
// TODO: Complete the word count topology
StreamsBuilder builder = new StreamsBuilder();

KStream<String, String> textLines = builder.stream("text-input");

KTable<String, Long> wordCounts = textLines
    // TODO: Split lines into words
    // TODO: Group by word
    // TODO: Count occurrences
    ;

wordCounts.toStream().to("word-counts");
```

### Exercise 2: Order enrichment

Enrich orders with customer data from a KTable:

```java
// TODO: Join orders stream with customers table
// Add customer name and email to each order
```

### Exercise 3: Windowed aggregation

Calculate hourly sales totals per product:

```java
// TODO: Create a tumbling window aggregation
// Sum order amounts per product per hour
```

---

## Key takeaways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA STREAMS KEY TAKEAWAYS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✓ Kafka Streams is a library, not a cluster - runs in your JVM            │
│                                                                             │
│  ✓ Scale by adding more application instances                              │
│                                                                             │
│  ✓ Use KStream for events, KTable for state/changelog                      │
│                                                                             │
│  ✓ GlobalKTable for small reference data that needs non-key joins          │
│                                                                             │
│  ✓ Stateful operations use local state stores (RocksDB)                    │
│                                                                             │
│  ✓ Exactly-once semantics available with processing.guarantee config       │
│                                                                             │
│  ✓ Use TopologyTestDriver for unit testing - no Kafka cluster needed       │
│                                                                             │
│  ✓ Configure error handlers for production resilience                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**[← Back to Module 4](./README.md)** | **[Next: ksqlDB →](./14_ksqldb.md)**

[↑ Back to Top](#lesson-13-kafka-streams)
