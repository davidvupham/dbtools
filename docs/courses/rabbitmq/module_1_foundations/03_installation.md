# Installing RabbitMQ

In this lesson, you set up RabbitMQ using Docker and explore the management interface. By the end, you'll have a working RabbitMQ instance ready for development.

## Prerequisites

Before starting, ensure you have:

- **Docker** or **Podman** installed
  ```bash
  docker --version   # Docker version 20.10+
  # or
  podman --version   # Podman version 3.0+
  ```
- **Python 3.8+** installed
  ```bash
  python --version   # Python 3.8+
  ```
- **Port 5672 and 15672** available on your machine

## Option 1: Docker run (Quick start)

The fastest way to start RabbitMQ for development:

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:management
```

**What this does:**
- `-d` - Run in background (detached)
- `--name rabbitmq` - Name the container "rabbitmq"
- `-p 5672:5672` - Expose AMQP port (client connections)
- `-p 15672:15672` - Expose management UI port
- `rabbitmq:management` - Use the image with management plugin enabled

### Verify it's running

```bash
# Check container status
docker ps

# Expected output:
# CONTAINER ID   IMAGE                 STATUS         PORTS
# abc123...      rabbitmq:management   Up 2 minutes   5672->5672, 15672->15672
```

### Access management UI

1. Open your browser to: **http://localhost:15672**
2. Login with default credentials:
   - Username: `guest`
   - Password: `guest`

```
┌─────────────────────────────────────────────────────────────┐
│                    RabbitMQ Management                       │
├─────────────────────────────────────────────────────────────┤
│  Overview │ Connections │ Channels │ Exchanges │ Queues     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Nodes: rabbit@hostname                                      │
│  Erlang: 26.x.x                                             │
│  RabbitMQ: 4.x.x                                            │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Queued messages:    0 ready │ 0 unacked │ 0 total   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Message rates:  0.0/s publish │ 0.0/s deliver             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Option 2: Docker Compose (Recommended)

For more control and reproducibility, use Docker Compose.

### Create docker-compose.yml

Create the file in your project directory:

```yaml
# docker-compose.yml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:management
    container_name: rabbitmq
    hostname: rabbitmq
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: secret123
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_running"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  rabbitmq_data:
```

### Start with Docker Compose

```bash
# Start RabbitMQ
docker-compose up -d

# View logs
docker-compose logs -f rabbitmq

# Stop RabbitMQ
docker-compose down

# Stop and remove data
docker-compose down -v
```

### Benefits of Docker Compose

| Feature | docker run | docker-compose |
|:---|:---|:---|
| Custom credentials | Command-line flags | Environment file |
| Data persistence | Manual volume | Automatic |
| Reproducibility | Copy/paste command | Version-controlled file |
| Health checks | Not included | Built-in |
| Multiple services | Multiple commands | Single file |

## Option 3: Course-provided setup script

For this course, you can use the provided setup script:

```bash
# Navigate to the course docker directory
cd /path/to/docs/courses/rabbitmq/docker

# Start RabbitMQ
docker-compose up -d

# Verify
docker-compose ps
```

## Exploring the management UI

The management UI is your primary tool for monitoring and debugging RabbitMQ.

### Overview tab

Shows cluster-wide statistics:

- **Nodes** - RabbitMQ servers in the cluster
- **Queued messages** - Ready, Unacked, Total
- **Message rates** - Publish, Deliver, Acknowledge per second
- **Connections/Channels** - Current counts

### Queues tab

Lists all queues with details:

| Column | Description |
|:---|:---|
| Name | Queue name |
| Type | Classic, Quorum, Stream |
| State | Running, Idle, Flow |
| Ready | Messages waiting for consumers |
| Unacked | Delivered but not acknowledged |
| Total | Ready + Unacked |
| Incoming | Messages/second being published |
| Deliver/get | Messages/second being delivered |

**Try it:** Click on a queue name to see details, publish test messages, or purge.

### Exchanges tab

Lists all exchanges:

| Column | Description |
|:---|:---|
| Name | Exchange name (empty = default) |
| Type | direct, topic, fanout, headers |
| Durable | Survives broker restart |
| Auto-delete | Deleted when last binding removed |

**Pre-declared exchanges:**
- `(AMQP default)` - Direct exchange, auto-binds to queues
- `amq.direct` - Direct exchange
- `amq.fanout` - Fanout exchange
- `amq.topic` - Topic exchange
- `amq.headers` - Headers exchange

### Connections tab

Shows client connections:

- **IP address** and port
- **Username** and virtual host
- **Protocol** (AMQP 0-9-1)
- **Channels** count
- **SSL/TLS** status

### Admin tab

Manage users, virtual hosts, and policies:

- **Users** - Create, modify, set permissions
- **Virtual Hosts** - Logical groupings (like databases)
- **Policies** - Apply settings to queues/exchanges by pattern
- **Limits** - Set maximum queues, connections

## Install Python Pika client

Now install the Python client library:

```bash
# Using pip
pip install pika

# Using uv (recommended for this repo)
uv pip install pika

# Verify installation
python -c "import pika; print(pika.__version__)"
# Output: 1.3.2 (or similar)
```

## Verify your setup

Let's run a quick test to ensure everything works.

### Test script

Create a file `test_connection.py`:

```python
#!/usr/bin/env python
"""Test RabbitMQ connection."""
import pika


def test_connection():
    """Test basic RabbitMQ connectivity."""
    try:
        # Connect to RabbitMQ
        credentials = pika.PlainCredentials('guest', 'guest')
        # Or if using docker-compose: ('admin', 'secret123')

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=credentials
            )
        )

        # Create channel
        channel = connection.channel()

        # Declare a test queue
        channel.queue_declare(queue='test_queue')

        # Publish a test message
        channel.basic_publish(
            exchange='',
            routing_key='test_queue',
            body='Hello, RabbitMQ!'
        )
        print("Message published successfully!")

        # Consume the message
        method, properties, body = channel.basic_get(
            queue='test_queue',
            auto_ack=True
        )

        if body:
            print(f"Message received: {body.decode()}")

        # Clean up
        channel.queue_delete(queue='test_queue')
        connection.close()

        print("\nRabbitMQ is working correctly!")
        return True

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Is RabbitMQ running? (docker ps)")
        print("2. Is port 5672 accessible?")
        print("3. Are credentials correct?")
        return False


if __name__ == "__main__":
    test_connection()
```

### Run the test

```bash
python test_connection.py
```

**Expected output:**
```
Message published successfully!
Message received: Hello, RabbitMQ!

RabbitMQ is working correctly!
```

## Troubleshooting

### Connection refused

```
pika.exceptions.AMQPConnectionError: Connection refused
```

**Solutions:**
1. Check if container is running: `docker ps`
2. Check container logs: `docker logs rabbitmq`
3. Verify port mapping: `docker port rabbitmq`
4. Wait for RabbitMQ to fully start (can take 10-30 seconds)

### Authentication failed

```
pika.exceptions.ProbableAuthenticationError: Connection closed
```

**Solutions:**
1. Verify username/password match your setup
2. Default is `guest/guest` for docker run
3. Check `docker-compose.yml` for custom credentials
4. `guest` user can only connect from localhost

### Port already in use

```
Error starting userland proxy: listen tcp 0.0.0.0:5672: bind: address already in use
```

**Solutions:**
1. Stop other RabbitMQ instances: `docker stop rabbitmq`
2. Find process using port: `lsof -i :5672`
3. Use different port: `-p 5673:5672`

### Management UI not accessible

**Solutions:**
1. Ensure port 15672 is mapped: `docker port rabbitmq`
2. Wait 30 seconds after container start
3. Check browser firewall/VPN settings
4. Try `http://127.0.0.1:15672` instead of `localhost`

## Container management commands

```bash
# Start container
docker start rabbitmq

# Stop container
docker stop rabbitmq

# Restart container
docker restart rabbitmq

# Remove container
docker rm -f rabbitmq

# View logs
docker logs rabbitmq
docker logs -f rabbitmq  # Follow

# Execute command in container
docker exec -it rabbitmq bash
docker exec rabbitmq rabbitmqctl status
docker exec rabbitmq rabbitmqctl list_queues
```

## Key takeaways

1. **Docker is the easiest way** to run RabbitMQ for development
2. **Use the management image** (`rabbitmq:management`) for the web UI
3. **Two important ports**: 5672 (AMQP) and 15672 (Management)
4. **Pika is the Python client** - Install with `pip install pika`
5. **Management UI** is essential for monitoring and debugging
6. **Test your setup** before proceeding to the next lessons

## What's next?

In the next lesson, you'll write your first producer and consumer - the classic "Hello World" of messaging.

---

[← Previous: Messaging Concepts](./02_messaging_concepts.md) | [Back to Module 1](./README.md) | [Next: Hello World →](./04_hello_world.md)
