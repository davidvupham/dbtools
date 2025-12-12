# Configure Corporate Docker Registry

## Security Policy

To ensure security, compliance, and caching efficiency, **all Docker images must be pulled via the corporate JFrog registry**. Direct access to external registries (like Docker Hub) is blocked or discouraged. The corporate registry acts as a secure proxy for these external sources.

To comply with this policy, your local Docker client must be configured to authenticate with the corporate JFrog instance.

## Requirement

You must have a `config.json` file in your `~/.docker/` directory (Windows: `$HOME\.docker\config.json`) that contains valid authentication credentials for the corporate registry.

## Setup Instructions

### Step 1: Generate Credentials

1.  Navigate to the **Corporate JFrog Manager Setup** page:
    *   **URL**: `https://<jfrog-manager-url>/setup` *(Replace `<jfrog-manager-url>` with the actual corporate JFrog domain)*
2.  Follow the instructions to generate a **Personal Access Token (PAT)** (also referred to as an Identity Token).
3.  Copy this token. You will need it for the next step.

### Step 2: Configure Docker Client

Run the following command in your terminal using the corporate registry address `<jfrog-package-manager-service-url>`. Paste your token when prompted for the password.

```bash
docker login <jfrog-package-manager-service-url>
# Username: <your-username>
# Password: <paste-your-token-here>
```

This command automatically creates or updates your `~/.docker/config.json` file with the required credentials. Manual editing of this file is not recommended.
