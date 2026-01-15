#!/usr/bin/env bash
# Cleanup script for Liquibase course - Remove files not used by Part 1 and Part 2
# This script removes internal documentation, Part 3 materials, archive files,
# and validation artifacts that are not needed for the user-facing tutorials.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COURSE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "========================================"
echo "Liquibase Course Cleanup Script"
echo "Remove files NOT used by Part 1 and Part 2"
echo "========================================"
echo
echo -e "${CYAN}Course directory:${NC} $COURSE_ROOT"
echo

# Arrays to track what will be deleted
DIRS_TO_DELETE=(
    # Archive directories
    "learning-paths/archive"
    "scripts/archive"
    "sql/archive"
    # Part 3 and CI/CD materials
    "runner_config"
    # Validation artifacts (internal testing)
    "validation"
)

FILES_TO_DELETE=(
    # Internal documentation (not user-facing)
    "BEST_PRACTICES_MODULARITY.md"
    "REFACTORING_SUMMARY.md"
    "architecture.md"
    "liquibase_course_design.md"
    "naming_conventions.md"
    "unused_materials_audit.md"

    # Part 3 and supplements (not Part 1/2)
    "learning-paths/series-part3-cicd.md"
    "learning-paths/tutorial-supplement-end-to-end-pipeline.md"
    "learning-paths/tutorial-supplement-runner-setup.md"

    # Part 3 scripts
    "scripts/setup-github-runner-config.sh"
    "scripts/validate_part3_cicd.sh"
    "scripts/verify-self-hosted-env.sh"

    # Internal/development scripts
    "scripts/build_container_image.sh"
    "scripts/deploy_liquibase_baseline.sh"
    "scripts/manual_review_part2.md"
    "scripts/review_tutorial_grammar.sh"
    "scripts/setup_environment.sh"
    "scripts/sqlcmd_tutorial.sh"
    "scripts/validate_tutorial.sh"
    "scripts/validate_tutorial_full.sh"
    "scripts/validate_tutorial_part2.sh"
)

# Function to check if dry run
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" || "${1:-}" == "-n" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}DRY RUN MODE - No files will be deleted${NC}"
    echo
fi

# Show what will be deleted
echo "----------------------------------------"
echo "Directories to delete:"
echo "----------------------------------------"
for dir in "${DIRS_TO_DELETE[@]}"; do
    full_path="$COURSE_ROOT/$dir"
    if [[ -d "$full_path" ]]; then
        file_count=$(find "$full_path" -type f 2>/dev/null | wc -l)
        echo -e "  ${RED}✗${NC} $dir/ ($file_count files)"
    else
        echo -e "  ${YELLOW}○${NC} $dir/ (not found)"
    fi
done
echo

echo "----------------------------------------"
echo "Files to delete:"
echo "----------------------------------------"
for file in "${FILES_TO_DELETE[@]}"; do
    full_path="$COURSE_ROOT/$file"
    if [[ -f "$full_path" ]]; then
        echo -e "  ${RED}✗${NC} $file"
    else
        echo -e "  ${YELLOW}○${NC} $file (not found)"
    fi
done
echo

# Count items to delete
dirs_found=0
files_found=0
for dir in "${DIRS_TO_DELETE[@]}"; do
    [[ -d "$COURSE_ROOT/$dir" ]] && ((dirs_found++)) || true
done
for file in "${FILES_TO_DELETE[@]}"; do
    [[ -f "$COURSE_ROOT/$file" ]] && ((files_found++)) || true
done

if [[ $dirs_found -eq 0 && $files_found -eq 0 ]]; then
    echo -e "${GREEN}Nothing to delete - all cleanup already done!${NC}"
    exit 0
fi

echo "----------------------------------------"
echo -e "Found: ${RED}$dirs_found directories${NC} and ${RED}$files_found files${NC} to delete"
echo "----------------------------------------"
echo

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}Dry run complete. Run without --dry-run to delete files.${NC}"
    exit 0
fi

# Prompt for confirmation
echo -e "${YELLOW}WARNING: This will permanently delete the above files and directories.${NC}"
read -p "Are you sure you want to continue? (y/N): " -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Delete directories
echo "Deleting directories..."
for dir in "${DIRS_TO_DELETE[@]}"; do
    full_path="$COURSE_ROOT/$dir"
    if [[ -d "$full_path" ]]; then
        rm -rf "$full_path"
        echo -e "  ${GREEN}✓${NC} Deleted $dir/"
    fi
done

# Delete files
echo "Deleting files..."
for file in "${FILES_TO_DELETE[@]}"; do
    full_path="$COURSE_ROOT/$file"
    if [[ -f "$full_path" ]]; then
        rm -f "$full_path"
        echo -e "  ${GREEN}✓${NC} Deleted $file"
    fi
done

echo
echo "========================================"
echo -e "${GREEN}Cleanup Complete${NC}"
echo "========================================"
echo
echo "The following files remain for Part 1 and Part 2:"
echo "  - README.md, course_overview.md, quick_reference.md"
echo "  - glossary.md, troubleshooting.md"
echo "  - learning-paths/series-part1-baseline.md"
echo "  - learning-paths/series-part2-manual.md"
echo "  - learning-paths/tutorial-supplement-drift.md"
echo "  - docker/ (all container definitions)"
echo "  - scripts/ (Part 1 and Part 2 scripts)"
echo "  - sql/ (SQL files, no archive)"
echo
echo "Run 'git status' to see all changes."
