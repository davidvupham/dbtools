#!/bin/bash
# compare_directories.sh
# 
# Description:
#   Traverses recursively a source directory to compare with a destination directory.
#   Identifies:
#   1. Files that are different.
#   2. Files in source that are not in target.
#   3. Files in target that are not in source.
#
# Usage:
#   ./compare_directories.sh <source_directory> <target_directory>

set -o nounset
set -o pipefail

# Check for correct number of arguments
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <source_directory> <target_directory>"
    exit 1
fi

# Get absolute paths
SOURCE_DIR=$(readlink -f "$1")
TARGET_DIR=$(readlink -f "$2")

# Validate directories
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist."
    exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Target directory '$TARGET_DIR' does not exist."
    exit 1
fi

echo "=========================================================="
echo "Comparing directories recursively:"
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo "=========================================================="
echo ""

# Run diff recursively (-r) and concisely (-q)
# diff exits with status 1 if differences are found, so we force success with "|| true" to continue script.
DIFF_OUTPUT=$(diff -rq "$SOURCE_DIR" "$TARGET_DIR" || true)

# 1. Identify a list of files that are different.
echo "1. Files that are different (content mismatch):"
echo "------------------------------------------------"
# Output format: "Files <path1> and <path2> differ"
# We extract the line, then remove the "Files " prefix and the " and ... differ" suffix to get the key file path.
# We then strip the source directory prefix to show a relative path.
DIFFERENTIALS=$(echo "$DIFF_OUTPUT" | grep "^Files .* differ$" || true)

if [[ -n "$DIFFERENTIALS" ]]; then
    echo "$DIFFERENTIALS" | sed -E "s|^Files $SOURCE_DIR/||" | sed -E "s| and .* differ$||"
else
    echo "None"
fi
echo ""

# 2. Identify a list of files in source that is not in target
echo "2. Files in Source but not in Target:"
echo "------------------------------------------------"
# Output format: "Only in <directory>: <filename>"
# We filter for lines starting with "Only in $SOURCE_DIR"
ONLY_IN_SOURCE=$(echo "$DIFF_OUTPUT" | grep "^Only in $SOURCE_DIR" || true)

if [[ -n "$ONLY_IN_SOURCE" ]]; then
    # Transform "Only in /path/to/src/subdir: file" -> "/path/to/src/subdir/file" -> "subdir/file"
    echo "$ONLY_IN_SOURCE" | sed -E "s|^Only in ||" | sed -E "s|: |/|" | sed -E "s|^$SOURCE_DIR/||"
else
    echo "None"
fi
echo ""

# 3. Identify a list of files in target that is not in the source
echo "3. Files in Target but not in Source:"
echo "------------------------------------------------"
# Output format: "Only in <directory>: <filename>"
# We filter for files in the TARGET directory path
ONLY_IN_TARGET=$(echo "$DIFF_OUTPUT" | grep "^Only in $TARGET_DIR" || true)

if [[ -n "$ONLY_IN_TARGET" ]]; then
    # Transform "Only in /path/to/tgt/subdir: file" -> "/path/to/tgt/subdir/file" -> "subdir/file"
    echo "$ONLY_IN_TARGET" | sed -E "s|^Only in ||" | sed -E "s|: |/|" | sed -E "s|^$TARGET_DIR/||"
else
    echo "None"
fi
echo ""
