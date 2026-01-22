#!/bin/bash
# HashiCorp Vault Course - Link Validator
#
# This script validates all internal markdown links in the course.
#
# Usage:
#   ./validate-links.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COURSE_DIR="${SCRIPT_DIR}/.."
ERRORS=0
WARNINGS=0

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARNINGS++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((ERRORS++))
}

validate_markdown_links() {
    print_header "Validating Markdown Links"

    local total_files=0
    local total_links=0

    # Find all markdown files
    while IFS= read -r -d '' file; do
        ((total_files++))
        local file_dir=$(dirname "$file")

        # Extract markdown links [text](path)
        while IFS= read -r link; do
            ((total_links++))

            # Skip external links, anchors only, and images
            if [[ "$link" =~ ^https?:// ]] || [[ "$link" =~ ^# ]] || [[ "$link" =~ \.(png|jpg|jpeg|gif|svg)$ ]]; then
                continue
            fi

            # Remove anchor from link
            local link_path="${link%%#*}"

            # Skip empty paths (anchor-only links)
            if [ -z "$link_path" ]; then
                continue
            fi

            # Resolve relative path
            local full_path
            if [[ "$link_path" = /* ]]; then
                full_path="$link_path"
            else
                full_path="$file_dir/$link_path"
            fi

            # Normalize path
            full_path=$(realpath -m "$full_path" 2>/dev/null || echo "$full_path")

            # Check if file exists
            if [ ! -f "$full_path" ]; then
                print_error "Broken link in $file:"
                echo "         Link: $link"
                echo "         Expected: $full_path"
            fi
        done < <(grep -oP '\]\(\K[^)]+' "$file" 2>/dev/null || true)

    done < <(find "$COURSE_DIR" -name "*.md" -type f -print0)

    echo ""
    echo "Scanned $total_files files, $total_links links"
}

validate_images() {
    print_header "Validating Image References"

    while IFS= read -r -d '' file; do
        local file_dir=$(dirname "$file")

        # Extract image references ![alt](path)
        while IFS= read -r img; do
            # Skip external images
            if [[ "$img" =~ ^https?:// ]]; then
                continue
            fi

            # Skip badge URLs
            if [[ "$img" =~ img\.shields\.io ]]; then
                continue
            fi

            # Resolve relative path
            local full_path
            if [[ "$img" = /* ]]; then
                full_path="$img"
            else
                full_path="$file_dir/$img"
            fi

            # Check if file exists
            if [ ! -f "$full_path" ]; then
                print_warning "Missing image in $file:"
                echo "           Image: $img"
            fi
        done < <(grep -oP '!\[[^\]]*\]\(\K[^)]+' "$file" 2>/dev/null || true)

    done < <(find "$COURSE_DIR" -name "*.md" -type f -print0)
}

validate_code_blocks() {
    print_header "Validating Code Block Languages"

    local unknown_languages=()
    local known_languages="bash sh shell python py hcl json yaml yml sql dockerfile terraform go javascript js typescript ts markdown md xml html css plaintext text console output"

    while IFS= read -r -d '' file; do
        # Find code blocks with language specifiers
        while IFS= read -r lang; do
            # Check if language is known
            if ! echo "$known_languages" | grep -qw "$lang"; then
                if [[ ! " ${unknown_languages[*]} " =~ " ${lang} " ]]; then
                    unknown_languages+=("$lang")
                    print_warning "Unknown code block language '$lang' in $file"
                fi
            fi
        done < <(grep -oP '```\K\w+' "$file" 2>/dev/null || true)

    done < <(find "$COURSE_DIR" -name "*.md" -type f -print0)
}

check_navigation() {
    print_header "Checking Navigation Structure"

    # Check each module has a README
    for module_dir in "$COURSE_DIR"/module-*/; do
        if [ -d "$module_dir" ]; then
            if [ ! -f "${module_dir}README.md" ]; then
                print_error "Missing README.md in $module_dir"
            else
                print_success "Found README.md in $(basename "$module_dir")"
            fi
        fi
    done

    # Check main course README exists
    if [ ! -f "$COURSE_DIR/README.md" ]; then
        print_error "Missing main course README.md"
    else
        print_success "Found main course README.md"
    fi
}

print_summary() {
    print_header "Validation Summary"

    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        print_success "All validations passed!"
    else
        if [ $ERRORS -gt 0 ]; then
            print_error "$ERRORS errors found"
        fi
        if [ $WARNINGS -gt 0 ]; then
            print_warning "$WARNINGS warnings found"
        fi
    fi

    exit $ERRORS
}

# Main execution
main() {
    print_header "Vault Course - Link Validator"

    validate_markdown_links
    validate_images
    validate_code_blocks
    check_navigation
    print_summary
}

main "$@"
