#!/bin/bash
# Generate MongoDB keyfile for replica set authentication
#
# Usage: ./generate-keyfile.sh <environment> <output_path>
#
# Example:
#   ./generate-keyfile.sh production /secrets/production/mongodb-keyfile

set -e

ENVIRONMENT=${1:-dev}
OUTPUT_PATH=${2:-/tmp/mongodb-keyfile-${ENVIRONMENT}}

echo "Generating MongoDB keyfile..."
echo "  Environment: ${ENVIRONMENT}"
echo "  Output Path: ${OUTPUT_PATH}"
echo ""

# Create directory if needed
mkdir -p "$(dirname "$OUTPUT_PATH")"

# Generate keyfile (756 bytes of base64 = ~1024 bytes before encoding)
# MongoDB requires 6-1024 bytes, base64 only
openssl rand -base64 756 > "$OUTPUT_PATH"

# Set correct permissions (MongoDB requires 400 or 600)
chmod 400 "$OUTPUT_PATH"

echo "✅ Generated keyfile: $OUTPUT_PATH"
echo ""
echo "⚠️  SECURITY WARNINGS:"
echo "  1. NEVER commit this file to source control!"
echo "  2. Distribute securely to all replica set members"
echo "  3. All members must have IDENTICAL keyfile"
echo "  4. Keep backups in secure location"
echo ""
echo "Next steps:"
echo "  1. Copy to all replica set members"
echo "  2. Set ownership: chown mongodb:mongodb ${OUTPUT_PATH}"
echo "  3. Mount in Docker: -v ${OUTPUT_PATH}:/data/mongodb/mongodb-keyfile:ro"
