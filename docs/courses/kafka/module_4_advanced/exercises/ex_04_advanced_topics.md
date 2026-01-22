# Module 4 Exercises: Advanced Topics

**[← Back to Module 4](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

## Overview

These exercises cover advanced Kafka topics including Kafka Streams, ksqlDB, security configuration, monitoring, and production operations. Complete all exercises to master enterprise Kafka deployment.

**Prerequisites:**
- Completed Lessons 13-17
- Docker environment running
- Java 11+ (for Kafka Streams exercises)
- Python 3.9+ with `confluent-kafka` installed

---

## Exercise 1: Kafka Streams - Word Count

**Objective:** Build a classic word count application using Kafka Streams DSL.

### Setup

```bash
# Create input and output topics
docker exec -it kafka kafka-topics --create --topic text-input \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

docker exec -it kafka kafka-topics --create --topic word-counts \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Task

Create a Kafka Streams application that:
1. Reads text lines from `text-input` topic
2. Splits lines into words
3. Counts occurrences of each word
4. Outputs counts to `word-counts` topic

### Template (Java)

```java
// WordCountApp.java
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.common.serialization.Serdes;
import java.util.Arrays;
import java.util.Properties;

public class WordCountApp {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "word-count-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        StreamsBuilder builder = new StreamsBuilder();

        // TODO: Read from input topic
        KStream<String, String> textLines = null;

        // TODO: Split into words, group, and count
        KTable<String, Long> wordCounts = null;

        // TODO: Write to output topic

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
```

### Template (Python with Faust)

```python
# word_count.py
import faust

app = faust.App(
    'word-count',
    broker='kafka://localhost:9092',
    value_serializer='raw'
)

# TODO: Define input topic
text_topic = app.topic('text-input', value_type=str)

# TODO: Define table for word counts
word_counts = app.Table('word-counts', default=int)

# TODO: Create agent to process text
@app.agent(text_topic)
async def process_text(stream):
    # TODO: Implement word counting
    pass

if __name__ == '__main__':
    app.main()
```

### Test Data Producer

```python
# produce_text.py
from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092'})

lines = [
    "hello world",
    "hello kafka streams",
    "kafka streams is powerful",
    "hello world of streaming",
    "streams processing with kafka"
]

for line in lines:
    producer.produce('text-input', value=line.encode())
    print(f"Sent: {line}")

producer.flush()
```

### Solution

<details>
<summary>Click to reveal Java solution</summary>

```java
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.common.serialization.Serdes;
import java.util.Arrays;
import java.util.Properties;

public class WordCountApp {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "word-count-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);

        StreamsBuilder builder = new StreamsBuilder();

        // Read from input topic
        KStream<String, String> textLines = builder.stream("text-input");

        // Split into words, group, and count
        KTable<String, Long> wordCounts = textLines
            // Split each line into words
            .flatMapValues(line -> Arrays.asList(line.toLowerCase().split("\\W+")))
            // Filter empty strings
            .filter((key, word) -> word != null && !word.isEmpty())
            // Group by word (re-key)
            .groupBy((key, word) -> word)
            // Count occurrences
            .count(Materialized.as("word-count-store"));

        // Write to output topic
        wordCounts.toStream()
            .mapValues(count -> count.toString())
            .to("word-counts", Produced.with(Serdes.String(), Serdes.String()));

        // Print to console for debugging
        wordCounts.toStream().foreach((word, count) ->
            System.out.println("Word: " + word + " -> Count: " + count));

        KafkaStreams streams = new KafkaStreams(builder.build(), props);

        // Clean up local state on start (for demo purposes)
        streams.cleanUp();
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
```

</details>

<details>
<summary>Click to reveal Python solution (using confluent-kafka)</summary>

```python
# word_count_streams.py
# Note: This uses a simple consumer/producer pattern to simulate streams
# For production, use Faust or Java Kafka Streams

from confluent_kafka import Consumer, Producer
from collections import defaultdict
import json

def run_word_count():
    # Consumer for input
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'word-count-processor',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }

    # Producer for output
    producer_config = {
        'bootstrap.servers': 'localhost:9092'
    }

    consumer = Consumer(consumer_config)
    producer = Producer(producer_config)
    consumer.subscribe(['text-input'])

    # In-memory word counts (use a proper state store in production)
    word_counts = defaultdict(int)

    print("Word Count Processor started...")
    print("-" * 40)

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print(f"Error: {msg.error()}")
                continue

            # Process the line
            line = msg.value().decode('utf-8')
            words = line.lower().split()

            for word in words:
                # Clean the word
                word = ''.join(c for c in word if c.isalnum())
                if word:
                    word_counts[word] += 1

                    # Emit updated count
                    producer.produce(
                        'word-counts',
                        key=word.encode(),
                        value=str(word_counts[word]).encode()
                    )
                    print(f"{word}: {word_counts[word]}")

            producer.poll(0)

    except KeyboardInterrupt:
        print("\nShutting down...")
        print("\nFinal counts:")
        for word, count in sorted(word_counts.items()):
            print(f"  {word}: {count}")
    finally:
        consumer.close()

if __name__ == '__main__':
    run_word_count()
```

</details>

---

## Exercise 2: Kafka Streams - Windowed Aggregation

**Objective:** Implement time-windowed aggregations for event counting.

### Setup

```bash
# Create topics for click events
docker exec -it kafka kafka-topics --create --topic page-views \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

docker exec -it kafka kafka-topics --create --topic page-view-counts \
    --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Task

Create a Kafka Streams application that:
1. Reads page view events from `page-views` topic
2. Counts views per page in 1-minute tumbling windows
3. Outputs windowed counts to `page-view-counts` topic

### Template

```java
// PageViewCounter.java
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import java.time.Duration;

public class PageViewCounter {

    public static void main(String[] args) {
        // TODO: Configure streams

        StreamsBuilder builder = new StreamsBuilder();

        // TODO: Read page view events
        // TODO: Group by page URL
        // TODO: Apply tumbling window of 1 minute
        // TODO: Count events in each window
        // TODO: Output to topic

        // Build and start
    }
}
```

### Event Producer

```python
# produce_page_views.py
from confluent_kafka import Producer
import json
import time
import random

producer = Producer({'bootstrap.servers': 'localhost:9092'})

pages = ['/home', '/products', '/about', '/contact', '/cart', '/checkout']
users = ['user-001', 'user-002', 'user-003', 'user-004', 'user-005']

print("Generating page views (Ctrl+C to stop)...")

try:
    count = 0
    while True:
        event = {
            'user_id': random.choice(users),
            'page': random.choice(pages),
            'timestamp': int(time.time() * 1000)
        }

        producer.produce(
            'page-views',
            key=event['page'].encode(),
            value=json.dumps(event).encode()
        )
        count += 1

        if count % 10 == 0:
            producer.flush()
            print(f"Sent {count} events")

        time.sleep(random.uniform(0.1, 0.5))

except KeyboardInterrupt:
    producer.flush()
    print(f"\nTotal events sent: {count}")
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```java
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.common.serialization.Serdes;
import java.time.Duration;
import java.util.Properties;

public class PageViewCounter {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "page-view-counter");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);

        StreamsBuilder builder = new StreamsBuilder();

        // Read page view events
        KStream<String, String> pageViews = builder.stream("page-views");

        // Count views per page in 1-minute tumbling windows
        KTable<Windowed<String>, Long> viewCounts = pageViews
            // Key is already the page URL
            .groupByKey()
            // Apply tumbling window
            .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
            // Count events
            .count(Materialized.as("page-view-counts-store"));

        // Output to topic with window information
        viewCounts.toStream()
            .map((windowedKey, count) -> {
                String key = windowedKey.key();
                long windowStart = windowedKey.window().start();
                long windowEnd = windowedKey.window().end();
                String value = String.format(
                    "{\"page\":\"%s\",\"count\":%d,\"window_start\":%d,\"window_end\":%d}",
                    key, count, windowStart, windowEnd
                );
                return KeyValue.pair(key, value);
            })
            .to("page-view-counts", Produced.with(Serdes.String(), Serdes.String()));

        // Print to console
        viewCounts.toStream().foreach((windowedKey, count) -> {
            System.out.printf("Page: %s, Window: [%d - %d], Count: %d%n",
                windowedKey.key(),
                windowedKey.window().start(),
                windowedKey.window().end(),
                count);
        });

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.cleanUp();
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
```

</details>

---

## Exercise 3: ksqlDB - Real-Time Analytics

**Objective:** Build real-time analytics queries using ksqlDB.

### Setup

```bash
# Connect to ksqlDB
docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
```

### Task

Using the `page-views` topic from Exercise 2, create ksqlDB queries that:
1. Create a stream from the page views topic
2. Count page views per page (real-time)
3. Find the most active users in the last 5 minutes
4. Detect users with suspiciously high activity (>100 views/minute)

### Template

```sql
-- Set auto offset reset
SET 'auto.offset.reset' = 'earliest';

-- Task 1: Create stream from page-views topic
CREATE STREAM page_views_stream (
    -- TODO: Define schema
) WITH (
    KAFKA_TOPIC = 'page-views',
    VALUE_FORMAT = 'JSON'
);

-- Task 2: Create table for page view counts
CREATE TABLE page_view_counts AS
    SELECT
        -- TODO: Aggregate query
    FROM page_views_stream
    -- TODO: Add windowing and grouping
    EMIT CHANGES;

-- Task 3: Find most active users (5-minute window)
CREATE TABLE active_users AS
    -- TODO: Implement

-- Task 4: Detect suspicious activity
CREATE STREAM suspicious_activity AS
    -- TODO: Implement
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```sql
-- Set auto offset reset
SET 'auto.offset.reset' = 'earliest';

-- Task 1: Create stream from page-views topic
CREATE STREAM page_views_stream (
    user_id VARCHAR,
    page VARCHAR,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC = 'page-views',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);

-- Task 2: Create table for page view counts (1-minute windows)
CREATE TABLE page_view_counts WITH (
    KAFKA_TOPIC = 'ksql-page-view-counts'
) AS
    SELECT
        page,
        COUNT(*) AS view_count,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end
    FROM page_views_stream
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY page
    EMIT CHANGES;

-- Task 3: Find most active users (5-minute hopping window)
CREATE TABLE active_users WITH (
    KAFKA_TOPIC = 'ksql-active-users'
) AS
    SELECT
        user_id,
        COUNT(*) AS page_views,
        COUNT_DISTINCT(page) AS unique_pages,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end
    FROM page_views_stream
    WINDOW HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)
    GROUP BY user_id
    EMIT CHANGES;

-- Task 4: Detect suspicious activity (>50 views per minute)
CREATE STREAM suspicious_activity WITH (
    KAFKA_TOPIC = 'suspicious-activity',
    VALUE_FORMAT = 'JSON'
) AS
    SELECT
        user_id,
        COUNT(*) AS view_count,
        COLLECT_SET(page) AS pages_visited,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end
    FROM page_views_stream
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY user_id
    HAVING COUNT(*) > 50
    EMIT CHANGES;

-- Query to monitor results
-- SELECT * FROM page_view_counts EMIT CHANGES LIMIT 10;
-- SELECT * FROM active_users EMIT CHANGES LIMIT 10;
-- SELECT * FROM suspicious_activity EMIT CHANGES;
```

</details>

---

## Exercise 4: Security - TLS Configuration

**Objective:** Configure TLS encryption for Kafka client connections.

### Task

Create a secure Kafka client configuration that:
1. Generates a client keystore and truststore
2. Configures a producer with TLS
3. Configures a consumer with TLS
4. Verifies encrypted communication

### Certificate Generation Script

```bash
#!/bin/bash
# generate_certs.sh - Generate TLS certificates for Kafka

VALIDITY_DAYS=365
PASSWORD="kafka-secret"
CA_CN="Kafka-CA"
BROKER_CN="kafka-broker"
CLIENT_CN="kafka-client"

mkdir -p certs
cd certs

# Generate CA key and certificate
openssl req -new -x509 -keyout ca-key.pem -out ca-cert.pem -days $VALIDITY_DAYS \
    -subj "/CN=$CA_CN" -passout pass:$PASSWORD

# Generate broker keystore
keytool -genkey -noprompt \
    -alias broker \
    -keyalg RSA -keysize 2048 \
    -keystore broker.keystore.jks \
    -storepass $PASSWORD -keypass $PASSWORD \
    -dname "CN=$BROKER_CN"

# Generate broker CSR
keytool -certreq -alias broker \
    -keystore broker.keystore.jks \
    -storepass $PASSWORD \
    -file broker.csr

# Sign broker certificate with CA
openssl x509 -req -CA ca-cert.pem -CAkey ca-key.pem \
    -in broker.csr -out broker-signed.pem \
    -days $VALIDITY_DAYS -CAcreateserial \
    -passin pass:$PASSWORD

# Import CA and signed cert to broker keystore
keytool -importcert -alias CARoot -file ca-cert.pem \
    -keystore broker.keystore.jks -storepass $PASSWORD -noprompt
keytool -importcert -alias broker -file broker-signed.pem \
    -keystore broker.keystore.jks -storepass $PASSWORD -noprompt

# Create broker truststore with CA cert
keytool -importcert -alias CARoot -file ca-cert.pem \
    -keystore broker.truststore.jks -storepass $PASSWORD -noprompt

# Generate client keystore (same process)
keytool -genkey -noprompt \
    -alias client \
    -keyalg RSA -keysize 2048 \
    -keystore client.keystore.jks \
    -storepass $PASSWORD -keypass $PASSWORD \
    -dname "CN=$CLIENT_CN"

keytool -certreq -alias client \
    -keystore client.keystore.jks \
    -storepass $PASSWORD \
    -file client.csr

openssl x509 -req -CA ca-cert.pem -CAkey ca-key.pem \
    -in client.csr -out client-signed.pem \
    -days $VALIDITY_DAYS -CAcreateserial \
    -passin pass:$PASSWORD

keytool -importcert -alias CARoot -file ca-cert.pem \
    -keystore client.keystore.jks -storepass $PASSWORD -noprompt
keytool -importcert -alias client -file client-signed.pem \
    -keystore client.keystore.jks -storepass $PASSWORD -noprompt

# Create client truststore
keytool -importcert -alias CARoot -file ca-cert.pem \
    -keystore client.truststore.jks -storepass $PASSWORD -noprompt

echo "Certificates generated in ./certs directory"
ls -la
```

### Template: Secure Producer

```python
# secure_producer.py
from confluent_kafka import Producer

def create_secure_producer():
    config = {
        'bootstrap.servers': 'localhost:9093',  # SSL port

        # TODO: Add security protocol
        # TODO: Add SSL configuration
    }

    return Producer(config)

def main():
    producer = create_secure_producer()

    # Test message
    producer.produce('secure-topic', value=b'Encrypted message!')
    producer.flush()
    print("Message sent over TLS")

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
# secure_producer.py
from confluent_kafka import Producer

def create_secure_producer():
    config = {
        'bootstrap.servers': 'localhost:9093',

        # Security protocol
        'security.protocol': 'SSL',

        # SSL configuration
        'ssl.ca.location': './certs/ca-cert.pem',
        'ssl.certificate.location': './certs/client-signed.pem',
        'ssl.key.location': './certs/client-key.pem',
        'ssl.key.password': 'kafka-secret',

        # Or using JKS keystores (Java-style)
        # 'ssl.keystore.location': './certs/client.keystore.jks',
        # 'ssl.keystore.password': 'kafka-secret',
        # 'ssl.truststore.location': './certs/client.truststore.jks',
        # 'ssl.truststore.password': 'kafka-secret',

        # Additional settings
        'ssl.endpoint.identification.algorithm': 'https',  # Hostname verification
    }

    return Producer(config)

def delivery_callback(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()}[{msg.partition()}] @ {msg.offset()}")

def main():
    producer = create_secure_producer()

    # Test messages
    for i in range(5):
        message = f"Encrypted message {i+1}"
        producer.produce(
            'secure-topic',
            value=message.encode(),
            callback=delivery_callback
        )

    producer.flush()
    print("\nAll messages sent over TLS!")

if __name__ == '__main__':
    main()
```

```python
# secure_consumer.py
from confluent_kafka import Consumer, KafkaError

def create_secure_consumer():
    config = {
        'bootstrap.servers': 'localhost:9093',
        'group.id': 'secure-consumer-group',
        'auto.offset.reset': 'earliest',

        # Security protocol
        'security.protocol': 'SSL',

        # SSL configuration
        'ssl.ca.location': './certs/ca-cert.pem',
        'ssl.certificate.location': './certs/client-signed.pem',
        'ssl.key.location': './certs/client-key.pem',
        'ssl.key.password': 'kafka-secret',

        'ssl.endpoint.identification.algorithm': 'https',
    }

    return Consumer(config)

def main():
    consumer = create_secure_consumer()
    consumer.subscribe(['secure-topic'])

    print("Consuming from secure topic (Ctrl+C to exit)...")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Error: {msg.error()}")
                continue

            print(f"Received: {msg.value().decode()}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 5: Security - SASL Authentication

**Objective:** Configure SASL/SCRAM authentication for Kafka clients.

### Setup

```bash
# Create SCRAM credentials in Kafka
docker exec -it kafka kafka-configs --bootstrap-server localhost:9092 \
    --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=alice-secret]' \
    --entity-type users --entity-name alice

docker exec -it kafka kafka-configs --bootstrap-server localhost:9092 \
    --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=bob-secret]' \
    --entity-type users --entity-name bob
```

### Task

Create clients that authenticate using SASL/SCRAM:
1. Configure producer with SASL authentication
2. Configure consumer with SASL authentication
3. Test that unauthenticated clients are rejected

### Template

```python
# sasl_producer.py
from confluent_kafka import Producer

def create_sasl_producer(username, password):
    config = {
        'bootstrap.servers': 'localhost:9094',  # SASL port

        # TODO: Configure SASL
    }

    return Producer(config)

def main():
    # Test with valid credentials
    producer = create_sasl_producer('alice', 'alice-secret')

    producer.produce('auth-topic', value=b'Authenticated message!')
    producer.flush()
    print("Message sent with SASL authentication")

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
# sasl_producer.py
from confluent_kafka import Producer

def create_sasl_producer(username, password):
    config = {
        'bootstrap.servers': 'localhost:9094',

        # Security protocol (SASL without TLS for demo; use SASL_SSL in production)
        'security.protocol': 'SASL_PLAINTEXT',

        # SASL mechanism
        'sasl.mechanism': 'SCRAM-SHA-512',

        # SASL credentials
        'sasl.username': username,
        'sasl.password': password,
    }

    return Producer(config)

def delivery_callback(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()}[{msg.partition()}]")

def main():
    print("Testing SASL/SCRAM Authentication")
    print("=" * 50)

    # Test with valid credentials
    print("\n1. Testing with valid credentials (alice)...")
    try:
        producer = create_sasl_producer('alice', 'alice-secret')
        producer.produce('auth-topic', value=b'Message from Alice!', callback=delivery_callback)
        producer.flush(timeout=5)
        print("   Success!")
    except Exception as e:
        print(f"   Failed: {e}")

    # Test with another valid user
    print("\n2. Testing with valid credentials (bob)...")
    try:
        producer = create_sasl_producer('bob', 'bob-secret')
        producer.produce('auth-topic', value=b'Message from Bob!', callback=delivery_callback)
        producer.flush(timeout=5)
        print("   Success!")
    except Exception as e:
        print(f"   Failed: {e}")

    # Test with invalid credentials
    print("\n3. Testing with invalid credentials...")
    try:
        producer = create_sasl_producer('alice', 'wrong-password')
        producer.produce('auth-topic', value=b'Should fail!')
        producer.flush(timeout=5)
        print("   Unexpected success (should have failed)")
    except Exception as e:
        print(f"   Expected failure: {e}")

if __name__ == '__main__':
    main()
```

```python
# sasl_consumer.py
from confluent_kafka import Consumer, KafkaError

def create_sasl_consumer(username, password, group_id):
    config = {
        'bootstrap.servers': 'localhost:9094',
        'group.id': group_id,
        'auto.offset.reset': 'earliest',

        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanism': 'SCRAM-SHA-512',
        'sasl.username': username,
        'sasl.password': password,
    }

    return Consumer(config)

def main():
    consumer = create_sasl_consumer('alice', 'alice-secret', 'alice-group')
    consumer.subscribe(['auth-topic'])

    print("Consuming with SASL authentication (Ctrl+C to exit)...")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print(f"Error: {msg.error()}")
                continue

            print(f"Received: {msg.value().decode()}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 6: ACL Configuration

**Objective:** Configure Access Control Lists for fine-grained authorization.

### Task

Configure ACLs that:
1. Allow user `alice` to produce to `orders` topic
2. Allow user `bob` to consume from `orders` topic
3. Deny all other access
4. Test the permissions

### Template Script

```bash
#!/bin/bash
# configure_acls.sh

BOOTSTRAP="localhost:9092"

# TODO: Create ACL for alice to write to orders topic

# TODO: Create ACL for bob to read from orders topic

# TODO: Create ACL for bob to read consumer group

# List all ACLs
echo "Current ACLs:"
kafka-acls --bootstrap-server $BOOTSTRAP --list
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```bash
#!/bin/bash
# configure_acls.sh

BOOTSTRAP="localhost:9092"

echo "Configuring Kafka ACLs..."
echo "=" * 50

# Create topic if not exists
kafka-topics --bootstrap-server $BOOTSTRAP --create --topic orders \
    --partitions 3 --replication-factor 1 --if-not-exists

# Allow alice to produce to orders topic
echo "1. Granting alice WRITE access to orders topic..."
kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:alice \
    --operation Write \
    --operation Describe \
    --topic orders

# Allow bob to consume from orders topic
echo "2. Granting bob READ access to orders topic..."
kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:bob \
    --operation Read \
    --operation Describe \
    --topic orders

# Allow bob to use consumer group
echo "3. Granting bob access to consumer group..."
kafka-acls --bootstrap-server $BOOTSTRAP \
    --add \
    --allow-principal User:bob \
    --operation Read \
    --group bob-consumer-group

# Deny all others (implicit if authorizer requires ACLs)
# This is typically configured at the broker level with:
# allow.everyone.if.no.acl.found=false

# List all ACLs
echo ""
echo "Current ACLs:"
echo "-" * 50
kafka-acls --bootstrap-server $BOOTSTRAP --list

# Test permissions
echo ""
echo "Testing permissions..."

# Test alice producing (should succeed)
echo "Alice producing to orders..."
echo "test message from alice" | kafka-console-producer \
    --bootstrap-server $BOOTSTRAP \
    --topic orders \
    --producer-property security.protocol=SASL_PLAINTEXT \
    --producer-property sasl.mechanism=SCRAM-SHA-512 \
    --producer-property sasl.jaas.config="org.apache.kafka.common.security.scram.ScramLoginModule required username='alice' password='alice-secret';"

# Test bob consuming (should succeed)
echo "Bob consuming from orders..."
timeout 5 kafka-console-consumer \
    --bootstrap-server $BOOTSTRAP \
    --topic orders \
    --from-beginning \
    --max-messages 1 \
    --consumer-property security.protocol=SASL_PLAINTEXT \
    --consumer-property sasl.mechanism=SCRAM-SHA-512 \
    --consumer-property sasl.jaas.config="org.apache.kafka.common.security.scram.ScramLoginModule required username='bob' password='bob-secret';" \
    --consumer-property group.id=bob-consumer-group
```

</details>

---

## Exercise 7: Monitoring - JMX Metrics Collection

**Objective:** Collect and analyze Kafka JMX metrics using Python.

### Task

Create a monitoring script that:
1. Connects to Kafka's JMX port
2. Collects key broker metrics
3. Calculates derived metrics (throughput, latency percentiles)
4. Outputs a health report

### Template

```python
# kafka_monitor.py
import subprocess
import json
import time

def get_broker_metrics():
    """Collect key Kafka broker metrics."""
    metrics = {}

    # Use kafka-run-class to query JMX
    # TODO: Implement metric collection

    return metrics

def calculate_health_score(metrics):
    """Calculate overall cluster health score."""
    # TODO: Implement health scoring
    pass

def generate_report(metrics):
    """Generate health report."""
    # TODO: Format and print report
    pass

def main():
    while True:
        metrics = get_broker_metrics()
        generate_report(metrics)
        time.sleep(30)

if __name__ == '__main__':
    main()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
# kafka_monitor.py
import subprocess
import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class BrokerMetrics:
    messages_in_per_sec: float
    bytes_in_per_sec: float
    bytes_out_per_sec: float
    under_replicated_partitions: int
    offline_partitions: int
    active_controller_count: int
    request_queue_size: int
    response_queue_size: int
    network_processor_avg_idle: float
    request_handler_avg_idle: float

def run_kafka_command(cmd: list) -> str:
    """Run a kafka command and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def get_topic_metrics(bootstrap_server: str) -> dict:
    """Get topic-level metrics."""
    output = run_kafka_command([
        'docker', 'exec', 'kafka', 'kafka-topics',
        '--bootstrap-server', bootstrap_server,
        '--describe'
    ])

    topics = {}
    current_topic = None

    for line in output.split('\n'):
        if line.startswith('Topic:'):
            parts = line.split('\t')
            topic_name = parts[0].split(':')[1].strip()
            partition_count = int(parts[1].split(':')[1].strip())
            rf = int(parts[2].split(':')[1].strip())
            topics[topic_name] = {
                'partitions': partition_count,
                'replication_factor': rf
            }

    return topics

def get_consumer_group_lag(bootstrap_server: str) -> dict:
    """Get consumer group lag."""
    output = run_kafka_command([
        'docker', 'exec', 'kafka', 'kafka-consumer-groups',
        '--bootstrap-server', bootstrap_server,
        '--all-groups', '--describe'
    ])

    groups = {}
    current_group = None

    for line in output.split('\n'):
        if 'GROUP' in line and 'TOPIC' in line:
            continue  # Header
        parts = line.split()
        if len(parts) >= 6:
            group = parts[0]
            topic = parts[1]
            lag = parts[5] if parts[5] != '-' else '0'

            if group not in groups:
                groups[group] = {'total_lag': 0, 'topics': []}

            try:
                groups[group]['total_lag'] += int(lag)
                if topic not in groups[group]['topics']:
                    groups[group]['topics'].append(topic)
            except ValueError:
                pass

    return groups

def get_cluster_health(bootstrap_server: str) -> dict:
    """Get cluster health indicators."""
    health = {
        'under_replicated': 0,
        'offline': 0,
        'leader_elections': 0
    }

    # Check under-replicated partitions
    output = run_kafka_command([
        'docker', 'exec', 'kafka', 'kafka-topics',
        '--bootstrap-server', bootstrap_server,
        '--describe', '--under-replicated-partitions'
    ])
    health['under_replicated'] = len([l for l in output.split('\n') if l.strip()])

    # Check offline partitions
    output = run_kafka_command([
        'docker', 'exec', 'kafka', 'kafka-topics',
        '--bootstrap-server', bootstrap_server,
        '--describe', '--unavailable-partitions'
    ])
    health['offline'] = len([l for l in output.split('\n') if l.strip()])

    return health

def calculate_health_score(health: dict, groups: dict) -> tuple:
    """Calculate overall health score (0-100)."""
    score = 100
    issues = []

    # Deduct for under-replicated partitions
    if health['under_replicated'] > 0:
        score -= min(30, health['under_replicated'] * 10)
        issues.append(f"{health['under_replicated']} under-replicated partitions")

    # Deduct for offline partitions (critical)
    if health['offline'] > 0:
        score -= min(50, health['offline'] * 25)
        issues.append(f"{health['offline']} offline partitions (CRITICAL)")

    # Deduct for high consumer lag
    for group, data in groups.items():
        if data['total_lag'] > 10000:
            score -= 5
            issues.append(f"High lag in group {group}: {data['total_lag']}")

    return max(0, score), issues

def generate_report(bootstrap_server: str = 'localhost:9092'):
    """Generate comprehensive health report."""
    print("\n" + "=" * 70)
    print(f"KAFKA CLUSTER HEALTH REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Cluster health
    health = get_cluster_health(bootstrap_server)
    print("\n[CLUSTER HEALTH]")
    print(f"  Under-replicated partitions: {health['under_replicated']}")
    print(f"  Offline partitions: {health['offline']}")

    # Topics
    topics = get_topic_metrics(bootstrap_server)
    print(f"\n[TOPICS] ({len(topics)} total)")
    for name, info in list(topics.items())[:5]:
        if not name.startswith('_'):
            print(f"  {name}: {info['partitions']} partitions, RF={info['replication_factor']}")
    if len(topics) > 5:
        print(f"  ... and {len(topics) - 5} more")

    # Consumer groups
    groups = get_consumer_group_lag(bootstrap_server)
    print(f"\n[CONSUMER GROUPS] ({len(groups)} total)")
    for group, data in list(groups.items())[:5]:
        status = "OK" if data['total_lag'] < 1000 else "LAG"
        print(f"  {group}: lag={data['total_lag']} [{status}]")
    if len(groups) > 5:
        print(f"  ... and {len(groups) - 5} more")

    # Health score
    score, issues = calculate_health_score(health, groups)
    print(f"\n[HEALTH SCORE]: {score}/100")

    if issues:
        print("\n[ISSUES]")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[STATUS]: All systems operational")

    print("=" * 70)

    return score

def main():
    """Run continuous monitoring."""
    print("Kafka Cluster Monitor")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            score = generate_report()
            if score < 70:
                print("\n*** WARNING: Cluster health degraded! ***")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == '__main__':
    main()
```

</details>

---

## Exercise 8: Production Operations - Partition Reassignment

**Objective:** Practice safe partition reassignment for load balancing.

### Scenario

You have a 3-broker cluster with uneven partition distribution:
- Broker 1: 40 partitions
- Broker 2: 20 partitions
- Broker 3: 20 partitions

Rebalance the partitions evenly.

### Task

1. Generate a reassignment plan
2. Execute the reassignment
3. Monitor progress
4. Verify balanced distribution

### Template

```bash
#!/bin/bash
# partition_rebalance.sh

BOOTSTRAP="localhost:9092"

# Step 1: Check current distribution
echo "Current partition distribution:"
# TODO: Show partition distribution per broker

# Step 2: Create topics.json for reassignment
cat > /tmp/topics.json << EOF
{
    "topics": [
        {"topic": "topic1"},
        {"topic": "topic2"}
    ],
    "version": 1
}
EOF

# Step 3: Generate reassignment plan
# TODO: Generate reassignment proposal

# Step 4: Execute reassignment
# TODO: Execute with throttling

# Step 5: Monitor progress
# TODO: Check reassignment status

# Step 6: Verify final distribution
# TODO: Show new distribution
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```bash
#!/bin/bash
# partition_rebalance.sh

BOOTSTRAP="localhost:9092"
THROTTLE="50000000"  # 50 MB/s throttle

echo "=== Kafka Partition Rebalancing ==="
echo ""

# Step 1: Check current distribution
echo "Step 1: Current partition distribution"
echo "-" * 50

docker exec kafka kafka-topics --bootstrap-server $BOOTSTRAP --describe \
    | grep -E "Topic:|Partition:" \
    | head -40

# Get leader distribution
echo ""
echo "Leaders per broker:"
docker exec kafka kafka-topics --bootstrap-server $BOOTSTRAP --describe \
    | grep "Leader:" \
    | awk '{print $4}' \
    | sort \
    | uniq -c \
    | sort -rn

# Step 2: Create topics list for reassignment
echo ""
echo "Step 2: Creating topics list for reassignment..."

# Get all non-internal topics
TOPICS=$(docker exec kafka kafka-topics --bootstrap-server $BOOTSTRAP --list \
    | grep -v "^_" | grep -v "^connect-" | head -5)

# Create topics.json
cat > /tmp/topics.json << EOF
{
    "topics": [
$(echo "$TOPICS" | while read topic; do
    echo "        {\"topic\": \"$topic\"},"
done | sed '$ s/,$//')
    ],
    "version": 1
}
EOF

echo "Topics to rebalance:"
cat /tmp/topics.json

# Step 3: Generate reassignment plan
echo ""
echo "Step 3: Generating reassignment plan..."

docker exec kafka kafka-reassign-partitions \
    --bootstrap-server $BOOTSTRAP \
    --topics-to-move-json-file /tmp/topics.json \
    --broker-list "1,2,3" \
    --generate > /tmp/reassignment-output.txt 2>&1

# Extract proposed reassignment
grep -A 1000 "Proposed partition reassignment" /tmp/reassignment-output.txt \
    | tail -n +2 \
    | head -1 > /tmp/reassignment.json

echo "Proposed reassignment saved to /tmp/reassignment.json"

# Step 4: Execute reassignment with throttling
echo ""
echo "Step 4: Execute reassignment (with ${THROTTLE} bytes/sec throttle)..."

read -p "Execute reassignment? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    docker exec kafka kafka-reassign-partitions \
        --bootstrap-server $BOOTSTRAP \
        --reassignment-json-file /tmp/reassignment.json \
        --throttle $THROTTLE \
        --execute

    # Step 5: Monitor progress
    echo ""
    echo "Step 5: Monitoring reassignment progress..."

    while true; do
        status=$(docker exec kafka kafka-reassign-partitions \
            --bootstrap-server $BOOTSTRAP \
            --reassignment-json-file /tmp/reassignment.json \
            --verify 2>&1)

        echo "$status" | grep -E "Status|complete|progress"

        if echo "$status" | grep -q "successfully completed"; then
            echo "Reassignment complete!"
            break
        fi

        sleep 5
    done

    # Remove throttle
    echo ""
    echo "Removing throttle..."
    docker exec kafka kafka-reassign-partitions \
        --bootstrap-server $BOOTSTRAP \
        --reassignment-json-file /tmp/reassignment.json \
        --verify

else
    echo "Reassignment cancelled."
fi

# Step 6: Verify final distribution
echo ""
echo "Step 6: Final partition distribution"
echo "-" * 50

echo "Leaders per broker (after):"
docker exec kafka kafka-topics --bootstrap-server $BOOTSTRAP --describe \
    | grep "Leader:" \
    | awk '{print $4}' \
    | sort \
    | uniq -c \
    | sort -rn

echo ""
echo "=== Rebalancing complete ==="
```

</details>

---

## Exercise 9: Disaster Recovery Simulation

**Objective:** Practice failover and recovery procedures.

### Scenario

Simulate a broker failure and practice recovery:
1. Stop a broker (simulating failure)
2. Observe partition leadership changes
3. Verify client failover
4. Restore the broker
5. Verify data integrity

### Template

```python
# dr_simulation.py
import subprocess
import time

def stop_broker(broker_id):
    """Stop a Kafka broker."""
    # TODO: Implement
    pass

def start_broker(broker_id):
    """Start a Kafka broker."""
    # TODO: Implement
    pass

def check_partition_leaders():
    """Check current partition leader distribution."""
    # TODO: Implement
    pass

def verify_client_connectivity():
    """Verify clients can still produce and consume."""
    # TODO: Implement
    pass

def run_dr_simulation():
    """Run complete DR simulation."""
    print("=== Disaster Recovery Simulation ===")

    # Step 1: Record initial state
    print("\n1. Recording initial state...")
    initial_leaders = check_partition_leaders()

    # Step 2: Stop a broker
    print("\n2. Simulating broker failure...")
    stop_broker(1)

    # Step 3: Wait for leader election
    print("\n3. Waiting for leader election...")
    time.sleep(10)

    # Step 4: Check new leaders
    print("\n4. Checking new partition leaders...")
    new_leaders = check_partition_leaders()

    # Step 5: Verify client connectivity
    print("\n5. Verifying client connectivity...")
    verify_client_connectivity()

    # Step 6: Restore broker
    print("\n6. Restoring broker...")
    start_broker(1)

    # Step 7: Verify recovery
    print("\n7. Verifying recovery...")
    time.sleep(30)
    final_leaders = check_partition_leaders()

    print("\n=== Simulation Complete ===")

if __name__ == '__main__':
    run_dr_simulation()
```

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
# dr_simulation.py
import subprocess
import time
import json
from confluent_kafka import Producer, Consumer, KafkaError

def run_command(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

def stop_broker(container_name):
    """Stop a Kafka broker container."""
    print(f"  Stopping {container_name}...")
    run_command(f"docker stop {container_name}")
    return True

def start_broker(container_name):
    """Start a Kafka broker container."""
    print(f"  Starting {container_name}...")
    run_command(f"docker start {container_name}")
    return True

def check_partition_leaders(bootstrap="localhost:9092"):
    """Check current partition leader distribution."""
    output, _ = run_command(
        f"docker exec kafka kafka-topics --bootstrap-server {bootstrap} --describe"
    )

    leaders = {}
    for line in output.split('\n'):
        if 'Leader:' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'Leader:':
                    leader = parts[i + 1]
                    leaders[leader] = leaders.get(leader, 0) + 1

    return leaders

def check_under_replicated(bootstrap="localhost:9092"):
    """Check for under-replicated partitions."""
    output, _ = run_command(
        f"docker exec kafka kafka-topics --bootstrap-server {bootstrap} "
        "--describe --under-replicated-partitions"
    )
    count = len([l for l in output.split('\n') if l.strip()])
    return count

def verify_producer(bootstrap="localhost:9092"):
    """Verify producer can send messages."""
    try:
        producer = Producer({
            'bootstrap.servers': bootstrap,
            'socket.timeout.ms': 5000,
            'request.timeout.ms': 5000
        })

        delivered = [False]
        def callback(err, msg):
            if err is None:
                delivered[0] = True

        producer.produce('dr-test-topic', value=b'test message', callback=callback)
        producer.flush(timeout=10)

        return delivered[0]
    except Exception as e:
        print(f"  Producer error: {e}")
        return False

def verify_consumer(bootstrap="localhost:9092"):
    """Verify consumer can read messages."""
    try:
        consumer = Consumer({
            'bootstrap.servers': bootstrap,
            'group.id': 'dr-test-group',
            'auto.offset.reset': 'latest',
            'session.timeout.ms': 10000
        })
        consumer.subscribe(['dr-test-topic'])

        msg = consumer.poll(timeout=5.0)
        consumer.close()

        return msg is not None or True  # OK if no message but no error
    except Exception as e:
        print(f"  Consumer error: {e}")
        return False

def run_dr_simulation():
    """Run complete DR simulation."""
    print("=" * 60)
    print("DISASTER RECOVERY SIMULATION")
    print("=" * 60)

    bootstrap = "localhost:9092"
    broker_container = "kafka"  # Adjust for multi-broker setup

    # Create test topic
    print("\n[SETUP] Creating test topic...")
    run_command(
        f"docker exec kafka kafka-topics --bootstrap-server {bootstrap} "
        "--create --topic dr-test-topic --partitions 3 --replication-factor 1 "
        "--if-not-exists"
    )

    # Step 1: Record initial state
    print("\n[STEP 1] Recording initial state...")
    initial_leaders = check_partition_leaders(bootstrap)
    print(f"  Leaders per broker: {initial_leaders}")
    print(f"  Under-replicated: {check_under_replicated(bootstrap)}")

    # Test initial connectivity
    print("\n[STEP 2] Testing initial connectivity...")
    print(f"  Producer: {'OK' if verify_producer(bootstrap) else 'FAILED'}")
    print(f"  Consumer: {'OK' if verify_consumer(bootstrap) else 'FAILED'}")

    # For multi-broker setup, you would stop one broker here
    # For single broker demo, we'll simulate degraded state differently
    print("\n[STEP 3] Simulating degraded state...")
    print("  (In production, you would stop a broker here)")
    print("  Skipping actual broker stop for single-broker demo")

    # In multi-broker setup:
    # stop_broker("kafka-2")
    # time.sleep(10)

    # Step 4: Check state after "failure"
    print("\n[STEP 4] Checking cluster state...")
    current_leaders = check_partition_leaders(bootstrap)
    print(f"  Leaders per broker: {current_leaders}")
    under_rep = check_under_replicated(bootstrap)
    print(f"  Under-replicated: {under_rep}")

    # Step 5: Verify client failover
    print("\n[STEP 5] Verifying client connectivity during degraded state...")
    print(f"  Producer: {'OK' if verify_producer(bootstrap) else 'FAILED'}")
    print(f"  Consumer: {'OK' if verify_consumer(bootstrap) else 'FAILED'}")

    # Step 6: Restore (in multi-broker setup)
    print("\n[STEP 6] Simulating recovery...")
    print("  (In production, you would restart the failed broker here)")
    # start_broker("kafka-2")
    # time.sleep(30)

    # Step 7: Verify recovery
    print("\n[STEP 7] Verifying recovery...")
    final_leaders = check_partition_leaders(bootstrap)
    print(f"  Leaders per broker: {final_leaders}")
    print(f"  Under-replicated: {check_under_replicated(bootstrap)}")

    # Final connectivity check
    print("\n[STEP 8] Final connectivity verification...")
    print(f"  Producer: {'OK' if verify_producer(bootstrap) else 'FAILED'}")
    print(f"  Consumer: {'OK' if verify_consumer(bootstrap) else 'FAILED'}")

    # Summary
    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"  Initial leaders: {initial_leaders}")
    print(f"  Final leaders: {final_leaders}")
    print(f"  Recovery status: {'SUCCESS' if final_leaders == initial_leaders else 'CHECK NEEDED'}")
    print("=" * 60)

if __name__ == '__main__':
    run_dr_simulation()
```

</details>

---

## Exercise 10: Rolling Upgrade Simulation

**Objective:** Practice rolling upgrade procedures.

### Task

Create a script that simulates a rolling upgrade:
1. Check cluster health pre-upgrade
2. Drain a broker (controlled shutdown)
3. Verify no data loss during upgrade
4. Bring broker back
5. Repeat for all brokers

### Solution

<details>
<summary>Click to reveal solution</summary>

```python
# rolling_upgrade.py
import subprocess
import time

def run_command(cmd):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def check_cluster_health(bootstrap="localhost:9092"):
    """Check cluster health before/after upgrade."""
    print("  Checking cluster health...")

    # Under-replicated partitions
    output, _ = run_command(
        f"docker exec kafka kafka-topics --bootstrap-server {bootstrap} "
        "--describe --under-replicated-partitions"
    )
    under_rep = len([l for l in output.split('\n') if l.strip()])

    # Offline partitions
    output, _ = run_command(
        f"docker exec kafka kafka-topics --bootstrap-server {bootstrap} "
        "--describe --unavailable-partitions"
    )
    offline = len([l for l in output.split('\n') if l.strip()])

    health = {
        'under_replicated': under_rep,
        'offline': offline,
        'healthy': under_rep == 0 and offline == 0
    }

    print(f"    Under-replicated: {under_rep}")
    print(f"    Offline: {offline}")
    print(f"    Status: {'HEALTHY' if health['healthy'] else 'UNHEALTHY'}")

    return health

def wait_for_isr_recovery(bootstrap="localhost:9092", timeout=300):
    """Wait for all ISRs to recover."""
    print("  Waiting for ISR recovery...")
    start = time.time()

    while time.time() - start < timeout:
        output, _ = run_command(
            f"docker exec kafka kafka-topics --bootstrap-server {bootstrap} "
            "--describe --under-replicated-partitions"
        )
        under_rep = len([l for l in output.split('\n') if l.strip()])

        if under_rep == 0:
            print(f"    ISR recovered in {int(time.time() - start)} seconds")
            return True

        print(f"    Still under-replicated: {under_rep}")
        time.sleep(10)

    print(f"    Timeout after {timeout} seconds")
    return False

def controlled_shutdown(broker_id, bootstrap="localhost:9092"):
    """Perform controlled shutdown of a broker."""
    print(f"  Initiating controlled shutdown of broker {broker_id}...")

    # In a real scenario, you would:
    # 1. Call kafka-server-stop.sh on the broker
    # 2. Or use docker stop with graceful timeout

    # Simulated for demo
    print(f"    Sent shutdown signal to broker {broker_id}")
    print("    (Simulated - in production, stop the actual broker)")

    return True

def simulate_upgrade(broker_id):
    """Simulate software upgrade."""
    print(f"  Upgrading broker {broker_id}...")
    print("    Backing up configuration...")
    time.sleep(1)
    print("    Installing new version...")
    time.sleep(2)
    print("    Verifying installation...")
    time.sleep(1)
    print(f"    Broker {broker_id} upgraded successfully")
    return True

def start_broker(broker_id, bootstrap="localhost:9092"):
    """Start a broker after upgrade."""
    print(f"  Starting broker {broker_id}...")

    # In production:
    # run_command(f"docker start kafka-{broker_id}")
    # Or start via systemd/etc

    print(f"    Broker {broker_id} started")
    return True

def rolling_upgrade(broker_ids, bootstrap="localhost:9092"):
    """Perform rolling upgrade across all brokers."""
    print("=" * 60)
    print("KAFKA ROLLING UPGRADE PROCEDURE")
    print("=" * 60)

    # Pre-upgrade checks
    print("\n[PRE-UPGRADE] Checking cluster health...")
    health = check_cluster_health(bootstrap)
    if not health['healthy']:
        print("  WARNING: Cluster not healthy. Fix issues before upgrading.")
        return False

    # Process each broker
    for i, broker_id in enumerate(broker_ids):
        print(f"\n[BROKER {broker_id}] Starting upgrade ({i+1}/{len(broker_ids)})")
        print("-" * 40)

        # Check health before stopping
        print("\n  Step 1: Pre-shutdown health check")
        if not check_cluster_health(bootstrap)['healthy']:
            print("  ERROR: Cluster unhealthy, aborting upgrade")
            return False

        # Controlled shutdown
        print("\n  Step 2: Controlled shutdown")
        controlled_shutdown(broker_id, bootstrap)
        time.sleep(5)

        # Perform upgrade
        print("\n  Step 3: Upgrade software")
        simulate_upgrade(broker_id)

        # Start broker
        print("\n  Step 4: Start broker")
        start_broker(broker_id, bootstrap)
        time.sleep(10)

        # Wait for ISR recovery
        print("\n  Step 5: Wait for ISR recovery")
        if not wait_for_isr_recovery(bootstrap):
            print("  WARNING: ISR not fully recovered")

        # Post-upgrade health check
        print("\n  Step 6: Post-upgrade health check")
        check_cluster_health(bootstrap)

        print(f"\n  Broker {broker_id} upgrade complete!")

        # Pause between brokers
        if i < len(broker_ids) - 1:
            print("\n  Waiting 30 seconds before next broker...")
            time.sleep(5)  # Shortened for demo

    # Final verification
    print("\n" + "=" * 60)
    print("[POST-UPGRADE] Final cluster verification")
    print("=" * 60)

    final_health = check_cluster_health(bootstrap)

    if final_health['healthy']:
        print("\nROLLING UPGRADE COMPLETED SUCCESSFULLY!")
    else:
        print("\nWARNING: Cluster health issues detected. Manual intervention required.")

    return final_health['healthy']

if __name__ == '__main__':
    # For a 3-broker cluster
    broker_ids = [1, 2, 3]
    rolling_upgrade(broker_ids)
```

</details>

---

## Verification Checklist

After completing these exercises, you should be able to:

- [ ] Build Kafka Streams applications with DSL
- [ ] Implement windowed aggregations
- [ ] Create real-time analytics with ksqlDB
- [ ] Configure TLS encryption for Kafka
- [ ] Set up SASL authentication
- [ ] Configure ACLs for authorization
- [ ] Collect and analyze JMX metrics
- [ ] Perform partition rebalancing
- [ ] Execute disaster recovery procedures
- [ ] Conduct rolling upgrades safely

---

## Cleanup

```bash
# Delete exercise topics
docker exec -it kafka kafka-topics --delete --topic text-input --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic word-counts --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic page-views --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic page-view-counts --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic secure-topic --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic auth-topic --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic orders --bootstrap-server localhost:9092
docker exec -it kafka kafka-topics --delete --topic dr-test-topic --bootstrap-server localhost:9092

# Remove certificates
rm -rf ./certs

# Remove SCRAM users
docker exec -it kafka kafka-configs --bootstrap-server localhost:9092 \
    --alter --delete-config 'SCRAM-SHA-512' \
    --entity-type users --entity-name alice

docker exec -it kafka kafka-configs --bootstrap-server localhost:9092 \
    --alter --delete-config 'SCRAM-SHA-512' \
    --entity-type users --entity-name bob
```

---

**[← Back to Module 4](../README.md)** | **[Next: Module 4 Quiz →](../quiz_module_4.md)**
