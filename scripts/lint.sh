#!/bin/bash
# Ruff Linting Script for Snowflake Monitoring Project
# Usage: ./lint.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
FIX=false
FORMAT=false
STATS=false
WATCH=false
FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --format)
            FORMAT=true
            shift
            ;;
        --stats)
            STATS=true
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        --file)
            FILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Ruff Linting Script"
            echo ""
            echo "Usage: ./lint.sh [options]"
            echo ""
            echo "Options:"
            echo "  --fix       Auto-fix issues"
            echo "  --format    Format code"
            echo "  --stats     Show statistics"
            echo "  --watch     Watch mode"
            echo "  --file FILE Lint specific file"
            echo "  --help      Show this help"
            echo ""
            echo "Examples:"
            echo "  ./lint.sh                    # Check for issues"
            echo "  ./lint.sh --fix              # Auto-fix issues"
            echo "  ./lint.sh --format           # Format code"
            echo "  ./lint.sh --fix --format     # Fix and format"
            echo "  ./lint.sh --stats            # Show statistics"
            echo "  ./lint.sh --file myfile.py   # Lint specific file"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo -e "${RED}Error: ruff is not installed${NC}"
    echo "Install with: pip install ruff"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Ruff Linting - Snowflake Monitoring  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Set target
TARGET="."
if [ -n "$FILE" ]; then
    TARGET="$FILE"
    echo -e "${YELLOW}Target: $FILE${NC}"
else
    echo -e "${YELLOW}Target: Entire project${NC}"
fi
echo ""

# Watch mode
if [ "$WATCH" = true ]; then
    echo -e "${BLUE}Starting watch mode...${NC}"
    ruff check --watch "$TARGET"
    exit 0
fi

# Run linting
if [ "$FIX" = true ]; then
    echo -e "${GREEN}Running Ruff with auto-fix...${NC}"
    ruff check --fix "$TARGET"
else
    echo -e "${GREEN}Running Ruff check...${NC}"
    if ruff check "$TARGET"; then
        echo -e "${GREEN}✓ No issues found!${NC}"
    else
        echo -e "${YELLOW}⚠ Issues found (see above)${NC}"
    fi
fi

echo ""

# Show statistics
if [ "$STATS" = true ]; then
    echo -e "${BLUE}Statistics:${NC}"
    ruff check "$TARGET" --statistics
    echo ""
fi

# Format code
if [ "$FORMAT" = true ]; then
    echo -e "${GREEN}Formatting code...${NC}"
    ruff format "$TARGET"
    echo -e "${GREEN}✓ Code formatted${NC}"
    echo ""
fi

# Summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            Linting Complete            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Quick commands:${NC}"
echo "  ./lint.sh --fix              # Auto-fix issues"
echo "  ./lint.sh --format           # Format code"
echo "  ./lint.sh --fix --format     # Fix and format"
echo "  ./lint.sh --stats            # Show statistics"
echo ""
