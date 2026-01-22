# RPC (Remote Procedure Call)

In this lesson, you learn to implement the RPC pattern - request/response communication over RabbitMQ.

## The pattern

**RPC** (Remote Procedure Call) provides synchronous-style request/response semantics over asynchronous messaging. A client sends a request and waits for a response.

```
┌────────┐                                           ┌────────┐
│ Client │                                           │ Server │
└───┬────┘                                           └───┬────┘
    │                                                    │
    │  1. Publish request to rpc_queue                   │
    │  ──────────────────────────────────────────────▶  │
    │     (reply_to=callback_queue, correlation_id=X)   │
    │                                                    │
    │                                                    │  2. Process
    │                                                    │
    │  3. Publish response to callback_queue            │
    │  ◀──────────────────────────────────────────────  │
    │     (correlation_id=X)                            │
    │                                                    │
    │  4. Match correlation_id, return result           │
    │                                                    │
```

**Key components:**
- **Request queue** - Well-known queue where server listens
- **Reply queue** - Client's private queue for responses
- **Correlation ID** - Links responses to requests

## When to use RPC

- **Service calls** - Query another service for data
- **Computations** - Offload calculations to workers
- **Validations** - Check data against remote rules
- **Synchronous needs** - When you must wait for a result

## When NOT to use RPC

- **Fire-and-forget** - Use simple publish instead
- **Long-running tasks** - Use work queues with callbacks
- **High latency tolerance** - Async patterns are better
- **Tight coupling concerns** - Consider REST or gRPC instead

## Basic implementation

### Server: rpc_server.py

```python
#!/usr/bin/env python
"""
rpc_server.py - RPC server that calculates Fibonacci numbers.
"""
import pika


def fib(n: int) -> int:
    """Calculate Fibonacci number."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)
    print(f" [.] fib({n})")

    result = fib(n)

    # Send response to the reply_to queue
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=str(result)
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue')
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue='rpc_queue',
        on_message_callback=on_request
    )

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

### Client: rpc_client.py

```python
#!/usr/bin/env python
"""
rpc_client.py - RPC client that requests Fibonacci calculations.
"""
import uuid
import pika


class FibonacciRpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()

        # Create exclusive callback queue
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        # Set up consumer for responses
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        """Handle response messages."""
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n: int) -> int:
        """Make RPC call and wait for response."""
        self.response = None
        self.corr_id = str(uuid.uuid4())

        # Publish request
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=str(n)
        )

        # Wait for response
        while self.response is None:
            self.connection.process_data_events(time_limit=None)

        return int(self.response)


def main():
    client = FibonacciRpcClient()

    print(" [x] Requesting fib(30)")
    response = client.call(30)
    print(f" [.] Got {response}")


if __name__ == '__main__':
    main()
```

## Testing

### Terminal 1: Start server

```bash
python rpc_server.py
# [x] Awaiting RPC requests
```

### Terminal 2: Run client

```bash
python rpc_client.py
# [x] Requesting fib(30)
# [.] Got 832040
```

## RPC with timeout

Real applications need timeouts to avoid waiting forever:

```python
import uuid
import pika


class RpcClient:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def _on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, routing_key: str, body: str) -> str | None:
        """Make RPC call with timeout."""
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                expiration=str(int(self.timeout * 1000))  # Message TTL
            ),
            body=body
        )

        # Wait with timeout
        start_time = time.time()
        while self.response is None:
            elapsed = time.time() - start_time
            if elapsed >= self.timeout:
                raise TimeoutError(f"RPC call timed out after {self.timeout}s")

            self.connection.process_data_events(time_limit=0.1)

        return self.response.decode()

    def close(self):
        self.connection.close()
```

## Production-ready RPC

### Enhanced server

```python
#!/usr/bin/env python
"""Production RPC server with error handling."""
import json
import logging
import traceback
import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RpcServer:
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)

        # Register handlers
        self.handlers = {}

    def register(self, method: str, handler):
        """Register a handler for a method."""
        self.handlers[method] = handler

    def _handle_request(self, ch, method, props, body):
        response = {'success': False, 'result': None, 'error': None}

        try:
            request = json.loads(body)
            method_name = request.get('method')
            params = request.get('params', {})

            if method_name not in self.handlers:
                raise ValueError(f"Unknown method: {method_name}")

            result = self.handlers[method_name](**params)
            response['success'] = True
            response['result'] = result

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            response['error'] = str(e)

        # Send response
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id,
                content_type='application/json'
            ),
            body=json.dumps(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """Start the RPC server."""
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._handle_request
        )
        logger.info(f"RPC Server listening on {self.queue_name}")
        self.channel.start_consuming()


# Usage
def calculate_fib(n: int) -> int:
    if n < 2:
        return n
    return calculate_fib(n - 1) + calculate_fib(n - 2)


def multiply(a: float, b: float) -> float:
    return a * b


server = RpcServer('math_rpc')
server.register('fib', calculate_fib)
server.register('multiply', multiply)
server.start()
```

### Enhanced client

```python
#!/usr/bin/env python
"""Production RPC client with error handling."""
import json
import uuid
import time
import pika


class RpcClientError(Exception):
    """RPC call error."""
    pass


class RpcClient:
    def __init__(self, queue_name: str, timeout: float = 30.0):
        self.queue_name = queue_name
        self.timeout = timeout

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )

        self.responses = {}

    def _on_response(self, ch, method, props, body):
        self.responses[props.correlation_id] = json.loads(body)

    def call(self, method: str, **params):
        """Make RPC call."""
        corr_id = str(uuid.uuid4())

        request = {'method': method, 'params': params}

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=corr_id,
                content_type='application/json'
            ),
            body=json.dumps(request)
        )

        # Wait for response
        start_time = time.time()
        while corr_id not in self.responses:
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"RPC timeout after {self.timeout}s")
            self.connection.process_data_events(time_limit=0.1)

        response = self.responses.pop(corr_id)

        if not response['success']:
            raise RpcClientError(response['error'])

        return response['result']

    def close(self):
        self.connection.close()


# Usage
client = RpcClient('math_rpc')

try:
    result = client.call('fib', n=10)
    print(f"fib(10) = {result}")

    result = client.call('multiply', a=7, b=6)
    print(f"7 * 6 = {result}")

except TimeoutError:
    print("Request timed out")
except RpcClientError as e:
    print(f"Server error: {e}")
finally:
    client.close()
```

## Correlation ID explained

The correlation ID is crucial for matching responses to requests:

```python
# Client sends request with unique correlation_id
correlation_id = str(uuid.uuid4())  # e.g., "abc-123"

channel.basic_publish(
    routing_key='rpc_queue',
    properties=pika.BasicProperties(
        reply_to='my_callback_queue',
        correlation_id=correlation_id  # "abc-123"
    ),
    body=request
)

# Server includes the SAME correlation_id in response
channel.basic_publish(
    routing_key=props.reply_to,  # "my_callback_queue"
    properties=pika.BasicProperties(
        correlation_id=props.correlation_id  # "abc-123"
    ),
    body=response
)

# Client matches response to request by correlation_id
if response_correlation_id == my_correlation_id:
    # This is MY response!
```

## RPC considerations

### Advantages

- Familiar request/response semantics
- Works through message broker (decoupled)
- Survives network blips (with retries)
- Can scale servers independently

### Disadvantages

- Adds latency (two network hops)
- More complex than HTTP
- Blocking calls can hurt performance
- Need to handle timeouts explicitly

### Best practices

1. **Always set timeouts** - Never wait forever
2. **Make operations idempotent** - Retries may duplicate requests
3. **Use message TTL** - Don't process stale requests
4. **Monitor queue depth** - Long queues indicate overload
5. **Consider alternatives** - HTTP/gRPC may be simpler

## Key takeaways

1. **RPC provides request/response** - Synchronous semantics over async messaging
2. **Correlation ID links responses** - Essential for matching
3. **Reply-to specifies callback queue** - Where server sends responses
4. **Always implement timeouts** - Avoid infinite waits
5. **Consider if RPC is needed** - Fire-and-forget is often better
6. **Scale servers independently** - Just add more consumers

## What's next?

You've completed the Messaging Patterns module! Test your knowledge with the quiz, then move on to Module 4: Production.

---

[← Previous: Topics](./04_topics.md) | [Back to Module 3](./README.md) | [Quiz →](./quiz_module_3.md)
