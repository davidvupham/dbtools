# Snowflake Replication Monitor

A Python script that monitors Snowflake failover group replication for failures and latency issues.

## Features

- **Automated Monitoring**: Continuously monitors Snowflake failover groups in 1-minute intervals
- **Failure Detection**: Detects replication failures and sends email notifications (only once per failure)
- **Latency Detection**: Calculates replication latency based on cron schedules with 10% buffer
- **Intelligent Account Switching**: Automatically connects to secondary accounts when needed (replication history can only be queried from secondary accounts)
- **Comprehensive Logging**: Logs all operations to `/var/log/monitor_snowflake_replication.log`

## Requirements

- Python 3.7+
- Snowflake account with appropriate permissions
- Access to failover groups
- SMTP server for email notifications (optional)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the script has write permissions to `/var/log`:
```bash
sudo touch /var/log/monitor_snowflake_replication.log
sudo chown $USER /var/log/monitor_snowflake_replication.log
```

## Configuration

### Environment Variables

The script uses environment variables for credentials and email configuration:

```bash
# Snowflake credentials
export SNOWFLAKE_USER="your_username"
export SNOWFLAKE_PASSWORD="your_password"

# Email configuration (optional)
export SMTP_SERVER="smtp.example.com"
export SMTP_USER="your_smtp_user"
export SMTP_PASSWORD="your_smtp_password"
export FROM_EMAIL="monitor@example.com"
export TO_EMAILS="admin1@example.com,admin2@example.com"
```

## Usage

### Basic Usage

```bash
python monitor_snowflake_replication.py <account_name>
```

### With Username/Password

```bash
python monitor_snowflake_replication.py myaccount --user myuser --password mypassword
```

### With SSO Authentication

```bash
python monitor_snowflake_replication.py myaccount --authenticator externalbrowser
```

### Custom Monitoring Interval

```bash
python monitor_snowflake_replication.py myaccount --interval 120  # 2 minutes
```

### Command Line Arguments

- `account` (required): Snowflake account name
- `--user`: Snowflake username (or set SNOWFLAKE_USER env var)
- `--password`: Snowflake password (or set SNOWFLAKE_PASSWORD env var)
- `--authenticator`: Authentication method (e.g., 'externalbrowser' for SSO)
- `--interval`: Monitoring interval in seconds (default: 60)

## How It Works

### 1. Failover Group Discovery
The script executes `SHOW FAILOVER GROUPS` to discover all failover groups in the account, including:
- Failover group name
- Cron schedule for replication
- Next scheduled refresh time

### 2. Primary/Secondary Detection
For each failover group, the script determines if the current account is primary or secondary:
- If **primary**: Connects to the secondary account to query replication history
- If **secondary**: Queries replication history directly

### 3. Failure Monitoring
Checks the last replication status:
- If status is `FAILED` or `ERROR`, sends an email notification
- Email is sent **only once** per failure to avoid spam
- Notification is cleared once the issue is resolved

### 4. Latency Monitoring
Calculates expected replication time based on:
- **Cron interval**: Time between scheduled replications
- **Last duration**: How long the last successful replication took
- **Buffer**: 10% additional time as tolerance

**Latency threshold** = `cron_interval + last_duration + (last_duration × 0.1)`

If time since last completion exceeds this threshold, a latency alert is sent.

### 5. Continuous Loop
The script runs continuously, checking all failover groups every minute (or custom interval).

## Example Output

```
2025-10-02 10:30:00 - INFO - ================================================================================
2025-10-02 10:30:00 - INFO - Starting Snowflake Replication Monitor for account: myaccount
2025-10-02 10:30:00 - INFO - ================================================================================
2025-10-02 10:30:01 - INFO - Connecting to Snowflake account: myaccount
2025-10-02 10:30:02 - INFO - Successfully connected to Snowflake account: myaccount
2025-10-02 10:30:02 - INFO - Executing SHOW FAILOVER GROUPS
2025-10-02 10:30:03 - INFO - Found 2 failover groups
2025-10-02 10:30:03 - INFO - Failover Group: FG_PROD_DB
2025-10-02 10:30:03 - INFO -   - Cron Schedule: */10 * * * *
2025-10-02 10:30:03 - INFO -   - Next Scheduled Refresh: 2025-10-02 10:40:00
2025-10-02 10:30:03 - INFO - Processing failover group: FG_PROD_DB
2025-10-02 10:30:03 - INFO - Failover group FG_PROD_DB is_primary: True
2025-10-02 10:30:03 - INFO - FG_PROD_DB - Current account is primary, connecting to secondary
2025-10-02 10:30:03 - INFO - Found secondary account: myaccount_secondary
2025-10-02 10:30:04 - INFO - Connecting to Snowflake account: myaccount_secondary
2025-10-02 10:30:05 - INFO - Successfully connected to Snowflake account: myaccount_secondary
2025-10-02 10:30:05 - INFO - Querying replication history for FG_PROD_DB
2025-10-02 10:30:06 - INFO - Retrieved 10 history records for FG_PROD_DB
2025-10-02 10:30:06 - INFO - Sleeping for 60 seconds...
```

## Email Notifications

### Failure Notification Example

```
Subject: Snowflake Replication Failure: FG_PROD_DB

Replication failure detected for failover group: FG_PROD_DB

Status: FAILED
Start Time: 2025-10-02 10:20:00
End Time: 2025-10-02 10:25:00
Error Message: Network timeout during replication

Please investigate immediately.
```

### Latency Notification Example

```
Subject: Snowflake Replication Latency: FG_PROD_DB

Replication latency detected for failover group: FG_PROD_DB

Time since last completion: 25.3 minutes
Threshold: 15.4 minutes
Last completion: 2025-10-02 10:05:00
Cron interval: 10 minutes
Last duration: 4.9 minutes

The replication is running behind schedule.
```

## Troubleshooting

### Permission Issues with Log File

```bash
sudo mkdir -p /var/log
sudo touch /var/log/monitor_snowflake_replication.log
sudo chown $USER /var/log/monitor_snowflake_replication.log
```

### Cannot Connect to Secondary Account

Ensure your Snowflake user has permissions to access both primary and secondary accounts. You may need to:
1. Use the same credentials for both accounts
2. Configure SSO if using `--authenticator externalbrowser`
3. Verify network access to both account regions

### Email Notifications Not Working

Verify all email environment variables are set:
```bash
echo $SMTP_SERVER
echo $SMTP_USER
echo $FROM_EMAIL
echo $TO_EMAILS
```

Check the log file for specific email errors.

## Running as a Service

### Systemd Service (Linux)

Create `/etc/systemd/system/snowflake-monitor.service`:

```ini
[Unit]
Description=Snowflake Replication Monitor
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/dpham/src/snowflake
Environment="SNOWFLAKE_USER=your_user"
Environment="SNOWFLAKE_PASSWORD=your_password"
Environment="SMTP_SERVER=smtp.example.com"
Environment="SMTP_USER=smtp_user"
Environment="SMTP_PASSWORD=smtp_password"
Environment="FROM_EMAIL=monitor@example.com"
Environment="TO_EMAILS=admin@example.com"
ExecStart=/usr/bin/python3 /home/dpham/src/snowflake/monitor_snowflake_replication.py myaccount
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable snowflake-monitor
sudo systemctl start snowflake-monitor
sudo systemctl status snowflake-monitor
```

View logs:
```bash
sudo journalctl -u snowflake-monitor -f
```

## License

MIT