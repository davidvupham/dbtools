# Project 1: Simple Chat System

Build a basic chat application where multiple users can send and receive messages in real-time.

## Overview

```
┌──────────┐          ┌────────────┐          ┌──────────┐
│  Alice   │─────────▶│            │─────────▶│   Bob    │
│ (Client) │          │  RabbitMQ  │          │ (Client) │
└──────────┘          │            │          └──────────┘
                      │   Fanout   │
┌──────────┐          │  Exchange  │          ┌──────────┐
│  Carol   │◀─────────│            │◀─────────│  David   │
│ (Client) │          └────────────┘          │ (Client) │
└──────────┘                                  └──────────┘
```

## Requirements

### Functional requirements

1. **Multiple participants** - Any number of users can join the chat
2. **Broadcast messages** - When one user sends a message, all others receive it
3. **User identification** - Each message shows who sent it
4. **Timestamps** - Messages display when they were sent
5. **Graceful exit** - Users can leave without affecting others

### Technical requirements

1. Use a **fanout exchange** for broadcasting
2. Each client creates an **exclusive queue** for receiving
3. Messages should include **headers** for metadata (username, timestamp)
4. Handle **keyboard interrupt** (Ctrl+C) gracefully
5. Use **manual acknowledgments** for reliability

## Project structure

```
project_1_chat/
├── chat_client.py    # Main chat application
├── config.py         # Configuration settings
└── README.md         # Usage instructions
```

## Implementation guide

### Step 1: Configuration (config.py)

```python
"""Chat application configuration."""

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
EXCHANGE_NAME = 'chat_room'
EXCHANGE_TYPE = 'fanout'
```

### Step 2: Chat client (chat_client.py)

Implement the following class:

```python
#!/usr/bin/env python
"""
Simple chat client using RabbitMQ.

Usage:
    python chat_client.py <username>

Example:
    python chat_client.py Alice
"""
import sys
import json
import threading
from datetime import datetime
import pika

from config import RABBITMQ_HOST, EXCHANGE_NAME, EXCHANGE_TYPE


class ChatClient:
    """RabbitMQ-based chat client."""

    def __init__(self, username: str):
        """
        Initialize chat client.

        Args:
            username: Display name for this user
        """
        self.username = username
        self.connection = None
        self.channel = None
        self.queue_name = None
        self._running = False

    def connect(self) -> None:
        """
        Connect to RabbitMQ and set up the chat infrastructure.

        TODO:
        1. Create a BlockingConnection
        2. Create a channel
        3. Declare the fanout exchange
        4. Declare an exclusive queue (let RabbitMQ generate the name)
        5. Bind the queue to the exchange
        """
        # Your implementation here
        pass

    def send_message(self, text: str) -> None:
        """
        Send a message to the chat room.

        TODO:
        1. Create message payload with username, text, timestamp
        2. Publish to the exchange with proper properties
           - content_type: application/json
           - headers: include username and timestamp
        """
        # Your implementation here
        pass

    def _receive_callback(self, ch, method, properties, body) -> None:
        """
        Handle received messages.

        TODO:
        1. Parse the JSON body
        2. Skip messages from self (check headers or body)
        3. Display formatted message: [timestamp] username: text
        4. Acknowledge the message
        """
        # Your implementation here
        pass

    def _start_receiving(self) -> None:
        """
        Start consuming messages in background.

        TODO:
        1. Set up basic_consume with the callback
        2. Start consuming (this runs in a separate thread)
        """
        # Your implementation here
        pass

    def run(self) -> None:
        """
        Main chat loop.

        TODO:
        1. Connect to RabbitMQ
        2. Start receiver thread
        3. Print welcome message
        4. Loop: read input and send messages
        5. Handle Ctrl+C gracefully
        """
        # Your implementation here
        pass

    def close(self) -> None:
        """Clean up resources."""
        self._running = False
        if self.connection and self.connection.is_open:
            self.connection.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python chat_client.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    client = ChatClient(username)

    try:
        client.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        client.close()


if __name__ == '__main__':
    main()
```

## Expected behavior

### Terminal 1: Alice joins

```bash
$ python chat_client.py Alice
Connected to chat room as Alice
Type messages and press Enter to send. Ctrl+C to exit.
----------------------------------------
Hello everyone!
[14:30:15] You: Hello everyone!
[14:30:22] Bob: Hi Alice!
Nice to meet you Bob
[14:30:28] You: Nice to meet you Bob
```

### Terminal 2: Bob joins

```bash
$ python chat_client.py Bob
Connected to chat room as Bob
Type messages and press Enter to send. Ctrl+C to exit.
----------------------------------------
[14:30:15] Alice: Hello everyone!
Hi Alice!
[14:30:22] You: Hi Alice!
[14:30:28] Alice: Nice to meet you Bob
```

### Terminal 3: Carol joins later

```bash
$ python chat_client.py Carol
Connected to chat room as Carol
Type messages and press Enter to send. Ctrl+C to exit.
----------------------------------------
Anyone still here?
[14:35:00] You: Anyone still here?
[14:35:05] Alice: Yes! Welcome Carol
```

## Testing checklist

- [ ] Single user can send and receive (should see own messages)
- [ ] Two users can chat back and forth
- [ ] Messages show correct username and timestamp
- [ ] New users joining don't affect existing users
- [ ] User leaving (Ctrl+C) doesn't crash others
- [ ] Messages are in order

## Bonus challenges

### Challenge 1: Private messages

Add support for private messages using direct exchange:

```
/pm Bob Hey, just between us!
```

### Challenge 2: Chat rooms

Support multiple chat rooms using topic exchange:

```
/join #general
/join #random
```

### Challenge 3: Message history

Store the last 100 messages and replay them when a user joins.

### Challenge 4: Typing indicator

Show "[username] is typing..." when someone is composing a message.

## Hints

<details>
<summary>Hint 1: Threading for receive</summary>

Use a separate thread for consuming messages while the main thread handles user input:

```python
import threading

receive_thread = threading.Thread(target=self._start_receiving, daemon=True)
receive_thread.start()
```

</details>

<details>
<summary>Hint 2: Exclusive queue</summary>

```python
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
```

</details>

<details>
<summary>Hint 3: Filtering own messages</summary>

Include username in headers and check in callback:

```python
if properties.headers.get('username') == self.username:
    return  # Skip own messages
```

</details>

<details>
<summary>Hint 4: Timestamp formatting</summary>

```python
from datetime import datetime

timestamp = datetime.now().strftime('%H:%M:%S')
```

</details>

## Evaluation criteria

| Criteria | Points |
|:---|:---|
| Connects and sets up exchange/queue correctly | 20 |
| Messages broadcast to all participants | 20 |
| Username and timestamp displayed correctly | 15 |
| Own messages handled appropriately | 15 |
| Graceful shutdown (no errors on Ctrl+C) | 15 |
| Code quality (structure, comments, error handling) | 15 |
| **Total** | **100** |

**Passing score:** 80 points

## Submission

Submit:
1. `chat_client.py` - Your complete implementation
2. `config.py` - Configuration file
3. `README.md` - Instructions for running your chat
4. Screenshot or recording demonstrating multi-user chat

---

[← Back to Module 1](./README.md) | [Proceed to Module 2 →](../module_2_core_concepts/README.md)
