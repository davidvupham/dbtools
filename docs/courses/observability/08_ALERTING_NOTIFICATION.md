# Part 8: Alerting and Notification

## What You'll Learn

In this part, you'll learn:

- Alert rule design and evaluation
- Building an alert evaluation service
- Deduplication and cooldown strategies
- Circuit breaker patterns for reliability
- Notification service integration
- Alert enrichment and auto-remediation

---

## Alerting Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALERTING PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Metrics (Kafka) ──► Evaluation ──► Dedup ──► Notify            │
│                          │            │          │               │
│                          ▼            ▼          ▼               │
│                    ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│                    │  Rule   │  │ Active  │  │Notifier │        │
│                    │ Engine  │  │ Alerts  │  │ Service │        │
│                    └─────────┘  └─────────┘  └─────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Alert Rule Design

### Rule Types

| Type | Description | Example |
|------|-------------|---------|
| **Threshold** | Value exceeds/falls below limit | CPU > 80% |
| **Rate** | Rate of change exceeds limit | Error rate > 5% |
| **Absence** | Expected data missing | No heartbeat for 5 min |
| **Anomaly** | Deviation from baseline | 3 std dev from norm |

### Alert Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| **Critical** | System down, data loss risk | Immediate | Database offline |
| **High** | Major impact, degraded service | 15 minutes | High error rate |
| **Medium** | Noticeable impact | 1 hour | Elevated latency |
| **Low** | Minor issue, no user impact | Next business day | Disk 70% full |

### Rule Definition

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class AlertSeverity(Enum):
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
    severity: AlertSeverity
    duration: int = 60              # Seconds condition must be true
    cooldown: int = 300             # Seconds between re-alerts
    labels: dict = None             # Additional context
    runbook_url: Optional[str] = None
    filters: dict = None            # e.g., {"environment": "production"}

# Example rules
rules = [
    AlertRule(
        id="cpu_high",
        name="High CPU Usage",
        description="CPU usage exceeds 80%",
        metric_name="cpu_usage_percent",
        operator=Operator.GT,
        threshold=80,
        severity=AlertSeverity.HIGH,
        duration=300,  # 5 minutes
        cooldown=900,  # 15 minutes
        runbook_url="https://wiki/runbooks/high-cpu",
        filters={"environment": "production"}
    ),
    AlertRule(
        id="disk_critical",
        name="Disk Space Critical",
        description="Disk usage exceeds 95%",
        metric_name="disk_usage_percent",
        operator=Operator.GT,
        threshold=95,
        severity=AlertSeverity.CRITICAL,
        duration=60,
        cooldown=300,
        runbook_url="https://wiki/runbooks/disk-full"
    ),
]
```

---

## Alert Evaluation Service

### Evaluator Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid

@dataclass
class Alert:
    """Represents a triggered alert."""
    id: str
    rule: AlertRule
    metric_value: float
    instance_id: str
    timestamp: datetime
    state: str = "firing"  # firing, acknowledged, resolved
    fire_count: int = 1

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
                if self._check_condition(metric, rule):
                    if self._check_duration(metric, rule):
                        if self._check_cooldown(rule):
                            return self._create_alert(metric, rule)

        return None

    def _matches_rule(self, metric: dict, rule: AlertRule) -> bool:
        """Check if metric matches rule criteria."""
        # Check metric name
        if metric.get('metric_name') != rule.metric_name:
            return False

        # Check filters
        if rule.filters:
            for key, value in rule.filters.items():
                if metric.get('tags', {}).get(key) != value:
                    return False

        return True

    def _check_condition(self, metric: dict, rule: AlertRule) -> bool:
        """Check if metric value meets threshold condition."""
        value = metric.get('value')
        threshold = rule.threshold

        operators = {
            Operator.GT: lambda v, t: v > t,
            Operator.GTE: lambda v, t: v >= t,
            Operator.LT: lambda v, t: v < t,
            Operator.LTE: lambda v, t: v <= t,
            Operator.EQ: lambda v, t: v == t,
            Operator.NEQ: lambda v, t: v != t,
        }

        return operators[rule.operator](value, threshold)

    def _check_duration(self, metric: dict, rule: AlertRule) -> bool:
        """Check if condition has been true for required duration."""
        key = f"{rule.id}:{metric.get('instance_id')}"
        now = datetime.utcnow()

        if key not in self.condition_start:
            self.condition_start[key] = now
            return False

        elapsed = (now - self.condition_start[key]).total_seconds()
        return elapsed >= rule.duration

    def _check_cooldown(self, rule: AlertRule) -> bool:
        """Check if cooldown period has passed."""
        key = rule.id

        if key not in self.last_fire_time:
            return True

        elapsed = (datetime.utcnow() - self.last_fire_time[key]).total_seconds()
        return elapsed >= rule.cooldown

    def _create_alert(self, metric: dict, rule: AlertRule) -> Alert:
        """Create a new alert."""
        alert_key = f"{rule.id}:{metric.get('instance_id')}"

        # Update tracking
        self.last_fire_time[rule.id] = datetime.utcnow()

        # Check if this is a new alert or re-fire
        if alert_key in self.active_alerts:
            existing = self.active_alerts[alert_key]
            existing.fire_count += 1
            existing.metric_value = metric.get('value')
            existing.timestamp = datetime.utcnow()
            return existing

        # Create new alert
        alert = Alert(
            id=str(uuid.uuid4()),
            rule=rule,
            metric_value=metric.get('value'),
            instance_id=metric.get('instance_id'),
            timestamp=datetime.utcnow()
        )

        self.active_alerts[alert_key] = alert
        return alert
```

### Kafka Consumer Integration

```python
from confluent_kafka import Consumer
import json

class AlertingService:
    """Consume metrics and evaluate alerts."""

    def __init__(self, bootstrap_servers: str, rules: List[AlertRule]):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'gds-alerting',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': False,
        })
        self.evaluator = AlertEvaluator(rules)
        self.notifier = NotificationServiceClient()

    def start(self):
        """Start consuming and evaluating metrics."""
        self.consumer.subscribe(['gds.metrics.production'])

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None or msg.error():
                    continue

                try:
                    metric = json.loads(msg.value().decode('utf-8'))
                    alert = self.evaluator.evaluate(metric)

                    if alert:
                        self.notifier.send_alert(alert)

                    self.consumer.commit()

                except Exception as e:
                    print(f"Processing error: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()
```

---

## Deduplication Strategies

### Alert Key Generation

```python
def generate_dedup_key(rule: AlertRule, metric: dict, window_minutes: int = 15) -> str:
    """Generate deduplication key for an alert."""

    instance_id = metric.get('instance_id', 'unknown')

    # Time bucket allows re-firing after window
    timestamp = datetime.utcnow()
    time_bucket = int(timestamp.timestamp() // (window_minutes * 60))

    return f"{rule.id}:{instance_id}:{metric.get('metric_name')}:{time_bucket}"
```

### State Machine for Alerts

```python
class AlertState(Enum):
    PENDING = "pending"      # Condition detected, awaiting duration
    FIRING = "firing"        # Alert active
    ACKNOWLEDGED = "acknowledged"  # Alert seen by responder
    RESOLVED = "resolved"    # Condition cleared
    SILENCED = "silenced"    # Manually suppressed

class AlertStateMachine:
    """Manage alert lifecycle states."""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}

    def transition(self, alert_key: str, new_state: AlertState):
        """Transition alert to new state."""
        if alert_key not in self.alerts:
            return

        alert = self.alerts[alert_key]
        old_state = alert.state

        # Validate transition
        valid_transitions = {
            AlertState.PENDING: [AlertState.FIRING, AlertState.RESOLVED],
            AlertState.FIRING: [AlertState.ACKNOWLEDGED, AlertState.RESOLVED, AlertState.SILENCED],
            AlertState.ACKNOWLEDGED: [AlertState.RESOLVED, AlertState.SILENCED],
            AlertState.RESOLVED: [AlertState.FIRING],  # Can re-fire
            AlertState.SILENCED: [AlertState.RESOLVED, AlertState.FIRING],
        }

        if new_state in valid_transitions.get(AlertState(old_state), []):
            alert.state = new_state.value
            self._on_transition(alert, old_state, new_state)

    def _on_transition(self, alert: Alert, old_state: str, new_state: AlertState):
        """Handle state transition events."""
        if new_state == AlertState.FIRING:
            self._send_notification(alert)
        elif new_state == AlertState.RESOLVED:
            self._send_resolution(alert)
```

---

## Circuit Breaker Pattern

Protect against notification service failures:

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == CircuitState.OPEN:
            if self._should_try_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _should_try_recovery(self) -> bool:
        """Check if recovery timeout has passed."""
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0
        else:
            self.failures = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failures += 1
        self.last_failure_time = time.time()
        self.successes = 0

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

class CircuitOpenError(Exception):
    pass
```

---

## Notification Service Integration

### Notification Client

```python
import aiohttp
from typing import Optional

class NotificationServiceClient:
    """Client for enterprise notification service."""

    def __init__(
        self,
        api_url: str = "https://notifications.example.com",
        timeout: int = 30
    ):
        self.api_url = api_url
        self.timeout = timeout
        self.circuit_breaker = CircuitBreaker()

    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to notification service."""

        payload = self._format_payload(alert)

        try:
            return await self.circuit_breaker.call(
                self._send_request, payload
            )
        except CircuitOpenError:
            # Queue for later or use fallback
            await self._queue_for_retry(alert)
            return False

    async def _send_request(self, payload: dict) -> bool:
        """Send HTTP request to notification service."""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/api/alerts",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    return True
                else:
                    raise Exception(f"HTTP {response.status}")

    def _format_payload(self, alert: Alert) -> dict:
        """Format alert for notification service API."""

        return {
            "alert_id": alert.id,
            "alert_name": alert.rule.name,
            "severity": alert.rule.severity.value,
            "instance_id": alert.instance_id,
            "message": self._format_message(alert),
            "value": alert.metric_value,
            "threshold": alert.rule.threshold,
            "runbook_url": alert.rule.runbook_url,
            "timestamp": alert.timestamp.isoformat() + "Z",
            "labels": alert.rule.labels or {},
            "fire_count": alert.fire_count,
        }

    def _format_message(self, alert: Alert) -> str:
        """Format human-readable alert message."""

        return f"""
🚨 {alert.rule.name}

Severity: {alert.rule.severity.value.upper()}
Instance: {alert.instance_id}
Value: {alert.metric_value} (threshold: {alert.rule.operator.value} {alert.rule.threshold})

Description: {alert.rule.description}

Runbook: {alert.rule.runbook_url or 'N/A'}
Fire Count: {alert.fire_count}
        """.strip()
```

---

## Alert Enrichment

Add context to alerts for faster resolution:

```python
class AlertEnricher:
    """Enrich alerts with additional context."""

    def __init__(self):
        self.log_client = LogQueryClient()
        self.trace_client = TraceQueryClient()
        self.cmdb_client = CMDBClient()

    async def enrich(self, alert: Alert) -> dict:
        """Gather enrichment data for an alert."""

        enrichment = {}

        # Get related logs
        try:
            logs = await self.log_client.query(
                instance_id=alert.instance_id,
                time_range="5m",
                level="ERROR"
            )
            enrichment["recent_errors"] = logs[:5]
        except Exception as e:
            enrichment["log_error"] = str(e)

        # Get related traces
        try:
            traces = await self.trace_client.query(
                service=alert.instance_id,
                status="ERROR",
                limit=5
            )
            enrichment["error_traces"] = [
                {"trace_id": t.trace_id, "url": t.url}
                for t in traces
            ]
        except Exception as e:
            enrichment["trace_error"] = str(e)

        # Get asset info from CMDB
        try:
            asset = await self.cmdb_client.get_asset(alert.instance_id)
            enrichment["owner"] = asset.owner
            enrichment["team"] = asset.team
            enrichment["environment"] = asset.environment
        except Exception as e:
            enrichment["cmdb_error"] = str(e)

        # Add dashboard link
        enrichment["dashboard_url"] = self._build_dashboard_url(alert)

        return enrichment

    def _build_dashboard_url(self, alert: Alert) -> str:
        """Build Grafana dashboard URL."""
        return (
            f"https://grafana.example.com/d/instance-health"
            f"?var-instance={alert.instance_id}"
            f"&from=now-1h&to=now"
        )
```

---

## Auto-Remediation

For known issues, attempt automatic fixes:

```python
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Remediation:
    """Definition of an auto-remediation action."""
    id: str
    name: str
    action: Callable
    alert_rules: List[str]  # Rule IDs this applies to
    requires_approval: bool = False
    max_attempts: int = 1
    cooldown: int = 3600  # 1 hour between attempts

class AutoRemediation:
    """Automatic remediation for known issues."""

    def __init__(self, remediations: List[Remediation]):
        self.remediations = {r.id: r for r in remediations}
        self.rule_to_remediation = {}
        self.last_attempt: Dict[str, datetime] = {}

        for r in remediations:
            for rule_id in r.alert_rules:
                self.rule_to_remediation[rule_id] = r

    async def attempt_remediation(self, alert: Alert) -> Optional[dict]:
        """Attempt auto-remediation for an alert."""

        remediation = self.rule_to_remediation.get(alert.rule.id)
        if not remediation:
            return None

        # Check cooldown
        key = f"{remediation.id}:{alert.instance_id}"
        if key in self.last_attempt:
            elapsed = (datetime.utcnow() - self.last_attempt[key]).total_seconds()
            if elapsed < remediation.cooldown:
                return {"status": "skipped", "reason": "cooldown"}

        # Attempt remediation
        try:
            self.last_attempt[key] = datetime.utcnow()

            result = await remediation.action(alert)

            return {
                "status": "success",
                "remediation": remediation.name,
                "result": result
            }

        except Exception as e:
            return {
                "status": "failed",
                "remediation": remediation.name,
                "error": str(e)
            }

# Example remediations
async def restart_agent(alert: Alert) -> str:
    """Restart monitoring agent on instance."""
    # Implementation...
    return "Agent restarted"

async def clear_temp_files(alert: Alert) -> str:
    """Clear temporary files to free disk space."""
    # Implementation...
    return "Cleared 5GB of temp files"

remediations = [
    Remediation(
        id="restart_agent",
        name="Restart Monitoring Agent",
        action=restart_agent,
        alert_rules=["agent_not_responding"],
        max_attempts=2,
        cooldown=3600
    ),
    Remediation(
        id="clear_temp",
        name="Clear Temporary Files",
        action=clear_temp_files,
        alert_rules=["disk_high", "disk_critical"],
        max_attempts=1,
        cooldown=86400  # Once per day
    ),
]
```

---

## Best Practices

### Alert Design

1. **Alert on symptoms, not causes** - Alert on user-visible impact
2. **Include actionable information** - Runbook, dashboard links
3. **Set appropriate thresholds** - Avoid alert fatigue
4. **Use escalation** - Low → High if not resolved
5. **Test alerts regularly** - Verify they fire when expected

### Monitoring Checklist

| Category | Metrics to Alert On |
|----------|---------------------|
| **Availability** | Service up/down, health checks |
| **Latency** | Response time p99, database query time |
| **Errors** | Error rate, exception counts |
| **Saturation** | CPU, memory, disk, connections |
| **Business** | Transaction failures, SLA breaches |

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Too many alerts | Alert fatigue | Prioritize, tune thresholds |
| Alerting on raw values | Noisy, false positives | Use averages, percentiles |
| No runbook | Slow resolution | Document every alert |
| Same severity for all | Can't prioritize | Use appropriate severity |
| No cooldown | Spam during incidents | Implement cooldown |

---

## Summary

| Topic | Key Points |
|-------|------------|
| **Rule Design** | Threshold, rate, absence, anomaly detection |
| **Severity** | Critical/High/Medium/Low with response times |
| **Deduplication** | Alert keys, time windows, state machine |
| **Circuit Breaker** | Protect against notification failures |
| **Enrichment** | Logs, traces, owner info, dashboards |
| **Auto-Remediation** | Safe, idempotent, with cooldowns |

### Key Takeaways

1. **Design rules carefully** - threshold, duration, cooldown
2. **Deduplicate alerts** - prevent spam during incidents
3. **Use circuit breakers** - handle notification failures gracefully
4. **Enrich alerts** - provide context for faster resolution
5. **Automate carefully** - only safe, tested remediations

---

## What's Next?

Part 9 covers **Best Practices** for building production observability systems.

[Continue to Part 9: Best Practices →](09_BEST_PRACTICES.md)
