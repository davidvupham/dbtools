# MIR3 Emergency Notification Integration

This document describes how to integrate the GDS Notification Service with MIR3 (OnSolve) for emergency notifications.

## Overview

MIR3 is an enterprise emergency notification platform that enables rapid, two-way communication during critical events. The GDS Notification Service integrates with MIR3 via its SOAP API to send high-priority alerts that require delivery confirmation and response tracking.

## When to Use MIR3

Use MIR3 instead of email for notifications that require:

| Requirement | Email | MIR3 |
|-------------|-------|------|
| Delivery confirmation | ❌ Limited | ✅ Full tracking |
| Response collection | ❌ Manual | ✅ Automated |
| Multi-channel delivery | ❌ Email only | ✅ SMS, Voice, Email, App |
| Escalation workflows | ❌ None | ✅ Built-in |
| Audit trail | ❌ Basic | ✅ Comprehensive |

**Recommended MIR3 usage:**

- Critical database outages
- Security incidents
- On-call escalation
- Emergency maintenance notifications

## Configuration

### Environment Variables

```bash
# Required
MIR3_WSDL_URL=https://your-mir3-instance.com/ws/NotificationService?wsdl
MIR3_USERNAME=api_user
MIR3_PASSWORD=api_secret

# Optional
MIR3_DEFAULT_METHOD=broadcast  # broadcast, first_response, callout, bulletin
MIR3_TIMEOUT=60               # Request timeout in seconds
```

### Python Configuration

```python
from gds_notification.providers import MIR3Provider
from gds_notification.providers.mir3 import MIR3NotificationMethod

provider = MIR3Provider(
    wsdl_url="https://your-mir3-instance.com/ws/NotificationService?wsdl",
    username="api_user",
    password="api_secret",
    default_method=MIR3NotificationMethod.BROADCAST,
    timeout=60,
    response_options=["Acknowledge", "Escalate", "Ignore"],
)
```

## Notification Methods

MIR3 supports four notification methods, each suited for different scenarios:

### Broadcast

Send the same message to all recipients simultaneously. Best for general announcements where you want everyone notified at once.

```python
from gds_notification.providers.mir3 import MIR3NotificationMethod

result = provider.send(notification, method=MIR3NotificationMethod.BROADCAST)
```

### First Response

Send to all recipients but stop tracking once the first recipient responds. Useful for "who can help?" scenarios.

```python
result = provider.send(notification, method=MIR3NotificationMethod.FIRST_RESPONSE)
```

### Callout

Sequential notification - contact recipients one at a time until someone responds. Ideal for on-call escalation chains.

```python
result = provider.send(notification, method=MIR3NotificationMethod.CALLOUT)
```

### Bulletin Board

Post a message that recipients can retrieve at their convenience. Good for non-urgent informational messages.

```python
result = provider.send(notification, method=MIR3NotificationMethod.BULLETIN_BOARD)
```

## Usage Examples

### Basic Emergency Notification

```python
from gds_notification.providers import MIR3Provider
from gds_notification.providers.base import Notification, NotificationPriority

# Initialize provider
provider = MIR3Provider(
    wsdl_url="https://mir3.example.com/ws/NotificationService?wsdl",
    username="api_user",
    password="api_secret",
)

# Create notification
notification = Notification(
    recipient="johndoe",  # MIR3 username
    subject="CRITICAL: Database Server Down",
    body="Production database db-prod-01 is unresponsive. Immediate action required.",
    priority=NotificationPriority.EMERGENCY,
    alert_name="DatabaseOutage",
    db_instance_id=42,
    idempotency_id="alert-12345",
)

# Send notification
result = provider.send(notification)

if result.is_success():
    print(f"Notification sent! Report ID: {result.metadata['report_id']}")
else:
    print(f"Failed: {result.error_message}")
```

### Bulk Notification with Status Tracking

```python
from gds_notification.providers import MIR3Provider
from gds_notification.providers.base import Notification, NotificationPriority

with MIR3Provider(
    wsdl_url="https://mir3.example.com/ws/NotificationService?wsdl",
    username="api_user",
    password="api_secret",
) as provider:

    # Create notifications for multiple recipients
    notifications = [
        Notification(
            recipient="user1",
            subject="Security Alert",
            body="Suspicious activity detected",
            priority=NotificationPriority.CRITICAL,
        ),
        Notification(
            recipient="user2",
            subject="Security Alert",
            body="Suspicious activity detected",
            priority=NotificationPriority.CRITICAL,
        ),
    ]

    # Send bulk (recipients with same subject/body are batched)
    results = provider.send_bulk(notifications)

    # Check delivery status
    for result in results:
        if result.is_success():
            # Get detailed status from MIR3
            status = provider.get_notification_status(result.message_id)
            print(f"{result.recipient}: Sent={status.sent_count}, Responded={status.responded_count}")
```

### Integration with Worker

To use MIR3 in the notification worker, update the worker to select the appropriate provider based on the delivery channel:

```python
from gds_notification.providers import SMTPProvider, MIR3Provider
from gds_notification.providers.base import Notification, NotificationPriority

# Initialize providers
smtp_provider = SMTPProvider(
    host="smtp.example.com",
    port=587,
    from_address="alerts@example.com",
)

mir3_provider = MIR3Provider(
    wsdl_url=os.getenv("MIR3_WSDL_URL"),
    username=os.getenv("MIR3_USERNAME"),
    password=os.getenv("MIR3_PASSWORD"),
)

def send_notification(recipient: dict, alert: dict) -> None:
    """Send notification via appropriate channel."""
    notification = Notification(
        recipient=recipient["email"] if recipient["channel"] == "email" else recipient["mir3_username"],
        subject=alert["subject"],
        body=alert["body_text"],
        priority=NotificationPriority.CRITICAL if alert.get("severity") == "critical" else NotificationPriority.NORMAL,
        alert_name=alert["alert_name"],
        idempotency_id=alert["idempotency_id"],
    )

    # Route to appropriate provider
    if recipient["channel"] == "mir3" or alert.get("severity") == "critical":
        result = mir3_provider.send(notification)
    else:
        result = smtp_provider.send(notification)

    return result
```

## Data Model Updates

To support MIR3 as a delivery channel, add the following to your database schema:

```sql
-- Add delivery channel to recipients table
ALTER TABLE dbo.recipients
ADD mir3_username NVARCHAR(100) NULL,
    preferred_channel NVARCHAR(20) DEFAULT 'email';

-- Track MIR3-specific status
ALTER TABLE dbo.recipient_send_status
ADD delivery_channel NVARCHAR(20) DEFAULT 'email',
    mir3_report_id NVARCHAR(100) NULL,
    mir3_response_status NVARCHAR(50) NULL;

-- Update stored procedure to return MIR3 recipients
-- See DATA_MODEL.sql for full implementation
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `NotificationConfigError: zeep library is required` | Missing dependency | Run `pip install zeep` |
| `NotificationConnectionError: Failed to load WSDL` | Invalid WSDL URL | Verify WSDL URL is accessible |
| `NotificationDeliveryError: Authentication failed` | Invalid credentials | Check MIR3 username/password |
| `NotificationTimeoutError` | Slow network or API | Increase timeout setting |

### Debug Logging

Enable debug logging to troubleshoot MIR3 API issues:

```python
import logging

logging.getLogger("gds_notification.providers.mir3").setLevel(logging.DEBUG)
logging.getLogger("zeep").setLevel(logging.DEBUG)
```

### Testing with Mock

For testing without a real MIR3 instance:

```python
from unittest.mock import MagicMock, patch

with patch("gds_notification.providers.mir3.Client") as mock_client:
    mock_response = MagicMock()
    mock_response.notificationReportId = "12345"
    mock_client.return_value.service.sendBroadcast.return_value = mock_response

    provider = MIR3Provider(
        wsdl_url="https://mock.mir3.com/wsdl",
        username="test",
        password="test",
    )
    result = provider.send(notification)

    assert result.is_success()
    assert result.metadata["report_id"] == "12345"
```

## Security Considerations

1. **Credential Storage**: Store MIR3 credentials in Vault/KeyVault, not in code or environment files
2. **Network Security**: Ensure TLS is used for WSDL endpoints
3. **API Permissions**: Use a dedicated API account with minimal required permissions
4. **Audit Logging**: Log all MIR3 API calls for security audit trail

## References

- [MIR3 OnSolve Documentation](https://www.onsolve.com/)
- [GDS Notification Service Design](DESIGN.md)
- [Provider Architecture](../gds_notification/providers/base.py)
