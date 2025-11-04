# GDS SNMP Receiver - Architecture & Design

## Overview

The GDS SNMP Receiver is designed as a robust, production-ready service that bridges SNMP-based monitoring systems with modern message queue architectures. This document explains the architectural decisions, design patterns, and technical implementation details.

---

## Design Goals

### 1. Reliability
- **Persistent messaging**: All published messages survive RabbitMQ restarts
- **Connection recovery**: Automatic reconnection on network failures
- **Graceful degradation**: Continue receiving traps even if RabbitMQ is temporarily unavailable
- **Signal handling**: Clean shutdown on SIGTERM/SIGINT

### 2. Observability
- **Structured logging**: All operations logged with appropriate levels
- **Debug mode**: Detailed varbind parsing and payload inspection
- **Idempotency keys**: SHA-256 hashes enable duplicate detection
- **Readiness markers**: Container health checks and E2E test coordination

### 3. Compatibility
- **Multi-version pysnmp**: Supports both asynsock (6.x) and asyncio (7.x) backends
- **SNMPv2c**: Industry-standard trap format
- **Docker-ready**: First-class container support with non-root user

### 4. Maintainability
- **Object-oriented design**: Single `SNMPReceiver` class encapsulates all logic
- **Type hints**: Full type annotations for IDE support
- **Documentation**: Comprehensive docstrings and tutorials
- **Testability**: E2E test framework included

---

## System Architecture

### Component Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    SNMPReceiver Class                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────┐    ┌──────────────────┐               │
│  │  SNMP Engine    │    │  RabbitMQ Client │               │
│  │  (pysnmp)       │    │  (pika)          │               │
│  ├─────────────────┤    ├──────────────────┤               │
│  │ • UDP Socket    │    │ • Connection     │               │
│  │ • Transport     │    │ • Channel        │               │
│  │ • Dispatcher    │    │ • Queue          │               │
│  │ • Callback Reg  │    │ • Publisher      │               │
│  └────────┬────────┘    └────────┬─────────┘               │
│           │                      │                         │
│           └──────────┬───────────┘                         │
│                      │                                     │
│              ┌───────▼────────┐                            │
│              │  Trap Handler  │                            │
│              │  (_trap_callback)                           │
│              ├────────────────┤                            │
│              │ • Parse varbinds                            │
│              │ • Extract alert name                        │
│              │ • Generate idempotency key                  │
│              │ • Build JSON payload                        │
│              │ • Publish to queue                          │
│              └────────────────┘                            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Network Packet (UDP)
   ↓
2. OS Socket Buffer
   ↓
3. pysnmp Transport (asyncio/asynsock)
   ↓
4. pysnmp Dispatcher (select/asyncio loop)
   ↓
5. Community String Authentication
   ↓
6. Varbind Decoding (ASN.1 BER)
   ↓
7. Callback Invocation (_trap_callback)
   ↓
8. Varbind Normalization (OID → string)
   ↓
9. Payload Construction (dict → JSON)
   ↓
10. RabbitMQ Publish (pika basic_publish)
    ↓
11. RabbitMQ Queue Persistence
```

---

## Key Design Patterns

### 1. Facade Pattern

The `SNMPReceiver` class provides a simple interface that hides complex pysnmp and pika APIs:

```python
# Simple external API
receiver = SNMPReceiver(...)
receiver.run()  # Everything is handled internally

# Instead of:
engine = SnmpEngine()
transport = UdpTransport().openServerMode(...)
config.addTransport(engine, ...)
config.addV1System(engine, ...)
ntfrcv.NotificationReceiver(engine, callback)
# ... many more steps
```

### 2. Template Method Pattern

The `run()` method defines the skeleton of the startup algorithm:

```python
def run(self):
    self._setup_snmp_engine()      # Step 1: SNMP setup
    self._ensure_pika_connection() # Step 2: RabbitMQ setup
    self._register_signals()       # Step 3: Signal handlers
    self._start_dispatcher()       # Step 4: Main loop
```

Subclasses could override individual steps while maintaining the overall flow.

### 3. Strategy Pattern

Backend selection based on pysnmp version:

```python
# At import time
try:
    from pysnmp.carrier.asynsock.dgram import udp
    _PYSNMP_BACKEND = "asynsock"
except:
    from pysnmp.carrier.asyncio.dgram import udp
    _PYSNMP_BACKEND = "asyncio"

# At runtime
if self._use_asyncio_backend:
    # Strategy A: asyncio event loop
    loop.run_until_complete(transport._lport)
    dispatcher.run_dispatcher()
else:
    # Strategy B: select-based loop
    dispatcher.runDispatcher()
```

### 4. Singleton (Per-Instance) Pattern

RabbitMQ connection is reused across trap publishes:

```python
def _ensure_pika_connection(self):
    if self._pika_conn is not None and self._pika_conn.is_open:
        return  # Reuse existing
    # Otherwise create new
```

---

## Threading Model

### Single-Threaded Event Loop

The receiver uses a single-threaded event loop model:

- **Asyncio backend** (pysnmp 7.x):
  ```python
  loop.run_forever()  # Handles UDP I/O + timer events
  ```

- **Select backend** (pysnmp 6.x):
  ```python
  select.select([socket], [], [], timeout)  # Blocking I/O
  ```

### Why Single-Threaded?

1. **SNMP traps are infrequent**: Typical networks generate 10-100 traps/minute
2. **RabbitMQ publish is fast**: <1ms for local broker
3. **Simpler concurrency**: No locks, no race conditions
4. **Lower resource usage**: Minimal memory and CPU

### Scaling Strategy

For high-volume environments (>1000 traps/sec):
- Run multiple receiver instances
- Use load balancer with consistent hashing
- Idempotency keys prevent duplicate processing

---

## State Management

### Receiver States

```
┌─────────┐
│ CREATED │ (initialized, not running)
└────┬────┘
     │ run()
     ▼
┌─────────┐
│ STARTING│ (setting up SNMP/RabbitMQ)
└────┬────┘
     │
     ▼
┌─────────┐
│ RUNNING │ (dispatching traps)
└────┬────┘
     │ signal or error
     ▼
┌─────────┐
│ STOPPING│ (closing connections)
└────┬────┘
     │
     ▼
┌─────────┐
│ STOPPED │ (cleanup complete)
└─────────┘
```

Tracked via `self._running` threading.Event():
```python
self._running.set()    # Transition to RUNNING
self._running.clear()  # Transition to STOPPED
self._running.is_set() # Check if running
```

### Connection States

**SNMP Engine:**
- `None`: Not initialized
- `SnmpEngine`: Ready to receive
- `SnmpEngine` (dispatcher closed): Shutting down

**RabbitMQ Connection:**
- `None`: Not connected
- `BlockingConnection` (open): Connected
- `BlockingConnection` (closed): Connection lost, retry needed

---

## Error Handling Strategy

### Levels of Error Handling

1. **Trap Processing Errors** (non-fatal)
   ```python
   try:
       self._trap_callback(...)
   except Exception:
       logger.exception("Error handling trap")
       # Continue receiving other traps
   ```

2. **Publish Errors** (retryable)
   ```python
   try:
       channel.basic_publish(...)
   except:
       self._ensure_pika_connection()  # Reconnect
       channel.basic_publish(...)      # Retry once
   ```

3. **Dispatcher Errors** (fatal)
   ```python
   try:
       dispatcher.runDispatcher()
   except Exception:
       logger.exception("Dispatcher error")
       self.stop()
       raise  # Exit process
   ```

### Retry Logic

**RabbitMQ Connection:**
- Max wait: 30 seconds
- Retry interval: 1 second
- On failure: Continue without RabbitMQ (traps logged but not published)

**Publish Retry:**
- First attempt: Use existing channel
- On failure: Reconnect once
- Second attempt: Use new channel
- On failure: Log error and drop message

---

## Security Considerations

### Network Security

1. **SNMPv2c Community Strings**
   - Plain text authentication (weak)
   - Configure firewall rules to restrict trap sources
   - Use VLANs to isolate SNMP traffic

2. **Port Binding**
   - Default port 162 requires root privileges
   - Recommended: Use port ≥1024 and map with iptables/firewall
   - Container: Run as non-root user with port 9162

3. **UDP Flood Protection**
   - pysnmp has no built-in rate limiting
   - Use OS-level firewall rules (iptables rate limiting)
   - Monitor CPU/memory for DoS attacks

### RabbitMQ Security

1. **Credentials**
   - Avoid hardcoding passwords
   - Use environment variables
   - Example: `RABBIT_URL=amqp://user:${RABBITMQ_PASSWORD}@host/`

2. **TLS/SSL**
   - Use `amqps://` for encrypted connections
   - Configure certificate validation

3. **Queue Permissions**
   - Grant receiver user only publish permission
   - Use RabbitMQ ACLs to restrict queue access

### Container Security

1. **Non-Root User**
   ```dockerfile
   RUN adduser --system --ingroup snmp snmp
   USER snmp
   ```

2. **Read-Only Root Filesystem**
   ```yaml
   security_opt:
     - no-new-privileges:true
   read_only: true
   tmpfs:
     - /tmp
   ```

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 256M
   ```

---

## Performance Characteristics

### Benchmarks (Approximate)

**Hardware:** 4 CPU cores, 8GB RAM, local RabbitMQ

| Metric                    | Value          |
|---------------------------|----------------|
| Trap processing latency   | 2-5 ms         |
| RabbitMQ publish latency  | 1-2 ms         |
| End-to-end latency        | 5-10 ms        |
| Maximum throughput        | 500-1000 traps/sec |
| Memory usage (idle)       | 50-80 MB       |
| Memory usage (loaded)     | 100-150 MB     |
| CPU usage (idle)          | <1%            |
| CPU usage (100 traps/sec) | 5-10%          |

### Bottlenecks

1. **RabbitMQ Network Latency**
   - Solution: Co-locate receiver and broker
   - Solution: Use connection pooling (future enhancement)

2. **JSON Serialization**
   - Solution: Use faster serializer (ujson, orjson)
   - Current: Python standard `json` module

3. **Callback Invocation**
   - pysnmp invokes callback synchronously
   - Blocking operation delays next trap
   - Solution: Queue payloads for async publishing (future)

### Optimization Opportunities

1. **Batch Publishing**
   ```python
   # Accumulate payloads
   self._batch.append(payload)
   
   # Publish in batches of 100
   if len(self._batch) >= 100:
       self._publish_batch(self._batch)
       self._batch.clear()
   ```

2. **Connection Pooling**
   - Maintain pool of pika connections
   - Round-robin publish across connections

3. **Async Publishing**
   - Queue payloads in memory
   - Background thread publishes to RabbitMQ
   - Main thread continues receiving traps

---

## Deployment Topologies

### 1. Single Instance (Development)

```
┌─────────────┐
│  Laptop     │
│  - Receiver │
│  - RabbitMQ │
│  - Consumer │
└─────────────┘
```

**Pros:**
- Simple setup
- Easy debugging

**Cons:**
- No redundancy
- Limited throughput

### 2. Containerized (Production)

```
┌──────────────────┐     ┌──────────────────┐
│  Docker Host     │     │  Docker Host     │
│  ┌────────────┐  │     │  ┌────────────┐  │
│  │ Receiver   │  │     │  │ RabbitMQ   │  │
│  └────────────┘  │────▶│  │ Cluster    │  │
└──────────────────┘     │  └────────────┘  │
                          └──────────────────┘
```

**Pros:**
- Isolated environments
- Easy scaling
- Health checks

**Cons:**
- Requires container orchestration

### 3. High Availability (Enterprise)

```
                         ┌──────────────────┐
                         │  Load Balancer   │
                         │  (HAProxy/Nginx) │
                         └─────────┬────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
    ┌──────────────┐       ┌──────────────┐     ┌──────────────┐
    │ Receiver 1   │       │ Receiver 2   │     │ Receiver 3   │
    └──────┬───────┘       └──────┬───────┘     └──────┬───────┘
           │                      │                      │
           └──────────────────────┼──────────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │  RabbitMQ        │
                         │  Cluster         │
                         │  (3 nodes)       │
                         └──────────────────┘
```

**Pros:**
- No single point of failure
- Horizontal scaling
- Load distribution

**Cons:**
- Complex setup
- UDP load balancing challenges
- Potential duplicate processing

---

## Future Enhancements

### Planned Features

1. **SNMPv3 Support**
   - Authenticated and encrypted traps
   - User-based security model (USM)

2. **Prometheus Metrics**
   - Trap counter by OID
   - Publish success/failure rates
   - Connection health gauges

3. **Configuration File**
   - YAML/TOML for complex setups
   - Multiple community strings
   - OID-based routing rules

4. **Async Publishing**
   - Non-blocking message queue
   - Background publisher thread
   - Configurable batch size

5. **MIB Support**
   - Load MIB files for OID resolution
   - Human-readable trap names
   - Symbolic varbind names

6. **Dead Letter Queue**
   - Retry failed publishes
   - Exponential backoff
   - Circuit breaker pattern

### API Stability

Current API is considered **beta**:
- Core functionality stable
- Configuration options may change
- New features via opt-in flags

Breaking changes will:
- Bump major version (2.0.0)
- Provide migration guide
- Maintain 1.x branch for 6 months

---

## Testing Strategy

### Unit Tests

```python
# Test trap parsing
def test_trap_callback_parses_varbinds():
    receiver = SNMPReceiver()
    varbinds = [
        (ObjectIdentifier('1.3.6.1.2.1.1.3.0'), Integer(12345)),
        (ObjectIdentifier('1.3.6.1.6.3.1.1.4.1.0'), ObjectIdentifier('1.3.6.1.6.3.1.1.5.3')),
    ]
    # Mock publish
    receiver.publish_alert = Mock()
    
    receiver._trap_callback(None, None, None, None, varbinds, None)
    
    assert receiver.publish_alert.called
    payload = receiver.publish_alert.call_args[0][0]
    assert payload['alert_name'] == '1.3.6.1.6.3.1.1.5.3'
```

### Integration Tests

```python
# Test with real RabbitMQ
def test_publish_to_rabbitmq():
    receiver = SNMPReceiver(rabbit_url='amqp://localhost:5672/')
    receiver._ensure_pika_connection()
    
    payload = {'test': 'data'}
    receiver.publish_alert(payload)
    
    # Verify message in queue
    conn = pika.BlockingConnection(...)
    method, properties, body = conn.channel().basic_get('alerts')
    assert json.loads(body)['test'] == 'data'
```

### End-to-End Tests

```bash
# Full system test with Docker Compose (from gds_snmp_receiver directory)
cd gds_snmp_receiver
docker compose -f docker-compose.e2e.yml up -d
docker compose -f docker-compose.e2e.yml run snmp-sender \
  python tools/e2e_send_and_check.py
```

---

## Monitoring & Operations

### Key Metrics to Monitor

1. **Trap Reception Rate**
   - Traps/second
   - Alert on sudden drops (receiver down)

2. **Publish Success Rate**
   - Successful publishes / total traps
   - Alert on rate < 99%

3. **RabbitMQ Connection Health**
   - Connection state (up/down)
   - Reconnection frequency

4. **Queue Depth**
   - Messages in 'alerts' queue
   - Alert on sustained growth (consumer lag)

5. **Container Health**
   - Readiness check status
   - Process uptime

### Log Analysis

Use structured logging for log aggregation:

```python
# Add structured fields
logger.info(
    "Trap received",
    extra={
        'trap_oid': alert_name,
        'source_ip': source_ip,
        'varbind_count': len(var_binds_list),
    }
)
```

Parse with ELK/Splunk/Loki:
```
# Count traps by OID
SELECT trap_oid, COUNT(*) FROM logs 
WHERE message='Trap received' 
GROUP BY trap_oid
```

### Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: snmp_receiver
    rules:
      - alert: SNMPReceiverDown
        expr: up{job="snmp-receiver"} == 0
        for: 1m
        
      - alert: HighPublishFailureRate
        expr: rate(snmp_publish_errors_total[5m]) > 0.01
        for: 5m
        
      - alert: QueueDepthHigh
        expr: rabbitmq_queue_messages{queue="alerts"} > 10000
        for: 10m
```

---

## Glossary

- **ASN.1**: Abstract Syntax Notation One - data serialization format
- **BER**: Basic Encoding Rules - ASN.1 encoding for SNMP
- **MIB**: Management Information Base - database of OID definitions
- **OID**: Object Identifier - dotted-decimal identifier (e.g., 1.3.6.1.2.1.1.3.0)
- **PDU**: Protocol Data Unit - SNMP message structure
- **Trap**: Unsolicited SNMP notification from agent to manager
- **Varbind**: Variable binding - OID-value pair in SNMP message
- **Community String**: SNMPv1/v2c password (sent in cleartext)
- **USM**: User-based Security Model - SNMPv3 authentication/encryption

---

## References

- [RFC 3416 - SNMP Protocol Operations](https://tools.ietf.org/html/rfc3416)
- [pysnmp Documentation](https://pysnmp.readthedocs.io/)
- [pika Documentation](https://pika.readthedocs.io/)
- [RabbitMQ Best Practices](https://www.rabbitmq.com/best-practices.html)
