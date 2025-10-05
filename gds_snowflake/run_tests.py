#!/usr/bin/env python3
"""
Test runner for Snowflake Replication Monitor
Runs all unit and integration tests
"""

import os
import sys
import unittest

# Add the parent directory to the path so tests can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_tests(verbosity=2, pattern='test*.py'):
    """
    Run all tests in the tests directory
    
    Args:
        verbosity: Test output verbosity (0=quiet, 1=normal, 2=verbose)
        pattern: File pattern for test files
        
    Returns:
        True if all tests passed, False otherwise
    """
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern=pattern)

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_test_module(module_name, verbosity=2):
    """
    Run tests from a specific module
    
    Args:
        module_name: Name of the test module (e.g., 'test_snowflake_connection')
        verbosity: Test output verbosity
        
    Returns:
        True if all tests passed, False otherwise
    """
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{module_name}')

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def print_usage():
    """Print usage information"""
    print("""
Snowflake Replication Monitor Test Runner

Usage:
    python run_tests.py [options]

Options:
    -h, --help              Show this help message
    -v, --verbose           Verbose output (verbosity=2)
    -q, --quiet             Quiet output (verbosity=0)
    -m MODULE, --module MODULE
                            Run specific test module
                            Examples:
                              test_snowflake_connection
                              test_snowflake_replication
                              test_monitor_integration

Examples:
    # Run all tests
    python run_tests.py
    
    # Run all tests quietly
    python run_tests.py -q
    
    # Run specific test module
    python run_tests.py -m test_snowflake_connection
    
    # Run specific test module verbosely
    python run_tests.py -v -m test_snowflake_replication
""")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Run tests for Snowflake Replication Monitor',
        add_help=False
    )
    parser.add_argument('-h', '--help', action='store_true',
                       help='Show help message')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet output')
    parser.add_argument('-m', '--module', type=str,
                       help='Run specific test module')

    args = parser.parse_args()

    if args.help:
        print_usage()
        return 0

    # Determine verbosity
    verbosity = 2  # Default
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2

    print("="*70)
    print("Snowflake Replication Monitor - Test Suite")
    print("="*70)

    if args.module:
        print(f"\nRunning tests from module: {args.module}\n")
        success = run_specific_test_module(args.module, verbosity)
    else:
        print("\nRunning all tests...\n")
        success = run_tests(verbosity)

    print("\n" + "="*70)
    if success:
        print("✓ All tests passed!")
        print("="*70)
        return 0
    print("✗ Some tests failed")
    print("="*70)
    return 1


if __name__ == '__main__':
    sys.exit(main())
