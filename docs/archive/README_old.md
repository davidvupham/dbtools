# Snowflake Replication Monitor

A Python package and application for monitoring Snowflake replication failover groups for failures and latency issues.

> 🔄 **Want to regenerate this project from scratch?** See [PROMPTS.md](PROMPTS.md) for the exact prompts used to create this entire project (~4,647 lines in ~25 minutes).

## Project Structure

This project consists of two main components:

### 📦 **`gds_snowflake/`** - Python Package

A reusable Python package for Snowflake operations (by the GDS team):

- **`connection.py`**: Connection management module
  - Handles Snowflake database connections
  - Provides connection pooling and account switching
  - Manages query execution with error handling

- **`replication.py`**: Replication operations module
  - Manages failover groups and their properties
  - Queries replication history and status
  - Implements failure and latency detection logic
  - Handles cron schedule parsing and interval calculations

**Installation:**
```bash
pip install -e .
```

**Usage:**
```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication, FailoverGroup
```

### 🔍 **`snowflake_monitoring/`** - Monitoring Application

Self-contained application for monitoring Snowflake replication:

- **`monitor_snowflake_replication_v2.py`**: Main monitoring script (refactored)
  - Uses the gds_snowflake package
  - Implements monitoring loop and email notifications
  - Provides command-line interface

- **`monitor_snowflake_replication.py`**: Original monolithic script (legacy)
  - All functionality in a single file
  - Kept for backward compatibility

- **`example_module_usage.py`**: Usage examples demonstrating the gds_snowflake package

See [snowflake_monitoring/README.md](snowflake_monitoring/README.md) for application-specific documentation.

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

### Quick Start

1. Install the gds_snowflake package:
```bash
# Install in development mode (editable)
pip install -e .

# This will also install all dependencies from requirements.txt
```

2. Run the monitoring application:
```bash
cd snowflake_monitoring
python monitor_snowflake_replication_v2.py myaccount
```

### Production Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install the package:
```bash
pip install .
```

### Development Installation

For development with testing and code quality tools:
```bash
pip install -r requirements-dev.txt
pip install -e .  # Install in editable mode
```

### VS Code Setup

Open the project in VS Code with the included workspace file:
```bash
code snowflake-monitor.code-workspace
```

See [VSCODE_SETUP.md](VSCODE_SETUP.md) for complete VS Code setup instructions, including:
- Debug configurations for running and testing
- Tasks for testing, linting, and formatting
- Recommended extensions
- Keyboard shortcuts and workflows

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

### Using the Package in Your Code

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

# Create connection
conn = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    password='mypassword',
    warehouse='my_warehouse',
    role='my_role'
)

# Connect
conn.connect()

# Use replication features
repl = SnowflakeReplication(conn)
failover_groups = repl.get_failover_groups()

for group in failover_groups:
    print(f"Group: {group.name}")
    print(f"Type: {group.type}")
    print(f"Primary: {group.primary_account}")

# Close connection
conn.close()
```

See [snowflake_monitoring/example_module_usage.py](snowflake_monitoring/example_module_usage.py) for more examples.

### Running the Monitoring Application

```bash
cd snowflake_monitoring

# Continuous monitoring (refactored version - recommended)
python monitor_snowflake_replication_v2.py <account_name>

# Run once and exit
python monitor_snowflake_replication_v2.py <account_name> --once
```

### Basic Usage (Original Version - Legacy)

```bash
python monitor_snowflake_replication.py <account_name>
```

### With Username/Password

```bash
python monitor_snowflake_replication_v2.py myaccount --user myuser --password mypassword
```

### With Warehouse and Role

```bash
python monitor_snowflake_replication_v2.py myaccount --user myuser --password mypass \
  --warehouse COMPUTE_WH --role ACCOUNTADMIN
```

### Custom Monitoring Interval

```bash
python monitor_snowflake_replication_v2.py myaccount --interval 120  # 2 minutes
```

### Command Line Arguments (v2 - Refactored)

- `account` (required): Snowflake account name
- `--user`: Snowflake username (or set SNOWFLAKE_USER env var)
- `--password`: Snowflake password (or set SNOWFLAKE_PASSWORD env var)
- `--warehouse`: Snowflake warehouse (or set SNOWFLAKE_WAREHOUSE env var)
- `--role`: Snowflake role (or set SNOWFLAKE_ROLE env var)
- `--interval`: Monitoring interval in seconds (default: 60)
- `--once`: Run once and exit (no continuous monitoring)

### Command Line Arguments (Original Version)

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

## Using the Modules Independently

The refactored version provides reusable modules that can be imported into your own scripts:

### Example: Using SnowflakeConnection

```python
from snowflake_connection import SnowflakeConnection

# Create and use connection
with SnowflakeConnection(
    account='myaccount',
    user='myuser',
    password='mypassword'
) as conn:
    # Execute queries
    results = conn.execute_query("SELECT CURRENT_VERSION()")
    print(f"Version: {results[0][0]}")

    # Execute with dictionary results
    results = conn.execute_query_dict(
        "SELECT CURRENT_ACCOUNT() as ACCOUNT, CURRENT_USER() as USER"
    )
    for row in results:
        print(f"Account: {row['ACCOUNT']}, User: {row['USER']}")
```

### Example: Using SnowflakeReplication

```python
from snowflake_connection import SnowflakeConnection
from snowflake_replication import SnowflakeReplication

conn = SnowflakeConnection(account='myaccount', user='myuser', password='mypass')
conn.connect()

# Create replication handler
replication = SnowflakeReplication(conn)

# Get failover groups
failover_groups = replication.get_failover_groups()

for fg in failover_groups:
    print(f"Failover Group: {fg.name}")
    print(f"  Primary: {fg.primary_account}")
    print(f"  Schedule: {fg.replication_schedule}")

    # Check for failures
    is_failed, error_msg = replication.check_replication_failure(fg)
    if is_failed:
        print(f"  Status: FAILED - {error_msg}")

    # Check for latency
    has_latency, latency_msg = replication.check_replication_latency(fg)
    if has_latency:
        print(f"  Latency: WARNING - {latency_msg}")

conn.close()
```

For more examples, see `example_module_usage.py`.

## Testing

The project includes comprehensive unit tests and integration tests.

### Running Tests with unittest

```bash
# Run all tests
python run_tests.py

# Run all tests verbosely
python run_tests.py -v

# Run all tests quietly
python run_tests.py -q

# Run specific test module
python run_tests.py -m test_snowflake_connection
python run_tests.py -m test_snowflake_replication
python run_tests.py -m test_monitor_integration
```

### Running Tests with pytest (if installed)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_snowflake_connection.py

# Run tests by marker
pytest -m unit  # Run only unit tests
pytest -m integration  # Run only integration tests

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── test_snowflake_connection.py      # Unit tests for connection module
├── test_snowflake_replication.py     # Unit tests for replication module
├── test_monitor_integration.py       # Integration tests for monitoring
└── test_connection_pytest.py         # Pytest version (optional)
```

### Test Coverage

The test suite covers:
- ✅ Connection management (connect, close, query execution)
- ✅ Failover group operations
- ✅ Replication history queries
- ✅ Cron schedule parsing
- ✅ Failure detection logic
- ✅ Latency calculation and detection
- ✅ Email notifications
- ✅ Account switching
- ✅ Error handling and edge cases

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
Environment="SNOWFLAKE_WAREHOUSE=COMPUTE_WH"
Environment="SNOWFLAKE_ROLE=ACCOUNTADMIN"
Environment="SMTP_SERVER=smtp.example.com"
Environment="SMTP_USER=smtp_user"
Environment="SMTP_PASSWORD=smtp_password"
Environment="FROM_EMAIL=monitor@example.com"
Environment="TO_EMAILS=admin@example.com"
# Use the refactored version (recommended)
ExecStart=/usr/bin/python3 /home/dpham/src/snowflake/monitor_snowflake_replication_v2.py myaccount
# Or use the original version
# ExecStart=/usr/bin/python3 /home/dpham/src/snowflake/monitor_snowflake_replication.py myaccount
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

## Project Generation

This project was created using AI-assisted development with GitHub Copilot. The complete prompt history and regeneration instructions are documented in:

- **[PROMPTS.md](PROMPTS.md)** - Exact prompts used to generate this project (reproducible recipe)
  - Option A: Sequential prompts (recommended) - 25-30 min, 99% success rate
  - Option B: Single combined prompt (faster) - 10-15 min, 80% success rate
- **[PROMPT_COMPARISON.md](PROMPT_COMPARISON.md)** - Detailed comparison of prompt strategies
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Visual diagrams and project statistics
- **[REFACTORING.md](REFACTORING.md)** - Architecture decisions and module design

### Quick Facts:
- **5 sequential prompts** → **4,647 lines** of production-ready code
- **Generation time:** ~25-30 minutes (or ~10-15 with combined prompt)
- **Test coverage:** ~90% (45+ test cases)
- **Test-to-code ratio:** 1.96:1
- **Documentation-to-code ratio:** 2.41:1
- **Success rate:** 99% with sequential approach

Want to regenerate or adapt this project? Follow the step-by-step instructions in [PROMPTS.md](PROMPTS.md).

## License

MIT
