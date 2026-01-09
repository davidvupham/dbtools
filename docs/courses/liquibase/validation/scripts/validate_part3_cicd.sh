#!/usr/bin/env bash
# Part 3 CI/CD Tutorial Validation Script
# Validates all steps in series-part3-cicd.md and documents issues

set -euo pipefail

# Timestamp for output files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VALIDATION_LOG="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/part3_validation_${TIMESTAMP}.log"
VALIDATION_REPORT="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/part3_validation_report_${TIMESTAMP}.md"
ISSUES_LOG="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/part3_issues_${TIMESTAMP}.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
SKIPPED=0
ISSUES=0

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${VALIDATION_LOG:-/dev/null}"
}

log_section() {
    echo "" | tee -a "${VALIDATION_LOG:-/dev/null}"
    echo "========================================" | tee -a "${VALIDATION_LOG:-/dev/null}"
    echo "SECTION: $*" | tee -a "${VALIDATION_LOG:-/dev/null}"
    echo "========================================" | tee -a "${VALIDATION_LOG:-/dev/null}"
    echo "" | tee -a "${VALIDATION_LOG:-/dev/null}"
}

log_pass() {
    ((PASSED++)) || true
    echo -e "${GREEN}✓ PASS${NC}: $*" | tee -a "${VALIDATION_LOG:-/dev/null}"
}

log_fail() {
    ((FAILED++)) || true
    ((ISSUES++)) || true
    echo -e "${RED}✗ FAIL${NC}: $*" | tee -a "${VALIDATION_LOG:-/dev/null}"
    echo "- **Issue #$ISSUES**: $*" >> "${ISSUES_LOG:-/dev/null}"
}

log_skip() {
    ((SKIPPED++)) || true
    echo -e "${YELLOW}⊘ SKIP${NC}: $*" | tee -a "${VALIDATION_LOG:-/dev/null}"
}

log_info() {
    echo -e "${BLUE}ℹ INFO${NC}: $*" | tee -a "${VALIDATION_LOG:-/dev/null}"
}

# Initialize reports
cat > "$VALIDATION_REPORT" << EOF
# Part 3 CI/CD Tutorial Validation Report

**Date:** $(date)
**Environment:** Ubuntu Linux
**Tutorial:** Part 3: From Local Liquibase Project to GitHub Actions CI/CD
**Validation Log:** $VALIDATION_LOG

## Summary

- **Passed:** 0
- **Failed:** 0
- **Skipped:** 0
- **Issues Found:** 0

## Validation Steps

EOF

cat > "$ISSUES_LOG" << EOF
# Part 3 Tutorial Issues and Fixes

**Date:** $(date)
**Tutorial:** series-part3-cicd.md

## Issues Found

EOF

# Check prerequisites
check_prerequisites() {
    log_section "Prerequisites Check"

    # Check if Part 1 and Part 2 files exist
    if [[ -z "${LIQUIBASE_TUTORIAL_DIR:-}" ]]; then
        # Try to determine tutorial dir from script location
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-}")" 2>/dev/null && pwd || echo "")"
        if [[ -n "$SCRIPT_DIR" ]]; then
            TUTORIAL_DIR="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || echo "")"
        else
            TUTORIAL_DIR=""
        fi
    else
        TUTORIAL_DIR="$LIQUIBASE_TUTORIAL_DIR"
    fi

    if [[ -z "$TUTORIAL_DIR" ]] || [[ ! -d "$TUTORIAL_DIR" ]]; then
        log_fail "Cannot determine tutorial directory. Set LIQUIBASE_TUTORIAL_DIR environment variable."
        # Don't return here - continue with validation using defaults
        TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-}"
    fi

    PART1_FILE="$TUTORIAL_DIR/learning-paths/series-part1-baseline.md"
    PART2_FILE="$TUTORIAL_DIR/learning-paths/series-part2-manual.md"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    if [[ -f "$PART1_FILE" ]]; then
        log_pass "Part 1 tutorial file exists: $PART1_FILE"
    else
        log_fail "Part 1 tutorial file missing: $PART1_FILE"
    fi

    if [[ -f "$PART2_FILE" ]]; then
        log_pass "Part 2 tutorial file exists: $PART2_FILE"
    else
        log_fail "Part 2 tutorial file missing: $PART2_FILE"
    fi

    if [[ -f "$PART3_FILE" ]]; then
        log_pass "Part 3 tutorial file exists: $PART3_FILE"
    else
        log_fail "Part 3 tutorial file missing: $PART3_FILE"
    fi

    # Check for required environment variables
    if [[ -n "${LIQUIBASE_TUTORIAL_DATA_DIR:-}" ]]; then
        log_pass "LIQUIBASE_TUTORIAL_DATA_DIR is set: $LIQUIBASE_TUTORIAL_DATA_DIR"
    else
        log_info "LIQUIBASE_TUTORIAL_DATA_DIR not set (will use default)"
    fi

    # Check for Docker/Podman
    if command -v docker &>/dev/null; then
        log_pass "Docker is installed"
        CONTAINER_RUNTIME="docker"
    elif command -v podman &>/dev/null; then
        log_pass "Podman is installed"
        CONTAINER_RUNTIME="podman"
    else
        log_fail "Neither Docker nor Podman is installed"
    fi

    # Check for Git
    if command -v git &>/dev/null; then
        log_pass "Git is installed: $(git --version)"
    else
        log_fail "Git is not installed"
    fi
}

# Validate file structure references
validate_file_structure() {
    log_section "File Structure Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Check if tutorial references correct file structure
    if grep -q "database/changelog/baseline/V0000__baseline.mssql.sql" "$PART3_FILE"; then
        log_pass "Tutorial references correct baseline file pattern"
    else
        log_fail "Tutorial may not reference baseline file correctly"
    fi

    if grep -q "database/changelog/changelog.xml" "$PART3_FILE"; then
        log_pass "Tutorial references changelog.xml"
    else
        log_fail "Tutorial missing reference to changelog.xml"
    fi

    if grep -q "env/liquibase.dev.properties" "$PART3_FILE"; then
        log_pass "Tutorial references environment properties files"
    else
        log_fail "Tutorial missing reference to environment properties"
    fi
}

# Validate YAML syntax in workflow examples
validate_yaml_syntax() {
    log_section "YAML Syntax Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Check if YAML workflow examples exist in tutorial
    # Note: Full YAML syntax validation requires yamllint and proper extraction
    # For now, we'll just verify the workflow examples are present
    if grep -q "name: Deploy to Development" "$PART3_FILE"; then
        log_pass "deploy-dev.yml workflow example found in tutorial"
        if command -v yamllint &>/dev/null; then
            log_info "yamllint is available (full YAML validation could be added)"
        else
            log_skip "yamllint not installed, skipping detailed YAML validation"
        fi
    else
        log_fail "deploy-dev.yml workflow example not found in tutorial"
    fi
}

# Validate GitHub Actions workflow syntax
validate_workflow_syntax() {
    log_section "GitHub Actions Workflow Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Check for proper runs-on syntax
    if grep -q "runs-on: \[self-hosted, liquibase-tutorial\]" "$PART3_FILE"; then
        log_pass "Workflow uses correct runs-on syntax with labels"
    else
        log_fail "Workflow may have incorrect runs-on syntax"
    fi

    # Check for proper secret references
    if grep -q '\${{ secrets\.DEV_DB_URL }}' "$PART3_FILE"; then
        log_pass "Workflow uses correct secret reference syntax"
    else
        log_fail "Workflow may have incorrect secret reference syntax"
    fi

    # Check for environment variable mapping
    if grep -q "MSSQL_LIQUIBASE_TUTORIAL_PWD: \${{ secrets.DEV_DB_PASSWORD }}" "$PART3_FILE"; then
        log_pass "Workflow correctly maps secrets to environment variables"
    else
        log_fail "Workflow may not correctly map secrets to environment variables"
    fi
}

# Validate JDBC URL examples
validate_jdbc_urls() {
    log_section "JDBC URL Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Check for JDBC URL examples
    if grep -q "jdbc:sqlserver://" "$PART3_FILE"; then
        log_pass "Tutorial includes JDBC URL examples"

        # Check for proper formatting
        if grep -q "jdbc:sqlserver://localhost:\${MSSQL_DEV_PORT:-14331}" "$PART3_FILE"; then
            log_pass "JDBC URLs use proper environment variable substitution"
        else
            log_fail "JDBC URLs may not use proper environment variable substitution"
        fi
    else
        log_fail "Tutorial missing JDBC URL examples"
    fi
}

# Check for grammar and spelling issues (basic checks)
check_grammar_spelling() {
    log_section "Grammar and Spelling Check"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Common misspellings to check
    local misspellings=(
        "recieve:receive"
        "seperate:separate"
        "occured:occurred"
        "existance:existence"
        "sucess:success"
        "sucessful:successful"
    )

    for pair in "${misspellings[@]}"; do
        wrong="${pair%%:*}"
        if grep -qi "$wrong" "$PART3_FILE"; then
            log_fail "Possible misspelling found: '$wrong'"
        fi
    done

    # Check for common grammar issues
    if grep -qi "it's" "$PART3_FILE" && ! grep -q "it is" "$PART3_FILE"; then
        log_info "Tutorial uses contractions (acceptable)"
    fi

    # Check for proper capitalization in headers
    if grep -q "^### Step [0-9]" "$PART3_FILE"; then
        log_pass "Step headers are properly formatted"
    else
        log_fail "Step headers may not be properly formatted"
    fi
}

# Validate code block formatting
validate_code_blocks() {
    log_section "Code Block Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Count code blocks (simplified to avoid backtick parsing issues)
    # Use grep with a simple pattern - count lines starting with ```
    local code_block_lines=0
    if command -v grep &>/dev/null; then
        # Use grep to count lines that start with three backticks
        code_block_lines=$(grep -c '^```' "$PART3_FILE" 2>/dev/null || echo "0")
    else
        # Fallback: simple line-by-line check (limited to first 1000 lines for performance)
        local line_count=0
        while IFS= read -r line && (( line_count < 1000 )); do
            if [[ "${line:0:3}" == "```" ]]; then
                ((code_block_lines++)) || true
            fi
            ((line_count++)) || true
        done < <(head -1000 "$PART3_FILE" 2>/dev/null || cat "$PART3_FILE")
    fi

    log_info "Found $code_block_lines code block markers in tutorial"

    # Check for unclosed code blocks (even number should mean all are closed)
    if (( code_block_lines % 2 == 0 )); then
        log_pass "All code blocks appear to be properly closed"
    else
        log_fail "Possible unclosed code block (odd number of code block markers)"
    fi
}

# Validate links and references
validate_links() {
    log_section "Link and Reference Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Check for broken internal links
    while IFS= read -r link; do
        if [[ "$link" =~ ^\[.*\]\(\./(.*)\)$ ]]; then
            local target="${BASH_REMATCH[1]}"
            local target_path="$TUTORIAL_DIR/learning-paths/$target"
            if [[ -f "$target_path" ]]; then
                log_pass "Link target exists: $target"
            else
                log_fail "Broken link: $target (referenced as ./$target)"
            fi
        fi
    done < <(grep -oE '\[.*\]\(\./.*\)' "$PART3_FILE" || true)

    # Check for references to guide-runner-setup.md
    if grep -q "guide-runner-setup.md" "$PART3_FILE"; then
        local guide_path="$TUTORIAL_DIR/learning-paths/guide-runner-setup.md"
        if [[ -f "$guide_path" ]]; then
            log_pass "Referenced guide-runner-setup.md exists"
        else
            log_fail "Referenced guide-runner-setup.md does not exist"
        fi
    fi
}

# Validate instructions clarity
validate_instructions() {
    log_section "Instruction Clarity Validation"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"

    # Check for placeholder values that need replacement
    if grep -q "ORG_NAME" "$PART3_FILE"; then
        if grep -q "Replace.*ORG_NAME\|ORG_NAME.*GitHub" "$PART3_FILE"; then
            log_pass "ORG_NAME placeholder is explained"
        else
            log_fail "ORG_NAME placeholder may not be clearly explained"
        fi
    fi

    if grep -q "YOUR_REGISTRATION_TOKEN" "$PART3_FILE"; then
        if grep -q "registration token\|Registration token" "$PART3_FILE"; then
            log_pass "Registration token placeholder is explained"
        else
            log_fail "Registration token placeholder may not be clearly explained"
        fi
    fi

    # Check for step numbering consistency
    local step_count=$(grep -c "^### Step [0-9]" "$PART3_FILE" || echo "0")
    log_info "Found $step_count numbered steps in tutorial"

    # Check for prerequisites section
    if grep -q "^## Prerequisites" "$PART3_FILE"; then
        log_pass "Prerequisites section exists"
    else
        log_fail "Prerequisites section missing"
    fi
}

# Validate requirements compliance
validate_requirements() {
    log_section "Requirements Compliance Check"

    TUTORIAL_DIR="${LIQUIBASE_TUTORIAL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    PART3_FILE="$TUTORIAL_DIR/learning-paths/series-part3-cicd.md"
    DESIGN_DOC="$TUTORIAL_DIR/liquibase_course_design.md"

    # Check requirement #11: Naming convention (underscores)
    if grep -q "liquibase_tutorial\|mssql_dev\|mssql_stg\|mssql_prd" "$PART3_FILE"; then
        log_pass "Tutorial uses underscore naming convention (requirement #11)"
    else
        log_fail "Tutorial may not consistently use underscore naming convention"
    fi

    # Check requirement #8: Database name is 'orderdb'
    if grep -q "databaseName=orderdb" "$PART3_FILE"; then
        log_pass "Tutorial uses 'orderdb' as database name (requirement #8)"
    else
        log_fail "Tutorial may not consistently use 'orderdb' database name"
    fi

    # Check requirement #9: Formatted SQL with .mssql.sql extension
    if grep -q "\.mssql\.sql" "$PART3_FILE"; then
        log_pass "Tutorial references .mssql.sql extension (requirement #9)"
    else
        log_fail "Tutorial may not reference .mssql.sql extension"
    fi
}

# Main execution
main() {
    # Ensure log files exist
    touch "$VALIDATION_LOG" "$VALIDATION_REPORT" "$ISSUES_LOG" 2>/dev/null || true

    log "Starting Part 3 CI/CD Tutorial Validation"
    log "Log file: $VALIDATION_LOG"
    log "Report file: $VALIDATION_REPORT"
    log "Issues file: $ISSUES_LOG"

    check_prerequisites
    validate_file_structure
    validate_yaml_syntax
    validate_workflow_syntax
    validate_jdbc_urls
    check_grammar_spelling
    validate_code_blocks
    validate_links
    validate_instructions
    validate_requirements

    # Final summary
    log_section "Validation Summary"
    log "Passed: $PASSED"
    log "Failed: $FAILED"
    log "Skipped: $SKIPPED"
    log "Total Issues: $ISSUES"

    # Update report with summary
    sed -i "s/- \*\*Passed:\*\* 0/- **Passed:** $PASSED/" "$VALIDATION_REPORT"
    sed -i "s/- \*\*Failed:\*\* 0/- **Failed:** $FAILED/" "$VALIDATION_REPORT"
    sed -i "s/- \*\*Skipped:\*\* 0/- **Skipped:** $SKIPPED/" "$VALIDATION_REPORT"
    sed -i "s/- \*\*Issues Found:\*\* 0/- **Issues Found:** $ISSUES/" "$VALIDATION_REPORT"

    echo "" >> "$VALIDATION_REPORT"
    echo "## Detailed Results" >> "$VALIDATION_REPORT"
    echo "" >> "$VALIDATION_REPORT"
    echo '```' >> "$VALIDATION_REPORT"
    tail -100 "$VALIDATION_LOG" >> "$VALIDATION_REPORT"
    echo '```' >> "$VALIDATION_REPORT"

    log "Validation complete. See $VALIDATION_REPORT for full report."
    log "Issues documented in: $ISSUES_LOG"

    if (( FAILED > 0 )); then
        exit 1
    else
        exit 0
    fi
}

main "$@"
