# The oc CLI

> **Module:** OpenShift | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Install and configure the oc CLI
- Authenticate to OpenShift clusters
- Use essential oc commands
- Understand the relationship between oc and kubectl

---

## Installing oc

### Download from OpenShift

```bash
# Get download URL from cluster
oc version --client  # If already installed

# Or download from:
# https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/

# Extract and install (Linux)
tar xzf openshift-client-linux.tar.gz
sudo mv oc kubectl /usr/local/bin/

# macOS
brew install openshift-cli

# Windows
# Download and add to PATH
```

### Verify installation

```bash
# Check version
oc version

# Output:
# Client Version: 4.14.0
# Kustomize Version: v5.0.1
# Server Version: 4.14.0 (if connected)
```

---

## oc vs kubectl

The `oc` CLI wraps `kubectl` and adds OpenShift-specific commands:

```bash
# These are equivalent
oc get pods
kubectl get pods

# OpenShift-specific commands (oc only)
oc new-project myproject
oc new-app nginx
oc expose service nginx
oc start-build myapp
oc login
```

### When to use each

| Use Case | Command |
|----------|---------|
| Standard K8s resources | `oc` or `kubectl` |
| OpenShift resources (Routes, BuildConfigs) | `oc` |
| Creating projects/apps | `oc` |
| Builds and ImageStreams | `oc` |
| Pure Kubernetes clusters | `kubectl` |

---

## Authentication

### Login methods

```bash
# Interactive login (prompts for credentials)
oc login https://api.cluster.example.com:6443

# With username/password
oc login -u myuser -p mypassword https://api.cluster.example.com:6443

# With token (from web console)
oc login --token=sha256~xxxxx --server=https://api.cluster.example.com:6443

# With certificate
oc login --certificate-authority=ca.crt https://api.cluster.example.com:6443
```

### Get login token from web console

1. Open web console
2. Click username (top right)
3. Select "Copy login command"
4. Click "Display Token"
5. Copy the `oc login --token=...` command

### Managing contexts

```bash
# View current context
oc whoami
oc whoami --show-server
oc whoami --show-context

# List all contexts
oc config get-contexts

# Switch context
oc config use-context my-context

# View config
oc config view
```

### Logout

```bash
# Logout (invalidates token)
oc logout

# Check if logged in
oc whoami
```

---

## Project management

### Working with projects

```bash
# List projects
oc projects
oc get projects

# Create project
oc new-project myproject
oc new-project myproject --description="My Project" --display-name="My Project"

# Switch project
oc project myproject

# View current project
oc project

# Delete project (and all resources)
oc delete project myproject
```

### Project vs namespace

```bash
# These are similar but not identical
oc new-project myproject   # Creates project with extras
oc create namespace myns   # Creates bare namespace

# Projects include:
# - Default service accounts
# - Default role bindings
# - Network policies (if configured)
```

---

## Application management

### Creating applications

```bash
# From container image
oc new-app nginx
oc new-app --image=nginx:alpine --name=my-nginx

# From source code (S2I)
oc new-app nodejs:18~https://github.com/user/repo.git
oc new-app nodejs:18~https://github.com/user/repo.git --name=myapp

# From Dockerfile
oc new-app https://github.com/user/repo.git --strategy=docker

# From template
oc new-app postgresql-persistent -p POSTGRESQL_USER=admin

# Dry run to see what would be created
oc new-app nginx -o yaml --dry-run
```

### Viewing applications

```bash
# List all resources
oc get all

# Specific resources
oc get pods
oc get deployments
oc get services
oc get routes
oc get buildconfigs
oc get imagestreams

# Detailed view
oc describe pod my-pod
oc describe deployment my-app

# Wide output
oc get pods -o wide

# YAML/JSON output
oc get deployment my-app -o yaml
oc get deployment my-app -o json
```

### Deleting applications

```bash
# Delete specific resources
oc delete deployment my-app
oc delete service my-app
oc delete route my-app

# Delete by label
oc delete all -l app=my-app

# Delete everything created by new-app
oc delete all --selector app=nginx
```

---

## Build commands

### Managing builds

```bash
# View build configs
oc get buildconfigs
oc get bc

# Start a build
oc start-build my-app
oc start-build my-app --follow

# Binary build from local directory
oc start-build my-app --from-dir=./app

# Binary build from file
oc start-build my-app --from-file=app.jar

# View build logs
oc logs -f bc/my-app
oc logs build/my-app-1

# List builds
oc get builds

# Cancel a build
oc cancel-build my-app-1

# View build history
oc describe bc/my-app
```

### Build troubleshooting

```bash
# Check build status
oc get builds
oc describe build my-app-1

# Get build logs
oc logs build/my-app-1

# Check events
oc get events --sort-by=.lastTimestamp

# Debug failed build
oc debug build/my-app-1
```

---

## Deployment commands

### Managing deployments

```bash
# View deployments
oc get deployments
oc get dc  # DeploymentConfigs (legacy)

# Scale
oc scale deployment my-app --replicas=3
oc scale dc my-app --replicas=3

# Rollout status
oc rollout status deployment/my-app

# Rollout history
oc rollout history deployment/my-app

# Rollback
oc rollout undo deployment/my-app
oc rollout undo deployment/my-app --to-revision=2

# Pause/resume
oc rollout pause deployment/my-app
oc rollout resume deployment/my-app

# Restart pods
oc rollout restart deployment/my-app
```

### Updating deployments

```bash
# Update image
oc set image deployment/my-app my-app=nginx:1.21

# Set environment variable
oc set env deployment/my-app DB_HOST=postgres

# Set resources
oc set resources deployment/my-app --limits=cpu=200m,memory=512Mi

# Set triggers
oc set triggers deployment/my-app --from-image=my-app:latest -c my-app
```

---

## Pod commands

### Executing in pods

```bash
# Get shell in pod
oc rsh my-pod
oc rsh deployment/my-app

# Execute command
oc exec my-pod -- ls -la
oc exec my-pod -c container-name -- command

# Interactive command
oc exec -it my-pod -- /bin/bash
```

### Viewing logs

```bash
# Pod logs
oc logs my-pod
oc logs my-pod -c container-name

# Follow logs
oc logs -f my-pod

# Previous container logs
oc logs my-pod --previous

# Deployment logs
oc logs deployment/my-app

# Build logs
oc logs bc/my-app
```

### Debugging

```bash
# Debug a pod
oc debug pod/my-pod

# Debug with specific image
oc debug pod/my-pod --image=registry.access.redhat.com/ubi8/ubi

# Debug node
oc debug node/worker-1

# Port forwarding
oc port-forward pod/my-pod 8080:80
oc port-forward svc/my-service 8080:80

# Copy files
oc cp my-pod:/path/to/file ./local-file
oc cp ./local-file my-pod:/path/to/file
```

---

## Route commands

### Managing routes

```bash
# Expose service as route
oc expose service my-app

# With hostname
oc expose service my-app --hostname=myapp.example.com

# Create TLS route
oc create route edge my-app --service=my-app
oc create route passthrough my-app-ssl --service=my-app
oc create route reencrypt my-app-reenc --service=my-app

# View routes
oc get routes
oc describe route my-app

# Get route URL
oc get route my-app -o jsonpath='{.spec.host}'
```

### Traffic management

```bash
# Set route backends (A/B testing)
oc set route-backends my-app my-app-v1=80 my-app-v2=20

# View backend weights
oc describe route my-app
```

---

## Image and registry commands

### Managing images

```bash
# Import image
oc import-image nginx:latest --from=docker.io/nginx:latest --confirm

# Tag image
oc tag nginx:latest nginx:production

# View imagestreams
oc get imagestreams
oc get is

# View image tags
oc get imagestreamtags
oc get istag

# Describe imagestream
oc describe is my-app
```

### Registry operations

```bash
# Login to internal registry
oc registry login

# Get registry URL
oc registry info

# Push to internal registry
podman login -u $(oc whoami) -p $(oc whoami -t) $(oc registry info)
podman push myimage $(oc registry info)/myproject/myimage:latest
```

---

## Useful aliases and shortcuts

### Common aliases

```bash
# Add to ~/.bashrc or ~/.zshrc

# Project shortcuts
alias ocp='oc project'
alias ocps='oc projects'

# Resource viewing
alias ocga='oc get all'
alias ocgp='oc get pods'
alias ocgd='oc get deployments'
alias ocgs='oc get services'
alias ocgr='oc get routes'

# Logs
alias ocl='oc logs -f'

# Shell access
alias ocr='oc rsh'

# Watch resources
alias ocw='oc get pods -w'
```

### Bash completion

```bash
# Enable bash completion
source <(oc completion bash)

# Add to ~/.bashrc
echo 'source <(oc completion bash)' >> ~/.bashrc

# Zsh completion
source <(oc completion zsh)
```

---

## Quick reference

### Most common commands

```bash
# Authentication
oc login                    # Login to cluster
oc logout                   # Logout
oc whoami                   # Current user

# Projects
oc project <name>           # Switch project
oc new-project <name>       # Create project

# Applications
oc new-app <image>          # Create app
oc expose svc/<name>        # Create route
oc delete all -l app=<name> # Delete app

# Builds
oc start-build <name>       # Start build
oc logs -f bc/<name>        # Build logs

# Pods
oc get pods                 # List pods
oc logs <pod>               # Pod logs
oc rsh <pod>                # Shell access
oc exec <pod> -- <cmd>      # Run command

# Deployments
oc scale deploy/<name>      # Scale
oc rollout restart          # Restart pods

# Troubleshooting
oc describe <resource>      # Details
oc get events               # Events
oc debug <pod>              # Debug mode
```

---

## Key takeaways

1. **oc wraps kubectl** and adds OpenShift-specific commands
2. **Login with token** from web console is most common
3. **Projects** are enhanced namespaces
4. **oc new-app** creates multiple resources at once
5. **oc rsh** provides quick shell access
6. **oc expose** creates routes from services

---

## What's next

Learn about Source-to-Image (S2I) builds in detail.

Continue to: [04-source-to-image.md](04-source-to-image.md)
