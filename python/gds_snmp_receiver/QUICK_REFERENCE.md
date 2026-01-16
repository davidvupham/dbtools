# GDS SNMP Receiver - Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Running

### Command Line
```bash
python -m gds_snmp_receiver.receiver \
  --host 0.0.0.0 \
  --port 9162 \
  --rabbit amqp://guest:guest@localhost:5672/ \
  --queue alerts \
  --log-level INFO
```

### Environment Variables
```bash
export SNMP_LISTEN_HOST="0.0.0.0"
export SNMP_LISTEN_PORT="9162"
export RABBIT_URL="amqp://guest:guest@rabbitmq:5672/"
export SNMP_QUEUE="alerts"
export GDS_SNMP_LOG_LEVEL="INFO"

python -m gds_snmp_receiver.receiver
```

### Python API
```python
from gds_snmp_receiver import SNMPReceiver

receiver = SNMPReceiver(
    listen_host="0.0.0.0",
    listen_port=9162,
    rabbit_url="amqp://guest:guest@localhost:5672/",
    queue_name="alerts"
)
receiver.run()
```

### Docker
```bash
docker run -d \
  -p 9162:9162/udp \
  -e RABBIT_URL="amqp://guest:guest@rabbitmq:5672/" \
  gds-snmp-receiver:latest
```

## Testing

### Send Test Trap
```bash
# Install snmptrap utility
apt-get install snmp

# Send SNMPv2c trap
snmptrap -v 2c -c public localhost:9162 '' .1.3.6.1.6.3.1.1.5.3

# Send trap with custom varbinds
snmptrap -v 2c -c public localhost:9162 '' \
  .1.3.6.1.4.1.12345.1.2.3 \
  sysUpTime.0 t 12345 \
  snmpTrapOID.0 o .1.3.6.1.4.1.12345.1.2.3 \
  myVar s "Test value"
```

### E2E Test
```bash
# From gds_snmp_receiver directory
cd gds_snmp_receiver
docker compose -f docker-compose.e2e.yml up -d
docker compose -f docker-compose.e2e.yml run --rm snmp-sender \
  python tools/e2e_send_and_check.py
```

### Consume Messages
```python
import pika
import json

connection = pika.BlockingConnection(
    pika.URLParameters('amqp://guest:guest@localhost:5672/')
)
channel = connection.channel()

def callback(ch, method, properties, body):
    msg = json.loads(body)
    print(f"Alert: {msg['alert_name']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='alerts', on_message_callback=callback)
channel.start_consuming()
```

## Configuration

### Common Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| listen_host | 0.0.0.0 | UDP bind address |
| listen_port | 162 | UDP port (162 requires root) |
| rabbit_url | amqp://guest:guest@rabbitmq:5672/ | RabbitMQ connection |
| queue_name | alerts | Queue for messages |
| log_level | INFO | DEBUG, INFO, WARNING, ERROR |

### RabbitMQ URL Format
```
amqp://[username]:[password]@[host]:[port]/[vhost]
```

### Community String
Edit `core.py`:
```python
config.addV1System(snmp_engine, 'my-area', 'YOUR_COMMUNITY')
```

## Message Format

### Published JSON Payload
```json
{
  "idempotency_id": "sha256-hash",
  "alert_name": "1.3.6.1.6.3.1.1.5.3",
  "source": "snmp",
  "received_at": "2025-11-04T12:34:56.789Z",
  "raw": {
    "1.3.6.1.2.1.1.3.0": "12345",
    "1.3.6.1.6.3.1.1.4.1.0": "1.3.6.1.6.3.1.1.5.3"
  },
  "subject": "SNMP Trap: 1.3.6.1.6.3.1.1.5.3",
  "body_text": "{\n  \"1.3.6.1.2.1.1.3.0\": \"12345\",\n  ...\n}"
}
```

## Common SNMP Trap OIDs

| OID | Name | Description |
|-----|------|-------------|
| 1.3.6.1.6.3.1.1.5.1 | coldStart | Device restarted |
| 1.3.6.1.6.3.1.1.5.2 | warmStart | Service restarted |
| 1.3.6.1.6.3.1.1.5.3 | linkDown | Interface down |
| 1.3.6.1.6.3.1.1.5.4 | linkUp | Interface up |
| 1.3.6.1.6.3.1.1.5.5 | authenticationFailure | Invalid community |

## Troubleshooting

### No Traps Received
```bash
# Check port listening
netstat -ulnp | grep 9162

# Capture traffic
tcpdump -i any udp port 9162 -vvv

# Enable debug logging
export GDS_SNMP_LOG_LEVEL=DEBUG
```

### RabbitMQ Connection Failed
```bash
# Test connectivity
telnet rabbitmq 5672

# Check credentials
rabbitmqctl list_users

# View logs
docker logs snmp-receiver
```

### Permission Denied (Port 162)
```bash
# Option 1: Run as root
sudo python -m gds_snmp_receiver.receiver

# Option 2: Use non-privileged port
export SNMP_LISTEN_PORT=9162

# Option 3: Grant capability
sudo setcap cap_net_bind_service=+ep $(which python3)
```

## Logging Levels

### DEBUG
- All operations
- Varbind details
- Connection state
- Payload contents

### INFO (Default)
- Trap reception
- Publish success
- Connection events

### WARNING
- Retry attempts
- Non-critical failures

### ERROR
- Connection failures
- Publish errors
- Exceptions

## Docker Compose Example

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"

  snmp-receiver:
    image: gds-snmp-receiver:latest
    depends_on:
      - rabbitmq
    ports:
      - "162:9162/udp"
    environment:
      SNMP_LISTEN_HOST: "0.0.0.0"
      SNMP_LISTEN_PORT: "9162"
      RABBIT_URL: "amqp://guest:guest@rabbitmq:5672/"
      SNMP_QUEUE: "alerts"
      GDS_SNMP_LOG_LEVEL: "INFO"
    restart: unless-stopped
```

## Health Check

```bash
# Container health
docker inspect --format='{{.State.Health.Status}}' snmp-receiver

# Manual check
test -f /tmp/gds_snmp_ready && echo "Ready" || echo "Not ready"
```

## Monitoring Queries

### RabbitMQ Queue Depth
```bash
rabbitmqctl list_queues name messages
```

### Trap Count (from logs)
```bash
docker logs snmp-receiver | grep "Received SNMP trap" | wc -l
```

### Failed Publishes
```bash
docker logs snmp-receiver | grep "Failed to publish" | wc -l
```

## Performance Tips

1. **Co-locate with RabbitMQ** - Reduce network latency
2. **Use non-privileged port** - Avoid root privileges
3. **Enable connection pooling** - Already implemented
4. **Monitor queue depth** - Alert on backlog
5. **Scale horizontally** - Run multiple instances

## Security Checklist

- [ ] Change default community string from 'public'
- [ ] Use firewall rules to restrict trap sources
- [ ] Use strong RabbitMQ credentials
- [ ] Enable RabbitMQ TLS (amqps://)
- [ ] Run container as non-root user
- [ ] Use network isolation (VLANs/security groups)
- [ ] Monitor for unusual trap volumes (DoS)
- [ ] Rotate credentials regularly

## Further Documentation

- **TUTORIAL.md** - Comprehensive guide with examples
- **ARCHITECTURE.md** - Design decisions and internals
- **DOCKER_E2E_HOWTO.md** - Container and testing guide
- **Code comments** - Inline documentation in core.py

## Support

For issues, questions, or contributions:
1. Check existing documentation
2. Enable DEBUG logging
3. Review logs for errors
4. Test with minimal configuration
5. Verify network connectivity
6. Check RabbitMQ queue state
