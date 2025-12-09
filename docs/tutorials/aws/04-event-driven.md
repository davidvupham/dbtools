# Event-Driven Architecture

## Introduction
Decouple services using events.

## Components

### Amazon SQS (Simple Queue Service)
Message queuing. Ensures messages are processed even if the consumer is down.
- **Standard**: At-least-once delivery.
- **FIFO**: Ordering guaranteed.

### Amazon SNS (Simple Notification Service)
Pub/Sub messaging.
- Fan-out messages to multiple queues or Lambda functions.

### Amazon EventBridge
Serverless event bus. Routes events from AWS services or custom apps to targets.
