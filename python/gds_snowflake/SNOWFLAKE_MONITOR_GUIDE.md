# Snowflake Monitor Class Documentation

## Overview

The `SnowflakeMonitor` class provides a comprehensive monitoring solution for Snowflake accounts, offering capabilities for:

- **Connectivity Monitoring**: Test account availability and network connectivity
- **Replication Failure Detection**: Monitor failover groups for replication issues
- **Replication Latency Monitoring**: Track replication delays and performance
- **Email Notifications**: Automated alerts for issues and failures
- **Configurable Thresholds**: Customizable alerting criteria

## Key Benefits

### 1. **Object-Oriented Design**
- Modular, reusable class-based architecture
- Clean separation of concerns
- Extensible for additional monitoring features

### 2. **Comprehensive Monitoring**
- Single class handles all monitoring types
- Consistent result formatting
- Built-in error handling and recovery

### 3. **Flexible Configuration**
- Environment variable integration
- Vault-based authentication support
- Customizable thresholds and timeouts

### 4. **Production Ready**
- Email notification system
- Structured logging
- Context manager support
- Error tracking and deduplication

## Quick Start

### Basic Usage

```python
from gds_snowflake import SnowflakeMonitor

# Create monitor instance
monitor = SnowflakeMonitor(
    account="your-account",
    connectivity_timeout=30,
    latency_threshold_minutes=30.0,
    enable_email_alerts=True
)

# Run comprehensive monitoring
results = monitor.monitor_all()

# Check results
if results['summary']['connectivity_ok']:
    print("✓ Connectivity OK")
else:
    print("✗ Connectivity Failed")

print(f"Failures: {results['summary']['groups_with_failures']}")
print(f"Latency Issues: {results['summary']['groups_with_latency']}")

# Clean up
monitor.close()
```

### Context Manager Usage

```python
from gds_snowflake import SnowflakeMonitor

# Use with context manager for automatic cleanup
with SnowflakeMonitor(account="your-account") as monitor:
    # Test connectivity only
    connectivity = monitor.monitor_connectivity()
    if connectivity.success:
        print(f"✓ Connected in {connectivity.response_time_ms}ms")

    # Check replication failures
    failures = monitor.monitor_replication_failures()
    for result in failures:
        if result.has_failure:
            print(f"✗ {result.failover_group}: {result.failure_message}")

    # Check replication latency
    latency_issues = monitor.monitor_replication_latency()
    for result in latency_issues:
        if result.has_latency:
            print(f"⚠ {result.failover_group}: {result.latency_minutes} min")
```

## Monitoring Methods

### 1. Connectivity Monitoring

```python
# Test account connectivity
result = monitor.monitor_connectivity()

print(f"Success: {result.success}")
print(f"Response Time: {result.response_time_ms} ms")
print(f"Account Info: {result.account_info}")
if result.error:
    print(f"Error: {result.error}")
```

**Returns**: `ConnectivityResult` with:
- `success`: Boolean indicating connectivity status
- `response_time_ms`: Connection response time
- `account_info`: Dictionary with account details
- `error`: Error message if connection failed
- `timestamp`: When the test was performed

### 2. Replication Failure Monitoring

```python
# Check for replication failures
results = monitor.monitor_replication_failures()

for result in results:
    print(f"Group: {result.failover_group}")
    print(f"Has Failure: {result.has_failure}")
    if result.has_failure:
        print(f"Message: {result.failure_message}")
        print(f"Last Refresh: {result.last_refresh}")
```

**Returns**: List of `ReplicationResult` objects with:
- `failover_group`: Name of the failover group
- `has_failure`: Boolean indicating if failure detected
- `failure_message`: Description of the failure (if any)
- `last_refresh`: Timestamp of last successful refresh
- `next_refresh`: Scheduled next refresh time

### 3. Replication Latency Monitoring

```python
# Check for replication latency issues
results = monitor.monitor_replication_latency()

for result in results:
    if result.has_latency:
        print(f"Group: {result.failover_group}")
        print(f"Latency: {result.latency_minutes} minutes")
        print(f"Message: {result.latency_message}")
```

**Returns**: List of `ReplicationResult` objects with:
- `failover_group`: Name of the failover group
- `has_latency`: Boolean indicating if latency exceeds threshold
- `latency_minutes`: Actual latency in minutes (if available)
- `latency_message`: Description of the latency issue

### 4. Comprehensive Monitoring

```python
# Run all monitoring checks
results = monitor.monitor_all()

# Access results
connectivity = results['connectivity']
failures = results['replication_failures']
latency = results['replication_latency']
summary = results['summary']

# Summary statistics
print(f"Connectivity OK: {summary['connectivity_ok']}")
print(f"Total Groups: {summary['total_failover_groups']}")
print(f"Failures: {summary['groups_with_failures']}")
print(f"Latency Issues: {summary['groups_with_latency']}")
print(f"Duration: {summary['monitoring_duration_ms']} ms")
```

## Configuration

### Constructor Parameters

```python
monitor = SnowflakeMonitor(
    # Required
    account="your-snowflake-account",

    # Optional Snowflake connection
    user="username",                    # Or use SNOWFLAKE_USER env var
    warehouse="warehouse_name",
    role="role_name",
    database="database_name",

    # Monitoring configuration
    connectivity_timeout=30,            # Seconds
    latency_threshold_minutes=30.0,     # Minutes
    enable_email_alerts=True,

    # Email configuration
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user="alerts@company.com",
    smtp_password="app_password",
    from_email="snowflake-monitor@company.com",
    to_emails=["admin@company.com", "ops@company.com"],

    # Vault configuration (optional)
    vault_namespace="namespace",
    vault_secret_path="secret/snowflake",
    vault_mount_point="kv-v2",
    vault_role_id="role-id",
    vault_secret_id="secret-id",
    vault_addr="https://vault.company.com"
)
```

### Environment Variables

The monitor can use environment variables for configuration:

```bash
# Snowflake connection
export SNOWFLAKE_USER="username"
export SNOWFLAKE_WAREHOUSE="warehouse"
export SNOWFLAKE_ROLE="role"
export SNOWFLAKE_DATABASE="database"

# Vault configuration (if using Vault)
export VAULT_ADDR="https://vault.company.com"
export VAULT_NAMESPACE="namespace"
export VAULT_SECRET_PATH="secret/snowflake"
export VAULT_MOUNT_POINT="kv-v2"
export VAULT_ROLE_ID="role-id"
export VAULT_SECRET_ID="secret-id"

# Email configuration
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="alerts@company.com"
export SMTP_PASSWORD="app_password"
export FROM_EMAIL="snowflake-monitor@company.com"
export TO_EMAILS="admin@company.com,ops@company.com"
```

## Email Notifications

### Automatic Alerts

The monitor sends automatic email notifications for:

1. **Connectivity Failures**: When account cannot be reached
2. **Replication Failures**: When failover group replication fails
3. **Latency Issues**: When replication exceeds threshold

### Notification Features

- **Deduplication**: Prevents spam by tracking notification state
- **Rich Content**: Detailed error information and diagnostics
- **Severity Levels**: Critical for failures, Warning for latency
- **Automatic Recovery**: Stops notifications when issues resolve

### Email Configuration

```python
# Configure email settings
monitor = SnowflakeMonitor(
    account="your-account",
    smtp_server="smtp.company.com",
    smtp_port=587,
    smtp_user="monitor@company.com",
    smtp_password="secure_password",
    from_email="snowflake-alerts@company.com",
    to_emails=["ops@company.com", "admin@company.com"],
    enable_email_alerts=True
)
```

## Command Line Usage

### Basic Monitoring Script

The package includes a ready-to-use monitoring script:

```bash
# Test connectivity only
python monitor_snowflake.py --account your-account --connectivity-only

# Check replication only
python monitor_snowflake.py --account your-account --replication-only

# Comprehensive monitoring (default)
python monitor_snowflake.py --account your-account

# Enable email notifications
python monitor_snowflake.py --account your-account --enable-email

# JSON output
python monitor_snowflake.py --account your-account --json

# Custom thresholds
python monitor_snowflake.py --account your-account \
    --connectivity-timeout 60 \
    --latency-threshold 45.0

# Verbose logging
python monitor_snowflake.py --account your-account --verbose
```

### Exit Codes

The script returns appropriate exit codes for automation:

- `0`: All monitoring checks passed
- `1`: Issues detected or errors occurred

## Integration Examples

### Cron Job

```bash
# Monitor every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/monitor_snowflake.py --account prod-account --enable-email >> /var/log/snowflake-monitor.log 2>&1
```

### Systemd Service

```ini
[Unit]
Description=Snowflake Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /opt/snowflake-monitor/monitor_snowflake.py --account prod-account --enable-email
User=monitor
Group=monitor

[Install]
WantedBy=multi-user.target
```

### Docker Container

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY monitor_snowflake.py .
COPY gds_snowflake/ ./gds_snowflake/

CMD ["python", "monitor_snowflake.py", "--account", "$SNOWFLAKE_ACCOUNT", "--enable-email"]
```

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: snowflake-monitor
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: monitor
            image: snowflake-monitor:latest
            env:
            - name: SNOWFLAKE_ACCOUNT
              value: "prod-account"
            - name: VAULT_ADDR
              valueFrom:
                secretKeyRef:
                  name: vault-config
                  key: vault-addr
          restartPolicy: OnFailure
```

## Advanced Usage

### Custom Monitoring Logic

```python
from gds_snowflake import SnowflakeMonitor, AlertSeverity

class CustomSnowflakeMonitor(SnowflakeMonitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_metrics = {}

    def monitor_custom_metrics(self):
        """Add custom monitoring logic."""
        # Your custom monitoring code here
        pass

    def send_custom_alert(self, message, severity=AlertSeverity.WARNING):
        """Send custom alerts."""
        self._send_email(
            subject=f"Custom Alert - {self.account}",
            body=message,
            severity=severity
        )

# Use custom monitor
monitor = CustomSnowflakeMonitor(account="your-account")
monitor.monitor_custom_metrics()
```

### Batch Monitoring Multiple Accounts

```python
from gds_snowflake import SnowflakeMonitor

accounts = ["prod-account", "staging-account", "dev-account"]
results = {}

for account in accounts:
    with SnowflakeMonitor(account=account) as monitor:
        results[account] = monitor.monitor_all()

# Process results
for account, result in results.items():
    if not result['summary']['connectivity_ok']:
        print(f"❌ {account}: Connectivity Failed")
    else:
        print(f"✅ {account}: All OK")
```

### Integration with Monitoring Systems

```python
import json
from gds_snowflake import SnowflakeMonitor

def send_to_prometheus(metrics):
    """Send metrics to Prometheus."""
    # Your Prometheus integration code
    pass

def send_to_datadog(metrics):
    """Send metrics to Datadog."""
    # Your Datadog integration code
    pass

# Monitor and export metrics
with SnowflakeMonitor(account="prod-account") as monitor:
    results = monitor.monitor_all()

    # Convert to metrics format
    metrics = {
        'snowflake_connectivity': 1 if results['summary']['connectivity_ok'] else 0,
        'snowflake_failover_groups_total': results['summary']['total_failover_groups'],
        'snowflake_replication_failures': results['summary']['groups_with_failures'],
        'snowflake_latency_issues': results['summary']['groups_with_latency']
    }

    # Export to monitoring systems
    send_to_prometheus(metrics)
    send_to_datadog(metrics)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Vault configuration and credentials
   - Check environment variables
   - Ensure RSA key is properly configured

2. **Connection Timeouts**
   - Increase `connectivity_timeout` parameter
   - Check network connectivity to Snowflake
   - Verify account name and region

3. **Email Notification Issues**
   - Verify SMTP server settings
   - Check firewall rules for SMTP ports
   - Ensure authentication credentials are correct

4. **Missing Failover Groups**
   - Verify role has appropriate permissions
   - Check if account has replication configured
   - Ensure user can access ACCOUNT_USAGE schema

### Logging

Enable verbose logging for troubleshooting:

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use monitor with debug logging
monitor = SnowflakeMonitor(account="your-account")
results = monitor.monitor_all()
```

### Testing

Test individual components:

```python
# Test connectivity only
connectivity = monitor.monitor_connectivity()
print(f"Connectivity: {'OK' if connectivity.success else 'FAILED'}")

# Test email configuration
monitor._send_email(
    subject="Test Email",
    body="This is a test email from SnowflakeMonitor",
    severity=AlertSeverity.INFO
)
```

## Migration from Script-Based Monitoring

### Key Differences

| Script-Based | Class-Based |
|--------------|-------------|
| Procedural code | Object-oriented |
| Single-use execution | Reusable instances |
| Global state | Encapsulated state |
| Hard to test | Easy to unit test |
| Limited extensibility | Highly extensible |

### Migration Steps

1. **Replace script imports**:
   ```python
   # Old
   from monitor_snowflake_replication import check_connectivity

   # New
   from gds_snowflake import SnowflakeMonitor
   ```

2. **Update monitoring logic**:
   ```python
   # Old
   if check_connectivity(account):
       check_replication_failures()

   # New
   with SnowflakeMonitor(account=account) as monitor:
       results = monitor.monitor_all()
   ```

3. **Modify automation scripts**:
   ```bash
   # Old
   python monitor_snowflake_replication.py --account prod

   # New
   python monitor_snowflake.py --account prod
   ```

This class-based approach provides better maintainability, testability, and extensibility compared to the original script-based monitoring solution.
