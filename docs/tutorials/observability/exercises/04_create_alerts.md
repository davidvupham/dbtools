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

## Step 1: Create the Alert System

Create `alerting.py`:

```python
"""
Simple Alert Evaluation System
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import uuid

# ============================================
# Data Models
# ============================================

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Operator(Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "=="
    NEQ = "!="

@dataclass
class AlertRule:
    """Definition of an alert rule."""
    id: str
    name: str
    description: str
    metric_name: str
    operator: Operator
    threshold: float
    severity: Severity
    duration: int = 60  # Seconds condition must be true
    cooldown: int = 300  # Seconds between re-alerts
    filters: Dict = field(default_factory=dict)
    runbook_url: Optional[str] = None

@dataclass
class Alert:
    """A triggered alert."""
    id: str
    rule: AlertRule
    metric_value: float
    instance_id: str
    timestamp: datetime
    state: str = "firing"
    fire_count: int = 1

# ============================================
# Alert Evaluator
# ============================================

class AlertEvaluator:
    """Evaluate metrics against alert rules."""

    def __init__(self, rules: List[AlertRule]):
        self.rules = {rule.id: rule for rule in rules}
        self.active_alerts: Dict[str, Alert] = {}
        self.last_fire_time: Dict[str, datetime] = {}
        self.condition_start: Dict[str, datetime] = {}

    def evaluate(self, metric: dict) -> Optional[Alert]:
        """Evaluate a metric against all applicable rules."""

        for rule in self.rules.values():
            if self._matches_rule(metric, rule):
                condition_met = self._check_condition(metric, rule)

                if condition_met:
                    if self._check_duration(metric, rule):
                        if self._check_cooldown(metric, rule):
                            return self._create_alert(metric, rule)
                else:
                    # Condition not met, reset duration tracking
                    self._reset_condition(metric, rule)

        return None

    def _matches_rule(self, metric: dict, rule: AlertRule) -> bool:
        """Check if metric matches rule criteria."""
        if metric.get('metric_name') != rule.metric_name:
            return False

        for key, value in rule.filters.items():
            if metric.get('tags', {}).get(key) != value:
                return False

        return True

    def _check_condition(self, metric: dict, rule: AlertRule) -> bool:
        """Check if metric value meets threshold condition."""
        value = metric.get('value', 0)
        threshold = rule.threshold

        ops = {
            Operator.GT: lambda v, t: v > t,
            Operator.GTE: lambda v, t: v >= t,
            Operator.LT: lambda v, t: v < t,
            Operator.LTE: lambda v, t: v <= t,
            Operator.EQ: lambda v, t: v == t,
            Operator.NEQ: lambda v, t: v != t,
        }

        return ops[rule.operator](value, threshold)

    def _check_duration(self, metric: dict, rule: AlertRule) -> bool:
        """Check if condition has been true for required duration."""
        key = f"{rule.id}:{metric.get('instance_id', 'default')}"
        now = datetime.utcnow()

        if key not in self.condition_start:
            self.condition_start[key] = now
            return False

        elapsed = (now - self.condition_start[key]).total_seconds()
        return elapsed >= rule.duration

    def _check_cooldown(self, metric: dict, rule: AlertRule) -> bool:
        """Check if cooldown period has passed."""
        key = f"{rule.id}:{metric.get('instance_id', 'default')}"

        if key not in self.last_fire_time:
            return True

        elapsed = (datetime.utcnow() - self.last_fire_time[key]).total_seconds()
        return elapsed >= rule.cooldown

    def _reset_condition(self, metric: dict, rule: AlertRule):
        """Reset condition tracking when condition is no longer met."""
        key = f"{rule.id}:{metric.get('instance_id', 'default')}"
        if key in self.condition_start:
            del self.condition_start[key]

    def _create_alert(self, metric: dict, rule: AlertRule) -> Alert:
        """Create or update an alert."""
        instance_id = metric.get('instance_id', 'default')
        alert_key = f"{rule.id}:{instance_id}"

        self.last_fire_time[alert_key] = datetime.utcnow()

        if alert_key in self.active_alerts:
            existing = self.active_alerts[alert_key]
            existing.fire_count += 1
            existing.metric_value = metric.get('value')
            existing.timestamp = datetime.utcnow()
            return existing

        alert = Alert(
            id=str(uuid.uuid4()),
            rule=rule,
            metric_value=metric.get('value'),
            instance_id=instance_id,
            timestamp=datetime.utcnow()
        )

        self.active_alerts[alert_key] = alert
        return alert

    def resolve(self, rule_id: str, instance_id: str) -> Optional[Alert]:
        """Resolve an active alert."""
        key = f"{rule_id}:{instance_id}"

        if key in self.active_alerts:
            alert = self.active_alerts[key]
            alert.state = "resolved"
            del self.active_alerts[key]
            return alert

        return None

# ============================================
# Notification System
# ============================================

class ConsoleNotifier:
    """Simple console notifier for testing."""

    def notify(self, alert: Alert):
        """Print alert to console."""
        emoji = {
            Severity.LOW: "📘",
            Severity.MEDIUM: "📙",
            Severity.HIGH: "🔶",
            Severity.CRITICAL: "🔴",
        }

        print(f"""
{emoji[alert.rule.severity]} ALERT: {alert.rule.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Severity:  {alert.rule.severity.value.upper()}
Instance:  {alert.instance_id}
Value:     {alert.metric_value} ({alert.rule.operator.value} {alert.rule.threshold})
Time:      {alert.timestamp.isoformat()}
Fires:     {alert.fire_count}

{alert.rule.description}

Runbook:   {alert.rule.runbook_url or 'N/A'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# ============================================
# Demo / Test
# ============================================

def main():
    """Demonstrate the alerting system."""

    # Define rules
    rules = [
        AlertRule(
            id="cpu_high",
            name="High CPU Usage",
            description="CPU usage has exceeded 80% for the configured duration.",
            metric_name="cpu_usage_percent",
            operator=Operator.GT,
            threshold=80,
            severity=Severity.HIGH,
            duration=5,  # 5 seconds for demo (normally 300)
            cooldown=30,  # 30 seconds for demo (normally 900)
            runbook_url="https://wiki/runbooks/high-cpu"
        ),
        AlertRule(
            id="disk_critical",
            name="Disk Space Critical",
            description="Disk usage has exceeded 95%. Immediate action required.",
            metric_name="disk_usage_percent",
            operator=Operator.GT,
            threshold=95,
            severity=Severity.CRITICAL,
            duration=0,  # Immediate for critical
            cooldown=60,
            runbook_url="https://wiki/runbooks/disk-critical"
        ),
        AlertRule(
            id="memory_low",
            name="Low Available Memory",
            description="Available memory has dropped below 10%.",
            metric_name="memory_available_percent",
            operator=Operator.LT,
            threshold=10,
            severity=Severity.MEDIUM,
            duration=10,
            cooldown=120
        ),
    ]

    evaluator = AlertEvaluator(rules)
    notifier = ConsoleNotifier()

    print("=" * 50)
    print("Alert Evaluation System Demo")
    print("=" * 50)

    # Simulate metrics
    test_metrics = [
        # Normal metrics - no alert
        {"metric_name": "cpu_usage_percent", "value": 45, "instance_id": "server-01"},
        {"metric_name": "disk_usage_percent", "value": 60, "instance_id": "server-01"},

        # High CPU - starts duration tracking
        {"metric_name": "cpu_usage_percent", "value": 85, "instance_id": "server-01"},
        {"metric_name": "cpu_usage_percent", "value": 87, "instance_id": "server-01"},
        {"metric_name": "cpu_usage_percent", "value": 90, "instance_id": "server-01"},

        # Critical disk - immediate alert
        {"metric_name": "disk_usage_percent", "value": 97, "instance_id": "server-02"},

        # Low memory
        {"metric_name": "memory_available_percent", "value": 8, "instance_id": "server-01"},
        {"metric_name": "memory_available_percent", "value": 5, "instance_id": "server-01"},
    ]

    import time

    for i, metric in enumerate(test_metrics):
        print(f"\n[{i+1}/{len(test_metrics)}] Evaluating: {metric['metric_name']} = {metric['value']} ({metric['instance_id']})")

        alert = evaluator.evaluate(metric)

        if alert:
            notifier.notify(alert)
        else:
            # Check if we're tracking a condition
            for rule in evaluator.rules.values():
                key = f"{rule.id}:{metric.get('instance_id', 'default')}"
                if key in evaluator.condition_start:
                    elapsed = (datetime.utcnow() - evaluator.condition_start[key]).total_seconds()
                    remaining = rule.duration - elapsed
                    if remaining > 0:
                        print(f"  ⏳ Condition met for {rule.name}, duration: {elapsed:.1f}s / {rule.duration}s")

        # Small delay to simulate real-time
        time.sleep(1)

    print("\n" + "=" * 50)
    print(f"Active alerts: {len(evaluator.active_alerts)}")
    for key, alert in evaluator.active_alerts.items():
        print(f"  - {alert.rule.name} on {alert.instance_id}")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

---

## Step 2: Run the Demo

```bash
python alerting.py
```

---

## Step 3: Observe the Output

You should see:

1. Normal metrics processed without alerts
2. CPU condition tracking as duration accumulates
3. Immediate critical alert for disk
4. Memory alert after duration threshold

---

## Step 4: Extend with Kafka Consumer

Create `alerting_kafka.py`:

```python
"""
Alert Evaluation with Kafka Consumer
"""

from confluent_kafka import Consumer, KafkaError
import json
from alerting import AlertRule, AlertEvaluator, ConsoleNotifier, Operator, Severity

def main():
    # Define rules
    rules = [
        AlertRule(
            id="cpu_high",
            name="High CPU Usage",
            description="CPU exceeds 80%",
            metric_name="cpu_usage_percent",
            operator=Operator.GT,
            threshold=80,
            severity=Severity.HIGH,
            duration=60,
            cooldown=300
        ),
    ]

    evaluator = AlertEvaluator(rules)
    notifier = ConsoleNotifier()

    # Kafka consumer
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'alert-evaluator',
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe(['gds.metrics.production'])

    print("Listening for metrics...")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Error: {msg.error()}")
                continue

            try:
                metric = json.loads(msg.value().decode('utf-8'))
                alert = evaluator.evaluate(metric)

                if alert:
                    notifier.notify(alert)

            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
```

---

## Step 5: Test with Kafka (Optional)

If you have Kafka running:

```bash
# Terminal 1: Run the consumer
python alerting_kafka.py

# Terminal 2: Send test metrics
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
