# Kubernetes integration

**[← Back to Track B: Infrastructure](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-4_Applied-blue)
![Lesson](https://img.shields.io/badge/Lesson-16-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Explain the different methods for integrating Vault with Kubernetes
- Configure Kubernetes authentication in Vault
- Deploy and configure the Vault Agent Injector
- Use the Vault CSI Provider to mount secrets as volumes
- Implement sidecar injection patterns for applications

## Table of contents

- [Integration methods overview](#integration-methods-overview)
- [Kubernetes authentication](#kubernetes-authentication)
- [Vault Agent Injector](#vault-agent-injector)
- [Vault CSI Provider](#vault-csi-provider)
- [Sidecar injection patterns](#sidecar-injection-patterns)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Integration methods overview

Vault provides multiple methods for Kubernetes integration, each suited for different use cases and security requirements.

### Comparison of integration methods

| Method | Description | Use Case | Pros | Cons |
|--------|-------------|----------|------|------|
| Direct API | Application calls Vault API directly | Full control needed | Maximum flexibility | Requires SDK integration |
| Agent Injector | Sidecar injects secrets via annotations | Most applications | No code changes | Additional pod resources |
| CSI Provider | Mounts secrets as volume files | File-based configs | Native K8s integration | Limited dynamic refresh |
| External Secrets | Syncs to K8s Secrets | Legacy apps | Simple adoption | Secrets stored in etcd |

### Architecture overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │   Application   │    │  Vault Agent    │    │  CSI Provider   │        │
│   │      Pod        │    │   Injector      │    │   DaemonSet     │        │
│   │                 │    │                 │    │                 │        │
│   │  ┌───────────┐  │    │  Watches for    │    │  Mounts secrets │        │
│   │  │   App     │  │    │  annotations    │    │  as volumes     │        │
│   │  │ Container │  │    │                 │    │                 │        │
│   │  └───────────┘  │    └────────┬────────┘    └────────┬────────┘        │
│   │  ┌───────────┐  │             │                      │                  │
│   │  │  Vault    │  │             │                      │                  │
│   │  │  Agent    │  │             │                      │                  │
│   │  │ (sidecar) │  │             │                      │                  │
│   │  └───────────┘  │             │                      │                  │
│   └────────┬────────┘             │                      │                  │
│            │                      │                      │                  │
│            └──────────────────────┼──────────────────────┘                  │
│                                   │                                          │
│                                   ▼                                          │
│                          ┌─────────────────┐                                │
│                          │ Kubernetes API  │                                │
│                          │    Server       │                                │
│                          └────────┬────────┘                                │
│                                   │                                          │
└───────────────────────────────────┼──────────────────────────────────────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  HashiCorp      │
                           │     Vault       │
                           └─────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Kubernetes authentication

The Kubernetes auth method allows pods to authenticate to Vault using their service account tokens.

### How it works

1. Pod presents its service account JWT token to Vault
2. Vault validates the token with the Kubernetes API server
3. Vault maps the service account to a Vault role
4. Vault issues a Vault token with appropriate policies

### Enabling Kubernetes auth

```bash
# Enable the Kubernetes auth method
vault auth enable kubernetes

# Configure the Kubernetes auth method
vault write auth/kubernetes/config \
    kubernetes_host="https://$KUBERNETES_HOST:443" \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
    token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token
```

### Creating a role

Vault roles map Kubernetes service accounts to policies:

```bash
# Create a role for an application
vault write auth/kubernetes/role/myapp \
    bound_service_account_names=myapp-sa \
    bound_service_account_namespaces=production \
    policies=myapp-policy \
    ttl=1h
```

### Role configuration options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `bound_service_account_names` | Allowed service account names | `myapp-sa,myapp-worker` |
| `bound_service_account_namespaces` | Allowed namespaces | `production,staging` |
| `policies` | Vault policies to attach | `myapp-read,db-creds` |
| `ttl` | Token TTL | `1h` |
| `max_ttl` | Maximum token TTL | `24h` |
| `audience` | Expected JWT audience | `vault` |

### Service account setup

```yaml
# service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: vault-token-reviewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
  - kind: ServiceAccount
    name: vault
    namespace: vault
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Vault Agent Injector

The Vault Agent Injector is a Kubernetes mutation webhook that automatically injects Vault Agent sidecars into pods.

### How the injector works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Pod Creation Flow                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. kubectl apply     2. Webhook Intercept     3. Inject Sidecar           │
│   ┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐        │
│   │   Pod Spec  │ ───▶ │ Agent Injector  │ ───▶ │  Modified Pod   │        │
│   │ (with       │      │   Webhook       │      │  + Vault Agent  │        │
│   │ annotations)│      │                 │      │  + Init         │        │
│   └─────────────┘      └─────────────────┘      └─────────────────┘        │
│                                                                              │
│   4. Pod Starts        5. Agent Authenticates   6. Secrets Rendered         │
│   ┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐        │
│   │ Init runs   │ ───▶ │ Gets Vault      │ ───▶ │ Writes secrets  │        │
│   │ first       │      │ token           │      │ to shared volume│        │
│   └─────────────┘      └─────────────────┘      └─────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Installing the injector

Install via Helm:

```bash
# Add HashiCorp Helm repository
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Install Vault with the injector enabled
helm install vault hashicorp/vault \
    --namespace vault \
    --create-namespace \
    --set "injector.enabled=true" \
    --set "server.dev.enabled=true"
```

### Pod annotations

Control the injector behavior with annotations:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  annotations:
    # Enable injection
    vault.hashicorp.com/agent-inject: "true"

    # Vault role to authenticate as
    vault.hashicorp.com/role: "myapp"

    # Secret path and output file
    vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"

    # Custom template for rendering
    vault.hashicorp.com/agent-inject-template-config: |
      {{- with secret "secret/data/myapp/config" -}}
      export DB_HOST="{{ .Data.data.db_host }}"
      export DB_USER="{{ .Data.data.db_user }}"
      export DB_PASS="{{ .Data.data.db_pass }}"
      {{- end }}
spec:
  serviceAccountName: myapp-sa
  containers:
    - name: myapp
      image: myapp:latest
      command: ["/bin/sh", "-c", "source /vault/secrets/config && ./start.sh"]
```

### Common annotations reference

| Annotation | Description | Default |
|------------|-------------|---------|
| `vault.hashicorp.com/agent-inject` | Enable/disable injection | `false` |
| `vault.hashicorp.com/role` | Vault role name | Required |
| `vault.hashicorp.com/agent-inject-secret-<name>` | Secret path to fetch | - |
| `vault.hashicorp.com/agent-inject-template-<name>` | Custom Go template | - |
| `vault.hashicorp.com/agent-pre-populate-only` | Only run init, no sidecar | `false` |
| `vault.hashicorp.com/agent-revoke-on-shutdown` | Revoke token on exit | `false` |
| `vault.hashicorp.com/agent-cache-enable` | Enable agent caching | `false` |
| `vault.hashicorp.com/secret-volume-path` | Mount path for secrets | `/vault/secrets` |

### Template syntax

The agent uses Go templates with Consul Template functions:

```yaml
vault.hashicorp.com/agent-inject-template-db: |
  {{- with secret "database/creds/myapp" -}}
  [database]
  host = "db.example.com"
  username = "{{ .Data.username }}"
  password = "{{ .Data.password }}"
  {{- end }}
```

**Useful template functions:**

| Function | Description | Example |
|----------|-------------|---------|
| `secret` | Fetch a secret | `{{ with secret "path" }}` |
| `base64Decode` | Decode base64 | `{{ .Data.cert \| base64Decode }}` |
| `toJSON` | Convert to JSON | `{{ .Data \| toJSON }}` |
| `toYAML` | Convert to YAML | `{{ .Data \| toYAML }}` |
| `env` | Read environment var | `{{ env "POD_NAME" }}` |

[↑ Back to Table of Contents](#table-of-contents)

---

## Vault CSI Provider

The Vault CSI Provider allows you to mount Vault secrets as Kubernetes volumes using the Container Storage Interface.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CSI Provider Flow                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐                                                       │
│   │  Application    │                                                       │
│   │      Pod        │                                                       │
│   │   ┌─────────┐   │     ┌─────────────────┐     ┌─────────────────┐      │
│   │   │ Volume  │◀──┼─────│  CSI Provider   │◀────│     Vault       │      │
│   │   │ Mount   │   │     │   (DaemonSet)   │     │                 │      │
│   │   └─────────┘   │     └─────────────────┘     └─────────────────┘      │
│   └─────────────────┘                                                       │
│                                                                              │
│   Secrets appear as files in the mounted volume                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Installing the CSI Provider

```bash
# Install the Secrets Store CSI Driver
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \
    --namespace kube-system

# Install the Vault CSI Provider
helm install vault hashicorp/vault \
    --namespace vault \
    --set "csi.enabled=true" \
    --set "injector.enabled=false"
```

### Creating a SecretProviderClass

Define which secrets to mount:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-db-creds
  namespace: production
spec:
  provider: vault
  parameters:
    vaultAddress: "https://vault.vault.svc:8200"
    roleName: "myapp"
    objects: |
      - objectName: "db-username"
        secretPath: "secret/data/myapp/db"
        secretKey: "username"
      - objectName: "db-password"
        secretPath: "secret/data/myapp/db"
        secretKey: "password"
```

### Using the SecretProviderClass in a pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  namespace: production
spec:
  serviceAccountName: myapp-sa
  containers:
    - name: myapp
      image: myapp:latest
      volumeMounts:
        - name: secrets-store
          mountPath: "/mnt/secrets"
          readOnly: true
  volumes:
    - name: secrets-store
      csi:
        driver: secrets-store.csi.k8s.io
        readOnly: true
        volumeAttributes:
          secretProviderClass: "vault-db-creds"
```

### Syncing to Kubernetes Secrets

Optionally sync CSI secrets to native Kubernetes Secrets:

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: vault-db-creds
spec:
  provider: vault
  secretObjects:
    - secretName: db-creds-k8s
      type: Opaque
      data:
        - objectName: db-username
          key: username
        - objectName: db-password
          key: password
  parameters:
    vaultAddress: "https://vault.vault.svc:8200"
    roleName: "myapp"
    objects: |
      - objectName: "db-username"
        secretPath: "secret/data/myapp/db"
        secretKey: "username"
      - objectName: "db-password"
        secretPath: "secret/data/myapp/db"
        secretKey: "password"
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Sidecar injection patterns

Different patterns for injecting secrets into applications.

### Pattern 1: Environment file sourcing

Best for shell scripts and applications that can source environment files:

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp"
  vault.hashicorp.com/agent-inject-secret-env: "secret/data/myapp/config"
  vault.hashicorp.com/agent-inject-template-env: |
    {{- with secret "secret/data/myapp/config" -}}
    export DATABASE_URL="{{ .Data.data.database_url }}"
    export API_KEY="{{ .Data.data.api_key }}"
    {{- end }}
```

```yaml
containers:
  - name: myapp
    command: ["/bin/sh", "-c", "source /vault/secrets/env && exec ./myapp"]
```

### Pattern 2: Configuration file injection

Best for applications reading config files:

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp"
  vault.hashicorp.com/agent-inject-secret-config.yaml: "secret/data/myapp/config"
  vault.hashicorp.com/agent-inject-template-config.yaml: |
    {{- with secret "secret/data/myapp/config" -}}
    database:
      host: {{ .Data.data.db_host }}
      port: {{ .Data.data.db_port }}
      username: {{ .Data.data.db_user }}
      password: {{ .Data.data.db_pass }}
    {{- end }}
```

### Pattern 3: Dynamic database credentials

Best for applications needing rotating database credentials:

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp"
  vault.hashicorp.com/agent-inject-secret-db: "database/creds/myapp-role"
  vault.hashicorp.com/agent-inject-template-db: |
    {{- with secret "database/creds/myapp-role" -}}
    DB_USERNAME={{ .Data.username }}
    DB_PASSWORD={{ .Data.password }}
    {{- end }}
```

### Pattern 4: TLS certificates

Best for applications needing PKI certificates:

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp"
  vault.hashicorp.com/agent-inject-secret-cert: "pki/issue/myapp"
  vault.hashicorp.com/agent-inject-template-cert: |
    {{- with secret "pki/issue/myapp" "common_name=myapp.example.com" -}}
    {{ .Data.certificate }}
    {{ .Data.ca_chain }}
    {{- end }}
  vault.hashicorp.com/agent-inject-secret-key: "pki/issue/myapp"
  vault.hashicorp.com/agent-inject-template-key: |
    {{- with secret "pki/issue/myapp" "common_name=myapp.example.com" -}}
    {{ .Data.private_key }}
    {{- end }}
```

### Pattern 5: Init container only (no sidecar)

Best for secrets that don't change during pod lifetime:

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp"
  vault.hashicorp.com/agent-pre-populate-only: "true"
  vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud-managed)
- kubectl configured
- Helm 3.x installed

### Setup

Start a local Kubernetes cluster with Vault:

```bash
# Start minikube (if using minikube)
minikube start --memory=4096

# Create vault namespace
kubectl create namespace vault

# Install Vault with injector
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

helm install vault hashicorp/vault \
    --namespace vault \
    --set "server.dev.enabled=true" \
    --set "server.dev.devRootToken=root" \
    --set "injector.enabled=true"

# Wait for Vault to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=vault -n vault --timeout=120s
```

### Exercise 1: Configure Kubernetes authentication

1. Get the Kubernetes host and CA certificate:

   ```bash
   # Port forward to Vault
   kubectl port-forward svc/vault -n vault 8200:8200 &

   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='root'
   ```

2. Enable and configure Kubernetes auth:

   ```bash
   # Enable Kubernetes auth
   vault auth enable kubernetes

   # Get Kubernetes API info
   K8S_HOST=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

   # Configure Kubernetes auth (from within the Vault pod)
   kubectl exec -n vault vault-0 -- vault write auth/kubernetes/config \
       kubernetes_host="https://kubernetes.default.svc"
   ```

3. Create a test policy and role:

   ```bash
   # Create a policy
   vault policy write myapp-policy - <<EOF
   path "secret/data/myapp/*" {
     capabilities = ["read"]
   }
   EOF

   # Create a Kubernetes auth role
   vault write auth/kubernetes/role/myapp \
       bound_service_account_names=myapp-sa \
       bound_service_account_namespaces=default \
       policies=myapp-policy \
       ttl=1h
   ```

4. Create a test secret:

   ```bash
   vault kv put secret/myapp/config \
       db_host="postgres.example.com" \
       db_user="myapp" \
       db_pass="secretpassword123"
   ```

**Observation:** The Kubernetes auth method is now configured and ready for pods to authenticate.

### Exercise 2: Deploy application with Agent Injector

1. Create the service account:

   ```bash
   kubectl create serviceaccount myapp-sa
   ```

2. Deploy a test application with injection annotations:

   ```bash
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: myapp-test
     annotations:
       vault.hashicorp.com/agent-inject: "true"
       vault.hashicorp.com/role: "myapp"
       vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"
       vault.hashicorp.com/agent-inject-template-config: |
         {{- with secret "secret/data/myapp/config" -}}
         DB_HOST={{ .Data.data.db_host }}
         DB_USER={{ .Data.data.db_user }}
         DB_PASS={{ .Data.data.db_pass }}
         {{- end }}
   spec:
     serviceAccountName: myapp-sa
     containers:
       - name: myapp
         image: busybox:latest
         command: ["/bin/sh", "-c", "cat /vault/secrets/config && sleep 3600"]
   EOF
   ```

3. Verify the secrets were injected:

   ```bash
   # Wait for pod to be ready
   kubectl wait --for=condition=ready pod/myapp-test --timeout=120s

   # Check the injected secrets
   kubectl exec myapp-test -c myapp -- cat /vault/secrets/config
   ```

**Observation:** The output should show the rendered secrets with database credentials.

### Exercise 3: Update secrets and observe refresh

1. Update the secret in Vault:

   ```bash
   vault kv put secret/myapp/config \
       db_host="postgres-new.example.com" \
       db_user="myapp" \
       db_pass="newpassword456"
   ```

2. Check the updated secrets in the pod:

   ```bash
   # The agent refreshes secrets automatically (default 5 minutes)
   # Or force a restart
   kubectl delete pod myapp-test

   # Recreate the pod
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: Pod
   metadata:
     name: myapp-test
     annotations:
       vault.hashicorp.com/agent-inject: "true"
       vault.hashicorp.com/role: "myapp"
       vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"
       vault.hashicorp.com/agent-inject-template-config: |
         {{- with secret "secret/data/myapp/config" -}}
         DB_HOST={{ .Data.data.db_host }}
         DB_USER={{ .Data.data.db_user }}
         DB_PASS={{ .Data.data.db_pass }}
         {{- end }}
   spec:
     serviceAccountName: myapp-sa
     containers:
       - name: myapp
         image: busybox:latest
         command: ["/bin/sh", "-c", "cat /vault/secrets/config && sleep 3600"]
   EOF

   kubectl wait --for=condition=ready pod/myapp-test --timeout=120s
   kubectl exec myapp-test -c myapp -- cat /vault/secrets/config
   ```

**Observation:** The pod now shows the updated credentials.

### Cleanup

```bash
# Delete the test pod
kubectl delete pod myapp-test

# Delete the service account
kubectl delete serviceaccount myapp-sa

# Uninstall Vault
helm uninstall vault -n vault

# Delete the namespace
kubectl delete namespace vault

# Stop port-forward
pkill -f "port-forward.*vault"
```

---

## Key takeaways

1. **Multiple integration methods** - Choose between Agent Injector, CSI Provider, or direct API based on your requirements
2. **Kubernetes auth is foundational** - All methods rely on the Kubernetes authentication backend to validate pod identities
3. **Agent Injector is the most flexible** - Supports templates, automatic refresh, and works with any application
4. **CSI Provider integrates natively** - Uses standard Kubernetes volume mounts but has limited refresh capabilities
5. **Service accounts are critical** - Properly configure and scope service accounts for least-privilege access
6. **Use annotations carefully** - Each annotation controls specific injection behavior
7. **Consider refresh patterns** - Dynamic secrets with the Agent Injector automatically refresh; CSI requires pod restart

---

[← Back to Track B: Infrastructure](./README.md) | [Next: Terraform Provider →](./17-terraform-provider.md)
