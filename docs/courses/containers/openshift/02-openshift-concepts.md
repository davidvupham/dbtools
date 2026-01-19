# OpenShift concepts

> **Module:** OpenShift | **Level:** Intermediate | **Time:** 35 minutes

## Learning objectives

By the end of this section, you will be able to:

- Work with Routes for external access
- Understand ImageStreams and image management
- Use BuildConfigs for automated builds
- Know when to use DeploymentConfig vs Deployment

---

## Routes

Routes are OpenShift's native way to expose services externally. They're more feature-rich than Kubernetes Ingress.

### Route vs Ingress comparison

| Feature | Ingress | Route |
|---------|---------|-------|
| TLS termination | Yes | Yes |
| Path-based routing | Yes | Yes |
| Host-based routing | Yes | Yes |
| Wildcard domains | Limited | Yes |
| Blue-green deployment | Manual | Native |
| A/B testing | Manual | Native (weights) |
| Sticky sessions | Annotation | Native |
| Rate limiting | Depends on controller | Native |

### Creating routes

```yaml
# route.yaml - Basic route
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: my-app
  namespace: my-project
spec:
  host: my-app.apps.cluster.example.com
  to:
    kind: Service
    name: my-app
    weight: 100
  port:
    targetPort: 8080
```

```bash
# Create route from service
oc expose service/my-app

# Create route with specific hostname
oc expose service/my-app --hostname=myapp.example.com

# Create route with TLS
oc create route edge my-app --service=my-app --hostname=myapp.example.com

# View routes
oc get routes
oc describe route my-app
```

### TLS termination types

```yaml
# Edge termination (TLS at router)
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: edge-route
spec:
  host: secure.example.com
  to:
    kind: Service
    name: my-app
  tls:
    termination: edge
    certificate: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      ...
      -----END RSA PRIVATE KEY-----
```

```yaml
# Passthrough (TLS handled by pod)
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: passthrough-route
spec:
  host: secure.example.com
  to:
    kind: Service
    name: my-app
  tls:
    termination: passthrough
```

```yaml
# Re-encrypt (TLS at router and to pod)
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: reencrypt-route
spec:
  host: secure.example.com
  to:
    kind: Service
    name: my-app
  tls:
    termination: reencrypt
    destinationCACertificate: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
```

### Traffic splitting (A/B testing)

```yaml
# Split traffic between services
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ab-route
spec:
  host: myapp.example.com
  to:
    kind: Service
    name: my-app-v1
    weight: 80
  alternateBackends:
    - kind: Service
      name: my-app-v2
      weight: 20
```

```bash
# Adjust weights via CLI
oc set route-backends ab-route my-app-v1=80 my-app-v2=20
```

---

## ImageStreams

ImageStreams are an abstraction layer over container images. They track image updates and trigger rebuilds/redeployments.

### Why use ImageStreams?

```mermaid
graph LR
    subgraph External["External Registry"]
        ExtImg[nginx:1.21]
    end

    subgraph OpenShift["OpenShift"]
        IS[ImageStream: nginx]
        IST1[Tag: latest]
        IST2[Tag: 1.21]

        IS --> IST1
        IS --> IST2

        Deploy[Deployment]
        BC[BuildConfig]

        IST1 -->|triggers| Deploy
        IST1 -->|base image| BC
    end

    ExtImg -->|imports| IST2
```

**Benefits:**
- **Abstraction**: Reference images by stream name, not registry URL
- **Triggers**: Auto-deploy when image updates
- **History**: Track image versions
- **Promotion**: Move images between environments
- **Security**: Scan and validate before deployment

### Creating ImageStreams

```yaml
# imagestream.yaml
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: my-app
  namespace: my-project
spec:
  lookupPolicy:
    local: true
```

```bash
# Create empty imagestream
oc create imagestream my-app

# Import image from external registry
oc import-image nginx:latest --from=docker.io/nginx:latest --confirm

# Import with scheduled updates (every 15 min)
oc import-image nginx:latest \
  --from=docker.io/nginx:latest \
  --scheduled=true \
  --confirm

# Tag an image
oc tag nginx:latest nginx:production

# View imagestream
oc get is
oc describe is nginx

# View image history
oc get istag
```

### ImageStream tags

```yaml
# Import specific tags
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: nodejs
spec:
  tags:
    - name: "18"
      from:
        kind: DockerImage
        name: registry.access.redhat.com/ubi8/nodejs-18:latest
      importPolicy:
        scheduled: true
    - name: "20"
      from:
        kind: DockerImage
        name: registry.access.redhat.com/ubi8/nodejs-20:latest
      importPolicy:
        scheduled: true
```

### Using ImageStreams in deployments

```yaml
# Reference imagestream in deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  annotations:
    image.openshift.io/triggers: |
      [{"from":{"kind":"ImageStreamTag","name":"my-app:latest"},"fieldPath":"spec.template.spec.containers[?(@.name==\"my-app\")].image"}]
spec:
  template:
    spec:
      containers:
        - name: my-app
          image: my-app:latest  # References imagestream
```

---

## BuildConfigs

BuildConfigs define how to build container images within OpenShift.

### Build strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Source-to-Image (S2I)** | Build from source code | Standard app builds |
| **Docker** | Build from Dockerfile | Custom builds |
| **Pipeline** | Tekton/Jenkins pipeline | Complex CI/CD |
| **Custom** | Custom builder image | Specialized needs |

### Source-to-Image (S2I) build

```yaml
# buildconfig-s2i.yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: my-nodejs-app
spec:
  source:
    type: Git
    git:
      uri: https://github.com/myorg/my-nodejs-app.git
      ref: main
  strategy:
    type: Source
    sourceStrategy:
      from:
        kind: ImageStreamTag
        name: nodejs:18
        namespace: openshift
  output:
    to:
      kind: ImageStreamTag
      name: my-nodejs-app:latest
  triggers:
    - type: ConfigChange
    - type: ImageChange
    - type: GitHub
      github:
        secret: my-webhook-secret
```

```bash
# Create from CLI
oc new-build nodejs:18~https://github.com/myorg/my-nodejs-app.git \
  --name=my-nodejs-app

# Start a build
oc start-build my-nodejs-app

# Follow build logs
oc logs -f bc/my-nodejs-app

# View builds
oc get builds
```

### Docker build

```yaml
# buildconfig-docker.yaml
apiVersion: build.openshift.io/v1
kind: BuildConfig
metadata:
  name: my-app-docker
spec:
  source:
    type: Git
    git:
      uri: https://github.com/myorg/my-app.git
    contextDir: docker/
  strategy:
    type: Docker
    dockerStrategy:
      dockerfilePath: Dockerfile.prod
      buildArgs:
        - name: APP_VERSION
          value: "1.0.0"
  output:
    to:
      kind: ImageStreamTag
      name: my-app:latest
```

### Binary build (from local files)

```bash
# Create build config for binary input
oc new-build --name=my-app --binary --strategy=docker

# Start build with local directory
oc start-build my-app --from-dir=./app --follow

# Start build with archive
oc start-build my-app --from-archive=app.tar.gz --follow
```

### Build triggers

```yaml
# Trigger types in BuildConfig
spec:
  triggers:
    # Rebuild on config change
    - type: ConfigChange

    # Rebuild when base image updates
    - type: ImageChange
      imageChange: {}

    # GitHub webhook
    - type: GitHub
      github:
        secret: github-webhook-secret

    # GitLab webhook
    - type: GitLab
      gitlab:
        secret: gitlab-webhook-secret

    # Generic webhook
    - type: Generic
      generic:
        secret: generic-webhook-secret
```

```bash
# Get webhook URLs
oc describe bc my-app | grep -A 1 "Webhook"

# Manually trigger build
oc start-build my-app --follow
```

---

## DeploymentConfig vs Deployment

### DeploymentConfig (OpenShift-specific, legacy)

```yaml
# deploymentconfig.yaml
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:latest
  triggers:
    - type: ConfigChange
    - type: ImageChange
      imageChangeParams:
        automatic: true
        containerNames:
          - my-app
        from:
          kind: ImageStreamTag
          name: my-app:latest
  strategy:
    type: Rolling
    rollingParams:
      maxSurge: 25%
      maxUnavailable: 25%
```

### Deployment (Kubernetes standard, recommended)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  annotations:
    image.openshift.io/triggers: |
      [{"from":{"kind":"ImageStreamTag","name":"my-app:latest"},
        "fieldPath":"spec.template.spec.containers[?(@.name==\"my-app\")].image"}]
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:latest
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
```

### Feature comparison

| Feature | DeploymentConfig | Deployment |
|---------|-----------------|------------|
| Standard | OpenShift-specific | Kubernetes native |
| Image triggers | Built-in | Via annotation |
| Lifecycle hooks | Yes | Via init containers |
| Custom strategies | Yes | Limited |
| Rollback | `oc rollback` | `kubectl rollout undo` |
| Future support | Deprecated | Recommended |

### Recommendation

**Use Kubernetes Deployments** with ImageStream trigger annotations for new applications. DeploymentConfig is maintained for backward compatibility but not actively developed.

```bash
# Create deployment with trigger
oc create deployment my-app --image=my-app:latest
oc set triggers deployment/my-app --from-image=my-app:latest -c my-app
```

---

## Templates

Templates are OpenShift's way to define parameterized multi-resource deployments.

### Template structure

```yaml
# template.yaml
apiVersion: template.openshift.io/v1
kind: Template
metadata:
  name: my-app-template
  annotations:
    description: "My application template"
    tags: "nodejs,web"
parameters:
  - name: APP_NAME
    description: Application name
    required: true
  - name: REPLICAS
    description: Number of replicas
    value: "2"
  - name: IMAGE_TAG
    description: Image tag
    value: latest
  - name: DB_PASSWORD
    description: Database password
    generate: expression
    from: "[a-zA-Z0-9]{16}"
objects:
  - apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: ${APP_NAME}
    spec:
      replicas: ${{REPLICAS}}
      selector:
        matchLabels:
          app: ${APP_NAME}
      template:
        metadata:
          labels:
            app: ${APP_NAME}
        spec:
          containers:
            - name: ${APP_NAME}
              image: ${APP_NAME}:${IMAGE_TAG}
              env:
                - name: DB_PASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: ${APP_NAME}-secrets
                      key: db-password

  - apiVersion: v1
    kind: Secret
    metadata:
      name: ${APP_NAME}-secrets
    stringData:
      db-password: ${DB_PASSWORD}

  - apiVersion: v1
    kind: Service
    metadata:
      name: ${APP_NAME}
    spec:
      ports:
        - port: 8080
      selector:
        app: ${APP_NAME}

  - apiVersion: route.openshift.io/v1
    kind: Route
    metadata:
      name: ${APP_NAME}
    spec:
      to:
        kind: Service
        name: ${APP_NAME}
```

### Using templates

```bash
# Process template (show YAML)
oc process -f template.yaml -p APP_NAME=myapp

# Apply template directly
oc process -f template.yaml -p APP_NAME=myapp | oc apply -f -

# Create template in cluster
oc create -f template.yaml

# Instantiate from cluster template
oc new-app my-app-template -p APP_NAME=myapp

# List available templates
oc get templates
oc get templates -n openshift  # Cluster templates
```

---

## Catalog and quick starts

### Developer Catalog

The Developer Catalog provides ready-to-use templates and operators:

```bash
# Browse catalog from CLI
oc get templates -n openshift

# Common catalog items
oc new-app postgresql-persistent  # Database with storage
oc new-app nodejs~https://github.com/user/app  # S2I build
oc new-app nginx  # Simple deployment
```

### Quick starts

Quick starts guide new users through common tasks:

- Creating applications
- Setting up CI/CD
- Configuring monitoring
- Managing secrets

Access via **Web Console > Help > Quick Starts**

---

## Key takeaways

1. **Routes** provide powerful ingress with native traffic splitting
2. **ImageStreams** abstract image management and enable triggers
3. **BuildConfigs** automate container builds within the cluster
4. **Use Deployments** over DeploymentConfig for new applications
5. **Templates** provide reusable, parameterized deployments

---

## What's next

Learn how to use the `oc` CLI effectively.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [OpenShift Introduction](01-openshift-introduction.md) | [Course Overview](../course_overview.md) | [OC CLI](03-oc-cli.md) |
