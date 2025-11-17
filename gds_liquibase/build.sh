#!/bin/bash
# Build script for gds_liquibase package

set -e

echo "Building gds_liquibase package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python setup.py sdist bdist_wheel

echo "Build complete! Distribution files:"
ls -lh dist/

echo ""
echo "To install locally:"
echo "  pip install dist/gds_liquibase-0.1.0-py3-none-any.whl"
echo ""
echo "To install in development mode:"
echo "  pip install -e ."
