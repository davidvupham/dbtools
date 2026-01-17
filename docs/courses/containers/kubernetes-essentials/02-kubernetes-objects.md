# Kubernetes objects

> **Module:** Kubernetes Essentials | **Level:** Advanced | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Create and manage Pods
- Deploy applications with Deployments
- Expose services to the network
- Use ConfigMaps and Secrets

---

## Pods

### What is a Pod?

A Pod is the smallest deployable unit in Kubernetes, containing one or more containers.

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: myapp
    environment: dev
spec:
  containers:
    - name: main
      image: nginx:alpine
      ports:
        - containerPort: 80
      resources:
        requests:
          memory: "64Mi"
          cpu: "250m"
        limits:
          memory: "128Mi"
          cpu: "500m"
```

### Pod lifecycle

```mermaid
graph LR
    A[Pending] --> B[Running]
    B --> C[Succeeded]
    B --> D[Failed]
    A --> D
```

### Multi-container Pods

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container
spec:
  containers:
    - name: main
      image: nginx:alpine
      ports:
        - containerPort: 80
    - name: sidecar
      image: fluent-bit
      volumeMounts:
        - name: logs
          mountPath: /var/log/nginx
  volumes:
    - name: logs
      emptyDir: {}
```

---

## Deployments

### Creating Deployments

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: myapi:v1
          ports:
            - containerPort: 5000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 15
            periodSeconds: 20
```

### Managing Deployments

```bash
# Apply deployment
kubectl apply -f deployment.yaml

# Check status
kubectl get deployments
kubectl get pods -l app=api

# Scale
kubectl scale deployment api --replicas=5

# Update image
kubectl set image deployment/api api=myapi:v2

# Rollout status
kubectl rollout status deployment/api

# Rollback
kubectl rollout undo deployment/api

# History
kubectl rollout history deployment/api
```

### Update strategies

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max pods above desired
      maxUnavailable: 0  # Max pods below desired
```

---

## Services

### Service types

| Type | Description |
|------|-------------|
| ClusterIP | Internal only (default) |
| NodePort | Exposed on each node's IP |
| LoadBalancer | Cloud provider load balancer |
| ExternalName | DNS CNAME record |

### ClusterIP Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 5000
  type: ClusterIP
```

### NodePort Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-nodeport
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 5000
      nodePort: 30080
  type: NodePort
```

### LoadBalancer Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-lb
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 5000
  type: LoadBalancer
```

### Headless Service

For direct pod access without load balancing:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-headless
spec:
  clusterIP: None
  selector:
    app: api
  ports:
    - port: 5000
```

---

## ConfigMaps

### Creating ConfigMaps

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # Simple key-value
  LOG_LEVEL: info
  CACHE_TTL: "300"

  # File content
  config.json: |
    {
      "feature_flags": {
        "new_ui": true,
        "beta_api": false
      }
    }
```

```bash
# From literal
kubectl create configmap app-config --from-literal=LOG_LEVEL=info

# From file
kubectl create configmap nginx-config --from-file=nginx.conf

# From directory
kubectl create configmap configs --from-file=./config/
```

### Using ConfigMaps

```yaml
# As environment variables
spec:
  containers:
    - name: app
      env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
      # Or all at once
      envFrom:
        - configMapRef:
            name: app-config

# As volume
spec:
  containers:
    - name: app
      volumeMounts:
        - name: config
          mountPath: /app/config
  volumes:
    - name: config
      configMap:
        name: app-config
```

---

## Secrets

### Creating Secrets

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  # Base64 encoded
  username: YWRtaW4=
  password: cGFzc3dvcmQxMjM=
```

```bash
# From literal
kubectl create secret generic db-secret \
    --from-literal=username=admin \
    --from-literal=password=password123

# From file
kubectl create secret generic tls-secret \
    --from-file=tls.crt \
    --from-file=tls.key

# TLS secret
kubectl create secret tls my-tls \
    --cert=tls.crt \
    --key=tls.key
```

### Using Secrets

```yaml
# As environment variable
spec:
  containers:
    - name: app
      env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password

# As volume
spec:
  containers:
    - name: app
      volumeMounts:
        - name: secrets
          mountPath: /app/secrets
          readOnly: true
  volumes:
    - name: secrets
      secret:
        secretName: db-secret
```

---

## Namespaces

### Working with namespaces

```bash
# Create namespace
kubectl create namespace production

# List namespaces
kubectl get namespaces

# Set default namespace
kubectl config set-context --current --namespace=production

# Deploy to specific namespace
kubectl apply -f deployment.yaml -n production
```

### Namespace isolation

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
```

---

## Labels and selectors

### Adding labels

```yaml
metadata:
  labels:
    app: api
    environment: production
    version: v2
    team: backend
```

### Selecting by labels

```bash
# Equality-based
kubectl get pods -l app=api
kubectl get pods -l app=api,environment=production

# Set-based
kubectl get pods -l 'environment in (production, staging)'
kubectl get pods -l 'app notin (frontend)'

# Combined
kubectl get pods -l 'app=api,environment in (production, staging)'
```

---

## Practical example: Complete application

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: myapp
data:
  LOG_LEVEL: info
  REDIS_HOST: redis
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: myapp
type: Opaque
stringData:
  DATABASE_URL: postgres://user:pass@postgres:5432/myapp
---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: myapi:v1
          ports:
            - containerPort: 5000
          envFrom:
            - configMapRef:
                name: app-config
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: DATABASE_URL
          resources:
            requests:
              memory: "128Mi"
              cpu: "250m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: myapp
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 5000
  type: ClusterIP
```

---

## Key takeaways

1. **Pods** are the basic unit, but rarely created directly
2. **Deployments** manage replica sets and rolling updates
3. **Services** provide stable networking for pods
4. **ConfigMaps** for configuration, **Secrets** for sensitive data
5. **Namespaces** isolate resources

---

## What's next

Learn about storage in Kubernetes.

Continue to: [03-kubernetes-storage.md](03-kubernetes-storage.md)
