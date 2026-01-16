# PagerDuty Integration

This document describes how to integrate the GDS Notification Service with PagerDuty for incident alerting and on-call management.

## Overview

PagerDuty is an incident management platform that helps teams detect, triage, and resolve operational issues. The GDS Notification Service integrates with PagerDuty via the Events API v2 to trigger, acknowledge, and resolve incidents.

## When to Use PagerDuty

| Requirement | Email | PagerDuty |
|-------------|-------|-----------|
| On-call routing | ❌ Manual | ✅ Automatic |
| Escalation policies | ❌ None | ✅ Configurable |
| Incident lifecycle | ❌ None | ✅ Trigger/Ack/Resolve |
| Alert grouping | ❌ None | ✅ Deduplication |
| Response tracking | ❌ None | ✅ Full audit |

**Recommended PagerDuty usage:**

- On-call alerting for production incidents
- Service health degradation
- SLA breach warnings
- Automated incident creation from monitoring

## Configuration

### PagerDuty Setup

1. Create a **Service** in PagerDuty for your alerts
2. Add an **Events API v2 Integration** to the service
3. Copy the **Integration Key** (routing key)

### Environment Variables

```bash
# Required
PAGERDUTY_ROUTING_KEY=your-integration-key-here

# Optional
PAGERDUTY_API_URL=https://events.pagerduty.com/v2/enqueue  # default
PAGERDUTY_TIMEOUT=30                                        # seconds
PAGERDUTY_DEFAULT_SEVERITY=error                           # info/warning/error/critical
```

### Python Configuration

```python
from gds_notification.providers import PagerDutyProvider
from gds_notification.providers.pagerduty import PagerDutySeverity

provider = PagerDutyProvider(
    routing_key="your-integration-key-here",
    timeout=30,
    default_severity=PagerDutySeverity.ERROR,
    source="gds_notification",
)
```

## Usage Examples

### Trigger an Incident

```python
from gds_notification.providers import PagerDutyProvider
from gds_notification.providers.base import Notification, NotificationPriority

provider = PagerDutyProvider(
    routing_key="your-integration-key-here",
)

notification = Notification(
    recipient="database-service",  # Used as component in PagerDuty
    subject="High CPU on db-prod-01",
    body="CPU usage exceeded 90% for 5 minutes. Immediate attention required.",
    priority=NotificationPriority.CRITICAL,
    alert_name="HighCPU",
    db_instance_id=42,
    idempotency_id="alert-12345",  # Becomes dedup_key
)

result = provider.trigger(notification)

if result.is_success():
    print(f"Incident created! Dedup key: {result.metadata['dedup_key']}")
```

### Acknowledge an Incident

```python
# Acknowledge using the dedup_key from trigger
result = provider.acknowledge(dedup_key="alert-12345")
```

### Resolve an Incident

```python
# Resolve using the dedup_key from trigger
result = provider.resolve(dedup_key="alert-12345")
```

### Full Incident Lifecycle

```python
from gds_notification.providers import PagerDutyProvider
from gds_notification.providers.base import Notification, NotificationPriority

with PagerDutyProvider(routing_key="your-key") as provider:
    # 1. Trigger incident when problem detected
    notification = Notification(
        recipient="database-service",
        subject="Database connection pool exhausted",
        body="All connections in use. New connections failing.",
        priority=NotificationPriority.CRITICAL,
        idempotency_id="db-pool-exhausted-001",
    )
    trigger_result = provider.trigger(notification)
    dedup_key = trigger_result.metadata["dedup_key"]

    # 2. Acknowledge when engineer starts working
    provider.acknowledge(dedup_key)

    # 3. Resolve when problem is fixed
    provider.resolve(dedup_key)
```

## Priority Mapping

| GDS Priority | PagerDuty Severity |
|--------------|-------------------|
| LOW | info |
| NORMAL | warning |
| HIGH | error |
| CRITICAL | critical |
| EMERGENCY | critical |

## Deduplication

PagerDuty uses `dedup_key` to group related events into a single incident:

- **Same dedup_key** → Events are grouped into one incident
- **Different dedup_key** → Separate incidents are created

The `idempotency_id` field from notifications becomes the `dedup_key` in PagerDuty.

```python
# These will create ONE incident (same idempotency_id)
notification1 = Notification(
    recipient="db",
    subject="High CPU",
    body="CPU at 91%",
    idempotency_id="cpu-alert-db01",
)
notification2 = Notification(
    recipient="db",
    subject="High CPU",
    body="CPU at 95%",
    idempotency_id="cpu-alert-db01",
)
```

## Integration with Worker

Route critical alerts to PagerDuty based on severity:

```python
from gds_notification.providers import SMTPProvider, PagerDutyProvider
from gds_notification.providers.base import Notification, NotificationPriority

smtp_provider = SMTPProvider(host="smtp.example.com", port=587)
pagerduty_provider = PagerDutyProvider(routing_key=os.getenv("PAGERDUTY_ROUTING_KEY"))

def send_notification(recipient: dict, alert: dict) -> None:
    """Route notification based on severity."""
    priority = (
        NotificationPriority.CRITICAL
        if alert.get("severity") == "critical"
        else NotificationPriority.NORMAL
    )

    notification = Notification(
        recipient=recipient["email"],
        subject=alert["subject"],
        body=alert["body_text"],
        priority=priority,
        alert_name=alert["alert_name"],
        idempotency_id=alert["idempotency_id"],
    )

    # Route critical alerts to PagerDuty
    if priority in (NotificationPriority.CRITICAL, NotificationPriority.EMERGENCY):
        result = pagerduty_provider.trigger(notification)
    else:
        result = smtp_provider.send(notification)

    return result
```

## Error Handling

```python
from gds_notification.exceptions import (
    NotificationConnectionError,
    NotificationDeliveryError,
    NotificationRateLimitError,
    NotificationTimeoutError,
)

try:
    result = provider.trigger(notification)
except NotificationRateLimitError as e:
    # PagerDuty rate limit hit
    print(f"Rate limited. Retry after {e.retry_after_seconds} seconds")
except NotificationTimeoutError as e:
    # Request timed out
    print(f"Timeout after {e.timeout_seconds} seconds")
except NotificationConnectionError as e:
    # Cannot reach PagerDuty
    print(f"Connection failed: {e}")
except NotificationDeliveryError as e:
    # PagerDuty rejected the event
    print(f"Delivery failed: {e}")
```

## Best Practices

1. **Use meaningful dedup_keys**: Include context like alert type and resource ID
2. **Set appropriate severities**: Reserve `critical` for truly urgent issues
3. **Include actionable details**: Body should help responder diagnose quickly
4. **Resolve incidents**: Always resolve when issue is fixed to keep PagerDuty clean
5. **Test in isolation**: Use a test service/integration key for development

## Comparison: PagerDuty vs MIR3

| Feature | PagerDuty | MIR3 |
|---------|-----------|------|
| **Focus** | IT incident management | Emergency mass notification |
| **API** | REST (simple) | SOAP (complex) |
| **Incident lifecycle** | ✅ Trigger/Ack/Resolve | ❌ Fire-and-forget |
| **On-call scheduling** | ✅ Built-in | ❌ External |
| **Response collection** | ❌ Limited | ✅ Full |
| **Multi-channel** | ✅ Phone/SMS/Email/App | ✅ Phone/SMS/Email/App |
| **Best for** | IT ops alerting | Emergency broadcasting |

## References

- [PagerDuty Events API v2 Documentation](https://developer.pagerduty.com/docs/events-api-v2/overview/)
- [PagerDuty Integration Guide](https://support.pagerduty.com/docs/services-and-integrations)
- [GDS Notification Provider Architecture](../gds_notification/providers/base.py)
