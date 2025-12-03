#!/bin/bash
set -e

# Script to create GitHub Actions runner configuration
# This script prompts for all necessary values and creates runner.env

echo "=================================="
echo "GitHub Actions Runner Setup"
echo "=================================="
echo ""
echo "This script will help you configure a self-hosted GitHub Actions runner."
echo ""

# Default values
DEFAULT_RUNNER_NAME="liquibase-tutorial-runner"
DEFAULT_RUNNER_LABELS="self-hosted,linux,x64,wsl,docker"
DEFAULT_RUNNER_GROUP="default"
DEFAULT_RUNNER_WORKDIR="/tmp/github-runner"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# runner_config lives one level up from scripts
DEFAULT_CONFIG_DIR="${SCRIPT_DIR%/scripts}/runner_config"
DEFAULT_OUTPUT_FILE_NAME="runner.env.local"

# Prompt for configuration directory (default inside repo)
echo "Where should the configuration file be stored? (Do NOT commit secrets)"
read -p "Configuration directory [${DEFAULT_CONFIG_DIR}]: " CONFIG_DIR
CONFIG_DIR=${CONFIG_DIR:-$DEFAULT_CONFIG_DIR}

# Create directory if it doesn't exist
mkdir -p "${CONFIG_DIR}"
CONFIG_FILE="${CONFIG_DIR}/${DEFAULT_OUTPUT_FILE_NAME}"

echo ""
echo "Step 1: GitHub Repository Information"
echo "--------------------------------------"
echo "Enter your GitHub repository URL (e.g., https://github.com/myorg/myrepo)"
read -p "Repository URL: " REPO_URL

while [[ -z "${REPO_URL}" ]]; do
    echo "❌ Repository URL is required!"
    read -p "Repository URL: " REPO_URL
done

echo ""
echo "Step 2: Runner Registration Token"
echo "----------------------------------"

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "GitHub CLI detected. Would you like to automatically generate a registration token?"
    read -p "Auto-generate token? (y/n) [y]: " AUTO_TOKEN
    AUTO_TOKEN=${AUTO_TOKEN:-y}

    if [[ "${AUTO_TOKEN}" =~ ^[Yy]$ ]]; then
        echo "Generating registration token..."

        # Extract owner and repo from URL
        REPO_PATH=$(echo "${REPO_URL}" | sed -E 's|https://github.com/([^/]+/[^/]+).*|\1|')

        # Generate token using GitHub CLI
        RUNNER_TOKEN=$(gh api --method POST -H "Accept: application/vnd.github+json" \
            "/repos/${REPO_PATH}/actions/runners/registration-token" \
            --jq '.token' 2>/dev/null)

        if [[ -n "${RUNNER_TOKEN}" ]]; then
            echo "✅ Token generated successfully!"
            echo "⚠️  Note: This token expires after 1 hour"
        else
            echo "❌ Failed to generate token automatically."
            echo "Please enter the token manually:"
            read -p "Registration Token: " RUNNER_TOKEN
        fi
    else
        echo "Enter your registration token from: GitHub → Settings → Actions → Runners → New self-hosted runner"
        echo "⚠️  Note: This token expires after 1 hour"
        read -p "Registration Token: " RUNNER_TOKEN
    fi
else
    echo "Enter your registration token from: GitHub → Settings → Actions → Runners → New self-hosted runner"
    echo "⚠️  Note: This token expires after 1 hour"
    echo ""
    echo "💡 Tip: Install GitHub CLI (gh) to auto-generate tokens in the future:"
    echo "   sudo apt install gh"
    read -p "Registration Token: " RUNNER_TOKEN
fi

while [[ -z "${RUNNER_TOKEN}" ]]; do
    echo "❌ Registration token is required!"
    read -p "Registration Token: " RUNNER_TOKEN
done

echo ""
echo "Step 3: Runner Configuration"
echo "----------------------------"
read -p "Runner name [${DEFAULT_RUNNER_NAME}]: " RUNNER_NAME
RUNNER_NAME=${RUNNER_NAME:-$DEFAULT_RUNNER_NAME}

read -p "Runner labels (comma-separated) [${DEFAULT_RUNNER_LABELS}]: " RUNNER_LABELS
RUNNER_LABELS=${RUNNER_LABELS:-$DEFAULT_RUNNER_LABELS}

read -p "Runner group [${DEFAULT_RUNNER_GROUP}]: " RUNNER_GROUP
RUNNER_GROUP=${RUNNER_GROUP:-$DEFAULT_RUNNER_GROUP}

read -p "Runner work directory [${DEFAULT_RUNNER_WORKDIR}]: " RUNNER_WORKDIR
RUNNER_WORKDIR=${RUNNER_WORKDIR:-$DEFAULT_RUNNER_WORKDIR}

# Create configuration file
echo ""
echo "Creating configuration file: ${CONFIG_FILE}"
echo "(File contains a short-lived registration token; NEVER commit it)"

cat > "${CONFIG_FILE}" << EOF
# GitHub Runner Configuration
# Generated on: $(date)

# Your GitHub repository URL
REPO_URL=${REPO_URL}

# Registration token from GitHub (Step 3.1)
RUNNER_TOKEN=${RUNNER_TOKEN}

# Runner name (appears in GitHub)
RUNNER_NAME=${RUNNER_NAME}

# Runner labels (comma-separated)
RUNNER_LABELS=${RUNNER_LABELS}

# Runner group (leave as default)
RUNNER_GROUP=${RUNNER_GROUP}

# Runner work directory
RUNNER_WORKDIR=${RUNNER_WORKDIR}
EOF

echo ""
echo "✅ Configuration file created successfully!"
echo ""
echo "Configuration summary:"
echo "====================="
cat "${CONFIG_FILE}"
echo ""
echo "Next steps:"
echo "1. Review the configuration above"
echo "2. Load and export variables then start via docker-compose:"
echo ""
echo "   source ${CONFIG_FILE}"
echo "   export RUNNER_NAME RUNNER_WORKDIR RUNNER_TOKEN REPO_URL RUNNER_LABELS RUNNER_GROUP"
echo "   cd \"${SCRIPT_DIR%/scripts}/docker\""
echo "   docker-compose --profile runner up -d github_runner"
echo ""
echo "   (Alternative: direct docker run)"
echo "   docker run -d \\"
echo "     --name ${RUNNER_NAME} \\"
echo "     --network liquibase_tutorial \\"
echo "     --restart unless-stopped \\"
echo "     -e RUNNER_NAME=\"${RUNNER_NAME}\" \\"
echo "     -e RUNNER_WORKDIR=\"${RUNNER_WORKDIR}\" \\"
echo "     -e RUNNER_TOKEN=\"${RUNNER_TOKEN}\" \\"
echo "     -e REPO_URL=\"${REPO_URL}\" \\"
echo "     -e RUNNER_LABELS=\"${RUNNER_LABELS}\" \\"
echo "     -e RUNNER_GROUP=\"${RUNNER_GROUP}\" \\"
echo "     -v /var/run/docker.sock:/var/run/docker.sock \\"
echo "     -v ~/github-runner:/tmp/github-runner \\"
echo "     myoung34/github-runner:latest"
echo ""
echo "3. Verify in GitHub: Settings → Actions → Runners"
echo "4. Add the file pattern to .gitignore if not already: runner.env.local"
echo ""
