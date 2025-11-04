# GDS SNMP Receiver - Complete Tutorial

## Table of Contents

1. [Introduction](#introduction)
2. [What is SNMP?](#what-is-snmp)
3. [Architecture Overview](#architecture-overview)
4. [Installation & Setup](#installation--setup)
5. [Running the Receiver](#running-the-receiver)
6. [Understanding the Code](#understanding-the-code)
7. [Configuration](#configuration)
8. [Docker Deployment](#docker-deployment)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Topics](#advanced-topics)

---

## Introduction

The **GDS SNMP Receiver** is a Python application that listens for SNMP trap messages over UDP, processes them, and publishes normalized alert messages to RabbitMQ. This enables integration between SNMP-enabled network devices (routers, switches, servers) and modern message queue-based alerting systems.

### Key Features

- **SNMP Trap Reception**: Listens on UDP port 162 (or configurable) for SNMPv2c trap messages
- **Message Normalization**: Converts SNMP trap varbinds into structured JSON payloads
- **RabbitMQ Integration**: Publishes alerts to a durable RabbitMQ queue
- **Asyncio Support**: Compatible with both legacy and modern pysnmp versions
- **Docker-Ready**: Fully containerized with health checks and E2E tests
- **Production Features**: Signal handling, connection retry, logging, idempotency keys

---

## What is SNMP?

**SNMP (Simple Network Management Protocol)** is an Internet standard protocol for collecting and organizing information about managed devices on IP networks. It's commonly used for monitoring network equipment like routers, switches, servers, printers, and more.

### SNMP Traps

**Traps** are unsolicited messages sent from an SNMP agent (device) to a manager (receiver) to notify about important events:

- Link up/down events
- Hardware failures
- Temperature thresholds exceeded
- Authentication failures
- Custom application events

### SNMP Message Structure

An SNMP trap contains:
- **Enterprise OID**: Identifies the source/type of trap
- **Timestamp** (sysUpTime): Device uptime when event occurred
- **Trap OID**: Specific identifier for the event type
- **Variable Bindings (varbinds)**: Key-value pairs with event details

Example trap structure:
```
sysUpTime: 12345678
snmpTrapOID: 1.3.6.1.6.3.1.1.5.3 (linkDown)
ifIndex: 2
ifDescr: "eth0"
```

---

## Architecture Overview

```
┌─────────────────┐         UDP:162          ┌──────────────────┐
│  SNMP Devices   │ ──────────────────────>  │ SNMP Receiver    │
│ (Traps/Informs) │      SNMPv2c Traps       │   (pysnmp)       │
└─────────────────┘                          └──────────────────┘
                                                      │
                                                      │ JSON
                                                      │ Messages
                                                      ▼
                                             ┌──────────────────┐
                                             │   RabbitMQ       │
                                             │  'alerts' queue  │
                                             └──────────────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Alert Consumers  │
                                             │ (Email, Slack,   │
                                             │  PagerDuty, etc) │
                                             └──────────────────┘
```

### Component Breakdown

1. **SNMP Engine** (pysnmp library)
   - Manages UDP socket binding
   - Handles SNMP protocol decoding
   - Authenticates community strings
   - Invokes callback for each trap

2. **Trap Callback Handler** (`_trap_callback`)
   - Extracts varbinds from trap
   - Normalizes data into JSON structure
   - Generates idempotency key
   - Triggers RabbitMQ publish

3. **RabbitMQ Publisher** (pika library)
   - Maintains persistent connection
   - Declares durable queue
   - Publishes with delivery_mode=2 (persistent)
   - Automatic reconnect on failure

4. **Signal Handler**
   - Graceful shutdown on SIGTERM/SIGINT
   - Closes SNMP dispatcher
   - Closes RabbitMQ connection
   - Cleanup of readiness markers

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- RabbitMQ server (3.x or higher)
- Network access to SNMP trap sources

### Local Installation

```bash
# Clone repository
git clone <repo-url>
cd dbtools/gds_snmp_receiver

# Install dependencies
pip install -r requirements.txt

# Or install from setup.py
pip install -e .
```

### Dependencies

```
pysnmp==7.1.22    # SNMP protocol implementation
pika==1.3.2       # RabbitMQ client
```

---

## Running the Receiver

### Command Line

```bash
# Run with defaults (requires RabbitMQ on localhost)
python -m gds_snmp_receiver.receiver

# Run with custom settings
python -m gds_snmp_receiver.receiver \
  --host 0.0.0.0 \
  --port 9162 \
  --rabbit amqp://guest:guest@localhost:5672/ \
  --queue alerts \
  --log-level DEBUG
```

### Environment Variables

```bash
# Configure via environment
export SNMP_LISTEN_HOST="0.0.0.0"
export SNMP_LISTEN_PORT="162"
export RABBIT_URL="amqp://guest:guest@rabbitmq:5672/"
export SNMP_QUEUE="alerts"
export GDS_SNMP_LOG_LEVEL="DEBUG"

python -m gds_snmp_receiver.receiver
```

### Python API

```python
from gds_snmp_receiver import SNMPReceiver

# Create receiver instance
receiver = SNMPReceiver(
    listen_host="0.0.0.0",
    listen_port=162,
    rabbit_url="amqp://guest:guest@localhost:5672/",
    queue_name="alerts"
)

# Start receiving (blocks until stopped)
receiver.run()
```

---

## Understanding the Code

### Module Structure

```
gds_snmp_receiver/
├── __init__.py           # Package initialization, exports SNMPReceiver
├── receiver.py           # CLI entry point with argument parsing
├── core.py               # Main SNMPReceiver class implementation
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container image definition
├── entrypoint.sh        # Container entrypoint script
├── healthcheck.py       # Container health check script
└── tests/               # Unit and integration tests
```

### Core Class: `SNMPReceiver`

Located in `core.py`, this is the main implementation.

#### Initialization (`__init__`)

```python
def __init__(
    self,
    listen_host: str = "0.0.0.0",
    listen_port: int = 162,
    rabbit_url: str = "amqp://guest:guest@rabbitmq:5672/",
    queue_name: str = "alerts",
) -> None:
```

**What it does:**
- Stores configuration parameters
- Initializes internal state variables
- Sets up logging with configurable level
- Prepares connection placeholders for SNMP engine and RabbitMQ

**Key attributes:**
- `_snmp_engine`: The pysnmp SnmpEngine instance
- `_pika_conn`: RabbitMQ connection (pika.BlockingConnection)
- `_pika_ch`: RabbitMQ channel for publishing
- `_running`: Threading event to track receiver state
- `_use_asyncio_backend`: Flag for pysnmp backend compatibility

#### Main Loop (`run`)

```python
def run(self) -> None:
    """Start the SNMP dispatcher and block until stopped."""
```

**Execution flow:**

1. **Setup SNMP Engine** (`_setup_snmp_engine`)
   - Creates pysnmp SnmpEngine
   - Binds UDP transport to listen address
   - Configures SNMPv2c community authentication
   - Registers trap callback handler

2. **Establish RabbitMQ Connection** (`_ensure_pika_connection`)
   - Connects to RabbitMQ with retry logic (30s max)
   - Declares durable queue
   - Writes readiness marker file (`/tmp/gds_snmp_ready`)

3. **Register Signal Handlers**
   - SIGINT (Ctrl+C) and SIGTERM trigger graceful shutdown

4. **Start Dispatcher Loop**
   - **Asyncio backend** (pysnmp 7.x):
     - Awaits UDP socket binding future
     - Calls `run_dispatcher()` which runs asyncio event loop
   - **Asynsock backend** (pysnmp 6.x):
     - Calls `runDispatcher()` which blocks in select() loop

5. **Block Until Stopped**
   - Dispatcher runs continuously, invoking callback for each trap
   - Exits on signal or exception

#### Trap Processing (`_trap_callback`)

```python
def _trap_callback(
    self, _snmpEngine, _stateReference, _contextEngineId, 
    _contextName, varBinds, _cbCtx
) -> None:
```

**Callback signature** (required by pysnmp):
- `_snmpEngine`: SNMP engine instance
- `_stateReference`: Internal state reference
- `_contextEngineId`: SNMP context engine ID
- `_contextName`: SNMP context name
- `varBinds`: Iterator of (OID, value) tuples
- `_cbCtx`: Callback context (optional user data)

**Processing steps:**

1. **Extract Varbinds**
   ```python
   var_binds_list = list(varBinds)  # Convert iterator to list
   ```

2. **Parse Alert Name**
   - Looks for standard trap OID (1.3.6.1.6.3.1.1.4.1.0)
   - Falls back to first varbind OID if not found

3. **Build Details Dictionary**
   ```python
   details = {str(oid): str(val) for oid, val in var_binds_list}
   ```

4. **Generate Idempotency Key**
   - SHA-256 hash of varbinds + current timestamp
   - Ensures uniqueness for duplicate detection

5. **Create Normalized Payload**
   ```json
   {
     "idempotency_id": "abc123...",
     "alert_name": "1.3.6.1.6.3.1.1.5.3",
     "source": "snmp",
     "received_at": "2025-11-04T12:34:56.789Z",
     "raw": {
       "1.3.6.1.2.1.1.3.0": "12345678",
       "1.3.6.1.6.3.1.1.4.1.0": "1.3.6.1.6.3.1.1.5.3"
     },
     "subject": "SNMP Trap: 1.3.6.1.6.3.1.1.5.3",
     "body_text": "{\n  \"1.3.6.1.2.1.1.3.0\": \"12345678\",\n  ...\n}"
   }
   ```

6. **Publish to RabbitMQ**
   ```python
   self.publish_alert(payload)
   ```

#### RabbitMQ Publishing (`publish_alert`)

```python
def publish_alert(self, payload: dict) -> None:
```

**Reliability features:**

1. **Connection Check**
   - Ensures channel exists before publish
   - Calls `_ensure_pika_connection()` if needed

2. **Persistent Messages**
   ```python
   properties=pika.BasicProperties(delivery_mode=2)
   ```
   - `delivery_mode=2` makes messages persistent (survive broker restart)

3. **Automatic Retry**
   - If publish fails, reconnects once and retries
   - Logs error if second attempt fails

4. **Detailed Logging**
   - Logs payload preview (truncated to 1000 chars)
   - Logs success with idempotency ID

#### Graceful Shutdown (`stop`)

```python
def stop(self) -> None:
```

**Cleanup steps:**
1. Close SNMP dispatcher (stops UDP listener)
2. Close RabbitMQ connection
3. Remove readiness marker file
4. Clear running flag

---

## Configuration

### Network Configuration

**Listen Interface:**
```bash
# Listen on all interfaces (default)
SNMP_LISTEN_HOST="0.0.0.0"

# Listen on specific interface
SNMP_LISTEN_HOST="192.168.1.100"

# Localhost only (testing)
SNMP_LISTEN_HOST="127.0.0.1"
```

**Listen Port:**
```bash
# Standard SNMP trap port (requires root/CAP_NET_BIND_SERVICE)
SNMP_LISTEN_PORT="162"

# Non-privileged port (recommended for containers)
SNMP_LISTEN_PORT="9162"
```

### RabbitMQ Configuration

**Connection URL format:**
```
amqp://[username]:[password]@[host]:[port]/[vhost]
```

**Examples:**
```bash
# Default (guest/guest on localhost)
RABBIT_URL="amqp://guest:guest@localhost:5672/"

# Custom credentials
RABBIT_URL="amqp://snmp_user:secret123@rabbitmq.example.com:5672/"

# Custom vhost
RABBIT_URL="amqp://user:pass@host:5672/production"
```

**Queue Configuration:**
```bash
# Queue name for alerts
SNMP_QUEUE="alerts"

# Environment-specific queue
SNMP_QUEUE="snmp_alerts_prod"
```

### SNMP Configuration

**Community String:**

Currently hardcoded to accept `'public'` community string. To modify:

```python
# In core.py, _setup_snmp_engine method
config.addV1System(snmp_engine, 'my-area', 'public')
#                                            ^^^^^^^^
#                                            Change this
```

For production, use environment variable:
```python
community = os.environ.get('SNMP_COMMUNITY', 'public')
config.addV1System(snmp_engine, 'my-area', community)
```

### Logging Configuration

**Log Levels:**
```bash
GDS_SNMP_LOG_LEVEL="DEBUG"    # Verbose debugging
GDS_SNMP_LOG_LEVEL="INFO"     # Standard operations
GDS_SNMP_LOG_LEVEL="WARNING"  # Warnings and errors only
GDS_SNMP_LOG_LEVEL="ERROR"    # Errors only
```

**What each level shows:**

- **DEBUG**: All operations, trap details, connection state, varbind parsing
- **INFO**: Trap reception, publish success, connection events
- **WARNING**: Retry attempts, non-critical failures
- **ERROR**: Connection failures, publish errors, exceptions

---

## Docker Deployment

### Building the Image

```bash
cd gds_snmp_receiver
docker build -t gds-snmp-receiver:latest .
```

### Running the Container

```bash
docker run -d \
  --name snmp-receiver \
  -p 9162:9162/udp \
  -e SNMP_LISTEN_HOST="0.0.0.0" \
  -e SNMP_LISTEN_PORT="9162" \
  -e RABBIT_URL="amqp://guest:guest@rabbitmq:5672/" \
  -e SNMP_QUEUE="alerts" \
  -e GDS_SNMP_LOG_LEVEL="INFO" \
  gds-snmp-receiver:latest
```

### Docker Compose (Production)

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: snmp_user
      RABBITMQ_DEFAULT_PASS: secure_password
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    restart: unless-stopped

  snmp-receiver:
    image: gds-snmp-receiver:latest
    depends_on:
      - rabbitmq
    ports:
      - "162:9162/udp"
    environment:
      SNMP_LISTEN_HOST: "0.0.0.0"
      SNMP_LISTEN_PORT: "9162"
      RABBIT_URL: "amqp://snmp_user:secure_password@rabbitmq:5672/"
      SNMP_QUEUE: "alerts"
      GDS_SNMP_LOG_LEVEL: "INFO"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "/app/healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  rabbitmq-data:
```

### Health Check

The container includes a health check script that verifies:
1. Python process is running
2. Readiness marker exists (`/tmp/gds_snmp_ready`)

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' snmp-receiver
```

---

## Testing

### End-to-End Test

The package includes a complete E2E test framework:

```bash
# Navigate to package directory
cd gds_snmp_receiver

# Start the E2E stack
docker compose -f docker-compose.e2e.yml up -d

# Run E2E test
docker compose -f docker-compose.e2e.yml run --rm snmp-sender \
  python tools/e2e_send_and_check.py

# View logs
docker compose -f docker-compose.e2e.yml logs -f gds-snmp-receiver

# Cleanup
docker compose -f docker-compose.e2e.yml down
```

**What the E2E test does:**
1. Waits for RabbitMQ to be ready
2. Waits for receiver to declare queue
3. Installs snmptrap utility
4. Sends SNMPv2c trap to receiver
5. Polls RabbitMQ queue for message
6. Validates message structure
7. Returns exit code 0 on success

### Manual Testing with snmptrap

```bash
# Install net-snmp tools
apt-get install snmp

# Send test trap to localhost
snmptrap -v 2c -c public localhost:9162 '' \
  .1.3.6.1.6.3.1.1.5.3 \
  ifIndex i 2 \
  ifDescr s "eth0"

# Send test trap with timestamp
snmptrap -v 2c -c public 192.168.1.100:162 '' \
  .1.3.6.1.4.1.12345.1.2.3 \
  sysUpTime.0 t 12345678 \
  snmpTrapOID.0 o .1.3.6.1.4.1.12345.1.2.3 \
  myVar.1 s "Test value"
```

### Consuming Messages from RabbitMQ

Python example:
```python
import pika
import json

connection = pika.BlockingConnection(
    pika.URLParameters('amqp://guest:guest@localhost:5672/')
)
channel = connection.channel()
channel.queue_declare(queue='alerts', durable=True)

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"Received alert: {message['alert_name']}")
    print(f"Details: {json.dumps(message['raw'], indent=2)}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='alerts', on_message_callback=callback)
print('Waiting for alerts...')
channel.start_consuming()
```

---

## Troubleshooting

### Common Issues

#### 1. "Permission denied" binding to port 162

**Problem:** Port 162 requires root privileges.

**Solutions:**
```bash
# Option A: Run with sudo
sudo python -m gds_snmp_receiver.receiver

# Option B: Use non-privileged port
export SNMP_LISTEN_PORT="9162"
python -m gds_snmp_receiver.receiver

# Option C: Grant capability (Linux)
sudo setcap 'cap_net_bind_service=+ep' $(which python3)
```

#### 2. "Connection refused" to RabbitMQ

**Problem:** RabbitMQ not running or wrong URL.

**Debug steps:**
```bash
# Check RabbitMQ is running
systemctl status rabbitmq-server

# Test connection
telnet localhost 5672

# Verify credentials
rabbitmqctl list_users

# Check URL format
export RABBIT_URL="amqp://guest:guest@localhost:5672/"
```

#### 3. No traps received

**Problem:** Firewall, wrong port, or incorrect device configuration.

**Debug steps:**
```bash
# Enable DEBUG logging
export GDS_SNMP_LOG_LEVEL="DEBUG"

# Check UDP port is listening
sudo netstat -ulnp | grep 9162

# Use tcpdump to capture traffic
sudo tcpdump -i any -n udp port 9162 -vvv

# Verify device trap destination
# (Check device SNMP configuration to ensure it's sending to correct IP:port)
```

#### 4. Traps received but not published to RabbitMQ

**Problem:** Authentication failure or queue issue.

**Debug steps:**
```bash
# Check logs for "UnknownCommunityName"
docker logs snmp-receiver | grep -i community

# Verify queue exists
rabbitmqctl list_queues name messages

# Check RabbitMQ logs
journalctl -u rabbitmq-server -f

# Verify network connectivity
docker exec snmp-receiver ping rabbitmq
```

#### 5. "UnknownCommunityName" error

**Problem:** Community string mismatch.

**Solution:**
- Receiver expects `'public'` by default
- Check device sends `public` community string
- Or modify receiver to accept your community string

---

## Advanced Topics

### Custom Community Strings

Modify `core.py` to accept multiple community strings:

```python
def _setup_snmp_engine(self) -> None:
    # ... existing code ...
    
    # Accept multiple community strings
    communities = ['public', 'private', 'monitoring']
    for comm in communities:
        config.addV1System(snmp_engine, f'area-{comm}', comm)
```

### SNMPv3 Support

For authenticated/encrypted traps, configure USM users:

```python
from pysnmp.entity.config import addV3User
from pysnmp.entity import engine
from pysnmp import hlapi

# Add USM user
addV3User(
    snmp_engine,
    userName='myuser',
    authProtocol=hlapi.usmHMACSHAAuthProtocol,
    authKey='authkey123',
    privProtocol=hlapi.usmAesCfb128Protocol,
    privKey='privkey456'
)
```

### Message Filtering

Add filtering logic in `_trap_callback`:

```python
def _trap_callback(self, ...):
    # ... parse trap ...
    
    # Filter by OID
    if alert_name.startswith('1.3.6.1.6.3.1.1.5.1'):
        logger.debug("Ignoring coldStart trap")
        return
    
    # Filter by content
    if 'test' in json.dumps(details).lower():
        logger.debug("Ignoring test trap")
        return
    
    # Continue with publish
    self.publish_alert(payload)
```

### Message Enrichment

Add additional data to published messages:

```python
def _trap_callback(self, ...):
    # ... existing code ...
    
    payload = {
        'idempotency_id': idempotency_id,
        'alert_name': alert_name,
        'source': 'snmp',
        'received_at': datetime.utcnow().isoformat() + 'Z',
        'raw': details,
        'subject': f'SNMP Trap: {alert_name}',
        'body_text': json.dumps(details, indent=2),
        
        # Add enrichment
        'receiver_host': socket.gethostname(),
        'environment': os.environ.get('ENV', 'production'),
        'severity': self._determine_severity(alert_name),
    }
```

### High Availability Setup

Run multiple receiver instances with load balancing:

```yaml
# docker-compose.yml
services:
  snmp-receiver-1:
    image: gds-snmp-receiver:latest
    # ... config ...
  
  snmp-receiver-2:
    image: gds-snmp-receiver:latest
    # ... config ...
  
  haproxy:
    image: haproxy:latest
    ports:
      - "162:162/udp"
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
```

**Note:** For UDP load balancing, use consistent hashing or accept duplicate processing with idempotency keys.

### Metrics and Monitoring

Add Prometheus metrics:

```python
from prometheus_client import Counter, Gauge, start_http_server

traps_received = Counter('snmp_traps_received_total', 'Total traps received')
traps_published = Counter('snmp_traps_published_total', 'Total traps published')
publish_errors = Counter('snmp_publish_errors_total', 'Publish failures')

def _trap_callback(self, ...):
    traps_received.inc()
    try:
        self.publish_alert(payload)
        traps_published.inc()
    except Exception:
        publish_errors.inc()
        raise

# In run():
start_http_server(8000)  # Expose metrics on :8000/metrics
```

---

## Further Reading

- **SNMP Protocol**: RFC 3411-3418 (SNMPv3)
- **SNMP Traps**: RFC 3416 (Protocol Operations)
- **pysnmp Documentation**: https://pysnmp.readthedocs.io/
- **RabbitMQ Tutorials**: https://www.rabbitmq.com/tutorials
- **pika Documentation**: https://pika.readthedocs.io/

---

## Contributing

When contributing to this package:

1. **Add tests** for new features
2. **Update documentation** for API changes
3. **Follow PEP 8** style guidelines
4. **Add docstrings** to all public methods
5. **Run E2E tests** before submitting PR

```bash
# Run tests
python -m pytest tests/

# Check style
ruff check gds_snmp_receiver/

# Format code
black gds_snmp_receiver/
```

---

## License

See LICENSE file in repository root.
