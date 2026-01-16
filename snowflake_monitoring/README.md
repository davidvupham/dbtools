# Snowflake Monitoring Application

A complete application for monitoring Snowflake replication, detecting failures and latency issues, with email notifications. This is part of the DBTools workspace.

## Features

- **Continuous Monitoring**: Monitor Snowflake failover groups in real-time
- **Failure Detection**: Detect replication failures and send alerts
- **Latency Detection**: Calculate and monitor replication latency with configurable thresholds
- **Email Notifications**: Send notifications only once per failure to avoid spam
- **Intelligent Account Switching**: Automatically query secondary accounts when needed
- **Comprehensive Logging**: All operations logged for audit and debugging
- **Flexible Scheduling**: Supports various cron schedules (10min, 30min, hourly, etc.)

## Contents

- `monitor_snowflake_replication.py` - Main monitoring script (uses gds_snowflake package with RSA key authentication)
- `example_module_usage.py` - Examples of using the gds_snowflake package
- `config.sh.example` - Configuration template
- `requirements.txt` - Application dependencies

## Installation

### Prerequisites

1. Install the gds_snowflake package:
```bash
# From PyPI (when published)
pip install gds-snowflake

# Or from source
cd ../gds_snowflake
pip install .
```

2. Install application dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

The application uses environment variables for credentials and email configuration:

```bash
# Snowflake credentials
export SNOWFLAKE_USER="your_username"
# Note: Password authentication removed - using RSA key authentication via Vault

# Optional: Warehouse and Role
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_ROLE="ACCOUNTADMIN"

# Email configuration (optional)
export SMTP_SERVER="smtp.example.com"
export SMTP_USER="smtp_user"
export SMTP_PASSWORD="smtp_password"
export FROM_EMAIL="monitor@example.com"
export TO_EMAILS="admin1@example.com,admin2@example.com"
```

### Using Configuration File

Copy and edit the configuration template:
```bash
cp config.sh.example config.sh
# Edit config.sh with your credentials
source config.sh
```

## Usage

### Basic Usage (Recommended)

```bash
# Continuous monitoring (checks every 60 seconds)
python monitor_snowflake_replication.py myaccount

# Run once and exit
python monitor_snowflake_replication.py myaccount --once

# Custom monitoring interval (in seconds)
python monitor_snowflake_replication.py myaccount --interval 300  # 5 minutes
```

### Connectivity Testing

```bash
# Test connectivity only (no replication monitoring)
python monitor_snowflake_replication.py myaccount --test-connectivity

# Test with custom timeout
python monitor_snowflake_replication.py myaccount --test-connectivity --connectivity-timeout 60
```

### With Command-Line Arguments

```bash
# Provide credentials via command line (Note: RSA key authentication via Vault)
python monitor_snowflake_replication.py myaccount \
    --user myuser \
    --warehouse COMPUTE_WH \
    --role ACCOUNTADMIN

# Run once for testing
python monitor_snowflake_replication.py myaccount \
    --user myuser \
    --once
```

## What It Monitors

### 1. Snowflake Connectivity

**Before each monitoring cycle**, the script tests:
- Network connectivity to Snowflake
- Authentication and authorization
- Account availability and status
- Response time and performance

**Benefits:**
- Early detection of network issues
- Prevents unnecessary processing when Snowflake is unavailable
- Provides detailed diagnostics for troubleshooting
- Automatic email alerts for connectivity problems

### 2. Replication Failures

The monitor checks for:
- Missing replication history entries
- Errors in replication jobs
- Failed replication attempts

**Alert Trigger:** When replication history shows failures or is missing for expected time periods

### 3. Replication Latency

Latency is calculated using the formula:
```
Expected Duration = Interval + Last Duration + 10% buffer
```

Where:
- **Interval**: Time between scheduled replication runs (from cron schedule)
- **Last Duration**: How long the last replication took
- **10% Buffer**: Extra time to account for normal variance

**Alert Trigger:** When time since last successful replication exceeds expected duration

### 3. Supported Cron Schedules

The application automatically parses cron schedules:
- `*/10 * * * *` - Every 10 minutes
- `*/30 * * * *` - Every 30 minutes
- `0 * * * *` - Every hour
- `0 */2 * * *` - Every 2 hours
- And more...

## Email Notifications

### Configuration

Set email configuration in environment variables:
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"  # Optional, defaults to 587
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export FROM_EMAIL="monitor@company.com"
export TO_EMAILS="admin1@company.com,admin2@company.com"
```

### Notification Logic

- **One alert per issue**: Notifications sent only once when issue is first detected
- **Resolution tracking**: Notification flag cleared when issue resolves
- **Clear subject lines**: "Snowflake Replication Failure" or "Snowflake Replication Latency"
- **Detailed body**: Includes failover group name, account, and issue description

## Logging

### Log File

Default: `/var/log/monitor_snowflake_replication_v2.log`

### Log Levels

- **INFO**: Normal operation, monitoring cycles, successful checks
- **WARNING**: Minor issues, missing configuration
- **ERROR**: Failures, connection errors, replication issues

### Setup Log File

```bash
# Create log file with proper permissions
sudo touch /var/log/monitor_snowflake_replication_v2.log
sudo chown $USER /var/log/monitor_snowflake_replication_v2.log

# Or use a local log file
export LOG_FILE="./monitoring.log"
```

## Deployment

### Running as a Service (systemd)

1. Create service file `/etc/systemd/system/snowflake-monitor.service`:

```ini
[Unit]
Description=Snowflake Replication Monitor
After=network.target

[Service]
Type=simple
User=snowflake-monitor
WorkingDirectory=/opt/snowflake_monitoring
Environment="SNOWFLAKE_USER=myuser"
Environment="SMTP_SERVER=smtp.example.com"
Environment="FROM_EMAIL=monitor@example.com"
Environment="TO_EMAILS=admin@example.com"
ExecStart=/usr/bin/python3 monitor_snowflake_replication.py myaccount
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable snowflake-monitor
sudo systemctl start snowflake-monitor
sudo systemctl status snowflake-monitor
```

3. View logs:
```bash
sudo journalctl -u snowflake-monitor -f
```

### Running in Docker

See `Dockerfile` (if provided) or create your own:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gds-snowflake

COPY . .

CMD ["python", "monitor_snowflake_replication.py", "myaccount"]
```

### Running in Kubernetes

Create a CronJob or Deployment to run the monitor.

## Examples

### Example 1: Basic Monitoring

```bash
#!/bin/bash
export SNOWFLAKE_USER="monitor_user"
# Note: Using RSA key authentication via Vault instead of password
export FROM_EMAIL="snowflake-monitor@company.com"
export TO_EMAILS="dba-team@company.com"

python monitor_snowflake_replication.py prod_account
```

### Example 2: Using the gds_snowflake Package

See `example_module_usage.py` for detailed examples of:
- Creating connections
- Querying failover groups
- Checking replication status
- Parsing cron schedules
- Detecting failures and latency
- Switching between accounts

## Troubleshooting

### No Failover Groups Found

**Issue:** "No failover groups found" message
**Solution:**
- Verify account has ACCOUNTADMIN or equivalent role
- Check that replication is configured
- Ensure account is part of a failover group

### Email Not Sending

**Issue:** Notifications not received
**Solution:**
- Verify SMTP credentials
- Check SMTP server and port
- Test with `--once` flag to see immediate results
- Check firewall rules for SMTP port

### Connection Failures

**Issue:** Cannot connect to Snowflake
**Solution:**
- Verify account name (format: `account.region`)
- Check credentials
- Ensure network connectivity
- Verify warehouse and role exist

### Permission Errors

**Issue:** Cannot query replication history
**Solution:**
- Use ACCOUNTADMIN role or equivalent
- Grant necessary permissions to monitor user
- Replication history can only be queried from secondary accounts

## Performance

- **Resource Usage**: Minimal CPU and memory
- **Network**: Light network usage, queries run every 60 seconds (configurable)
- **Scalability**: Can monitor dozens of failover groups efficiently

## Security

- **Credentials**: Use RSA key authentication via Vault, environment variables for user info
- **Permissions**: Use least-privilege principle (dedicated monitoring user)
- **Logging**: Sensitive data never logged
- **Network**: Use TLS for Snowflake and SMTP connections

## License

See LICENSE file in the package root.

## Support

For issues and questions:
- GitHub Issues: https://github.com/davidvupham/dbtools/issues
- Email: gds@example.com

## Version History

### Version 2.0.0
- Refactored to use gds_snowflake package
- Improved modularity
- Enhanced error handling

### Version 1.0.0
- Initial monolithic version
- All functionality in single file
