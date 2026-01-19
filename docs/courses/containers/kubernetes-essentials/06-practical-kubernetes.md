# Practical Kubernetes deployments

> **Module:** Kubernetes Essentials | **Level:** Advanced | **Time:** 30 minutes

## Learning objectives

By the end of this section, you will be able to:

- Deploy a complete application to Kubernetes
- Implement production patterns
- Handle common deployment scenarios
- Migrate from Docker Compose

---

## From Docker Compose to Kubernetes

### Example Compose file

```yaml
# compose.yaml
services:
  api:
    image: myapi:v1
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### Converted to Kubernetes

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: myapp
type: Opaque
stringData:
  postgres-password: pass
  database-url: postgres://user:pass@postgres:5432/app
---
# postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: myapp
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: postgres-password
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: myapp
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
    - port: 5432
---
# redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: myapp
spec:
  selector:
    app: redis
  ports:
    - port: 6379
---
# api.yaml
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
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: database-url
            - name: REDIS_URL
              value: redis://redis:6379
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
```

---

## Conversion tools

### Kompose

```bash
# Install kompose
brew install kompose  # macOS

# Convert compose file
kompose convert

# Convert and deploy
kompose up

# Convert with specific options
kompose convert -f compose.yaml --out ./k8s/
```

---

## Production deployment patterns

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2
  # or maxUnavailable: 1
  selector:
    matchLabels:
      app: api
```

### Resource quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "100"
    services: "20"
```

### Limit ranges

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "2"
        memory: "2Gi"
      min:
        cpu: "50m"
        memory: "64Mi"
```

---

## Complete production example

```yaml
# kustomization.yaml structure:
# base/
#   kustomization.yaml
#   namespace.yaml
#   deployment.yaml
#   service.yaml
# overlays/
#   production/
#     kustomization.yaml
#     replicas.yaml
#   staging/
#     kustomization.yaml

# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
  - ingress.yaml

configMapGenerator:
  - name: app-config
    literals:
      - LOG_LEVEL=info

secretGenerator:
  - name: app-secrets
    type: Opaque
    literals:
      - API_KEY=placeholder
---
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

namespace: production

patches:
  - path: replicas.yaml

configMapGenerator:
  - name: app-config
    behavior: merge
    literals:
      - LOG_LEVEL=warn

images:
  - name: myapi
    newTag: v1.2.3
---
# overlays/production/replicas.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 5
```

Deploy with Kustomize:
```bash
kubectl apply -k overlays/production/
```

---

## Deployment workflow

### Development

```bash
# Start local cluster
minikube start

# Build image in minikube
eval $(minikube docker-env)
docker build -t myapi:dev .

# Deploy
kubectl apply -f k8s/

# Port forward for testing
kubectl port-forward svc/api 5000:80
```

### Staging

```bash
# Deploy to staging
kubectl apply -k overlays/staging/

# Run tests
kubectl run test --image=test-runner --rm -it -- ./run-tests.sh
```

### Production

```bash
# Deploy with Helm
helm upgrade --install myapp ./charts/myapp \
    --namespace production \
    --values values-production.yaml \
    --set image.tag=$VERSION \
    --atomic \
    --timeout 5m

# Verify
kubectl rollout status deployment/api -n production
```

---

## Troubleshooting checklist

### Pod not starting

```bash
# Check pod status
kubectl get pods -l app=api
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by=.lastTimestamp

# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Crashed container
```

### Service not reachable

```bash
# Check service
kubectl get svc api
kubectl describe svc api

# Check endpoints
kubectl get endpoints api

# Test DNS
kubectl run test --image=busybox --rm -it -- nslookup api
```

### Resource issues

```bash
# Check resource usage
kubectl top pods
kubectl top nodes

# Check resource quotas
kubectl describe resourcequota

# Check events for OOM
kubectl get events | grep -i oom
```

---

## Key takeaways

1. **Compose to K8s** is straightforward with proper mapping
2. **Use Kustomize or Helm** for environment-specific config
3. **Add resource requests/limits** to all containers
4. **Implement HPA** for automatic scaling
5. **Use PDBs** for high availability

---

## What's next

Review Kubernetes concepts with the quiz.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Helm Basics](05-helm-basics.md) | [Course Overview](../course_overview.md) | [Kubernetes Quiz](quiz.md) |
