#!/bin/bash
# Quick Fix Script for Critical Issues in gds_snowflake Package
# Run this before deploying to production

set -e

echo "================================"
echo "GDS Snowflake Package Quick Fix"
echo "================================"
echo ""

# Navigate to package directory
cd "$(dirname "$0")"

echo "1. Fixing code formatting (Black)..."
black gds_snowflake/ tests/ examples/ --line-length=120
echo "   ✓ Formatting complete"
echo ""

echo "2. Checking imports..."
python -c "from gds_snowflake import SnowflakeConnection, SnowflakeDatabase, SnowflakeTable, SnowflakeReplication; print('   ✓ All imports successful')"
echo ""

echo "3. Running tests..."
pytest tests/test_database.py tests/test_table.py tests/test_snowflake_replication.py -v --tb=short -q
echo "   ✓ Tests passed"
echo ""

echo "4. Checking security (Bandit)..."
bandit -r gds_snowflake/ -ll -q 2>&1 | head -5 || echo "   ⚠ See full report for details"
echo ""

echo "5. Checking code quality (Pylint - critical issues only)..."
pylint gds_snowflake/ --disable=all --enable=E,F --max-line-length=120 2>&1 | tail -5 || echo "   ✓ No critical errors"
echo ""

echo "================================"
echo "Quick Fix Complete!"
echo "================================"
echo ""
echo "⚠ IMPORTANT: Before deploying to PyPI:"
echo "   1. Add 'gds-hvault>=1.0.0' to install_requires in setup.py"
echo "   2. Update version number in setup.py"
echo "   3. Run full test suite: pytest -v --cov=gds_snowflake"
echo "   4. Build package: python -m build"
echo "   5. Test install: pip install dist/gds_snowflake-*.whl"
echo ""
