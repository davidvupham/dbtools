# GDS SNMP Receiver - Developer Guide

## Introduction

This guide is for developers who need to understand, modify, or extend the `gds_snmp_receiver` codebase. It provides detailed explanations of the implementation, design patterns, and best practices.

---

## Prerequisites

Before diving into the code, you should understand:

1. **Python Basics**
   - Object-oriented programming
   - Type hints and annotations
   - Context managers and decorators
   - Threading and signals

2. **SNMP Protocol**
   - What SNMP traps are
   - OID (Object Identifier) format
   - SNMPv2c community strings
   - Variable bindings (varbinds)

3. **RabbitMQ**
   - Message queue concepts
   - AMQP protocol basics
   - Durable queues and persistent messages
   - Publisher/consumer pattern

4. **Asyncio (for pysnmp 7.x)**
   - Event loop concepts
   - Futures and coroutines
   - `run_until_complete()` vs `run_forever()`

---

## Code Walkthrough

### Entry Point: `receiver.py`

This is a thin CLI wrapper that:
1. Parses command-line arguments
2. Configures logging
3. Creates `SNMPReceiver` instance
4. Calls `run()` method

**Why separate CLI from core logic?**
- Enables testing without CLI complexity
- Allows library usage without CLI dependencies
- Follows single responsibility principle

```python
def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="gds_snmp_receiver CLI")
    # ... parse arguments ...

    receiver = SNMPReceiver(
        listen_host=args.host,
        listen_port=args.port,
        rabbit_url=args.rabbit,
        queue_name=args.queue
    )
    receiver.run()
```

**Key Design Decision:**
The CLI uses `argparse` with environment variable fallbacks. This provides maximum flexibility - users can configure via CLI flags, environment variables, or both.

---

### Core Implementation: `core.py`

#### Module-Level Backend Detection

```python
try:
    from pysnmp.carrier.asynsock.dgram import udp
    _PYSNMP_BACKEND = "asynsock"
except Exception:
    from pysnmp.carrier.asyncio.dgram import udp
    _PYSNMP_BACKEND = "asyncio"
```

**Why at import time?**
- pysnmp changed backends between versions 6.x and 7.x
- We detect the backend once at import time
- Runtime code uses `_PYSNMP_BACKEND` to choose dispatch strategy
- This ensures compatibility without version pinning

**Tradeoff:**
Import-time detection is brittle if pysnmp changes again. Alternative would be version checking via `importlib.metadata`, but that adds dependency complexity.

---

#### Class Initialization: `__init__`

**State Management:**

```python
self._snmp_engine: Optional[engine.SnmpEngine] = None
self._snmp_transport = None
self._use_asyncio_backend = False
self._running = threading.Event()
self._pika_conn: Optional[pika.BlockingConnection] = None
self._pika_ch = None
```

**Design Pattern: Lazy Initialization**

The SNMP engine and RabbitMQ connection are created in `run()`, not `__init__()`. This allows:
- Unit testing without live connections
- Deferred connection establishment
- Multiple `run()` calls (after `stop()`)

**Logging Configuration:**

```python
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(...))
    logger.addHandler(h)
```

**Why check `if not logger.handlers`?**
- Prevents duplicate handlers on re-import
- Respects user's logging configuration
- Adds default handler only if needed

**Environment Variable Priority:**

```python
lvl = os.getenv("GDS_SNMP_LOG_LEVEL") or os.getenv("LOG_LEVEL")
```

Checks both `GDS_SNMP_LOG_LEVEL` (specific) and `LOG_LEVEL` (generic). Specific wins via short-circuit evaluation.

---

#### Main Loop: `run()`

**Execution Flow:**

```
1. _setup_snmp_engine()          # Configure pysnmp
2. _ensure_pika_connection()     # Connect to RabbitMQ (with retry)
3. Write readiness marker        # For health checks
4. Register signal handlers      # SIGTERM/SIGINT → stop()
5. Start dispatcher              # Block in event loop
6. Cleanup on exit               # Finally block
```

**Retry Logic for RabbitMQ:**

```python
max_wait = 30
waited = 0
while self._pika_conn is None:
    self._ensure_pika_connection()
    if self._pika_conn is not None:
        break
    if waited >= max_wait:
        logger.warning("Could not establish RabbitMQ connection...")
        break
    waited += 1
    time.sleep(1)
```

**Why retry?**
- RabbitMQ may start slower than receiver (Docker Compose)
- Prevents receiver crash on temporary network issues
- 30-second timeout is reasonable for most environments

**Alternative Design:**
Use `tenacity` library for exponential backoff. Current approach is simpler and sufficient for most cases.

**Readiness Marker:**

```python
with open("/tmp/gds_snmp_ready", "w") as f:
    f.write("ready\n")
```

**Why a file?**
- Simple inter-process communication
- Health check script can check file existence
- E2E tests can wait for readiness
- No network dependencies

**Alternative:** HTTP endpoint on port 8080. More complex but enables richer health checks.

**Backend-Specific Dispatch:**

```python
if self._use_asyncio_backend:
    # pysnmp 7.x: asyncio event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self._snmp_transport._lport)
    self._snmp_engine.transportDispatcher.run_dispatcher()
else:
    # pysnmp 6.x: select-based loop
    self._snmp_engine.transportDispatcher.runDispatcher()
```

**Critical Bug Fixed:**
pysnmp 7.x's asyncio transport binds UDP socket asynchronously. The `_lport` future must be awaited before `run_dispatcher()` starts the event loop. Without this, the socket never binds and traps are never received.

**How This Was Discovered:**
- Traps arrived (tcpdump proved it)
- But callback never invoked
- Enabled pysnmp debug logging
- Discovered "UnknownCommunityName" error
- Then discovered socket wasn't bound
- Inspected pysnmp source code
- Found `_lport` future in `open_server_mode()`
- Added explicit await

---

#### SNMP Engine Setup: `_setup_snmp_engine()`

**Step-by-Step:**

```python
# 1. Create engine
snmp_engine = engine.SnmpEngine()

# 2. Bind UDP transport
transport = udp.UdpTransport().openServerMode(listen_addr)
config.addTransport(snmp_engine, udp.domainName, transport)

# 3. Configure authentication
config.addV1System(snmp_engine, 'my-area', 'public')

# 4. Register callback
ntfrcv.NotificationReceiver(snmp_engine, self._trap_callback)

# 5. Store references
self._snmp_engine = snmp_engine
self._snmp_transport = transport
```

**Why store transport?**
Needed to await `_lport` future in asyncio backend. Without this reference, we can't access the future.

**Community String Configuration:**

```python
config.addV1System(snmp_engine, 'my-area', 'public')
```

- `'my-area'`: Security name (internal identifier)
- `'public'`: Community string (password)

**Improvement Opportunity:**
Move community string to environment variable:
```python
community = os.environ.get('SNMP_COMMUNITY', 'public')
config.addV1System(snmp_engine, 'my-area', community)
```

**Callback Registration:**

```python
ntfrcv.NotificationReceiver(snmp_engine, self._trap_callback)
```

Creates notification receiver that invokes `_trap_callback` for each trap. The callback signature is defined by pysnmp and must match exactly.

---

#### Trap Processing: `_trap_callback()`

**Callback Signature:**

```python
def _trap_callback(
    self,
    _snmpEngine: Any,      # SNMP engine instance
    _stateReference: Any,  # Internal state
    _contextEngineId: Any, # Context engine ID
    _contextName: Any,     # Context name
    varBinds: Iterable[Any],  # OID-value pairs
    _cbCtx: Any           # Callback context
) -> None:
```

**Why underscore prefix?**
Convention for unused parameters. Signals to readers (and linters) that these are required by interface but not used in implementation.

**Processing Steps:**

1. **Convert Iterator to List**
   ```python
   var_binds_list = list(varBinds)
   ```
   Varbinds may be a generator. We need multiple passes (logging + extraction), so convert to list.

2. **Extract OID-Value Pairs**
   ```python
   for oid, val in var_binds_list:
       oid_str = str(oid)
       details[oid_str] = str(val)
   ```
   pysnmp returns custom types (`ObjectIdentifier`, `Integer`, etc.). Convert everything to strings for JSON serialization.

3. **Identify Trap Type**
   ```python
   if (oid_str.endswith('.1.3.6.1.6.3.1.1.4.1.0') or
           oid_str.endswith('1.3.6.1.6.3.1.1.4.1.0')):
       alert_name = str(val)
   ```

   **SNMPv2 Standard:**
   - OID `1.3.6.1.6.3.1.1.4.1.0` = `snmpTrapOID.0`
   - Value is the trap type (e.g., `1.3.6.1.6.3.1.1.5.3` = linkDown)

   **Why check both with/without leading dot?**
   pysnmp may return OIDs with or without leading dot depending on version. Defensive programming.

4. **Fallback Alert Name**
   ```python
   if not alert_name and var_binds_list:
       first = var_binds_list[0]
       alert_name = f"snmp:{str(first[0])}"
   ```

   If trap doesn't follow SNMPv2 standard, use first OID as alert name. Better than `None`.

5. **Generate Idempotency Key**
   ```python
   idempotency_id = self.compute_idempotency_from_trap(var_binds_list)
   ```

   SHA-256 hash of varbinds + timestamp. Enables downstream duplicate detection.

6. **Build Payload**
   ```python
   payload = {
       'idempotency_id': idempotency_id,
       'alert_name': alert_name,
       'source': 'snmp',
       'received_at': datetime.utcnow().isoformat() + 'Z',
       'raw': details,
       'subject': f'SNMP Trap: {alert_name}',
       'body_text': json.dumps(details, indent=2),
   }
   ```

   **Payload Design:**
   - `idempotency_id`: For deduplication
   - `alert_name`: For routing/filtering
   - `source`: For multi-source systems
   - `received_at`: ISO 8601 UTC timestamp
   - `raw`: Complete varbind data
   - `subject`/`body_text`: Ready for email/notification

7. **Publish**
   ```python
   self.publish_alert(payload)
   ```

**Error Handling:**

```python
try:
    # ... entire callback body ...
except Exception:
    logger.exception("Error handling SNMP trap")
```

**Why catch everything?**
A single malformed trap should not crash the receiver. Log the error and continue processing other traps.

---

#### RabbitMQ Connection: `_ensure_pika_connection()`

**Connection Reuse:**

```python
if self._pika_conn is not None and self._pika_ch is not None:
    if self._pika_conn.is_open:
        return  # Reuse existing
```

**Why reuse?**
- TCP connection establishment is expensive (3-way handshake)
- Authentication adds latency
- Persistent connections reduce overhead

**Connection Steps:**

```python
params = pika.URLParameters(self.rabbit_url)
conn = pika.BlockingConnection(params)
ch = conn.channel()
ch.queue_declare(queue=self.queue_name, durable=True)
```

**Queue Declaration:**
- `durable=True`: Queue survives broker restart
- Idempotent operation: Safe to call multiple times
- Creates queue if doesn't exist, no-op if exists

**Error Handling:**

```python
except Exception:
    logger.exception("Failed to establish pika connection")
    self._pika_conn = None
    self._pika_ch = None
```

On any error, clear connection state. This ensures next call attempts reconnection instead of using stale objects.

---

#### Publishing: `publish_alert()`

**Two-Tier Retry:**

```python
try:
    # First attempt with existing channel
    self._pika_ch.basic_publish(...)
except Exception:
    # Reconnect and retry
    self._ensure_pika_connection()
    if self._pika_ch is not None:
        self._pika_ch.basic_publish(...)
```

**Why only one retry?**
- More retries risk message duplication
- If two attempts fail, likely prolonged outage
- Better to drop message than retry forever (prevents memory buildup)

**Publishing Parameters:**

```python
self._pika_ch.basic_publish(
    exchange="",                    # Default exchange
    routing_key=self.queue_name,    # Direct routing
    body=json.dumps(payload),       # JSON string
    properties=pika.BasicProperties(
        delivery_mode=2             # Persistent
    ),
)
```

**Delivery Mode:**
- `1` = Transient (lost on broker restart)
- `2` = Persistent (written to disk)

Must use `2` with `durable=True` queue for full persistence.

**Alternative Design:**
Publish to an exchange with routing keys for topic-based routing. Current approach is simpler for point-to-point use case.

---

#### Idempotency Key: `compute_idempotency_from_trap()`

```python
@staticmethod
def compute_idempotency_from_trap(var_binds: Iterable[Any]) -> str:
    s = ''.join(f"{str(x[0])}={str(x[1])};" for x in var_binds)
    s += datetime.utcnow().isoformat()
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
```

**Why include timestamp?**
Without timestamp, duplicate traps (e.g., device reboots repeatedly) would have same hash. Including timestamp ensures uniqueness.

**Trade-off:**
Can't detect true duplicates (same trap received twice). If duplicate detection is needed, remove timestamp and implement deduplication window in consumer.

**Why SHA-256?**
- Standard cryptographic hash
- 64-character hex string (256 bits)
- Collision probability negligible
- Fast computation

---

#### Graceful Shutdown: `stop()`

```python
def stop(self) -> None:
    # 1. Close SNMP dispatcher
    if self._snmp_engine is not None:
        self._snmp_engine.transportDispatcher.closeDispatcher()

    # 2. Close RabbitMQ connection
    if self._pika_conn is not None:
        self._pika_conn.close()
        self._pika_conn = None
        self._pika_ch = None

    # 3. Remove readiness marker
    if os.path.exists("/tmp/gds_snmp_ready"):
        os.remove("/tmp/gds_snmp_ready")

    # 4. Clear running flag
    self._running.clear()
```

**Why this order?**
1. Stop receiving new traps
2. Publish pending traps (if any queued)
3. Close connections
4. Clean up filesystem state

**Signal Handler:**

```python
def _signal_handler(self, signum: int, frame: Any) -> None:
    logger.info("Received signal %s, shutting down", signum)
    self.stop()
```

Registered for SIGTERM (Docker) and SIGINT (Ctrl+C). Enables graceful shutdown in containers.

---

## Extending the Receiver

### Adding SNMPv3 Support

```python
from pysnmp.entity.config import addV3User
from pysnmp import hlapi

def _setup_snmp_engine(self):
    # ... existing code ...

    # Add USM user for SNMPv3
    addV3User(
        snmp_engine,
        userName=os.environ.get('SNMP_V3_USER', 'snmpuser'),
        authProtocol=hlapi.usmHMACSHAAuthProtocol,
        authKey=os.environ.get('SNMP_V3_AUTH_KEY'),
        privProtocol=hlapi.usmAesCfb128Protocol,
        privKey=os.environ.get('SNMP_V3_PRIV_KEY')
    )
```

### Adding Message Filtering

```python
def _trap_callback(self, ...):
    # ... parse trap ...

    # Filter by OID
    if self._should_filter(alert_name):
        logger.debug("Filtered trap: %s", alert_name)
        return

    # Continue processing
    self.publish_alert(payload)

def _should_filter(self, oid: str) -> bool:
    # Load filter rules from config
    filters = os.environ.get('SNMP_FILTER_OIDS', '').split(',')
    return any(oid.startswith(f) for f in filters if f)
```

### Adding Metrics

```python
from prometheus_client import Counter, Histogram

class SNMPReceiver:
    def __init__(self, ...):
        # ... existing code ...

        # Metrics
        self.traps_received = Counter(
            'snmp_traps_received_total',
            'Total traps received'
        )
        self.traps_published = Counter(
            'snmp_traps_published_total',
            'Total traps published'
        )
        self.publish_duration = Histogram(
            'snmp_publish_duration_seconds',
            'Time to publish to RabbitMQ'
        )

    def _trap_callback(self, ...):
        self.traps_received.inc()
        # ... process trap ...

        with self.publish_duration.time():
            self.publish_alert(payload)

        self.traps_published.inc()
```

### Adding Async Publishing

For high-volume scenarios, decouple trap reception from RabbitMQ publishing:

```python
import queue
import threading

class SNMPReceiver:
    def __init__(self, ...):
        # ... existing code ...
        self._publish_queue = queue.Queue(maxsize=1000)
        self._publisher_thread = None

    def run(self):
        # ... existing code ...

        # Start publisher thread
        self._publisher_thread = threading.Thread(
            target=self._publisher_loop
        )
        self._publisher_thread.start()

        # ... run dispatcher ...

    def _trap_callback(self, ...):
        # ... parse trap ...

        try:
            self._publish_queue.put_nowait(payload)
        except queue.Full:
            logger.error("Publish queue full, dropping trap")

    def _publisher_loop(self):
        while self._running.is_set():
            try:
                payload = self._publish_queue.get(timeout=1)
                self.publish_alert(payload)
            except queue.Empty:
                continue
```

---

## Testing Strategies

### Unit Testing Trap Parsing

```python
import unittest
from unittest.mock import Mock
from gds_snmp_receiver import SNMPReceiver

class TestTrapParsing(unittest.TestCase):
    def test_parse_varbinds(self):
        receiver = SNMPReceiver()
        receiver.publish_alert = Mock()

        # Mock varbinds
        varbinds = [
            (ObjectIdentifier('1.3.6.1.2.1.1.3.0'), Integer(12345)),
            (ObjectIdentifier('1.3.6.1.6.3.1.1.4.1.0'),
             ObjectIdentifier('1.3.6.1.6.3.1.1.5.3')),
        ]

        receiver._trap_callback(None, None, None, None, varbinds, None)

        # Verify publish was called
        assert receiver.publish_alert.called
        payload = receiver.publish_alert.call_args[0][0]
        assert payload['alert_name'] == '1.3.6.1.6.3.1.1.5.3'
```

### Integration Testing with RabbitMQ

```python
def test_publish_to_real_rabbitmq():
    receiver = SNMPReceiver(rabbit_url='amqp://localhost/')
    receiver._ensure_pika_connection()

    payload = {'test': 'data'}
    receiver.publish_alert(payload)

    # Verify message in queue
    import pika
    conn = pika.BlockingConnection(pika.URLParameters('amqp://localhost/'))
    ch = conn.channel()
    method, props, body = ch.basic_get('alerts')
    assert json.loads(body)['test'] == 'data'
```

### E2E Testing

See `tools/e2e_send_and_check.py` for complete E2E test framework.

---

## Debugging Tips

### Enable pysnmp Debug Logging

```python
# Add to _setup_snmp_engine
from pysnmp import debug
debug.set_logger(debug.Debug('all'))
```

Shows internal pysnmp state, trap decoding, authentication, etc.

### Inspect Varbinds

```python
def _trap_callback(self, ...):
    for oid, val in varBinds:
        print(f"Type: {type(oid).__name__}, Value: {oid}")
        print(f"Type: {type(val).__name__}, Value: {val}")
```

Helps understand pysnmp's custom types.

### Monitor RabbitMQ

```bash
# Watch queue depth
watch -n1 'rabbitmqctl list_queues name messages'

# View messages
rabbitmqctl list_queues name messages consumers
```

### Capture UDP Traffic

```bash
sudo tcpdump -i any udp port 9162 -X -vvv
```

Shows raw SNMP packets. Verify traps are arriving.

---

## Best Practices

1. **Always use type hints** - Enables IDE autocomplete and catches errors early
2. **Add docstrings** - Explain what, why, and how
3. **Log at appropriate levels** - DEBUG for details, INFO for operations, ERROR for failures
4. **Handle exceptions gracefully** - Don't crash on single bad trap
5. **Test with real RabbitMQ** - Unit tests can't catch all issues
6. **Use environment variables** - Never hardcode credentials
7. **Document breaking changes** - Maintain CHANGELOG.md

---

## Common Pitfalls

1. **Forgetting to await asyncio futures** - Socket won't bind in pysnmp 7.x
2. **Not converting varbinds to list** - Can only iterate generator once
3. **Hardcoding community string** - Use environment variable
4. **Not checking channel is_open** - Leads to publish errors
5. **Infinite retry loops** - Always have max retry count
6. **Blocking operations in callback** - Keep callback fast

---

## Performance Optimization

1. **Reuse connections** - Already implemented
2. **Batch publishes** - See async publishing section
3. **Use ujson** - Faster JSON serialization
   ```python
   import ujson as json
   ```
4. **Profile with cProfile** - Find bottlenecks
   ```bash
   python -m cProfile -o profile.stats -m gds_snmp_receiver.receiver
   ```
5. **Monitor memory** - Use `memory_profiler`

---

## Further Resources

- **pysnmp Documentation**: https://pysnmp.readthedocs.io/
- **pika Documentation**: https://pika.readthedocs.io/
- **SNMP RFCs**: RFC 3411-3418
- **Python Logging**: https://docs.python.org/3/library/logging.html
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

This developer guide should give you everything you need to understand and modify the codebase. Happy coding!
