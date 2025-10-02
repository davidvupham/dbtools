#!/usr/bin/env python3
"""
Snowflake Replication Monitor
Monitors Snowflake failover groups for replication failures and latency issues.
"""

import argparse
import logging
import os
import sys
import time
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
import snowflake.connector
from croniter import croniter


# Script name for logging
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
LOG_FILE = f"/var/log/{SCRIPT_NAME}.log"

# Email notification tracking (to send only once per failure)
notified_failures = set()


def setup_logging():
    """Configure logging to write to /var/log"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def connect_to_snowflake(account: str, user: str = None, password: str = None,
                         authenticator: str = None) -> snowflake.connector.SnowflakeConnection:
    """
    Connect to Snowflake account.

    Args:
        account: Snowflake account name
        user: Username (optional, can use environment variable)
        password: Password (optional, can use environment variable)
        authenticator: Authentication method (optional, e.g., 'externalbrowser')

    Returns:
        Snowflake connection object
    """
    try:
        logging.info(f"Connecting to Snowflake account: {account}")

        conn_params = {
            'account': account,
            'user': user or os.getenv('SNOWFLAKE_USER'),
            'password': password or os.getenv('SNOWFLAKE_PASSWORD'),
        }

        if authenticator:
            conn_params['authenticator'] = authenticator

        conn = snowflake.connector.connect(**conn_params)
        logging.info(f"Successfully connected to Snowflake account: {account}")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to Snowflake account {account}: {e}")
        raise


def get_failover_groups(conn: snowflake.connector.SnowflakeConnection) -> List[Dict]:
    """
    Execute 'SHOW FAILOVER GROUPS' and return parsed results.

    Returns:
        List of dictionaries containing failover group information
    """
    try:
        logging.info("Executing SHOW FAILOVER GROUPS")
        cursor = conn.cursor()
        cursor.execute("SHOW FAILOVER GROUPS")

        # Get column names
        columns = [col[0] for col in cursor.description]

        # Fetch all rows and convert to list of dictionaries
        failover_groups = []
        for row in cursor.fetchall():
            fg_dict = dict(zip(columns, row))
            failover_groups.append(fg_dict)
            
            # Log the failover group details
            fg_name = fg_dict.get('name', 'Unknown')
            cron_schedule = fg_dict.get('replication_schedule', 'Not set')
            next_scheduled = fg_dict.get('next_scheduled_refresh', 'Not available')
            
            logging.info(f"Failover Group: {fg_name}")
            logging.info(f"  - Cron Schedule: {cron_schedule}")
            logging.info(f"  - Next Scheduled Refresh: {next_scheduled}")

        logging.info(f"Found {len(failover_groups)} failover groups")
        return failover_groups
    except Exception as e:
        logging.error(f"Failed to get failover groups: {e}")
        raise


def parse_cron_schedule(cron_expr: str) -> Optional[croniter]:
    """
    Parse cron schedule expression.

    Args:
        cron_expr: Cron expression string

    Returns:
        croniter object or None if parsing fails
    """
    try:
        return croniter(cron_expr, datetime.now())
    except Exception as e:
        logging.error(f"Failed to parse cron expression '{cron_expr}': {e}")
        return None


def get_cron_interval_minutes(cron_expr: str) -> Optional[int]:
    """
    Calculate the interval in minutes from a cron expression.

    Args:
        cron_expr: Cron expression string

    Returns:
        Interval in minutes or None if cannot determine
    """
    try:
        cron = croniter(cron_expr, datetime.now())
        next_run = cron.get_next(datetime)
        following_run = cron.get_next(datetime)
        interval = (following_run - next_run).total_seconds() / 60
        return int(interval)
    except Exception as e:
        logging.error(f"Failed to calculate interval from cron '{cron_expr}': {e}")
        return None


def is_primary_account(conn: snowflake.connector.SnowflakeConnection,
                       failover_group_name: str) -> bool:
    """
    Determine if the current account is the primary for the failover group.

    Args:
        conn: Snowflake connection
        failover_group_name: Name of the failover group

    Returns:
        True if primary, False if secondary
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW FAILOVER GROUPS LIKE '{failover_group_name}'")

        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()

        if row:
            fg_dict = dict(zip(columns, row))
            # Check various possible field names for primary status
            # Snowflake uses 'is_primary', 'type', or 'primary' field
            is_primary = (
                fg_dict.get('is_primary', 'false').lower() == 'true' or
                fg_dict.get('IS_PRIMARY', 'false').lower() == 'true' or
                fg_dict.get('type', '').upper() == 'PRIMARY' or
                fg_dict.get('TYPE', '').upper() == 'PRIMARY' or
                fg_dict.get('primary', 'false').lower() == 'true'
            )
            logging.info(f"Failover group {failover_group_name} is_primary: {is_primary}")
            return is_primary

        return False
    except Exception as e:
        logging.error(f"Failed to determine primary status for {failover_group_name}: {e}")
        return False


def get_secondary_account(failover_group: Dict, current_account: str) -> Optional[str]:
    """
    Extract secondary account name from failover group information.

    Args:
        failover_group: Failover group dictionary
        current_account: Current account name to exclude

    Returns:
        Secondary account name or None
    """
    try:
        # Parse allowed_accounts or secondary_accounts field
        # This depends on the actual structure returned by SHOW FAILOVER GROUPS
        allowed_accounts_str = (
            failover_group.get('allowed_accounts', '') or
            failover_group.get('ALLOWED_ACCOUNTS', '') or
            failover_group.get('account_locator', '') or
            failover_group.get('ACCOUNT_LOCATOR', '')
        )
        
        if not allowed_accounts_str:
            logging.warning(f"No allowed_accounts found for failover group")
            return None
            
        accounts = [acc.strip() for acc in str(allowed_accounts_str).split(',')]
        
        # Filter out the current account to find the secondary
        secondary_accounts = [acc for acc in accounts if acc and acc != current_account]
        
        if secondary_accounts:
            secondary = secondary_accounts[0]
            logging.info(f"Found secondary account: {secondary}")
            return secondary

        return None
    except Exception as e:
        logging.error(f"Failed to get secondary account: {e}")
        return None


def get_replication_history(conn: snowflake.connector.SnowflakeConnection,
                            failover_group_name: str) -> List[Dict]:
    """
    Get replication history for a failover group.
    Can only be queried from the secondary account.

    Args:
        conn: Snowflake connection (must be to secondary account)
        failover_group_name: Name of the failover group

    Returns:
        List of replication history records
    """
    try:
        logging.info(f"Querying replication history for {failover_group_name}")
        cursor = conn.cursor()

        # Query the replication history
        query = f"""
        SELECT *
        FROM TABLE(INFORMATION_SCHEMA.REPLICATION_GROUP_REFRESH_HISTORY('{failover_group_name}'))
        ORDER BY START_TIME DESC
        LIMIT 10
        """

        cursor.execute(query)
        columns = [col[0] for col in cursor.description]

        history = []
        for row in cursor.fetchall():
            history.append(dict(zip(columns, row)))

        logging.info(f"Retrieved {len(history)} history records for {failover_group_name}")
        return history
    except Exception as e:
        logging.error(f"Failed to get replication history for {failover_group_name}: {e}")
        return []


def check_for_failures(failover_group_name: str, history: List[Dict]) -> Optional[Dict]:
    """
    Check if the last replication failed.

    Args:
        failover_group_name: Name of the failover group
        history: List of replication history records

    Returns:
        Failure information dict if failed, None otherwise
    """
    if not history:
        logging.warning(f"No history available for {failover_group_name}")
        return None

    last_run = history[0]
    status = last_run.get('STATUS', '').upper()

    if status == 'FAILED' or status == 'ERROR':
        logging.error(f"Replication failure detected for {failover_group_name}")
        return {
            'failover_group': failover_group_name,
            'status': status,
            'start_time': last_run.get('START_TIME'),
            'end_time': last_run.get('END_TIME'),
            'error_message': last_run.get('ERROR_MESSAGE', 'No error message available')
        }

    return None


def check_for_latency(failover_group_name: str, cron_expr: str,
                      history: List[Dict]) -> Optional[Dict]:
    """
    Check if there is latency in replication based on cron schedule.
    Latency = cron_interval + last_duration + 10% of last_duration

    Args:
        failover_group_name: Name of the failover group
        cron_expr: Cron schedule expression
        history: List of replication history records

    Returns:
        Latency information dict if latency detected, None otherwise
    """
    if not history:
        return None

    # Get cron interval
    interval_minutes = get_cron_interval_minutes(cron_expr)
    if interval_minutes is None:
        return None

    last_run = history[0]

    # Only check if last run was successful
    if last_run.get('STATUS', '').upper() != 'SUCCESS':
        return None

    end_time = last_run.get('END_TIME')
    start_time = last_run.get('START_TIME')

    if not end_time or not start_time:
        return None

    # Calculate last replication duration
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

    last_duration = (end_time - start_time).total_seconds() / 60  # minutes

    # Calculate expected threshold: interval + duration + 10% buffer
    threshold_minutes = interval_minutes + last_duration + (last_duration * 0.1)

    # Calculate time since last completion
    now = datetime.now(end_time.tzinfo) if end_time.tzinfo else datetime.now()
    time_since_completion = (now - end_time).total_seconds() / 60

    if time_since_completion > threshold_minutes:
        logging.warning(f"Latency detected for {failover_group_name}: "
                       f"{time_since_completion:.1f} minutes since last completion "
                       f"(threshold: {threshold_minutes:.1f} minutes)")
        return {
            'failover_group': failover_group_name,
            'time_since_completion': time_since_completion,
            'threshold': threshold_minutes,
            'last_completion': end_time,
            'cron_interval': interval_minutes,
            'last_duration': last_duration
        }

    return None


def send_email_notification(subject: str, body: str,
                           smtp_server: str = None,
                           smtp_port: int = 587,
                           from_addr: str = None,
                           to_addrs: List[str] = None,
                           smtp_user: str = None,
                           smtp_password: str = None):
    """
    Send email notification.

    Args:
        subject: Email subject
        body: Email body
        smtp_server: SMTP server address
        smtp_port: SMTP port
        from_addr: Sender email address
        to_addrs: List of recipient email addresses
        smtp_user: SMTP username
        smtp_password: SMTP password
    """
    try:
        # Use environment variables if parameters not provided
        smtp_server = smtp_server or os.getenv('SMTP_SERVER')
        from_addr = from_addr or os.getenv('FROM_EMAIL')
        to_addrs = to_addrs or os.getenv('TO_EMAILS', '').split(',')
        smtp_user = smtp_user or os.getenv('SMTP_USER')
        smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')

        if not all([smtp_server, from_addr, to_addrs, smtp_user, smtp_password]):
            logging.error("Email configuration incomplete. Skipping email notification.")
            return

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        logging.info(f"Sending email notification: {subject}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logging.info("Email notification sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")


def monitor_failover_groups(account: str, user: str = None, password: str = None,
                           authenticator: str = None):
    """
    Main monitoring function for failover groups.

    Args:
        account: Snowflake account name
        user: Username
        password: Password
        authenticator: Authentication method
    """
    global notified_failures

    # Connect to primary account
    conn = connect_to_snowflake(account, user, password, authenticator)

    try:
        # Get all failover groups
        failover_groups = get_failover_groups(conn)

        for fg in failover_groups:
            fg_name = fg.get('name', 'Unknown')
            cron_schedule = fg.get('replication_schedule', '')

            logging.info(f"Processing failover group: {fg_name}")
            logging.info(f"Cron schedule: {cron_schedule}")

            # Get next scheduled refresh time
            next_scheduled_refresh = fg.get('next_scheduled_refresh') or fg.get('NEXT_SCHEDULED_REFRESH')
            if next_scheduled_refresh:
                logging.info(f"Next scheduled refresh for {fg_name}: {next_scheduled_refresh}")

            # Check if current account is primary
            if is_primary_account(conn, fg_name):
                logging.info(f"{fg_name} - Current account is primary, connecting to secondary")

                # Get secondary account and connect
                secondary_account = get_secondary_account(fg, account)
                if not secondary_account:
                    logging.error(f"Could not determine secondary account for {fg_name}")
                    continue

                # Connect to secondary to query replication history
                try:
                    secondary_conn = connect_to_snowflake(secondary_account, user, password, authenticator)
                    history = get_replication_history(secondary_conn, fg_name)
                    secondary_conn.close()
                except Exception as e:
                    logging.error(f"Failed to connect to secondary account {secondary_account}: {e}")
                    continue
            else:
                logging.info(f"{fg_name} - Current account is secondary")
                history = get_replication_history(conn, fg_name)

            # Check for failures
            failure_info = check_for_failures(fg_name, history)
            if failure_info:
                failure_key = f"{fg_name}_failure"
                if failure_key not in notified_failures:
                    subject = f"Snowflake Replication Failure: {fg_name}"
                    body = f"""
Replication failure detected for failover group: {fg_name}

Status: {failure_info['status']}
Start Time: {failure_info['start_time']}
End Time: {failure_info['end_time']}
Error Message: {failure_info['error_message']}

Please investigate immediately.
                    """
                    send_email_notification(subject, body)
                    notified_failures.add(failure_key)
            else:
                # Clear notification flag if no longer failing
                failure_key = f"{fg_name}_failure"
                if failure_key in notified_failures:
                    notified_failures.remove(failure_key)

            # Check for latency
            if cron_schedule:
                latency_info = check_for_latency(fg_name, cron_schedule, history)
                if latency_info:
                    latency_key = f"{fg_name}_latency"
                    if latency_key not in notified_failures:
                        subject = f"Snowflake Replication Latency: {fg_name}"
                        body = f"""
Replication latency detected for failover group: {fg_name}

Time since last completion: {latency_info['time_since_completion']:.1f} minutes
Threshold: {latency_info['threshold']:.1f} minutes
Last completion: {latency_info['last_completion']}
Cron interval: {latency_info['cron_interval']} minutes
Last duration: {latency_info['last_duration']:.1f} minutes

The replication is running behind schedule.
                        """
                        send_email_notification(subject, body)
                        notified_failures.add(latency_key)
                else:
                    # Clear notification flag if latency resolved
                    latency_key = f"{fg_name}_latency"
                    if latency_key in notified_failures:
                        notified_failures.remove(latency_key)

    finally:
        conn.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Monitor Snowflake replication failover groups')
    parser.add_argument('account', help='Snowflake account name')
    parser.add_argument('--user', help='Snowflake username (or set SNOWFLAKE_USER env var)')
    parser.add_argument('--password', help='Snowflake password (or set SNOWFLAKE_PASSWORD env var)')
    parser.add_argument('--authenticator', help='Authentication method (e.g., externalbrowser)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    logging.info("="*80)
    logging.info(f"Starting Snowflake Replication Monitor for account: {args.account}")
    logging.info("="*80)

    # Main monitoring loop
    try:
        while True:
            try:
                monitor_failover_groups(
                    account=args.account,
                    user=args.user,
                    password=args.password,
                    authenticator=args.authenticator
                )
            except Exception as e:
                logging.error(f"Error in monitoring cycle: {e}")

            logging.info(f"Sleeping for {args.interval} seconds...")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
