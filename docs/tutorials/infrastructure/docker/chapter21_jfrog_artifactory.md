# Chapter 21: JFrog Artifactory as Docker Registry

## Introduction

JFrog Artifactory is an enterprise-grade universal artifact repository that supports Docker images alongside other package types (Maven, npm, PyPI, NuGet, etc.). It offers advanced features like fine-grained access control, replication, high availability, and comprehensive auditing - making it ideal for organizations with strict compliance and security requirements.

**What you'll learn**:
- What is JFrog Artifactory and why use it for Docker images
- How to set up and configure Artifactory for Docker
- Authentication and access control
- Pushing and pulling Docker images
- Repository types (local, remote, virtual)
- Scanning for vulnerabilities
- Best practices for enterprise Docker registry management
- Integration with CI/CD pipelines

## What is JFrog Artifactory?

**JFrog Artifactory** is a universal binary repository manager that serves as a single source of truth for all your artifacts, including Docker images.

### Why Use Artifactory for Docker?

#### 1. **Universal Repository**
- Store Docker images alongside Maven, npm, PyPI, etc.
- Single authentication and access control system
- Unified view of all artifacts

#### 2. **Enterprise Features**
- Fine-grained access control (RBAC)
- Replication across data centers
- High availability and disaster recovery
- Comprehensive audit logs
- Retention policies
- Storage optimization

#### 3. **Security and Compliance**
- Vulnerability scanning (JFrog Xray integration)
- License compliance
- Artifact provenance tracking
- Immutable artifacts (prevent overwrites)
- Content filtering and validation

#### 4. **Performance**
- Local caching of remote registries (Docker Hub, etc.)
- Faster builds (cache layers)
- Bandwidth savings
- Global CDN support

#### 5. **CI/CD Integration**
- Webhooks for automation
- Build info tracking
- Promotion workflows
- Integration with Jenkins, GitLab CI, GitHub Actions, etc.

### Artifactory vs. Other Registries

| Feature | JFrog Artifactory | Docker Hub | Harbor | AWS ECR |
|---------|-------------------|------------|--------|---------|
| **Multi-format support** | ✅ 30+ formats | ❌ Docker only | ❌ Docker/Helm | ❌ Docker only |
| **Self-hosted** | ✅ Yes | ❌ SaaS only | ✅ Yes | ❌ AWS only |
| **Fine-grained RBAC** | ✅ Advanced | ⚠️ Basic | ✅ Advanced | ⚠️ IAM-based |
| **Replication** | ✅ Multi-site | ❌ No | ✅ Yes | ⚠️ Limited |
| **Vulnerability scanning** | ✅ Xray | ⚠️ Limited | ✅ Trivy | ✅ ECR Scanning |
| **Enterprise support** | ✅ Yes | ⚠️ Paid tiers | ⚠️ Community/paid | ✅ AWS Support |
| **Cost** | $$$ Enterprise | $ Free/Pro | Free (OSS) | $ Pay-per-use |

---

## Artifactory Repository Types

Artifactory uses three repository types:

### 1. **Local Repositories**

**Purpose**: Store your own artifacts (images you build).

**Use cases**:
- Internal applications
- Custom base images
- Snapshots and releases

**Example**:
- `docker-local` - Store production images
- `docker-dev-local` - Store development images
- `docker-snapshots` - Store CI/CD build snapshots

### 2. **Remote Repositories**

**Purpose**: Proxy and cache external registries (Docker Hub, etc.).

**Benefits**:
- Faster pulls (local cache)
- Bandwidth savings
- Protection against external registry outages
- Control over what can be pulled

**Example**:
- `docker-hub-remote` - Caches Docker Hub images
- `gcr-remote` - Caches Google Container Registry
- `quay-remote` - Caches Quay.io images

### 3. **Virtual Repositories**

**Purpose**: Aggregate multiple repositories behind a single URL.

**Benefits**:
- Single endpoint for developers
- Simplifies configuration
- Enables repository precedence (check local first, then remote)

**Example**:
```
docker-virtual
  ├── docker-local (check first)
  ├── docker-dev-local
  └── docker-hub-remote (fallback)
```

**Workflow**:
1. Developer pulls `artifactory.company.com/docker/nginx:latest`
2. Artifactory checks `docker-local` (not found)
3. Artifactory checks `docker-hub-remote` (found, downloads and caches)
4. Returns image to developer
5. Next pull is instant (served from cache)

---

## Setting Up Artifactory for Docker

### Installation Options

#### Option 1: Docker (Quickstart)

**Run Artifactory in Docker** (for testing/development):

```bash
# Create directories for persistence
mkdir -p ~/artifactory_data

# Run Artifactory
docker run -d \
  --name artifactory \
  -p 8081:8081 \
  -p 8082:8082 \
  -v ~/artifactory_data:/var/opt/jfrog/artifactory \
  releases-docker.jfrog.io/jfrog/artifactory-oss:latest

# Wait for startup (may take 2-3 minutes)
docker logs -f artifactory

# Access UI: http://localhost:8081
# Default credentials: admin / password
```

**⚠️ Note**: Change the admin password on first login!

#### Option 2: Kubernetes (Production)

```yaml
# Using Helm chart
helm repo add jfrog https://charts.jfrog.io
helm repo update

# Install Artifactory
helm install artifactory jfrog/artifactory \
  --set artifactory.persistence.enabled=true \
  --set artifactory.persistence.size=100Gi \
  --set postgresql.enabled=true
```

#### Option 3: Cloud (JFrog SaaS)

Sign up at [jfrog.com](https://jfrog.com) for a cloud-hosted instance.

### Configuring Docker Repository

**Step 1: Create a Local Docker Repository**

1. Login to Artifactory UI: `http://your-artifactory:8081`
2. Admin → Repositories → Local → New Local Repository
3. Select: **Docker**
4. Repository Key: `docker-local`
5. Click **Save & Finish**

**Step 2: Create a Remote Docker Repository** (cache Docker Hub)

1. Admin → Repositories → Remote → New Remote Repository
2. Select: **Docker**
3. Repository Key: `docker-hub-remote`
4. URL: `https://registry-1.docker.io/`
5. Click **Test** to verify connectivity
6. Click **Save & Finish**

**Step 3: Create a Virtual Docker Repository**

1. Admin → Repositories → Virtual → New Virtual Repository
2. Select: **Docker**
3. Repository Key: `docker`
4. Select repositories to include:
   - ✓ `docker-local`
   - ✓ `docker-hub-remote`
5. Set Default Deployment Repository: `docker-local`
6. Click **Save & Finish**

**Step 4: Enable Docker API**

1. Admin → Artifactory → General
2. Scroll to **Docker Settings**
3. Enable: **Docker API**
4. Set **Port**: `8082` (or your chosen port)
5. Click **Save**

**Your Artifactory is now ready for Docker!**

---

## Authentication and Access Control

### Authenticating Docker CLI to Artifactory

#### Method 1: Using Username/Password

```bash
# Login to your Artifactory instance
docker login your-artifactory.jfrog.io

# Enter your Artifactory username and password
Username: myuser
Password: ********
Login Succeeded
```

#### Method 2: Using Identity Token (Recommended)

**Generate an identity token** (safer than using password):

1. Artifactory UI → User Profile (click your username)
2. Generate an Identity Token
3. Copy the token

**Login with token**:

```bash
echo $JFROG_TOKEN | docker login your-artifactory.jfrog.io -u myuser --password-stdin
```

#### Method 3: Using Access Token (Scoped)

**Generate an access token** with limited scope:

1. Artifactory UI → Administration → User Management → Access Tokens
2. Click **Generate Token**
3. Scope: `api:*` (or specific scopes)
4. Expiry: Set expiration
5. Copy token

**Login with access token**:

```bash
echo $ACCESS_TOKEN | docker login your-artifactory.jfrog.io -u myuser --password-stdin
```

#### Method 4: Using API Key (Legacy, Less Secure)

```bash
# Generate API key in Artifactory UI: User Profile → API Key

# Login using API key
docker login your-artifactory.jfrog.io -u myuser -p $API_KEY
```

### Access Control (Permissions)

**Create a permission target** for Docker repositories:

1. Admin → User Management → Permissions
2. Click **New Permission**
3. Name: `docker-developers`
4. Add repositories:
   - ✓ `docker-local`
   - ✓ `docker` (virtual)
5. Users/Groups:
   - **Developers** group → Read, Write, Annotate
   - **QA** group → Read only
   - **DevOps** group → Admin
6. Click **Save**

**Permission levels**:
- **Read**: Pull images
- **Deploy/Cache**: Push images
- **Delete/Overwrite**: Delete images
- **Manage**: Manage repository
- **Admin**: Full control

---

## Pushing Images to Artifactory

### Step 1: Tag Your Image

**Tagging format**:
```
ARTIFACTORY_URL/REPOSITORY_KEY/IMAGE_NAME:TAG
```

**Example**:

```bash
# Build your image
docker build -t myapp:1.0 .

# Tag for Artifactory (local repository)
docker tag myapp:1.0 your-artifactory.jfrog.io/docker-local/myapp:1.0

# Tag for Artifactory (virtual repository)
docker tag myapp:1.0 your-artifactory.jfrog.io/docker/myapp:1.0
```

### Step 2: Push to Artifactory

```bash
# Push to local repository
docker push your-artifactory.jfrog.io/docker-local/myapp:1.0

# Or push to virtual repository (routes to docker-local)
docker push your-artifactory.jfrog.io/docker/myapp:1.0
```

**Example output**:

```
The push refers to repository [your-artifactory.jfrog.io/docker/myapp]
5f70bf18a086: Pushed
1.0: digest: sha256:abc123... size: 1234
```

### Step 3: Verify in Artifactory UI

1. Navigate to: Artifacts → docker-local → myapp
2. You should see your image with tag `1.0`
3. Click on it to view details:
   - Layers
   - Manifest
   - Properties
   - Statistics

### Multiple Tags

```bash
# Tag different versions
docker tag myapp:1.0 your-artifactory.jfrog.io/docker/myapp:1.0
docker tag myapp:1.0 your-artifactory.jfrog.io/docker/myapp:1.0.0
docker tag myapp:1.0 your-artifactory.jfrog.io/docker/myapp:latest

# Push all tags
docker push your-artifactory.jfrog.io/docker/myapp:1.0
docker push your-artifactory.jfrog.io/docker/myapp:1.0.0
docker push your-artifactory.jfrog.io/docker/myapp:latest
```

---

## Pulling Images from Artifactory

### Pull from Specific Repository

```bash
# Pull from local repository
docker pull your-artifactory.jfrog.io/docker-local/myapp:1.0

# Pull from virtual repository
docker pull your-artifactory.jfrog.io/docker/myapp:1.0
```

### Pull Through Remote Repository (Cache Docker Hub)

```bash
# First time: Downloads from Docker Hub and caches in Artifactory
docker pull your-artifactory.jfrog.io/docker-hub-remote/library/nginx:alpine

# Second time: Instant (served from Artifactory cache)
docker pull your-artifactory.jfrog.io/docker-hub-remote/library/nginx:alpine
```

### Pull Through Virtual Repository (Best Practice)

**Configure Docker to use virtual repository**:

```bash
# Pull nginx (Artifactory checks local first, then remote)
docker pull your-artifactory.jfrog.io/docker/nginx:alpine

# What happens:
# 1. Checks docker-local (not found)
# 2. Checks docker-hub-remote (finds it, downloads and caches)
# 3. Returns image
```

**Benefits**:
- Single URL for all images
- Local images have priority
- External images are cached automatically
- Protection against external registry outages

---

## Advanced Features

### 1. Repository Replication

**Replicate Docker images across data centers**:

1. Admin → Repositories → Replication
2. Click **New Replication**
3. Source: `docker-local`
4. Target: Remote Artifactory instance
5. Schedule: Real-time or scheduled
6. Click **Save**

**Use cases**:
- Multi-region deployments
- Disaster recovery
- Edge caching

### 2. Retention Policies

**Automatically clean up old images**:

1. Admin → Repositories → Local → `docker-local`
2. Scroll to **Cleanup**
3. Enable **Cleanup Policy**
4. Set rules:
   - Keep last `N` versions
   - Delete images older than `X` days
   - Keep images with specific tags (e.g., `latest`, `stable`)
5. Click **Save**

**Example policy**:
```
Keep last 5 versions
Keep tags matching: latest, stable, v*
Delete images older than 90 days
```

### 3. Build Info and Promotion

**Track build information**:

```bash
# Build with build info
docker build -t myapp:1.0 .

# Tag and push
docker tag myapp:1.0 your-artifactory.jfrog.io/docker-local/myapp:1.0
docker push your-artifactory.jfrog.io/docker-local/myapp:1.0

# Add build info (using JFrog CLI)
jf rt build-collect-env mybuild 1
jf rt build-add-git mybuild 1
jf rt build-docker-create docker-local --build-name mybuild --build-number 1
jf rt build-publish mybuild 1
```

**Promote build**:
```bash
# Promote from dev to production
jf rt build-promote mybuild 1 docker-prod-local \
  --status "Production" \
  --comment "Passed QA tests"
```

### 4. Webhooks

**Trigger actions on Docker events**:

1. Admin → Webhooks → Create Webhook
2. Event: `Docker Tag Pushed`
3. Repository: `docker-local`
4. URL: `https://your-ci-system.com/webhook`
5. Payload:
   ```json
   {
     "event": "docker.tagPushed",
     "repository": "{{repo}}",
     "image": "{{image}}",
     "tag": "{{tag}}",
     "digest": "{{digest}}"
   }
   ```
6. Click **Save**

**Use cases**:
- Trigger CI/CD pipelines
- Send notifications (Slack, email)
- Update deployment manifests
- Initiate security scans

### 5. Vulnerability Scanning (JFrog Xray)

**Scan images for vulnerabilities**:

**Prerequisites**: JFrog Xray installed and configured

**Create a policy**:
1. Xray → Policies → Create Policy
2. Name: `Docker Security Policy`
3. Rules:
   - Block: Critical CVEs
   - Warn: High CVEs
   - Allow: Medium and below
4. Click **Save**

**Create a watch**:
1. Xray → Watches → Create Watch
2. Name: `Docker Watch`
3. Resources: Add `docker-local`
4. Assigned Policies: `Docker Security Policy`
5. Click **Save**

**View scan results**:
```bash
# Push image
docker push your-artifactory.jfrog.io/docker-local/myapp:1.0

# View in UI: Xray → Security & Compliance → Violations
# Or use CLI:
jf xr scan your-artifactory.jfrog.io/docker-local/myapp:1.0
```

---

## CI/CD Integration

### GitHub Actions

**Example workflow** (.github/workflows/docker-build.yml):

```yaml
name: Build and Push to Artifactory

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Login to JFrog Artifactory
      uses: docker/login-action@v2
      with:
        registry: your-artifactory.jfrog.io
        username: ${{ secrets.JFROG_USERNAME }}
        password: ${{ secrets.JFROG_TOKEN }}

    - name: Build Docker image
      run: |
        docker build -t myapp:${{ github.sha }} .

    - name: Tag for Artifactory
      run: |
        docker tag myapp:${{ github.sha }} \
          your-artifactory.jfrog.io/docker-local/myapp:${{ github.sha }}
        docker tag myapp:${{ github.sha }} \
          your-artifactory.jfrog.io/docker-local/myapp:latest

    - name: Push to Artifactory
      run: |
        docker push your-artifactory.jfrog.io/docker-local/myapp:${{ github.sha }}
        docker push your-artifactory.jfrog.io/docker-local/myapp:latest

    - name: Scan with Xray
      run: |
        # Install JFrog CLI
        curl -fL https://getcli.jfrog.io | sh

        # Configure
        ./jf config add artifactory \
          --url=https://your-artifactory.jfrog.io \
          --access-token=${{ secrets.JFROG_TOKEN }}

        # Scan
        ./jf docker scan your-artifactory.jfrog.io/docker-local/myapp:latest
```

### GitLab CI

**Example .gitlab-ci.yml**:

```yaml
stages:
  - build
  - push
  - scan

variables:
  ARTIFACTORY_REGISTRY: your-artifactory.jfrog.io
  IMAGE_NAME: docker-local/myapp

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $IMAGE_NAME:latest
  only:
    - main

push:
  stage: push
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - echo $JFROG_TOKEN | docker login $ARTIFACTORY_REGISTRY -u $JFROG_USERNAME --password-stdin
  script:
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $ARTIFACTORY_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $ARTIFACTORY_REGISTRY/$IMAGE_NAME:latest
    - docker push $ARTIFACTORY_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $ARTIFACTORY_REGISTRY/$IMAGE_NAME:latest
  only:
    - main

scan:
  stage: scan
  image: releases-docker.jfrog.io/jfrog/jfrog-cli-v2:latest
  script:
    - jf config add artifactory --url=https://$ARTIFACTORY_REGISTRY --access-token=$JFROG_TOKEN
    - jf docker scan $ARTIFACTORY_REGISTRY/$IMAGE_NAME:latest
  only:
    - main
```

### Jenkins

**Jenkinsfile example**:

```groovy
pipeline {
    agent any

    environment {
        ARTIFACTORY_URL = 'your-artifactory.jfrog.io'
        ARTIFACTORY_REPO = 'docker-local'
        IMAGE_NAME = 'myapp'
        JFROG_CREDS = credentials('jfrog-credentials')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push to Artifactory') {
            steps {
                script {
                    docker.withRegistry("https://${ARTIFACTORY_URL}", 'jfrog-credentials') {
                        def image = docker.image("${IMAGE_NAME}:${BUILD_NUMBER}")
                        image.push("${BUILD_NUMBER}")
                        image.push("latest")
                    }
                }
            }
        }

        stage('Scan with Xray') {
            steps {
                script {
                    sh """
                        jf docker scan ${ARTIFACTORY_URL}/${ARTIFACTORY_REPO}/${IMAGE_NAME}:${BUILD_NUMBER}
                    """
                }
            }
        }
    }
}
```

---

## Best Practices

### 1. Repository Naming Conventions

**Organize by purpose**:
```
docker-prod-local      # Production images
docker-dev-local       # Development images
docker-test-local      # Test images
docker-snapshots       # CI/CD snapshots
```

**Organize by team**:
```
docker-team-a-local
docker-team-b-local
docker-shared-local
```

### 2. Tagging Strategy

**Use semantic versioning**:
```bash
docker-local/myapp:1.0.0
docker-local/myapp:1.0
docker-local/myapp:1
docker-local/myapp:latest
```

**Include metadata**:
```bash
docker-local/myapp:1.0.0-git-abc123
docker-local/myapp:1.0.0-build-456
docker-local/myapp:1.0.0-20240106
```

### 3. Virtual Repository Configuration

**Set repository resolution order**:
1. Local repositories first (fastest)
2. Remote repositories second (cached)

**Example virtual repository**:
```
docker-virtual
  ├── docker-prod-local (priority 1)
  ├── docker-dev-local (priority 2)
  └── docker-hub-remote (priority 3)
```

### 4. Retention and Cleanup

**Prevent disk bloat**:
- Keep only necessary versions
- Clean up old snapshots
- Use retention policies
- Monitor storage usage

**Example policy**:
```
Keep:
  - All production tags (v*, latest, stable)
  - Last 10 dev builds
  - Last 5 snapshots per branch

Delete:
  - Images older than 90 days (non-production)
  - Unused layers
```

### 5. Access Control

**Principle of least privilege**:
- Developers: Read from all, write to dev repos
- CI/CD: Write to dev/snapshot repos
- QA: Read from all repos
- Production deployment: Read from prod repos only
- Admins: Full control

**Example permissions**:
```
Group: developers
  docker-dev-local: Read, Write, Annotate
  docker-prod-local: Read only
  docker-hub-remote: Read only

Group: cicd
  docker-dev-local: Read, Write, Delete
  docker-snapshot-local: Read, Write, Delete
  docker-prod-local: Read only

Group: production-deploy
  docker-prod-local: Read only
  docker-virtual: Read only
```

### 6. Security

**Enable security features**:
- ✅ Use identity tokens (not passwords)
- ✅ Enable Xray scanning
- ✅ Set up security policies
- ✅ Enable audit logs
- ✅ Use HTTPS only
- ✅ Implement IP whitelisting
- ✅ Enable 2FA for admin accounts

### 7. High Availability

**Production setup**:
- Use multiple Artifactory nodes
- Configure shared storage (NFS, S3, etc.)
- Set up load balancer
- Enable replication
- Regular backups

---

## Troubleshooting

### Issue: Cannot Push to Artifactory

**Symptom**:
```
denied: permission denied
```

**Solutions**:

1. **Check authentication**:
   ```bash
   docker login your-artifactory.jfrog.io
   ```

2. **Verify permissions**:
   - Artifactory UI → User Management → Permissions
   - Ensure user has "Deploy/Cache" permission on the repository

3. **Check repository path**:
   ```bash
   # Correct format:
   your-artifactory.jfrog.io/docker-local/myapp:1.0

   # Not:
   your-artifactory.jfrog.io/myapp:1.0
   ```

### Issue: Slow Pulls from Artifactory

**Possible causes**:
- Network issues
- Remote repository not caching
- Large images

**Solutions**:

1. **Enable caching for remote repositories**:
   - Admin → Repositories → Remote → docker-hub-remote
   - Enable "Store Artifacts Locally"

2. **Increase cache retention**:
   - Set "Unused Artifacts Cleanup Period" to higher value

3. **Check network**:
   ```bash
   curl -I https://your-artifactory.jfrog.io
   ```

### Issue: "Layer Already Exists" but Image Not Visible

**Cause**: Artifact is in cache but not indexed yet.

**Solution**:
```bash
# Recalculate index
# Artifactory UI → Admin → Repositories → Local → docker-local
# Actions → Recalculate Index
```

### Issue: Disk Space Full

**Check disk usage**:
```bash
# Artifactory UI → Admin → Storage
# View: Storage Summary
```

**Solutions**:

1. **Run cleanup**:
   - Admin → Storage → Cleanup
   - Run unused artifacts cleanup

2. **Enable retention policy**:
   - Admin → Repositories → Local → docker-local
   - Enable cleanup policy

3. **Delete old images**:
   ```bash
   # Using JFrog CLI
   jf rt delete "docker-local/myapp/*" --older-than=90d --quiet
   ```

---

## Comparison: Using Artifactory in Practice

### Before Artifactory

```bash
# Developers pull from multiple registries
docker pull docker.io/nginx:alpine
docker pull gcr.io/my-project/myapp:latest
docker pull quay.io/prometheus/prometheus

# Problems:
# - Multiple authentication setups
# - No caching (slow, expensive bandwidth)
# - Vulnerable to external registry outages
# - No audit trail
# - No vulnerability scanning
```

### After Artifactory

```bash
# Configure Docker to use Artifactory virtual repository
# .docker/config.json points to: your-artifactory.jfrog.io/docker

# Developers pull from single source
docker pull your-artifactory.jfrog.io/docker/nginx:alpine
docker pull your-artifactory.jfrog.io/docker/myapp:latest
docker pull your-artifactory.jfrog.io/docker/prometheus/prometheus

# Benefits:
# ✅ Single authentication
# ✅ All images cached locally (fast, cheap)
# ✅ Protection from external outages
# ✅ Complete audit trail
# ✅ Automatic vulnerability scanning
# ✅ Access control and governance
```

---

## Summary

You've learned:

✅ What JFrog Artifactory is and why it's valuable for Docker
✅ How to set up and configure Artifactory for Docker
✅ Repository types: local, remote, and virtual
✅ How to authenticate and manage access control
✅ How to push and pull Docker images
✅ Advanced features: replication, retention, scanning
✅ CI/CD integration patterns
✅ Best practices for enterprise Docker registry management
✅ Troubleshooting common issues

**Key Takeaways**:
1. **Use virtual repositories** for single-endpoint access
2. **Enable remote repositories** to cache external registries
3. **Implement access control** with granular permissions
4. **Set up retention policies** to manage disk space
5. **Integrate with Xray** for vulnerability scanning
6. **Automate with CI/CD** for seamless workflows

**Next steps**:
1. Set up Artifactory in your environment
2. Configure repository structure
3. Migrate existing images
4. Integrate with CI/CD pipelines
5. Enable Xray scanning
6. Train your team on new workflows

---

**Previous Chapter**: [Chapter 20: Beyond the Basics](./chapter20_beyond_the_basics.md)

**Next Chapter**: [Chapter 22: Self-Hosted Applications](./chapter22_self_hosted_apps.md)

**Back to**: [Tutorial Index](./README.md)
