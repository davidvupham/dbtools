# Kafka Troubleshooting Guide

**[← Back to Course Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Troubleshooting-orange)

## Table of contents

- [Quick diagnostics](#quick-diagnostics)
- [Connection issues](#connection-issues)
- [Producer issues](#producer-issues)
- [Consumer issues](#consumer-issues)
- [Performance issues](#performance-issues)
- [Docker issues](#docker-issues)
- [Common error messages](#common-error-messages)

---

## Quick diagnostics

Run these commands first to understand your cluster state:

```bash
# Check if Kafka is running
docker exec -it kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# List topics
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check consumer groups
docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Describe a topic
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic <topic>

# Check under-replicated partitions
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --under-replicated-partitions

# View container logs
docker logs kafka --tail 100
```

---

## Connection issues

### Cannot connect to Kafka

**Symptoms:**
- `Connection refused`
- `Broker not available`
- `Network is unreachable`

**Diagnosis:**
```bash
# 1. Check if Kafka container is running
docker ps | grep kafka

# 2. Check container health
docker inspect kafka --format='{{.State.Health.Status}}'

# 3. Test port connectivity
nc -zv localhost 9092

# 4. Check logs for errors
docker logs kafka | grep -i error
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Container not running | `docker compose up -d` |
| Port conflict | Check `lsof -i :9092`, stop conflicting service |
| Wrong bootstrap server | Use `localhost:9092` from host, `kafka:29092` from Docker |
| Firewall blocking | Check firewall rules for port 9092 |

### Connection from inside Docker network

If connecting from another container, use the internal address:

```python
# From host machine
config = {'bootstrap.servers': 'localhost:9092'}

# From Docker network
config = {'bootstrap.servers': 'kafka:29092'}
```

---

## Producer issues

### Messages not being delivered

**Diagnosis:**
```python
# Add delivery callback to see errors
def delivery_callback(err, msg):
    if err:
        print(f"FAILED: {err}")
    else:
        print(f"SUCCESS: {msg.topic()}[{msg.partition()}]@{msg.offset()}")

producer.produce(topic, value, callback=delivery_callback)
producer.flush()  # Wait for delivery
```

**Common causes:**

| Symptom | Cause | Solution |
|---------|-------|----------|
| `BufferError` | Buffer full | Increase `buffer.memory` or call `poll()` |
| `Timeout` | Broker unreachable | Check connection, increase `request.timeout.ms` |
| `SerializationError` | Invalid data | Check schema compatibility |
| `TopicNotFound` | Topic doesn't exist | Create topic or enable auto-create |

### Slow producer

```bash
# Check producer metrics
# In your application, log these periodically:
# - batch-size-avg
# - record-send-rate
# - request-latency-avg
```

**Tuning tips:**
```python
config = {
    'bootstrap.servers': 'localhost:9092',
    'batch.size': 65536,       # Larger batches
    'linger.ms': 20,           # Wait for batch fill
    'compression.type': 'lz4', # Compress
    'acks': 1                  # Reduce durability for speed
}
```

---

## Consumer issues

### Consumer not receiving messages

**Diagnosis:**
```bash
# 1. Check if messages exist in topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic <topic> \
  --from-beginning \
  --max-messages 5

# 2. Check consumer group status
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group <group-id>
```

**Common causes:**

| Symptom | Cause | Solution |
|---------|-------|----------|
| No messages | Wrong `auto.offset.reset` | Set to `earliest` for new groups |
| No messages | Consumer started after production | Use `--from-beginning` |
| Stuck consumer | Processing timeout | Increase `max.poll.interval.ms` |
| Only some messages | Wrong partition assignment | Check consumer group members |

### High consumer lag

```bash
# Check lag
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group <group-id>
```

**Solutions:**

1. **Add more consumers** (up to partition count)
2. **Increase batch size**: `max.poll.records`
3. **Reduce processing time** per message
4. **Scale partitions** (requires topic recreation)

### Consumer group rebalancing constantly

**Symptoms:**
- `Rebalancing` messages in logs
- Consumers dropping and rejoining

**Causes and solutions:**

| Cause | Solution |
|-------|----------|
| Processing takes too long | Increase `max.poll.interval.ms` |
| Network issues | Increase `session.timeout.ms` |
| Consumer crashes | Check application logs |
| Too many consumers | Reduce consumers or add partitions |

---

## Performance issues

### Low throughput

**Diagnosis:**
```bash
# Produce test messages and measure
docker exec -it kafka kafka-producer-perf-test \
  --topic test-perf \
  --num-records 100000 \
  --record-size 1000 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092
```

**Tuning checklist:**

| Area | Check | Optimization |
|------|-------|--------------|
| Producer | Batch size | Increase `batch.size` to 64KB+ |
| Producer | Linger | Set `linger.ms=10-50` |
| Producer | Compression | Enable `lz4` |
| Consumer | Fetch size | Increase `fetch.min.bytes` |
| Broker | Threads | Increase `num.io.threads` |
| Hardware | Disk I/O | Use SSD, check iostat |

### High latency

**Diagnosis:**
```bash
# Check end-to-end latency
docker exec -it kafka kafka-run-class kafka.tools.EndToEndLatency \
  localhost:9092 test-latency 10000 all 1
```

**Optimization tips:**

```python
# Low latency producer
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 1,
    'linger.ms': 0,
    'batch.size': 16384
}

# Low latency consumer
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'low-latency-group',
    'fetch.min.bytes': 1,
    'fetch.max.wait.ms': 100
}
```

---

## Docker issues

### Container won't start

```bash
# Check logs
docker logs kafka

# Check resources
docker stats

# Verify docker-compose.yml
docker compose config
```

**Common fixes:**

| Error | Solution |
|-------|----------|
| OOM killed | Increase Docker memory |
| Port in use | Stop conflicting service or change port |
| Volume permission | `chmod` volume directory |
| Invalid config | Validate `docker-compose.yml` |

### Reset environment

```bash
# Stop and remove everything
docker compose down -v

# Remove orphan containers
docker container prune

# Clean volumes
docker volume prune

# Restart fresh
docker compose up -d
```

---

## Common error messages

### `LEADER_NOT_AVAILABLE`

**Cause:** Topic/partition doesn't have an elected leader.

```bash
# Check topic state
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic <topic>

# Wait for election or restart broker
docker restart kafka
```

### `NOT_ENOUGH_REPLICAS`

**Cause:** `min.insync.replicas` cannot be satisfied.

```bash
# Check ISR
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic <topic>

# For development, reduce min.insync.replicas
docker exec -it kafka kafka-configs \
  --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name <topic> \
  --alter --add-config min.insync.replicas=1
```

### `OFFSET_OUT_OF_RANGE`

**Cause:** Consumer offset no longer exists (data deleted).

```bash
# Reset to earliest
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group <group-id> \
  --topic <topic> \
  --reset-offsets \
  --to-earliest \
  --execute
```

### `UNKNOWN_TOPIC_OR_PARTITION`

**Cause:** Topic doesn't exist or still being created.

```bash
# Create topic
docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic <topic> \
  --partitions 3 \
  --replication-factor 1
```

---

## Getting help

If you're still stuck:

1. **Check logs**: `docker logs kafka --tail 200`
2. **Search errors**: Copy the exact error message
3. **Review configuration**: Validate all settings
4. **Community resources**:
   - [Apache Kafka Users Mailing List](https://kafka.apache.org/contact)
   - [Confluent Community Forum](https://forum.confluent.io/)
   - [Stack Overflow - kafka tag](https://stackoverflow.com/questions/tagged/apache-kafka)

---

[↑ Back to Table of Contents](#table-of-contents)
