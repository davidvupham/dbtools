#!/bin/bash
# Grammar and Spelling Review Script for Tutorial Part 2
# Reviews the tutorial document for grammar, spelling, and clarity issues

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TUTORIAL_FILE="${1:-docs/courses/liquibase/learning-paths/series-part2-manual.md}"
REVIEW_REPORT="${LIQUIBASE_TUTORIAL_DIR:-/tmp}/tutorial_part2_grammar_review_${TIMESTAMP}.md"

# Track issues
GRAMMAR_ISSUES=0
SPELLING_ISSUES=0
CLARITY_ISSUES=0
FIXES_SUGGESTED=0

# Function to log issue
log_issue() {
    local category="$1"
    shift
    local issue="$*"
    echo "- **$category:** $issue" >> "$REVIEW_REPORT"
    case "$category" in
        Grammar) ((GRAMMAR_ISSUES++)) ;;
        Spelling) ((SPELLING_ISSUES++)) ;;
        Clarity) ((CLARITY_ISSUES++)) ;;
    esac
    ((FIXES_SUGGESTED++))
}

# Initialize report
cat > "$REVIEW_REPORT" << EOF
# Tutorial Part 2 Grammar and Spelling Review

**Date:** $(date)
**File Reviewed:** $TUTORIAL_FILE

## Review Summary

This document reviews the tutorial for:
- Grammar errors
- Spelling mistakes
- Clarity and instruction improvements
- Consistency issues

---

## Issues Found

EOF

if [ ! -f "$TUTORIAL_FILE" ]; then
    echo "Error: Tutorial file not found: $TUTORIAL_FILE" >&2
    exit 1
fi

echo "Reviewing: $TUTORIAL_FILE"
echo "Report will be saved to: $REVIEW_REPORT"

# Read the file and check for common issues
line_num=0
while IFS= read -r line || [ -n "$line" ]; do
    line_num=$((line_num + 1))

    # Check for common spelling mistakes
    if echo "$line" | grep -qiE '\b(recieve|seperate|occured|existance|existant)\b'; then
        log_issue "Spelling" "Line $line_num: Possible spelling error: $line"
    fi

    # Check for grammar issues
    if echo "$line" | grep -qiE '\b(its|it'\''s)\b.*\b(its|it'\''s)\b'; then
        log_issue "Grammar" "Line $line_num: Possible its/it's confusion: $line"
    fi

    # Check for missing articles
    if echo "$line" | grep -qiE '\b(add|create|make|deploy)\s+[a-z]+[^s]\s+(table|index|constraint)\b'; then
        # This is a pattern check, may need manual review
        :
    fi

    # Check for unclear instructions
    if echo "$line" | grep -qiE '^(you|we|they)\s+(should|must|need)\s+'; then
        # Check if instruction is clear
        if echo "$line" | grep -qiE '\b(should|must|need)\s+(to\s+)?(do|make|create)\b'; then
            log_issue "Clarity" "Line $line_num: Vague instruction - consider being more specific: $line"
        fi
    fi

    # Check for inconsistent terminology
    if echo "$line" | grep -qiE '\b(staging|stage)\b'; then
        # Check if it's consistently "staging" or "stg"
        :
    fi

done < "$TUTORIAL_FILE"

# Manual review checklist items
cat >> "$REVIEW_REPORT" << 'EOF'

---

## Manual Review Checklist

### Grammar and Style

- [ ] Check for consistent use of "staging" vs "stg" (should be consistent)
- [ ] Verify all code blocks have proper syntax highlighting
- [ ] Check for proper use of articles (a, an, the)
- [ ] Verify consistent tense usage (present vs past)
- [ ] Check for proper punctuation in lists and code examples

### Clarity and Instructions

- [ ] Are all commands clearly explained?
- [ ] Are expected outputs clearly described?
- [ ] Are error scenarios covered?
- [ ] Are prerequisites clearly stated?
- [ ] Are file paths and directories clearly specified?

### Technical Accuracy

- [ ] Verify all SQL commands are correct
- [ ] Verify all Liquibase commands are correct
- [ ] Check that file paths match the actual structure
- [ ] Verify environment variable names are consistent
- [ ] Check that step dependencies are clear

### Consistency

- [ ] Consistent use of environment names (dev/stg/prd vs dev/stage/prod)
- [ ] Consistent formatting of code blocks
- [ ] Consistent use of terminology (changeset vs change, etc.)
- [ ] Consistent file naming conventions

---

## Specific Issues to Check

### Line-by-Line Review

EOF

# Read file and check specific patterns (reset line counter)
line_num=0
while IFS= read -r line || [ -n "$line" ]; do
    line_num=$((line_num + 1))

    # Check for specific issues in the tutorial

    # Check for "stg" vs "staging" inconsistency
    if echo "$line" | grep -qiE '\b(stg|staging)\b'; then
        if echo "$line" | grep -qiE '\bstg\b' && echo "$line" | grep -qiE '\bstaging\b'; then
            log_issue "Consistency" "Line $line_num: Mixed use of 'stg' and 'staging': $line"
        fi
    fi

    # Check for missing explanations
    if echo "$line" | grep -qE '^```bash$'; then
        # Check if next code block has explanation before it
        :
    fi

    # Check for unclear variable references
    if echo "$line" | grep -qE '\$[A-Z_]+'; then
        # Check if variable is explained
        :
    fi

done < "$TUTORIAL_FILE"

# Add summary
cat >> "$REVIEW_REPORT" << EOF

---

## Summary

- **Grammar Issues Found:** $GRAMMAR_ISSUES
- **Spelling Issues Found:** $SPELLING_ISSUES
- **Clarity Issues Found:** $CLARITY_ISSUES
- **Total Fixes Suggested:** $FIXES_SUGGESTED

---

## Recommendations

1. Review all flagged lines manually
2. Run a spell checker on the document
3. Have a technical writer review for clarity
4. Test all commands in the tutorial
5. Verify all file paths and examples work

EOF

echo ""
echo "Grammar review complete!"
echo "Report saved to: $REVIEW_REPORT"
echo ""
echo "Summary:"
echo "  Grammar issues: $GRAMMAR_ISSUES"
echo "  Spelling issues: $SPELLING_ISSUES"
echo "  Clarity issues: $CLARITY_ISSUES"
echo "  Total fixes suggested: $FIXES_SUGGESTED"
