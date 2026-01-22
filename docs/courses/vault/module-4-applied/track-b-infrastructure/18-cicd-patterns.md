# CI/CD patterns

**[← Back to Track B: Infrastructure](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-18-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Integrate Vault with GitHub Actions for secure secret injection
- Configure Jenkins pipelines to authenticate with Vault
- Implement secure secret retrieval patterns in CI/CD workflows
- Apply best practices for Vault authentication in automated pipelines

## Table of contents

- [CI/CD integration overview](#cicd-integration-overview)
- [GitHub Actions integration](#github-actions-integration)
- [Jenkins integration](#jenkins-integration)
- [GitLab CI integration](#gitlab-ci-integration)
- [Security best practices](#security-best-practices)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## CI/CD integration overview

CI/CD pipelines require access to secrets for deployments, but storing secrets in pipeline configurations creates security risks. Vault provides centralized, audited secret management for CI/CD workflows.

### Common CI/CD secret challenges

| Challenge | Traditional Approach | Vault Solution |
|-----------|---------------------|----------------|
| Secret sprawl | Secrets in env vars, files, configs | Centralized secret storage |
| Access control | Pipeline-level permissions | Fine-grained policies |
| Rotation | Manual updates across pipelines | Dynamic secrets, auto-rotation |
| Auditing | Limited visibility | Complete audit trail |
| Secret exposure | Logs, error messages | Response wrapping, TTLs |

### Authentication options for CI/CD

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CI/CD Authentication Methods                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                         Recommended                                   │  │
│   │                                                                       │  │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │  │
│   │  │   AppRole   │    │     JWT     │    │  Cloud IAM  │              │  │
│   │  │             │    │   (OIDC)    │    │ (AWS/GCP/   │              │  │
│   │  │ Role ID +   │    │             │    │  Azure)     │              │  │
│   │  │ Secret ID   │    │ GitHub/     │    │             │              │  │
│   │  │             │    │ GitLab      │    │ Native      │              │  │
│   │  │             │    │ tokens      │    │ workload    │              │  │
│   │  │             │    │             │    │ identity    │              │  │
│   │  └─────────────┘    └─────────────┘    └─────────────┘              │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                        Not Recommended                                │  │
│   │                                                                       │  │
│   │  ┌─────────────┐                                                     │  │
│   │  │ Static      │  Long-lived tokens are security risks               │  │
│   │  │ Tokens      │  Use only if no other option available              │  │
│   │  └─────────────┘                                                     │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## GitHub Actions integration

GitHub Actions can authenticate to Vault using JWT/OIDC tokens or AppRole.

### Method 1: JWT authentication (recommended)

GitHub Actions provides OIDC tokens that Vault can validate directly.

**Vault configuration:**

```bash
# Enable JWT auth for GitHub
vault auth enable -path=github-actions jwt

# Configure JWT auth with GitHub's OIDC provider
vault write auth/github-actions/config \
    bound_issuer="https://token.actions.githubusercontent.com" \
    oidc_discovery_url="https://token.actions.githubusercontent.com"

# Create a role for your repository
vault write auth/github-actions/role/deploy \
    role_type="jwt" \
    bound_audiences="https://github.com/YOUR_ORG" \
    bound_claims_type="glob" \
    bound_claims='{
        "repository": "YOUR_ORG/YOUR_REPO",
        "ref": "refs/heads/main"
    }' \
    user_claim="repository" \
    policies="deploy-policy" \
    ttl="10m" \
    max_ttl="15m"
```

**GitHub Actions workflow:**

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to Vault
        uses: hashicorp/vault-action@v3
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: jwt
          path: github-actions
          role: deploy
          jwtGithubAudience: https://github.com/YOUR_ORG
          secrets: |
            secret/data/deploy/aws access_key | AWS_ACCESS_KEY_ID ;
            secret/data/deploy/aws secret_key | AWS_SECRET_ACCESS_KEY ;
            secret/data/deploy/db password | DB_PASSWORD

      - name: Deploy application
        run: |
          echo "Deploying with credentials..."
          # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DB_PASSWORD are now set
```

### Method 2: AppRole authentication

For environments where JWT isn't available.

**Vault configuration:**

```bash
# Enable AppRole
vault auth enable approle

# Create policy
vault policy write github-deploy - <<EOF
path "secret/data/deploy/*" {
  capabilities = ["read"]
}
EOF

# Create AppRole
vault write auth/approle/role/github-deploy \
    secret_id_ttl=10m \
    token_ttl=10m \
    token_max_ttl=15m \
    policies="github-deploy"

# Get Role ID (store in GitHub secrets)
vault read -field=role_id auth/approle/role/github-deploy/role-id

# Generate Secret ID (store in GitHub secrets)
vault write -f -field=secret_id auth/approle/role/github-deploy/secret-id
```

**GitHub Actions workflow:**

```yaml
# .github/workflows/deploy.yml
name: Deploy with AppRole

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to Vault
        uses: hashicorp/vault-action@v3
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: approle
          roleId: ${{ secrets.VAULT_ROLE_ID }}
          secretId: ${{ secrets.VAULT_SECRET_ID }}
          secrets: |
            secret/data/deploy/aws access_key | AWS_ACCESS_KEY_ID ;
            secret/data/deploy/aws secret_key | AWS_SECRET_ACCESS_KEY

      - name: Deploy
        run: ./deploy.sh
```

### Advanced patterns

**Multi-environment deployment:**

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [staging, production]

    environment: ${{ matrix.environment }}

    steps:
      - uses: hashicorp/vault-action@v3
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: jwt
          path: github-actions
          role: deploy-${{ matrix.environment }}
          secrets: |
            secret/data/${{ matrix.environment }}/app api_key | API_KEY
```

**Using Vault for Terraform:**

```yaml
jobs:
  terraform:
    runs-on: ubuntu-latest

    steps:
      - uses: hashicorp/vault-action@v3
        id: vault
        with:
          url: ${{ secrets.VAULT_ADDR }}
          method: jwt
          path: github-actions
          role: terraform
          exportToken: true  # Export VAULT_TOKEN for Terraform provider

      - name: Terraform Apply
        run: terraform apply -auto-approve
        env:
          VAULT_ADDR: ${{ secrets.VAULT_ADDR }}
          VAULT_TOKEN: ${{ steps.vault.outputs.token }}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Jenkins integration

Jenkins integrates with Vault through plugins or direct API calls.

### Using the HashiCorp Vault Plugin

**Install the plugin:**

1. Navigate to Manage Jenkins → Plugins → Available
2. Search for "HashiCorp Vault"
3. Install and restart Jenkins

**Configure Vault in Jenkins:**

```groovy
// Jenkinsfile with Vault plugin
pipeline {
    agent any

    environment {
        VAULT_ADDR = 'https://vault.example.com:8200'
    }

    stages {
        stage('Deploy') {
            steps {
                withVault(
                    configuration: [
                        vaultUrl: "${VAULT_ADDR}",
                        vaultCredentialId: 'vault-approle',
                        engineVersion: 2
                    ],
                    vaultSecrets: [
                        [
                            path: 'secret/deploy/aws',
                            secretValues: [
                                [envVar: 'AWS_ACCESS_KEY_ID', vaultKey: 'access_key'],
                                [envVar: 'AWS_SECRET_ACCESS_KEY', vaultKey: 'secret_key']
                            ]
                        ],
                        [
                            path: 'secret/deploy/db',
                            secretValues: [
                                [envVar: 'DB_PASSWORD', vaultKey: 'password']
                            ]
                        ]
                    ]
                ) {
                    sh '''
                        echo "Deploying with Vault secrets..."
                        ./deploy.sh
                    '''
                }
            }
        }
    }
}
```

### Using AppRole with Jenkins credentials

**Store AppRole in Jenkins:**

1. Go to Manage Jenkins → Credentials
2. Add "Vault App Role Credential"
3. Enter Role ID and Secret ID

**Jenkinsfile:**

```groovy
pipeline {
    agent any

    stages {
        stage('Get Secrets') {
            steps {
                withCredentials([
                    vaultAppRole(
                        credentialsId: 'vault-approle',
                        path: 'secret/data/app/config',
                        secretValues: [
                            [envVar: 'DB_HOST', vaultKey: 'db_host'],
                            [envVar: 'DB_PASS', vaultKey: 'db_pass']
                        ]
                    )
                ]) {
                    sh 'echo "DB Host: $DB_HOST"'
                }
            }
        }
    }
}
```

### Direct API calls (without plugin)

```groovy
pipeline {
    agent any

    environment {
        VAULT_ADDR = 'https://vault.example.com:8200'
    }

    stages {
        stage('Authenticate') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'vault-role-id', variable: 'ROLE_ID'),
                        string(credentialsId: 'vault-secret-id', variable: 'SECRET_ID')
                    ]) {
                        def response = sh(
                            script: '''
                                curl -s -X POST \
                                    "${VAULT_ADDR}/v1/auth/approle/login" \
                                    -d '{"role_id":"'"${ROLE_ID}"'","secret_id":"'"${SECRET_ID}"'"}'
                            ''',
                            returnStdout: true
                        )
                        def json = readJSON text: response
                        env.VAULT_TOKEN = json.auth.client_token
                    }
                }
            }
        }

        stage('Get Secrets') {
            steps {
                script {
                    def response = sh(
                        script: '''
                            curl -s -H "X-Vault-Token: ${VAULT_TOKEN}" \
                                "${VAULT_ADDR}/v1/secret/data/app/config"
                        ''',
                        returnStdout: true
                    )
                    def json = readJSON text: response
                    env.DB_HOST = json.data.data.db_host
                    env.DB_PASS = json.data.data.db_pass
                }
            }
        }

        stage('Deploy') {
            steps {
                sh './deploy.sh'
            }
        }
    }

    post {
        always {
            // Revoke the token
            sh '''
                curl -s -X POST \
                    -H "X-Vault-Token: ${VAULT_TOKEN}" \
                    "${VAULT_ADDR}/v1/auth/token/revoke-self" || true
            '''
        }
    }
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## GitLab CI integration

GitLab CI supports Vault integration through JWT authentication or HashiCorp's integration.

### JWT authentication with GitLab

**Vault configuration:**

```bash
# Enable JWT auth for GitLab
vault auth enable -path=gitlab jwt

# Configure with GitLab's OIDC
vault write auth/gitlab/config \
    jwks_url="https://gitlab.com/-/jwks" \
    bound_issuer="https://gitlab.com"

# Create role for project
vault write auth/gitlab/role/deploy \
    role_type="jwt" \
    bound_claims='{
        "project_path": "myorg/myproject",
        "ref_protected": "true"
    }' \
    user_claim="user_email" \
    policies="deploy-policy" \
    ttl="15m"
```

**GitLab CI pipeline:**

```yaml
# .gitlab-ci.yml
stages:
  - deploy

deploy:
  stage: deploy
  image: hashicorp/vault:1.15

  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com

  variables:
    VAULT_ADDR: https://vault.example.com:8200

  script:
    # Authenticate with JWT
    - export VAULT_TOKEN=$(vault write -field=token auth/gitlab/login role=deploy jwt=$VAULT_ID_TOKEN)

    # Get secrets
    - export AWS_ACCESS_KEY_ID=$(vault kv get -field=access_key secret/deploy/aws)
    - export AWS_SECRET_ACCESS_KEY=$(vault kv get -field=secret_key secret/deploy/aws)

    # Deploy
    - ./deploy.sh

  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

### Using GitLab's native Vault integration

GitLab Premium/Ultimate includes native Vault integration:

```yaml
# .gitlab-ci.yml
deploy:
  stage: deploy

  secrets:
    DATABASE_PASSWORD:
      vault: production/db/password@secret
      file: false
    AWS_ACCESS_KEY_ID:
      vault: production/aws/access_key@secret
    AWS_SECRET_ACCESS_KEY:
      vault: production/aws/secret_key@secret

  script:
    - echo "Secrets are available as environment variables"
    - ./deploy.sh
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Security best practices

### 1. Use short-lived tokens

```bash
# Configure AppRole with short TTLs
vault write auth/approle/role/cicd \
    token_ttl=5m \
    token_max_ttl=10m \
    secret_id_ttl=10m \
    secret_id_num_uses=1
```

### 2. Implement least privilege policies

```hcl
# Minimal policy for CI/CD
path "secret/data/deploy/+/config" {
  capabilities = ["read"]
}

# Deny access to everything else implicitly
```

### 3. Use response wrapping for sensitive handoffs

```bash
# Wrap the secret ID
vault write -wrap-ttl=120s -f auth/approle/role/cicd/secret-id

# In CI/CD, unwrap and use immediately
WRAPPED_TOKEN="..."
vault unwrap $WRAPPED_TOKEN
```

### 4. Implement audit logging

```bash
# Enable audit logging
vault audit enable file file_path=/var/log/vault/audit.log

# CI/CD operations will be logged with:
# - Timestamp
# - Client token (hashed)
# - Operation performed
# - Request/response data
```

### 5. Rotate secrets regularly

```yaml
# GitHub Actions secret rotation workflow
name: Rotate Vault Secrets

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - name: Generate new Secret ID
        run: |
          # Generate new Secret ID
          NEW_SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/cicd/secret-id)

          # Update GitHub secret (requires GitHub CLI)
          gh secret set VAULT_SECRET_ID --body "$NEW_SECRET_ID"
```

### 6. Never log secrets

```yaml
# BAD - secrets may appear in logs
- run: echo ${{ env.DB_PASSWORD }}

# GOOD - mask secrets
- name: Deploy
  run: ./deploy.sh
  env:
    DB_PASSWORD: ${{ env.DB_PASSWORD }}
```

### 7. Use namespaces for isolation (Enterprise)

```bash
# Create namespace per team/project
vault namespace create team-a

# Configure auth in namespace
vault write -namespace=team-a auth/approle/role/deploy ...
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Docker installed
- GitHub account (for Actions lab) or local Jenkins

### Setup

```bash
# Start Vault dev server
docker run -d --name vault-cicd \
    -p 8200:8200 \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
    hashicorp/vault:1.15

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'
```

### Exercise 1: Configure AppRole for CI/CD

1. Create a CI/CD policy:

   ```bash
   vault policy write cicd-policy - <<EOF
   path "secret/data/cicd/*" {
     capabilities = ["read"]
   }
   EOF
   ```

2. Enable and configure AppRole:

   ```bash
   # Enable AppRole
   vault auth enable approle

   # Create role with CI/CD-appropriate settings
   vault write auth/approle/role/cicd \
       token_policies="cicd-policy" \
       token_ttl=5m \
       token_max_ttl=10m \
       secret_id_ttl=10m \
       secret_id_num_uses=1
   ```

3. Get the credentials:

   ```bash
   # Get Role ID (static, can be shared)
   ROLE_ID=$(vault read -field=role_id auth/approle/role/cicd/role-id)
   echo "Role ID: $ROLE_ID"

   # Generate Secret ID (single-use)
   SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/cicd/secret-id)
   echo "Secret ID: $SECRET_ID"
   ```

4. Create test secrets:

   ```bash
   vault kv put secret/cicd/deploy \
       api_key="sk-test-12345" \
       db_password="supersecret"
   ```

**Observation:** AppRole is configured with short TTLs and single-use Secret IDs for security.

### Exercise 2: Simulate CI/CD authentication

1. Authenticate using AppRole:

   ```bash
   # Login (simulating CI/CD pipeline)
   VAULT_TOKEN=$(vault write -field=token auth/approle/login \
       role_id="$ROLE_ID" \
       secret_id="$SECRET_ID")

   echo "Got token: ${VAULT_TOKEN:0:10}..."
   ```

2. Retrieve secrets:

   ```bash
   # Export token for subsequent commands
   export VAULT_TOKEN

   # Get secrets
   vault kv get secret/cicd/deploy

   # Get specific field
   API_KEY=$(vault kv get -field=api_key secret/cicd/deploy)
   echo "API Key: ${API_KEY:0:8}..."
   ```

3. Try using expired Secret ID:

   ```bash
   # Try to login again with the same Secret ID
   vault write auth/approle/login \
       role_id="$ROLE_ID" \
       secret_id="$SECRET_ID"
   ```

**Observation:** The Secret ID is single-use and fails on second attempt.

### Exercise 3: Create a shell script CI/CD simulation

1. Create a deployment script:

   ```bash
   cat > deploy.sh <<'EOF'
   #!/bin/bash
   set -e

   VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"

   echo "=== CI/CD Deployment Script ==="

   # Step 1: Authenticate to Vault
   echo "Authenticating to Vault..."
   VAULT_TOKEN=$(curl -s -X POST \
       "${VAULT_ADDR}/v1/auth/approle/login" \
       -d "{\"role_id\":\"${ROLE_ID}\",\"secret_id\":\"${SECRET_ID}\"}" \
       | jq -r '.auth.client_token')

   if [ "$VAULT_TOKEN" == "null" ] || [ -z "$VAULT_TOKEN" ]; then
       echo "ERROR: Failed to authenticate"
       exit 1
   fi
   echo "Authentication successful"

   # Step 2: Retrieve secrets
   echo "Retrieving deployment secrets..."
   SECRETS=$(curl -s -H "X-Vault-Token: ${VAULT_TOKEN}" \
       "${VAULT_ADDR}/v1/secret/data/cicd/deploy" \
       | jq -r '.data.data')

   API_KEY=$(echo "$SECRETS" | jq -r '.api_key')
   DB_PASSWORD=$(echo "$SECRETS" | jq -r '.db_password')

   echo "Secrets retrieved successfully"

   # Step 3: Deploy (simulation)
   echo "Deploying application..."
   echo "  API Key: ${API_KEY:0:8}..."
   echo "  DB configured: yes"
   echo "Deployment complete!"

   # Step 4: Revoke token
   echo "Revoking Vault token..."
   curl -s -X POST \
       -H "X-Vault-Token: ${VAULT_TOKEN}" \
       "${VAULT_ADDR}/v1/auth/token/revoke-self"
   echo "Token revoked"

   echo "=== Deployment Finished ==="
   EOF

   chmod +x deploy.sh
   ```

2. Generate new Secret ID and run:

   ```bash
   # Get Role ID
   export ROLE_ID=$(vault read -field=role_id auth/approle/role/cicd/role-id)

   # Generate new Secret ID
   export SECRET_ID=$(vault write -f -field=secret_id auth/approle/role/cicd/secret-id)

   # Run deployment
   ./deploy.sh
   ```

**Observation:** The script authenticates, retrieves secrets, and revokes the token after use.

### Cleanup

```bash
# Stop and remove container
docker stop vault-cicd && docker rm vault-cicd

# Remove script
rm -f deploy.sh
```

---

## Key takeaways

1. **Use JWT/OIDC when available** - GitHub Actions and GitLab CI support OIDC, eliminating the need to store Vault credentials
2. **AppRole for traditional CI/CD** - When OIDC isn't available, AppRole with single-use Secret IDs provides security
3. **Short TTLs are critical** - CI/CD tokens should have minimal lifetimes (5-15 minutes)
4. **Single-use Secret IDs** - Prevent credential reuse if leaked
5. **Always revoke tokens** - Clean up tokens after pipeline completion
6. **Least privilege policies** - CI/CD should only access secrets it needs for deployment
7. **Audit everything** - Enable audit logging to track all CI/CD access to secrets

---

[← Previous: Terraform Provider](./17-terraform-provider.md) | [Back to Track B: Infrastructure](./README.md)
