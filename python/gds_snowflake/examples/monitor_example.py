#!/usr/bin/env python3
"""
Example script demonstrating the use of the SnowflakeMonitor class.

This script shows how to:
1. Create a SnowflakeMonitor instance
2. Monitor connectivity, replication failures, and latency
3. Run comprehensive monitoring
4. Handle results and notifications

Usage:
    python monitor_example.py --account your-account [options]
"""

import argparse
import json
import logging
import sys

from gds_snowflake import SnowflakeMonitor


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Snowflake monitoring example using SnowflakeMonitor class")

    # Required arguments
    parser.add_argument("--account", required=True, help="Snowflake account name")

    # Optional Snowflake connection parameters
    parser.add_argument("--user", help="Snowflake username")
    parser.add_argument("--warehouse", help="Snowflake warehouse")
    parser.add_argument("--role", help="Snowflake role")
    parser.add_argument("--database", help="Snowflake database")

    # Monitoring options
    parser.add_argument("--connectivity-only", action="store_true", help="Only test connectivity")
    parser.add_argument("--failures-only", action="store_true", help="Only check replication failures")
    parser.add_argument("--latency-only", action="store_true", help="Only check replication latency")
    parser.add_argument(
        "--connectivity-timeout", type=int, default=30, help="Connectivity timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--latency-threshold", type=float, default=30.0, help="Latency threshold in minutes (default: 30.0)"
    )

    # Email configuration
    parser.add_argument("--smtp-server", help="SMTP server for notifications")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--smtp-user", help="SMTP username")
    parser.add_argument("--smtp-password", help="SMTP password")
    parser.add_argument("--from-email", help="From email address")
    parser.add_argument("--to-emails", nargs="+", help="Recipient email addresses")
    parser.add_argument("--disable-email", action="store_true", help="Disable email notifications")

    # Output options
    parser.add_argument("--json-output", action="store_true", help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Create monitor instance
        logger.info(f"Creating SnowflakeMonitor for account: {args.account}")

        monitor = SnowflakeMonitor(
            account=args.account,
            user=args.user,
            warehouse=args.warehouse,
            role=args.role,
            database=args.database,
            smtp_server=args.smtp_server,
            smtp_port=args.smtp_port,
            smtp_user=args.smtp_user,
            smtp_password=args.smtp_password,
            from_email=args.from_email,
            to_emails=args.to_emails,
            connectivity_timeout=args.connectivity_timeout,
            latency_threshold_minutes=args.latency_threshold,
            enable_email_alerts=not args.disable_email,
        )

        # Run monitoring based on options
        if args.connectivity_only:
            logger.info("Running connectivity monitoring only")
            result = monitor.monitor_connectivity()

            if args.json_output:
                print(
                    json.dumps(
                        {
                            "connectivity": {
                                "success": result.success,
                                "response_time_ms": result.response_time_ms,
                                "account_info": result.account_info,
                                "error": result.error,
                                "timestamp": result.timestamp.isoformat(),
                            }
                        },
                        indent=2,
                    )
                )
            else:
                print_connectivity_result(result)

        elif args.failures_only:
            logger.info("Running replication failure monitoring only")
            results = monitor.monitor_replication_failures()

            if args.json_output:
                print(
                    json.dumps(
                        {
                            "replication_failures": [
                                {
                                    "failover_group": r.failover_group,
                                    "has_failure": r.has_failure,
                                    "failure_message": r.failure_message,
                                    "last_refresh": r.last_refresh.isoformat() if r.last_refresh else None,
                                    "next_refresh": r.next_refresh.isoformat() if r.next_refresh else None,
                                }
                                for r in results
                            ]
                        },
                        indent=2,
                    )
                )
            else:
                print_replication_results(results, "Failure")

        elif args.latency_only:
            logger.info("Running replication latency monitoring only")
            results = monitor.monitor_replication_latency()

            if args.json_output:
                print(
                    json.dumps(
                        {
                            "replication_latency": [
                                {
                                    "failover_group": r.failover_group,
                                    "has_latency": r.has_latency,
                                    "latency_minutes": r.latency_minutes,
                                    "latency_message": r.latency_message,
                                    "last_refresh": r.last_refresh.isoformat() if r.last_refresh else None,
                                    "next_refresh": r.next_refresh.isoformat() if r.next_refresh else None,
                                }
                                for r in results
                            ]
                        },
                        indent=2,
                    )
                )
            else:
                print_replication_results(results, "Latency")

        else:
            logger.info("Running comprehensive monitoring")
            results = monitor.monitor_all()

            if args.json_output:
                # Convert datetime objects to ISO strings for JSON serialization
                json_results = json.loads(json.dumps(results, default=str))
                print(json.dumps(json_results, indent=2))
            else:
                print_comprehensive_results(results)

        # Close monitor
        monitor.close()

        logger.info("Monitoring completed successfully")

    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during monitoring: {e!s}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def print_connectivity_result(result):
    """Print connectivity result in human-readable format."""
    print("\n=== Connectivity Results ===")
    print(f"Account: {result.account_info.get('account', 'Unknown')}")
    print(f"Success: {'✓' if result.success else '✗'}")
    print(f"Response Time: {result.response_time_ms} ms")
    print(f"Timestamp: {result.timestamp}")

    if result.error:
        print(f"Error: {result.error}")

    if result.account_info:
        print("\nAccount Information:")
        for key, value in result.account_info.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")


def print_replication_results(results, check_type):
    """Print replication results in human-readable format."""
    print(f"\n=== Replication {check_type} Results ===")

    if not results:
        print("No failover groups found")
        return

    for result in results:
        status_icon = "✗" if (result.has_failure or result.has_latency) else "✓"
        print(f"\n{status_icon} Failover Group: {result.failover_group}")

        if check_type == "Failure" and result.has_failure:
            print(f"   Failure: {result.failure_message}")
        elif check_type == "Latency" and result.has_latency:
            print(f"   Latency: {result.latency_message}")
            if result.latency_minutes:
                print(f"   Duration: {result.latency_minutes} minutes")

        if result.last_refresh:
            print(f"   Last Refresh: {result.last_refresh}")
        if result.next_refresh:
            print(f"   Next Refresh: {result.next_refresh}")


def print_comprehensive_results(results):
    """Print comprehensive monitoring results in human-readable format."""
    print("\n=== Comprehensive Monitoring Results ===")
    print(f"Account: {results['account']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Duration: {results['summary']['monitoring_duration_ms']} ms")

    # Connectivity
    conn = results.get("connectivity")
    if conn:
        status = "✓ CONNECTED" if conn.success else "✗ DISCONNECTED"
        print(f"\nConnectivity: {status}")
        if not conn.success and conn.error:
            print(f"  Error: {conn.error}")
        else:
            print(f"  Response Time: {conn.response_time_ms} ms")

    # Summary
    summary = results["summary"]
    print("\nSummary:")
    print(f"  Total Failover Groups: {summary['total_failover_groups']}")
    print(f"  Groups with Failures: {summary['groups_with_failures']}")
    print(f"  Groups with Latency Issues: {summary['groups_with_latency']}")

    # Failures
    failures = results.get("replication_failures", [])
    if any(r.has_failure for r in failures):
        print("\nReplication Failures:")
        for result in failures:
            if result.has_failure:
                print(f"  ✗ {result.failover_group}: {result.failure_message}")

    # Latency
    latency_issues = results.get("replication_latency", [])
    if any(r.has_latency for r in latency_issues):
        print("\nLatency Issues:")
        for result in latency_issues:
            if result.has_latency:
                duration = f" ({result.latency_minutes} min)" if result.latency_minutes else ""
                print(f"  ⚠ {result.failover_group}: {result.latency_message}{duration}")

    # Overall status
    has_issues = (
        not summary["connectivity_ok"] or summary["groups_with_failures"] > 0 or summary["groups_with_latency"] > 0
    )

    overall_status = "⚠ ISSUES DETECTED" if has_issues else "✓ ALL SYSTEMS OK"
    print(f"\nOverall Status: {overall_status}")


if __name__ == "__main__":
    main()
