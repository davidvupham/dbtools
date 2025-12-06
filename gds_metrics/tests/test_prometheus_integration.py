#!/usr/bin/env python3
"""
Integration test for gds_metrics with Prometheus.

This script verifies that PrometheusMetrics correctly exposes metrics
that can be scraped by a Prometheus server.

Prerequisites:
    1. Start Prometheus: cd docker/prometheus && docker compose up -d
    2. Run this script: python tests/test_prometheus_integration.py

Verification:
    1. Check http://localhost:8080/metrics for raw metrics
    2. Check http://localhost:9090/targets for scrape status
    3. Query metrics in Prometheus UI at http://localhost:9090
"""

import sys
import time
import urllib.error
import urllib.request

from gds_metrics import PrometheusMetrics

# Add parent directory for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])


def check_prometheus_available() -> bool:
    """Check if Prometheus server is running."""
    try:
        urllib.request.urlopen("http://localhost:9090/-/healthy", timeout=2)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


def check_metrics_endpoint(port: int = 8080) -> bool:
    """Check if metrics endpoint is accessible."""
    try:
        response = urllib.request.urlopen(f"http://localhost:{port}/metrics", timeout=2)
        content = response.read().decode("utf-8")
        return "# HELP" in content or "# TYPE" in content
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


def run_integration_test():
    """Run the integration test."""
    print("=" * 60)
    print("GDS Metrics - Prometheus Integration Test")
    print("=" * 60)

    # Check Prometheus availability
    print("\n[1/5] Checking Prometheus server...")
    if check_prometheus_available():
        print("      ✓ Prometheus is running at http://localhost:9090")
    else:
        print("      ⚠ Prometheus not available (optional for this test)")
        print("        Start with: cd docker/prometheus && docker compose up -d")

    # Create PrometheusMetrics
    print("\n[2/5] Creating PrometheusMetrics instance...")
    try:
        metrics = PrometheusMetrics(prefix="integration_test", port=8080)
        print("      ✓ PrometheusMetrics created (port 8080)")
    except Exception as e:
        print(f"      ✗ Failed to create PrometheusMetrics: {e}")
        return False

    # Wait for HTTP server to start
    time.sleep(0.5)

    # Check metrics endpoint
    print("\n[3/5] Checking metrics endpoint...")
    if check_metrics_endpoint(8080):
        print("      ✓ Metrics endpoint available at http://localhost:8080/metrics")
    else:
        print("      ✗ Metrics endpoint not accessible")
        return False

    # Generate test metrics
    print("\n[4/5] Generating test metrics...")
    try:
        # Counters
        for status in ["200", "201", "400", "404", "500"]:
            count = {"200": 100, "201": 20, "400": 5, "404": 10, "500": 2}.get(status, 1)
            metrics.increment("http_requests_total", value=count, labels={"status": status})
            print(f"      ✓ Counter: http_requests_total{{status={status}}} += {count}")

        # Gauges
        metrics.gauge("active_connections", 42.0, labels={"pool": "main"})
        print("      ✓ Gauge: active_connections{pool=main} = 42.0")

        metrics.gauge("memory_usage_bytes", 1024 * 1024 * 256.0)
        print("      ✓ Gauge: memory_usage_bytes = 268435456.0")

        # Histograms
        for duration in [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]:
            metrics.histogram(
                "request_duration_seconds", duration, labels={"endpoint": "/api/test"}
            )
        print("      ✓ Histogram: request_duration_seconds (7 observations)")

        # Timing
        for ms in [10, 25, 50, 100, 250, 500]:
            metrics.timing("query_time_ms", float(ms), labels={"query": "select"})
        print("      ✓ Timing: query_time_ms (6 observations)")

    except Exception as e:
        print(f"      ✗ Failed to generate metrics: {e}")
        return False

    # Verify metrics content
    print("\n[5/5] Verifying metrics content...")
    try:
        response = urllib.request.urlopen("http://localhost:8080/metrics", timeout=2)
        content = response.read().decode("utf-8")

        expected_metrics = [
            "integration_test_http_requests_total",
            "integration_test_active_connections",
            "integration_test_memory_usage_bytes",
            "integration_test_request_duration_seconds",
            "integration_test_query_time_ms",
        ]

        all_found = True
        for metric in expected_metrics:
            if metric in content:
                print(f"      ✓ Found: {metric}")
            else:
                print(f"      ✗ Missing: {metric}")
                all_found = False

        if not all_found:
            return False

    except Exception as e:
        print(f"      ✗ Failed to verify metrics: {e}")
        return False

    print("\n" + "=" * 60)
    print("Integration Test: PASSED")
    print("=" * 60)

    print("\nNext steps:")
    print("  1. View raw metrics: curl http://localhost:8080/metrics")
    print("  2. View in Prometheus: http://localhost:9090")
    print("  3. View in Grafana: http://localhost:3000 (admin/admin)")

    return True


def run_interactive_demo():
    """Run an interactive demo that keeps generating metrics."""
    print("\n" + "=" * 60)
    print("Interactive Demo Mode")
    print("=" * 60)
    print("\nGenerating metrics continuously...")
    print("Press Ctrl+C to stop\n")

    metrics = PrometheusMetrics(prefix="demo", port=8080)
    iteration = 0

    try:
        while True:
            iteration += 1

            # Simulate HTTP requests
            import random

            status = random.choices(["200", "201", "400", "404", "500"], weights=[80, 10, 5, 4, 1])[
                0
            ]
            metrics.increment("requests_total", labels={"status": status})

            # Simulate active connections
            connections = random.randint(10, 50)
            metrics.gauge("active_connections", float(connections))

            # Simulate request duration
            duration = random.uniform(0.01, 0.5)
            metrics.histogram("request_duration_seconds", duration)

            # Simulate query time
            query_time = random.uniform(5, 200)
            metrics.timing("query_time_ms", query_time)

            if iteration % 10 == 0:
                print(
                    f"  Iteration {iteration}: status={status}, "
                    f"connections={connections}, duration={duration:.3f}s"
                )

            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n\nStopped after {iteration} iterations")
        print("Metrics are still available at http://localhost:8080/metrics")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GDS Metrics Prometheus Integration Test")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo mode")
    args = parser.parse_args()

    if args.demo:
        run_interactive_demo()
    else:
        success = run_integration_test()
        sys.exit(0 if success else 1)
