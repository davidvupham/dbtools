#!/usr/bin/env python3
"""
Snowflake monitoring using the SnowflakeMonitor class.

This script provides a simple interface to monitor Snowflake accounts using
the comprehensive SnowflakeMonitor class for connectivity, replication failures,
and latency monitoring.

Usage:
    python monitor_snowflake.py --account your-account [options]
"""

import argparse
import json
import logging
import os
import sys

from gds_snowflake import SnowflakeMonitor


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor Snowflake account connectivity and replication"
    )

    # Required arguments
    parser.add_argument(
        "--account",
        required=True,
        help="Snowflake account name"
    )

    # Monitoring mode
    parser.add_argument(
        "--connectivity-only",
        action="store_true",
        help="Only test connectivity"
    )
    parser.add_argument(
        "--replication-only",
        action="store_true",
        help="Only check replication (failures and latency)"
    )

    # Configuration
    parser.add_argument(
        "--connectivity-timeout",
        type=int,
        default=30,
        help="Connectivity timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--latency-threshold",
        type=float,
        default=30.0,
        help="Latency threshold in minutes (default: 30.0)"
    )

    # Email notifications
    parser.add_argument(
        "--enable-email",
        action="store_true",
        help="Enable email notifications (requires env vars)"
    )

    # Output
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Create monitor with environment-based configuration
        logger.info(f"Creating SnowflakeMonitor for account: {args.account}")

        monitor = SnowflakeMonitor(
            account=args.account,
            connectivity_timeout=args.connectivity_timeout,
            latency_threshold_minutes=args.latency_threshold,
            enable_email_alerts=args.enable_email,
            # Email configuration from environment variables
            smtp_server=os.getenv('SMTP_SERVER'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_user=os.getenv('SMTP_USER'),
            smtp_password=os.getenv('SMTP_PASSWORD'),
            from_email=os.getenv('FROM_EMAIL'),
            to_emails=os.getenv('TO_EMAILS', '').split(',') if os.getenv('TO_EMAILS') else None,
        )

        # Run monitoring based on options
        if args.connectivity_only:
            logger.info("Running connectivity monitoring only")
            result = monitor.monitor_connectivity()

            if args.json:
                output = {
                    'connectivity': {
                        'success': result.success,
                        'response_time_ms': result.response_time_ms,
                        'account_info': result.account_info,
                        'error': result.error,
                        'timestamp': result.timestamp.isoformat()
                    }
                }
                print(json.dumps(output, indent=2))
            else:
                status = "✓ CONNECTED" if result.success else "✗ DISCONNECTED"
                print(f"Connectivity: {status}")
                if result.success:
                    print(f"Response Time: {result.response_time_ms} ms")
                else:
                    print(f"Error: {result.error}")

            # Exit with appropriate code
            sys.exit(0 if result.success else 1)

        elif args.replication_only:
            logger.info("Running replication monitoring only")

            # Check failures
            failure_results = monitor.monitor_replication_failures()
            latency_results = monitor.monitor_replication_latency()

            if args.json:
                output = {
                    'replication_failures': [
                        {
                            'failover_group': r.failover_group,
                            'has_failure': r.has_failure,
                            'failure_message': r.failure_message
                        }
                        for r in failure_results
                    ],
                    'replication_latency': [
                        {
                            'failover_group': r.failover_group,
                            'has_latency': r.has_latency,
                            'latency_minutes': r.latency_minutes,
                            'latency_message': r.latency_message
                        }
                        for r in latency_results
                    ]
                }
                print(json.dumps(output, indent=2))
            else:
                failures = sum(1 for r in failure_results if r.has_failure)
                latency_issues = sum(1 for r in latency_results if r.has_latency)

                print("Replication Status:")
                print(f"  Total Groups: {len(failure_results)}")
                print(f"  Failures: {failures}")
                print(f"  Latency Issues: {latency_issues}")

                if failures > 0:
                    print("\nFailures:")
                    for r in failure_results:
                        if r.has_failure:
                            print(f"  ✗ {r.failover_group}: {r.failure_message}")

                if latency_issues > 0:
                    print("\nLatency Issues:")
                    for r in latency_results:
                        if r.has_latency:
                            duration = f" ({r.latency_minutes} min)" if r.latency_minutes else ""
                            print(f"  ⚠ {r.failover_group}: {r.latency_message}{duration}")

            # Exit with appropriate code
            has_issues = failures > 0 or latency_issues > 0
            sys.exit(1 if has_issues else 0)

        else:
            # Comprehensive monitoring (default)
            logger.info("Running comprehensive monitoring")
            results = monitor.monitor_all()

            if args.json:
                # Convert datetime objects for JSON serialization
                json_results = json.loads(json.dumps(results, default=str))
                print(json.dumps(json_results, indent=2))
            else:
                summary = results['summary']
                conn_ok = summary['connectivity_ok']
                failures = summary['groups_with_failures']
                latency_issues = summary['groups_with_latency']

                print("Monitoring Results:")
                print(f"  Account: {results['account']}")
                print(f"  Connectivity: {'✓ OK' if conn_ok else '✗ FAILED'}")
                print(f"  Failover Groups: {summary['total_failover_groups']}")
                print(f"  Replication Failures: {failures}")
                print(f"  Latency Issues: {latency_issues}")
                print(f"  Duration: {summary['monitoring_duration_ms']} ms")

                # Show details if there are issues
                if not conn_ok:
                    conn = results.get('connectivity', {})
                    print(f"\nConnectivity Error: {conn.get('error', 'Unknown')}")

                if failures > 0:
                    print("\nReplication Failures:")
                    for r in results.get('replication_failures', []):
                        if r.has_failure:
                            print(f"  ✗ {r.failover_group}: {r.failure_message}")

                if latency_issues > 0:
                    print("\nLatency Issues:")
                    for r in results.get('replication_latency', []):
                        if r.has_latency:
                            duration = f" ({r.latency_minutes} min)" if r.latency_minutes else ""
                            print(f"  ⚠ {r.failover_group}: {r.latency_message}{duration}")

                # Overall status
                has_issues = not conn_ok or failures > 0 or latency_issues > 0
                overall = "⚠ ISSUES DETECTED" if has_issues else "✓ ALL OK"
                print(f"\nOverall Status: {overall}")

            # Exit with appropriate code
            has_issues = (
                not results['summary']['connectivity_ok'] or
                results['summary']['groups_with_failures'] > 0 or
                results['summary']['groups_with_latency'] > 0
            )
            sys.exit(1 if has_issues else 0)

    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during monitoring: {e!s}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up
        try:
            monitor.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
