# Exercise 4: Create Monitoring Alerts

## Objective

Build a simple alert evaluation system that:

- Defines alert rules with thresholds
- Evaluates metrics against rules
- Implements deduplication and cooldown
- Sends notifications

## Prerequisites

- Python 3.9+
- Understanding of alerting concepts from Part 8

---

## Step 1: Inspect the Alert System

Navigate to the exercise source directory:

```bash
cd src/04_create_alerts
```

Open `alerting.py`. This script defines:

1. **Data Models**: `AlertRule` and `Alert`.
2. **AlertEvaluator**: The core logic for checking thresholds, duration, and cooldowns.
3. **ConsoleNotifier**: A simple output handler.
4. **Main Demo**: A simulation loop that feeds test metrics to the evaluator.

---

## Step 2: Run the Demo

Run the standalone demo script:

```bash
python alerting.py
```

### Observe the Output

You should see:

1. Normal metrics processed without alerts.
2. CPU condition tracking as duration accumulates (look for "⏳ Condition met").
3. Immediate critical alert for disk.
4. Memory alert after duration threshold.

---

## Step 3: Inspect Kafka Consumer

Open `alerting_kafka.py`. This script extends the system to consume real metrics from a Kafka topic.

```python
# Excerpt from alerting_kafka.py
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'alert-evaluator',
    'auto.offset.reset': 'latest'
})
consumer.subscribe(['gds.metrics.production'])
```

---

## Step 4: Test with Kafka (Optional)

If you have a running Kafka instance (e.g., from Part 7), you can test the consumer.

### Terminal 1: Run the Consumer

```bash
python alerting_kafka.py
```

### Terminal 2: Produce Test Metrics

```bash
echo '{"metric_name":"cpu_usage_percent","value":85,"instance_id":"server-01"}' | \
  kafka-console-producer.sh --topic gds.metrics.production --bootstrap-server localhost:9092
```

---

## Verification Checklist

- [ ] Rules are defined with thresholds and severity
- [ ] Evaluator correctly checks conditions
- [ ] Duration tracking works (condition must be sustained)
- [ ] Cooldown prevents alert spam
- [ ] Alerts are deduplicated (same alert updates fire_count)
- [ ] Notifications display alert details

---

## Challenge Tasks

1. Add email notification using smtplib
2. Implement alert acknowledgment
3. Add alert resolution when condition clears
4. Create a simple web dashboard for active alerts
5. Implement alert grouping (combine related alerts)

---

## Summary

You've built a functional alert evaluation system with:

- Threshold-based rules
- Duration and cooldown logic
- Deduplication
- Extensible notification

This foundation can be extended for production use by adding:

- Persistent storage for alert state
- Enterprise notification integrations
- Web API for rule management
- Metrics on alert performance
