#!/usr/bin/env python3
"""
Snowflake Replication Monitor (Refactored Version)
Monitors Snowflake failover groups for replication failures and latency issues.

This version uses modular architecture with separate modules for:
- snowflake_connection: Connection management
- snowflake_replication: Replication and failover group operations

Note: All Vault/secret management is now handled in the connection module,
not here.
"""

import argparse
import logging
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from gds_snowflake import FailoverGroup, SnowflakeConnection, SnowflakeReplication

# Script name for logging
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
LOG_FILE = f"/var/log/{SCRIPT_NAME}.log"

# Email notification tracking (to send only once per failure)
notified_failures: set[str] = set()


def setup_logging():
    """Configure logging to write to /var/log"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
    )


def send_email_notification(
    subject: str,
    body: str,
    smtp_server: str = None,
    smtp_port: int = 587,
    from_addr: str = None,
    to_addrs: list[str] = None,
    smtp_user: str = None,
    smtp_password: str = None,
):
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
        smtp_server = smtp_server or os.getenv("SMTP_SERVER")
        from_addr = from_addr or os.getenv("FROM_EMAIL")
        to_addrs = to_addrs or os.getenv("TO_EMAILS", "").split(",")
        smtp_user = smtp_user or os.getenv("SMTP_USER")
        smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

        if not all([smtp_server, from_addr, to_addrs, smtp_user, smtp_password]):
            logging.error("Email configuration incomplete. Skipping email notification.")
            return

        # Filter empty email addresses
        to_addrs = [addr.strip() for addr in to_addrs if addr.strip()]
        if not to_addrs:
            logging.error("No valid recipient email addresses. Skipping email notification.")
            return

        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        logging.info(f"Sending email notification: {subject}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logging.info("Email notification sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")


def check_snowflake_connectivity(account: str, timeout_seconds: int = 30) -> bool:
    """
    Test connectivity to Snowflake account and log results.

    Args:
        account: Snowflake account name
        timeout_seconds: Connection timeout in seconds

    Returns:
        bool: True if connectivity test passed, False otherwise
    """
    logging.info(f"Starting connectivity check for account: {account}")

    try:
        # Create a temporary connection just for testing
        test_conn = SnowflakeConnection(account=account)

        # Run connectivity test
        result = test_conn.test_connectivity(timeout_seconds=timeout_seconds)

        if result["success"]:
            logging.info(f"✓ Connectivity test PASSED for {account} (response time: {result['response_time_ms']}ms)")

            # Log account information
            account_info = result.get("account_info", {})
            if account_info:
                logging.info(f"  - Account: {account_info.get('account_name')}")
                logging.info(f"  - User: {account_info.get('current_user')}")
                logging.info(f"  - Role: {account_info.get('current_role')}")
                logging.info(f"  - Warehouse: {account_info.get('current_warehouse')}")
                logging.info(f"  - Region: {account_info.get('region')}")
                logging.info(f"  - Version: {account_info.get('snowflake_version')}")

            return True
        logging.error(f"✗ Connectivity test FAILED for {account} (response time: {result['response_time_ms']}ms)")
        logging.error(f"  Error: {result.get('error', 'Unknown error')}")

        # Send alert for connectivity issues
        send_connectivity_alert(account, result)
        return False

    except Exception as e:
        logging.error(f"✗ Connectivity test FAILED for {account}: {e!s}")

        # Send alert for connectivity issues
        send_connectivity_alert(account, {"error": str(e), "success": False})
        return False


def send_connectivity_alert(account: str, test_result: dict):
    """
    Send email alert for connectivity issues.

    Args:
        account: Snowflake account name
        test_result: Connectivity test result dictionary
    """
    subject = f"🚨 Snowflake Connectivity Alert - {account}"

    body = f"""
Snowflake connectivity test failed for account: {account}

Test Results:
- Success: {test_result.get("success", False)}
- Response Time: {test_result.get("response_time_ms", "N/A")} ms
- Error: {test_result.get("error", "Unknown error")}
- Timestamp: {test_result.get("timestamp", "N/A")}

This could indicate:
1. Network connectivity issues
2. Snowflake service disruption
3. Authentication problems
4. Account suspension or configuration issues

Please investigate immediately.

---
Snowflake Replication Monitor
Account: {account}
    """

    try:
        send_email_notification(subject.strip(), body.strip())
        logging.info(f"Connectivity alert email sent for {account}")
    except Exception as e:
        logging.error(f"Failed to send connectivity alert for {account}: {e}")


def process_failover_group(
    failover_group: FailoverGroup,
    replication: SnowflakeReplication,
    connection: SnowflakeConnection,
    current_account: str,
):
    """
    Process a single failover group to check for failures and latency.

    Args:
        failover_group: FailoverGroup object to process
        replication: SnowflakeReplication instance
        connection: SnowflakeConnection instance
        current_account: Current account name
    """
    global notified_failures

    fg_name = failover_group.name
    logging.info(f"Processing failover group: {fg_name}")
    logging.info(f"  - Type: {failover_group.type}")
    logging.info(f"  - Primary: {failover_group.primary_account}")
    logging.info(f"  - Replication Schedule: {failover_group.replication_schedule}")
    logging.info(f"  - Next Scheduled Refresh: {failover_group.next_scheduled_refresh}")

    # Determine if we need to switch to secondary account for querying history
    need_to_switch = failover_group.is_primary(current_account)
    original_account = current_account

    try:
        if need_to_switch:
            logging.info(f"{fg_name} - Current account is primary, switching to secondary for history query")
            if not replication.switch_to_secondary_account(failover_group, current_account):
                logging.error(f"Failed to switch to secondary account for {fg_name}, skipping")
                return

        # Check for replication failures
        is_failed, error_message = replication.check_replication_failure(failover_group)
        if is_failed:
            failure_key = f"{fg_name}_failure"
            if failure_key not in notified_failures:
                subject = f"Snowflake Replication Failure: {fg_name}"
                body = f"""
Replication failure detected for failover group: {fg_name}

Account: {current_account}
Primary Account: {failover_group.primary_account}
Error Message: {error_message}

Please investigate immediately.
                """
                send_email_notification(subject, body)
                notified_failures.add(failure_key)
                logging.info(f"Sent failure notification for {fg_name}")
        else:
            # Clear notification flag if no longer failing
            failure_key = f"{fg_name}_failure"
            if failure_key in notified_failures:
                notified_failures.remove(failure_key)
                logging.info(f"Cleared failure notification flag for {fg_name}")

        # Check for replication latency
        if failover_group.replication_schedule:
            has_latency, latency_message = replication.check_replication_latency(failover_group)
            if has_latency:
                latency_key = f"{fg_name}_latency"
                if latency_key not in notified_failures:
                    subject = f"Snowflake Replication Latency: {fg_name}"
                    body = f"""
Replication latency detected for failover group: {fg_name}

Account: {current_account}
Primary Account: {failover_group.primary_account}
Schedule: {failover_group.replication_schedule}

{latency_message}

The replication is running behind schedule. Please investigate.
                    """
                    send_email_notification(subject, body)
                    notified_failures.add(latency_key)
                    logging.info(f"Sent latency notification for {fg_name}")
            else:
                # Clear notification flag if latency resolved
                latency_key = f"{fg_name}_latency"
                if latency_key in notified_failures:
                    notified_failures.remove(latency_key)
                    logging.info(f"Cleared latency notification flag for {fg_name}")

    except Exception as e:
        logging.error(f"Error processing failover group {fg_name}: {e!s}")

    finally:
        # Switch back to original account if we changed it
        if need_to_switch and connection.account != original_account:
            try:
                logging.info(f"Switching back to original account: {original_account}")
                connection.switch_account(original_account)
            except Exception as e:
                logging.error(f"Error switching back to original account: {e!s}")


def monitor_failover_groups(
    account: str,
    user: str = None,
    password: str = None,
    warehouse: str = None,
    role: str = None,
):
    """
    Main monitoring function for failover groups.

    Args:
        account: Snowflake account name
        user: Username
        password: Password
        warehouse: Warehouse name
        role: Role name
    """
    # Get credentials from environment if not provided
    user = user or os.getenv("SNOWFLAKE_USER")
    warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
    role = role or os.getenv("SNOWFLAKE_ROLE")

    if not user:
        raise ValueError("Snowflake user not provided. Set via arguments or SNOWFLAKE_USER environment variable.")

    # Create connection (secret management handled in connection module)
    connection = SnowflakeConnection(
        account=account,
        user=user,
        warehouse=warehouse,
        role=role,
    )

    try:
        # First, test connectivity to Snowflake
        logging.info("=" * 60)
        logging.info("Starting Snowflake connectivity check")
        logging.info("=" * 60)

        if not check_snowflake_connectivity(account):
            logging.error(f"Connectivity test failed for {account}. Skipping replication monitoring.")
            return

        logging.info("Connectivity test passed. Proceeding with replication monitoring.")
        logging.info("=" * 60)

        # Connect to Snowflake
        connection.connect()

        # Create replication handler
        replication = SnowflakeReplication(connection)

        # Get all failover groups
        failover_groups = replication.get_failover_groups()

        if not failover_groups:
            logging.warning("No failover groups found")
            return

        # Process each failover group
        for fg in failover_groups:
            process_failover_group(fg, replication, connection, account)

        logging.info("Completed monitoring cycle for %d failover groups", len(failover_groups))

    except Exception as e:
        logging.error("Error in monitoring cycle: %s", str(e))
        raise

    finally:
        connection.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Monitor Snowflake replication failover groups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  SNOWFLAKE_USER        Snowflake username
  SNOWFLAKE_PASSWORD    Snowflake password
  SNOWFLAKE_WAREHOUSE   Snowflake warehouse (optional)
  SNOWFLAKE_ROLE        Snowflake role (optional)
  SMTP_SERVER           SMTP server for email notifications
  SMTP_USER             SMTP username
  SMTP_PASSWORD         SMTP password
  FROM_EMAIL            From email address
  TO_EMAILS             Comma-separated list of recipient emails

Example:
  %(prog)s myaccount --user myuser --password mypass --interval 60
        """,
    )

    parser.add_argument("account", help="Snowflake account name")
    parser.add_argument("--user", help="Snowflake username (or set SNOWFLAKE_USER env var)")
    parser.add_argument("--warehouse", help="Snowflake warehouse (or set SNOWFLAKE_WAREHOUSE env var)")
    parser.add_argument("--role", help="Snowflake role (or set SNOWFLAKE_ROLE env var)")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds (default: 60)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (no continuous monitoring)",
    )
    parser.add_argument(
        "--test-connectivity",
        action="store_true",
        help="Test connectivity only and exit (no replication monitoring)",
    )
    parser.add_argument(
        "--connectivity-timeout",
        type=int,
        default=30,
        help="Connectivity test timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    logging.info("=" * 80)
    logging.info(
        "Starting Snowflake Replication Monitor (Refactored) for account: %s",
        args.account,
    )

    # Handle connectivity test only mode
    if args.test_connectivity:
        logging.info("Running connectivity test only...")
        logging.info("Connectivity timeout: %d seconds", args.connectivity_timeout)
        logging.info("=" * 80)

        success = check_snowflake_connectivity(args.account, timeout_seconds=args.connectivity_timeout)

        if success:
            logging.info("=" * 80)
            logging.info("✓ Connectivity test completed successfully")
            sys.exit(0)
        else:
            logging.error("=" * 80)
            logging.error("✗ Connectivity test failed")
            sys.exit(1)

    logging.info("Monitoring interval: %d seconds", args.interval)
    logging.info("Run mode: %s", "One-time" if args.once else "Continuous")
    logging.info("=" * 80)

    # Main monitoring loop
    try:
        monitor_kwargs = dict(
            account=args.account,
            user=args.user,
            warehouse=args.warehouse,
            role=args.role,
        )
        if args.once:
            # Run once and exit
            monitor_failover_groups(**monitor_kwargs)
            logging.info("One-time monitoring completed")
        else:
            # Continuous monitoring
            while True:
                try:
                    monitor_failover_groups(**monitor_kwargs)
                except Exception as e:
                    logging.error("Error in monitoring cycle: %s", e)

                logging.info("Sleeping for %d seconds...", args.interval)
                time.sleep(args.interval)

    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
