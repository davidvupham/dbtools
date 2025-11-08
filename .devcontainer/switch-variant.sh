#!/bin/bash
# Switch between Red Hat and Ubuntu dev container variants
# Usage: ./switch-variant.sh [redhat|ubuntu]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT="${1:-}"

if [ -z "$VARIANT" ]; then
    echo "Usage: ./switch-variant.sh [redhat|ubuntu]"
    echo ""
    echo "Current variant:"
    if [ -L "$SCRIPT_DIR/devcontainer.json" ]; then
        readlink "$SCRIPT_DIR/devcontainer.json"
    elif [ -f "$SCRIPT_DIR/devcontainer.json" ]; then
        echo "  Regular file (not a symlink)"
    else
        echo "  Not configured"
    fi
    exit 1
fi

case "$VARIANT" in
    redhat|red-hat|rh)
        DEVCONTAINER_TARGET="redhat/devcontainer.json"
        DOCKERFILE_TARGET="redhat/Dockerfile"
        VARIANT_NAME="Red Hat"
        ;;
    ubuntu|ub)
        DEVCONTAINER_TARGET="ubuntu/devcontainer.json"
        DOCKERFILE_TARGET="ubuntu/Dockerfile"
        VARIANT_NAME="Ubuntu"
        ;;
    *)
        echo "Error: Unknown variant '$VARIANT'"
        echo "Usage: ./switch-variant.sh [redhat|ubuntu]"
        exit 1
        ;;
esac

# Remove existing devcontainer.json if it exists
if [ -e "$SCRIPT_DIR/devcontainer.json" ]; then
    rm "$SCRIPT_DIR/devcontainer.json"
    echo "Removed existing devcontainer.json"
fi

# Remove existing Dockerfile if it exists
if [ -e "$SCRIPT_DIR/Dockerfile" ]; then
    rm "$SCRIPT_DIR/Dockerfile"
    echo "Removed existing Dockerfile"
fi

# Create symlinks
ln -s "$DEVCONTAINER_TARGET" "$SCRIPT_DIR/devcontainer.json"
ln -s "$DOCKERFILE_TARGET" "$SCRIPT_DIR/Dockerfile"

echo "✓ Switched to $VARIANT_NAME variant"
echo "  devcontainer.json -> $DEVCONTAINER_TARGET"
echo "  Dockerfile -> $DOCKERFILE_TARGET"
echo ""
echo "Next steps:"
echo "  1. Rebuild the dev container in Cursor"
echo "  2. Or run: cursor ."
