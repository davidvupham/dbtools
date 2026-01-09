#!/bin/bash
# Validate Liquibase Properties
# Validates that properties files exist and have correct content
# Reusable across all tutorial parts

set -u

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Validating Liquibase Properties"
echo "========================================"
echo

LIQUIBASE_TUTORIAL_DATA_DIR="${LIQUIBASE_TUTORIAL_DATA_DIR:-/data/${USER}/liquibase_tutorial}"

if [[ ! -d "$LIQUIBASE_TUTORIAL_DATA_DIR" ]]; then
    echo -e "${RED}ERROR: LIQUIBASE_TUTORIAL_DATA_DIR not set or directory doesn't exist${NC}"
    echo "Run setup_liquibase_environment.sh first"
    exit 1
fi

FAILURES=0

pass() { echo -e "[${GREEN}PASS${NC}] $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAILURES=$((FAILURES+1)); }

ENV_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/env"
CHANGELOG_DIR="$LIQUIBASE_TUTORIAL_DATA_DIR/database/changelog"

echo "Checking properties files..."
echo

# Check env directory exists
if [[ -d "$ENV_DIR" ]]; then
    pass "env/ directory exists"
else
    fail "env/ directory not found at $ENV_DIR"
fi

# Check each properties file
for env in dev stg prd; do
    prop_file="$ENV_DIR/liquibase.${env}.properties"
    expected_port=$((14331 + $(echo "dev stg prd" | tr ' ' '\n' | grep -n "^${env}$" | cut -d: -f1) - 1))

    echo -n "  Checking liquibase.${env}.properties... "
    if [[ -f "$prop_file" ]]; then
        pass "File exists"

        # Check required properties
        if grep -q "url=jdbc:sqlserver://" "$prop_file"; then
            pass "    Contains JDBC URL"

            # Check port is correct
            if grep -q "localhost:${expected_port}" "$prop_file"; then
                pass "    Port ${expected_port} correct"
            else
                fail "    Port mismatch (expected ${expected_port})"
            fi

            # Check database name
            if grep -q "databaseName=orderdb" "$prop_file"; then
                pass "    Database name correct (orderdb)"
            else
                fail "    Database name incorrect (expected orderdb)"
            fi
        else
            fail "    Missing JDBC URL"
        fi

        if grep -q "username=sa" "$prop_file"; then
            pass "    Username correct (sa)"
        else
            fail "    Username incorrect"
        fi

        if grep -q "changelog-file=database/changelog/changelog.xml" "$prop_file"; then
            pass "    Changelog file path correct"
        else
            fail "    Changelog file path incorrect"
        fi

        if grep -q "search-path=/data" "$prop_file"; then
            pass "    Search path correct"
        else
            fail "    Search path incorrect"
        fi
    else
        fail "File not found: $prop_file"
    fi
    echo
done

# Check master changelog exists
echo "Checking master changelog..."
changelog_file="$CHANGELOG_DIR/changelog.xml"
if [[ -f "$changelog_file" ]]; then
    pass "changelog.xml exists"

    # Check it's valid XML
    if grep -q "<?xml version" "$changelog_file" && grep -q "<databaseChangeLog" "$changelog_file"; then
        pass "    Valid XML structure"
    else
        fail "    Invalid XML structure"
    fi

    # Check baseline include
    if grep -q "V0000__baseline.mssql.sql" "$changelog_file"; then
        pass "    Includes baseline file"
    else
        fail "    Missing baseline include"
    fi
else
    fail "changelog.xml not found at $changelog_file"
fi

echo
echo "========================================"
if [[ "$FAILURES" -eq 0 ]]; then
    echo -e "${GREEN}VALIDATION SUCCESSFUL${NC}"
    echo "========================================"
    echo
    echo "Expected output summary:"
    echo "  ✓ env/ directory exists"
    echo "  ✓ liquibase.dev.properties exists with correct config (port 14331)"
    echo "  ✓ liquibase.stg.properties exists with correct config (port 14332)"
    echo "  ✓ liquibase.prd.properties exists with correct config (port 14333)"
    echo "  ✓ All properties files have: url, username, changelog-file, search-path"
    echo "  ✓ changelog.xml exists and includes baseline"
    echo
    exit 0
else
    echo -e "${RED}VALIDATION FAILED ($FAILURES errors)${NC}"
    echo "========================================"
    echo
    echo "To fix:"
    echo "  1. Run setup_liquibase_environment.sh to create properties files"
    echo "  2. Or manually create properties files in $ENV_DIR"
    echo
    exit 1
fi
