#!/bin/bash
# Quick backup before making changes
# Usage: ./backup_current.sh <test_name>
# Example: ./backup_current.sh test3

test_name=${1:-"manual_$(date +%s)"}
timestamp=$(date +%Y%m%d_%H%M%S)

mkdir -p archive

echo "Creating backup: ${test_name}_${timestamp}"

if [ -f Dockerfile ]; then
    cp -p Dockerfile "archive/Dockerfile.${test_name}_${timestamp}"
    echo "  ✓ Dockerfile"
fi

if [ -f devcontainer.json ]; then
    cp -p devcontainer.json "archive/devcontainer.json.${test_name}_${timestamp}"
    echo "  ✓ devcontainer.json"
fi

if [ -f postCreate.sh ]; then
    cp -p postCreate.sh "archive/postCreate.sh.${test_name}_${timestamp}"
    echo "  ✓ postCreate.sh"
else
    echo "  - postCreate.sh (not present)"
fi

echo ""
echo "✅ Backup complete: ${test_name}_${timestamp}"
echo ""
echo "To restore this version later:"
echo "  ./restore_version.sh ${test_name}_${timestamp}"
