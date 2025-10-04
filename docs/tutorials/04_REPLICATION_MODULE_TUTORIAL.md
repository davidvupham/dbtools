# Replication Module Tutorial - Beginner's Guide

## Understanding Snowflake Replication Monitoring

This tutorial explains the `gds_snowflake.replication` module, which monitors Snowflake failover groups and replication operations to ensure data is properly synced across accounts.

---

## Table of Contents

1. [What is Replication?](#what-is-replication)
2. [Module Overview](#module-overview)
3. [The FailoverGroup Class](#the-failovergroup-class)
4. [The SnowflakeReplication Class](#the-snowflakereplication-class)
5. [Step-by-Step Code Walkthrough](#step-by-step-code-walkthrough)
6. [Usage Examples](#usage-examples)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## What is Replication?

### Database Replication Explained

Imagine you have a notebook:
- **Primary notebook** (Original) - You write in this one
- **Secondary notebook** (Copy) - Automatically copied from the original

**Replication** is keeping the copy synchronized with the original!

```
Primary Account          Secondary Account
┌──────────────┐         ┌──────────────┐
│              │         │              │
│   Database   │ ------> │   Database   │
│   (Original) │ Sync    │    (Copy)    │
│              │         │              │
└──────────────┘         └──────────────┘
```

### Why Do We Need Replication?

1. **Disaster Recovery**: If primary fails, use secondary
2. **Geographic Distribution**: Data closer to users
3. **Load Balancing**: Distribute workload
4. **Compliance**: Data must exist in specific regions

### What is a Failover Group?

A **failover group** is a collection of database objects that are replicated together:
- Databases
- Shares
- Integrations

Think of it as a "replication package" with a schedule.

---

## Module Overview

### File: `gds_snowflake/replication.py`

This module contains two main classes:

1. **FailoverGroup**: Represents a failover group with its properties
2. **SnowflakeReplication**: Monitors replication and checks for issues

### Key Features

- ✓ Get all failover groups
- ✓ Parse replication schedules
- ✓ Check for replication failures
- ✓ Detect replication latency
- ✓ Get replication history
- ✓ Switch to secondary accounts

---

## The FailoverGroup Class

### What It Represents

A **FailoverGroup** object stores information about one failover group:

```python
class FailoverGroup:
    """Represents a Snowflake failover group with its properties."""
    
    def __init__(self, name: str, properties: Dict):
        self.name = name                        # "MY_FAILOVER_GROUP"
        self.type = properties.get('type')       # "ACCOUNT FAILOVER"
        self.primary_account = properties.get('primary')  # "ACCOUNT1"
        self.secondary_accounts = [...]          # ["ACCOUNT2", "ACCOUNT3"]
        self.replication_schedule = "..."        # "USING CRON */10 * * * * UTC"
        self.next_scheduled_refresh = "..."      # Next run time
```

### Key Properties

| Property | Description | Example |
|----------|-------------|---------|
| `name` | Failover group name | `"PROD_REPLICATION"` |
| `type` | Type of failover | `"ACCOUNT FAILOVER"` |
| `primary_account` | Primary account | `"ACCOUNT1.WEST"` |
| `secondary_accounts` | List of secondary accounts | `["ACCOUNT2.EAST"]` |
| `replication_schedule` | When to replicate | `"USING CRON */10 * * * * UTC"` |
| `next_scheduled_refresh` | Next run time | `"2025-10-04 10:30:00"` |

### Parsing Secondary Accounts

```python
def _parse_secondary_accounts(self, secondary_state: str) -> List[str]:
    """
    Parse secondary accounts from the secondary_state string.
    
    Args:
        secondary_state: "ACCOUNT2:READY, ACCOUNT3:READY"
        
    Returns:
        ["ACCOUNT2", "ACCOUNT3"]
    """
    if not secondary_state:
        return []
    
    accounts = []
    for part in secondary_state.split(','):
        part = part.strip()
        if ':' in part:
            account = part.split(':')[0].strip()
            accounts.append(account)
    return accounts
```

**How it works:**

Input: `"ACCOUNT2:READY, ACCOUNT3:READY"`

1. Split by comma: `["ACCOUNT2:READY", "ACCOUNT3:READY"]`
2. For each part:
   - Strip whitespace: `"ACCOUNT2:READY"`
   - Split by colon: `["ACCOUNT2", "READY"]`
   - Take first part: `"ACCOUNT2"`
3. Result: `["ACCOUNT2", "ACCOUNT3"]`

### Checking if Account is Primary

```python
def is_primary(self, current_account: str) -> bool:
    """
    Check if the current account is the primary for this failover group.
    """
    # Normalize account names for comparison
    current = current_account.upper().split('.')[0]
    primary = self.primary_account.upper().split('.')[0]
    return current == primary
```

**Example:**

```python
fg = FailoverGroup("PROD_FG", {"primary": "ACCOUNT1.WEST"})

fg.is_primary("ACCOUNT1.WEST")  # True
fg.is_primary("account1.west")  # True (normalized)
fg.is_primary("ACCOUNT2.EAST")  # False
```

**Why normalize?**
- Account names can be `"ACCOUNT1.WEST"` or just `"ACCOUNT1"`
- We want to compare just the account part
- Case-insensitive comparison

---

## The SnowflakeReplication Class

### What It Does

**SnowflakeReplication** monitors replication and detects issues:

```
SnowflakeReplication
├── Get failover groups
├── Get replication history
├── Parse cron schedules
├── Check for failures
├── Check for latency
└── Switch accounts
```

### Initialization

```python
class SnowflakeReplication:
    """Handles Snowflake replication monitoring and operations."""
    
    def __init__(self, connection: SnowflakeConnection):
        """
        Initialize replication handler.
        
        Args:
            connection: SnowflakeConnection instance
        """
        self.connection = connection
```

**Usage:**

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

# Create connection
conn = SnowflakeConnection(account="my-account")
conn.connect()

# Create replication monitor
replication = SnowflakeReplication(conn)
```

---

## Step-by-Step Code Walkthrough

### Part 1: Getting Failover Groups

```python
def get_failover_groups(self) -> List[FailoverGroup]:
    """
    Retrieve all failover groups from Snowflake.
    
    Returns:
        List of FailoverGroup objects
    """
    try:
        logger.info("Retrieving failover groups")
        results = self.connection.execute_query("SHOW FAILOVER GROUPS")
        
        failover_groups = []
        for row in results:
            # Parse the row into a dictionary
            properties = {}
            if len(row) >= 2:
                name = row[1]  # name is typically the second column
                
                # Extract properties from row columns
                if len(row) > 2:
                    properties['type'] = row[2] if len(row) > 2 else ''
                    properties['primary'] = row[5] if len(row) > 5 else ''
                    properties['secondary_state'] = row[8] if len(row) > 8 else ''
                    properties['replication_schedule'] = row[9] if len(row) > 9 else ''
                    properties['next_scheduled_refresh'] = row[10] if len(row) > 10 else ''
                    properties['allowed_databases'] = row[11] if len(row) > 11 else ''
                    properties['allowed_shares'] = row[12] if len(row) > 12 else ''
                    properties['allowed_integration_types'] = row[13] if len(row) > 13 else ''
                
                fg = FailoverGroup(name, properties)
                failover_groups.append(fg)
                logger.info(
                    "Found failover group: %s (Primary: %s, Schedule: %s)",
                    fg.name,
                    fg.primary_account,
                    fg.replication_schedule
                )
        
        logger.info("Retrieved %s failover groups", len(failover_groups))
        return failover_groups
        
    except Exception as e:
        logger.error("Error retrieving failover groups: %s", str(e))
        raise
```

**Step-by-Step:**

1. **Execute Snowflake command**:
   ```sql
   SHOW FAILOVER GROUPS
   ```

2. **Parse each row**:
   - Snowflake returns rows as tuples
   - Each position has specific data
   - Extract relevant columns

3. **Create FailoverGroup objects**:
   ```python
   fg = FailoverGroup(name, properties)
   ```

4. **Return list**: All failover groups

**Example Output:**

```
[Row from SHOW FAILOVER GROUPS]
Index:  0    1              2                  3    4    5           ...
Value: [ts, "PROD_FG", "ACCOUNT FAILOVER", ..., ..., "ACCOUNT1", ...]
```

---

### Part 2: Getting Replication History

```python
def get_replication_history(self, failover_group_name: str, limit: int = 10) -> List[Dict]:
    """
    Get replication history for a failover group.
    
    Args:
        failover_group_name: Name of the failover group
        limit: Maximum number of history records to retrieve
        
    Returns:
        List of replication history records as dictionaries
    """
    try:
        query = f"""
        SELECT
            start_time,
            end_time,
            status,
            message
        FROM TABLE(INFORMATION_SCHEMA.REPLICATION_GROUP_REFRESH_HISTORY('{failover_group_name}'))
        ORDER BY start_time DESC
        LIMIT {limit}
        """
        
        logger.debug("Querying replication history for %s", failover_group_name)
        results = self.connection.execute_query_dict(query)
        
        return results
        
    except Exception as e:
        logger.error("Error retrieving replication history for %s: %s", failover_group_name, str(e))
        raise
```

**What This Does:**

1. **Query Snowflake function**: 
   ```sql
   INFORMATION_SCHEMA.REPLICATION_GROUP_REFRESH_HISTORY('PROD_FG')
   ```
   - Returns history of replication runs

2. **Get recent runs**: 
   - `ORDER BY start_time DESC` → Most recent first
   - `LIMIT 10` → Only 10 records

3. **Return as dictionaries**: Easy to access by key

**Example Result:**

```python
[
    {
        'START_TIME': datetime(2025, 10, 4, 10, 0, 0),
        'END_TIME': datetime(2025, 10, 4, 10, 5, 23),
        'STATUS': 'SUCCEEDED',
        'MESSAGE': 'Replication completed successfully'
    },
    {
        'START_TIME': datetime(2025, 10, 4, 9, 50, 0),
        'END_TIME': datetime(2025, 10, 4, 9, 55, 12),
        'STATUS': 'FAILED',
        'MESSAGE': 'Network timeout during replication'
    }
]
```

---

### Part 3: Parsing Cron Schedules

```python
def parse_cron_schedule(self, cron_expression: str) -> Optional[int]:
    """
    Parse a cron schedule and calculate the interval in minutes.
    
    Args:
        cron_expression: "USING CRON */10 * * * * UTC"
        
    Returns:
        Interval in minutes (10), or None if unable to parse
    """
    try:
        # Extract the cron part from the expression
        # Format: "USING CRON */10 * * * * UTC"
        if 'USING CRON' in cron_expression.upper():
            parts = cron_expression.split()
            # Find the cron expression (typically after 'CRON' keyword)
            cron_idx = next((i for i, p in enumerate(parts) if p.upper() == 'CRON'), None)
            if cron_idx is not None and len(parts) > cron_idx + 5:
                # Get the 5 fields of cron expression
                cron_fields = parts[cron_idx + 1:cron_idx + 6]
                cron_str = ' '.join(cron_fields)
                
                # Use croniter to calculate the interval
                base_time = datetime.now()
                cron = croniter(cron_str, base_time)
                next_time = cron.get_next(datetime)
                following_time = cron.get_next(datetime)
                
                interval = (following_time - next_time).total_seconds() / 60
                logger.debug("Parsed cron schedule '%s' -> %s minutes", cron_expression, interval)
                return int(interval)
        
        logger.warning("Unable to parse cron schedule: %s", cron_expression)
        return None
        
    except Exception as e:
        logger.error("Error parsing cron schedule '%s': %s", cron_expression, str(e))
        return None
```

**Understanding Cron Expressions:**

Cron format: `minute hour day month weekday`

Examples:
- `*/10 * * * *` → Every 10 minutes
- `0 * * * *` → Every hour (at :00)
- `0 0 * * *` → Every day at midnight
- `0 12 * * 1` → Every Monday at noon

**How Parsing Works:**

Input: `"USING CRON */10 * * * * UTC"`

1. **Split string**: `["USING", "CRON", "*/10", "*", "*", "*", "*", "UTC"]`

2. **Find "CRON"**: Index 1

3. **Extract cron fields**: `["*/10", "*", "*", "*", "*"]` (5 fields after "CRON")

4. **Use croniter library**:
   ```python
   cron = croniter("*/10 * * * *", datetime.now())
   next_time = cron.get_next(datetime)      # 10:10
   following_time = cron.get_next(datetime)  # 10:20
   ```

5. **Calculate interval**: `10:20 - 10:10 = 10 minutes`

---

### Part 4: Checking for Replication Failures

```python
def check_replication_failure(self, failover_group: FailoverGroup) -> Tuple[bool, Optional[str]]:
    """
    Check if the last replication failed for a failover group.
    
    Args:
        failover_group: FailoverGroup object
        
    Returns:
        Tuple of (is_failed, error_message)
    """
    try:
        history = self.get_replication_history(failover_group.name, limit=1)
        
        if not history:
            logger.warning("No replication history found for %s", failover_group.name)
            return False, None
        
        last_run = history[0]
        status = last_run.get('STATUS', '').upper()
        
        if status == 'FAILED' or status == 'PARTIALLY_FAILED':
            message = last_run.get('MESSAGE', 'No error message available')
            logger.warning("Replication failed for %s: %s", failover_group.name, message)
            return True, message
        
        return False, None
        
    except Exception as e:
        logger.error("Error checking replication failure for %s: %s", failover_group.name, str(e))
        return False, None
```

**Logic Flow:**

```
1. Get most recent replication run (limit=1)
   ↓
2. Check if history exists
   ↓
3. Get status from last run
   ↓
4. Check if status is "FAILED" or "PARTIALLY_FAILED"
   ↓
5. Return (is_failed, error_message)
```

**Example:**

```python
fg = FailoverGroup("PROD_FG", {...})
is_failed, error = replication.check_replication_failure(fg)

if is_failed:
    print(f"ERROR: Replication failed - {error}")
else:
    print("✓ Replication successful")
```

---

### Part 5: Checking for Replication Latency

```python
def check_replication_latency(self, failover_group: FailoverGroup) -> Tuple[bool, Optional[str]]:
    """
    Check if there is replication latency for a failover group.
    
    Latency is calculated as: expected_time = last_completion + interval + (last_duration * 1.1)
    If current time > expected_time, then there is latency.
    
    Args:
        failover_group: FailoverGroup object
        
    Returns:
        Tuple of (has_latency, latency_message)
    """
    try:
        # Parse the cron schedule to get the interval
        interval_minutes = self.parse_cron_schedule(failover_group.replication_schedule)
        if interval_minutes is None:
            logger.warning("Cannot determine latency for %s - unable to parse schedule", failover_group.name)
            return False, None
        
        # Get the last replication history
        history = self.get_replication_history(failover_group.name, limit=1)
        if not history:
            logger.warning("No replication history found for %s", failover_group.name)
            return False, None
        
        last_run = history[0]
        end_time = last_run.get('END_TIME')
        start_time = last_run.get('START_TIME')
        
        if not end_time or not start_time:
            logger.warning("Missing time information for %s", failover_group.name)
            return False, None
        
        # Calculate the duration of the last replication
        duration = (end_time - start_time).total_seconds() / 60  # in minutes
        
        # Calculate expected next completion time
        # Formula: last_completion + interval + (duration * 1.1)
        expected_next = end_time + timedelta(minutes=interval_minutes + (duration * 1.1))
        
        current_time = datetime.now(end_time.tzinfo) if end_time.tzinfo else datetime.now()
        
        if current_time > expected_next:
            delay_minutes = (current_time - expected_next).total_seconds() / 60
            message = (f"Replication latency detected for {failover_group.name}. "
                      f"Expected completion by {expected_next}, but current time is {current_time}. "
                      f"Delay: {delay_minutes:.1f} minutes. "
                      f"Last replication took {duration:.1f} minutes, interval is {interval_minutes} minutes.")
            logger.warning(message)
            return True, message
        
        return False, None
        
    except Exception as e:
        logger.error(
            "Error checking replication latency for %s: %s",
            failover_group.name,
            str(e)
        )
        return False, None
```

**Understanding the Latency Formula:**

```
Expected Next Completion = Last Completion + Interval + (Last Duration × 1.1)
```

**Example Calculation:**

```
Last replication:
- Started: 10:00
- Ended: 10:05 (took 5 minutes)
- Interval: 10 minutes

Expected next completion:
= 10:05 + 10 minutes + (5 × 1.1 minutes)
= 10:05 + 10 + 5.5
= 10:20:30

Current time: 10:25

Is there latency?
10:25 > 10:20:30 → YES! Latency of 4.5 minutes
```

**Why × 1.1 (110%)?**

- Gives a 10% buffer for normal variation
- Replication might take slightly longer sometimes
- Avoids false alarms

**Visual Timeline:**

```
10:00  10:05    10:15      10:20:30  10:25
  |      |        |            |        |
Start   End    Scheduled   Expected  Current
        ↓        ↓            ↓         ↓
       [5min]  [10min]    [+10% buffer]
```

---

## Usage Examples

### Example 1: List All Failover Groups

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

# Connect
conn = SnowflakeConnection(account="my-account")
conn.connect()

# Create replication monitor
replication = SnowflakeReplication(conn)

# Get all failover groups
failover_groups = replication.get_failover_groups()

print(f"Found {len(failover_groups)} failover groups:")
for fg in failover_groups:
    print(f"  - {fg.name}")
    print(f"    Primary: {fg.primary_account}")
    print(f"    Schedule: {fg.replication_schedule}")
    print(f"    Secondaries: {fg.secondary_accounts}")
```

**Output:**

```
Found 2 failover groups:
  - PROD_REPLICATION
    Primary: ACCOUNT1.WEST
    Schedule: USING CRON */10 * * * * UTC
    Secondaries: ['ACCOUNT2.EAST']
  - DEV_REPLICATION
    Primary: ACCOUNT1.WEST
    Schedule: USING CRON 0 * * * * UTC
    Secondaries: ['ACCOUNT3.CENTRAL']
```

### Example 2: Check for Failures

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(account="my-account")
conn.connect()
replication = SnowflakeReplication(conn)

# Get failover groups
failover_groups = replication.get_failover_groups()

# Check each for failures
for fg in failover_groups:
    is_failed, error = replication.check_replication_failure(fg)
    
    if is_failed:
        print(f"❌ {fg.name}: FAILED")
        print(f"   Error: {error}")
    else:
        print(f"✓ {fg.name}: OK")
```

**Output:**

```
✓ PROD_REPLICATION: OK
❌ DEV_REPLICATION: FAILED
   Error: Network timeout during replication
```

### Example 3: Check for Latency

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(account="my-account")
conn.connect()
replication = SnowflakeReplication(conn)

failover_groups = replication.get_failover_groups()

for fg in failover_groups:
    has_latency, message = replication.check_replication_latency(fg)
    
    if has_latency:
        print(f"⚠️  {fg.name}: LATENCY DETECTED")
        print(f"   {message}")
    else:
        print(f"✓ {fg.name}: On schedule")
```

### Example 4: Get Replication History

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(account="my-account")
conn.connect()
replication = SnowflakeReplication(conn)

# Get history for a specific failover group
history = replication.get_replication_history("PROD_REPLICATION", limit=5)

print("Recent replication runs:")
for run in history:
    print(f"  {run['START_TIME']} -> {run['END_TIME']}")
    print(f"    Status: {run['STATUS']}")
    if run['MESSAGE']:
        print(f"    Message: {run['MESSAGE']}")
```

**Output:**

```
Recent replication runs:
  2025-10-04 10:00:00 -> 2025-10-04 10:05:23
    Status: SUCCEEDED
  2025-10-04 09:50:00 -> 2025-10-04 09:55:12
    Status: SUCCEEDED
  2025-10-04 09:40:00 -> 2025-10-04 09:42:45
    Status: FAILED
    Message: Network timeout during replication
```

### Example 5: Parse Cron Schedule

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(account="my-account")
conn.connect()
replication = SnowflakeReplication(conn)

# Parse various schedules
schedules = [
    "USING CRON */10 * * * * UTC",
    "USING CRON 0 * * * * UTC",
    "USING CRON 0 0 * * * UTC",
]

for schedule in schedules:
    interval = replication.parse_cron_schedule(schedule)
    print(f"{schedule} -> {interval} minutes")
```

**Output:**

```
USING CRON */10 * * * * UTC -> 10 minutes
USING CRON 0 * * * * UTC -> 60 minutes
USING CRON 0 0 * * * UTC -> 1440 minutes
```

---

## Common Patterns

### Pattern 1: Complete Health Check

```python
def check_replication_health(replication):
    """Complete health check for all failover groups."""
    failover_groups = replication.get_failover_groups()
    
    issues = []
    
    for fg in failover_groups:
        # Check for failures
        is_failed, error = replication.check_replication_failure(fg)
        if is_failed:
            issues.append(f"{fg.name}: FAILED - {error}")
        
        # Check for latency
        has_latency, message = replication.check_replication_latency(fg)
        if has_latency:
            issues.append(f"{fg.name}: LATENCY - {message}")
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All replication healthy")
    
    return len(issues) == 0

# Usage
is_healthy = check_replication_health(replication)
```

### Pattern 2: Alert on Issues

```python
def alert_on_issues(replication, send_email_func):
    """Send alerts if replication has issues."""
    failover_groups = replication.get_failover_groups()
    
    for fg in failover_groups:
        # Check for failures
        is_failed, error = replication.check_replication_failure(fg)
        if is_failed:
            send_email_func(
                subject=f"Replication Failed: {fg.name}",
                body=f"Failover group {fg.name} has failed:\n{error}"
            )
        
        # Check for latency
        has_latency, message = replication.check_replication_latency(fg)
        if has_latency:
            send_email_func(
                subject=f"Replication Latency: {fg.name}",
                body=f"Failover group {fg.name} has latency:\n{message}"
            )
```

### Pattern 3: Scheduled Monitoring

```python
import time
import schedule

def monitor_replication():
    """Monitoring function to run on schedule."""
    conn = SnowflakeConnection(account="my-account")
    conn.connect()
    replication = SnowflakeReplication(conn)
    
    # Check health
    is_healthy = check_replication_health(replication)
    
    if not is_healthy:
        alert_on_issues(replication, send_email)
    
    conn.close()

# Run every 5 minutes
schedule.every(5).minutes.do(monitor_replication)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Troubleshooting

### Error: "No replication history found"

**Problem:** `get_replication_history()` returns empty list.

**Solutions:**
1. Verify failover group name is correct
2. Check if replication has run at least once
3. Verify account permissions to view history
4. Check if failover group is active

### Error: "Unable to parse cron schedule"

**Problem:** Cron expression format is not recognized.

**Solutions:**
1. Check cron expression format: `"USING CRON */10 * * * * UTC"`
2. Verify croniter library is installed
3. Check for typos in cron expression
4. Test with simple cron expression first

### False Latency Alerts

**Problem:** Getting latency alerts when replication is fine.

**Solutions:**
1. Check the 1.1 multiplier (adjust if needed)
2. Verify cron schedule is correct
3. Account for timezone differences
4. Consider network variability

### Permission Errors

**Problem:** Cannot view failover groups or history.

**Solutions:**
1. Verify user has `MONITOR` privilege on failover groups
2. Check account role permissions
3. Verify user is on correct account
4. Check if failover groups exist

---

## Key Takeaways

1. **FailoverGroup** represents a replication configuration
2. **SnowflakeReplication** monitors replication health
3. **Cron schedules** define when replication runs
4. **Failure detection** checks if replication succeeded
5. **Latency detection** checks if replication is delayed
6. **History tracking** helps debug issues

---

## Practice Exercise

Create a monitoring script that:
1. Connects to Snowflake
2. Gets all failover groups
3. Checks each for failures and latency
4. Prints a summary report
5. Closes the connection

```python
import logging
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

logging.basicConfig(level=logging.INFO)

def main():
    """Monitor Snowflake replication."""
    conn = None
    try:
        # Your code here
        pass
    except Exception as e:
        # Your error handling
        pass
    finally:
        # Your cleanup
        pass

if __name__ == "__main__":
    main()
```

---

## Next Tutorial

Ready to learn about comprehensive monitoring? Continue to:
**[Monitor Module Tutorial](05_MONITOR_MODULE_TUTORIAL.md)**

This tutorial covers the complete monitoring system that uses all previous modules!

---

## Additional Resources

- [Snowflake Replication Documentation](https://docs.snowflake.com/en/user-guide/account-replication-intro.html)
- [Failover Groups](https://docs.snowflake.com/en/user-guide/account-replication-failover.html)
- [Cron Expression Guide](https://crontab.guru/)
- [croniter Library](https://github.com/kiorky/croniter)
