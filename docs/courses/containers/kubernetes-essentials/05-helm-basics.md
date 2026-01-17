# Helm package manager

> **Module:** Kubernetes Essentials | **Level:** Advanced | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Understand Helm concepts
- Install and manage Helm charts
- Create custom charts
- Use Helm in CI/CD

---

## What is Helm?

Helm is the package manager for Kubernetes, similar to apt, yum, or brew.

### Key concepts

| Concept | Description |
|---------|-------------|
| **Chart** | Package of Kubernetes resources |
| **Release** | Installed instance of a chart |
| **Repository** | Collection of charts |
| **Values** | Configuration for a chart |

### Helm vs raw manifests

| Raw YAML | Helm |
|----------|------|
| Copy & modify | Install & configure |
| Manual versioning | Automatic versioning |
| No templating | Full templating |
| Manual rollback | Built-in rollback |

---

## Installing Helm

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

---

## Using Helm charts

### Add repositories

```bash
# Add official stable repo
helm repo add bitnami https://charts.bitnami.com/bitnami

# Add prometheus community
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Update repos
helm repo update

# List repos
helm repo list

# Search charts
helm search repo nginx
helm search repo postgresql
```

### Install a chart

```bash
# Basic install
helm install my-nginx bitnami/nginx

# With namespace
helm install my-nginx bitnami/nginx -n web --create-namespace

# With values file
helm install my-nginx bitnami/nginx -f values.yaml

# With inline values
helm install my-nginx bitnami/nginx --set replicaCount=3

# Dry run (preview)
helm install my-nginx bitnami/nginx --dry-run
```

### Manage releases

```bash
# List releases
helm list
helm list -A  # All namespaces

# Get release info
helm status my-nginx
helm get values my-nginx
helm get manifest my-nginx

# Upgrade
helm upgrade my-nginx bitnami/nginx --set replicaCount=5

# Rollback
helm rollback my-nginx 1  # Revision number

# Uninstall
helm uninstall my-nginx
```

---

## Values and configuration

### View default values

```bash
helm show values bitnami/nginx > values.yaml
```

### Custom values file

```yaml
# values.yaml
replicaCount: 3

image:
  repository: nginx
  tag: "1.25"

service:
  type: LoadBalancer
  port: 80

resources:
  limits:
    cpu: 500m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

ingress:
  enabled: true
  hostname: myapp.example.com
  tls: true
```

```bash
helm install my-nginx bitnami/nginx -f values.yaml
```

### Override specific values

```bash
# Single value
helm install my-nginx bitnami/nginx --set replicaCount=3

# Nested value
helm install my-nginx bitnami/nginx --set image.tag=1.25

# Multiple values
helm install my-nginx bitnami/nginx \
    --set replicaCount=3 \
    --set service.type=LoadBalancer
```

---

## Creating charts

### Chart structure

```bash
# Create new chart
helm create myapp
```

```
myapp/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default values
├── charts/             # Dependencies
├── templates/          # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── _helpers.tpl    # Template helpers
│   └── NOTES.txt       # Post-install notes
└── .helmignore
```

### Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: My application chart
type: application
version: 0.1.0      # Chart version
appVersion: "1.0.0" # App version

dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
```

### values.yaml

```yaml
# values.yaml
replicaCount: 1

image:
  repository: myapp
  pullPolicy: IfNotPresent
  tag: ""  # Defaults to appVersion

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 500m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

postgresql:
  enabled: true
  auth:
    database: myapp
```

### Template example

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### Helper templates

```yaml
# templates/_helpers.tpl
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "myapp.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## Chart development

### Test templates

```bash
# Lint chart
helm lint myapp/

# Render templates locally
helm template myapp myapp/

# Render with custom values
helm template myapp myapp/ -f custom-values.yaml

# Debug (verbose output)
helm install myapp myapp/ --debug --dry-run
```

### Package and publish

```bash
# Package chart
helm package myapp/

# Create/update index
helm repo index . --url https://charts.example.com

# Push to OCI registry
helm push myapp-0.1.0.tgz oci://registry.example.com/charts
```

---

## Dependencies

### Add dependencies

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

```bash
# Download dependencies
helm dependency update myapp/

# Build dependencies
helm dependency build myapp/
```

---

## Helm in CI/CD

### GitHub Actions example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Helm
        uses: azure/setup-helm@v3

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBECONFIG }}

      - name: Deploy
        run: |
          helm upgrade --install myapp ./charts/myapp \
            --namespace production \
            --create-namespace \
            --set image.tag=${{ github.sha }} \
            --wait
```

### GitOps with ArgoCD

```yaml
# Application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp
    targetRevision: HEAD
    path: charts/myapp
    helm:
      valueFiles:
        - values-production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## Key takeaways

1. **Helm** packages Kubernetes manifests into reusable charts
2. **Values** customize chart behavior
3. **Repositories** distribute charts
4. **Templates** enable dynamic configuration
5. **Dependencies** manage complex applications

---

## What's next

Learn about practical Kubernetes deployments.

Continue to: [06-practical-kubernetes.md](06-practical-kubernetes.md)
