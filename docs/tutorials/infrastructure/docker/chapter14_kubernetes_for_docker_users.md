# Chapter 14: Kubernetes Concepts for Docker Users

If you know Docker, you're already halfway to understanding Kubernetes. This chapter maps Docker concepts to Kubernetes equivalents.

## Docker → Kubernetes Mapping

| Docker Concept | Kubernetes Equivalent | Description |
| :--- | :--- | :--- |
| Container | Container | Same concept |
| Image | Image | Same concept |
| `docker run` | Pod | Smallest deployable unit (1+ containers) |
| `docker-compose.yml` | Deployment + Service | Desired state definition |
| `docker service` | Deployment | Manages replicas and updates |
| Port mapping (`-p`) | Service | Exposes pods to network |
| Volume | PersistentVolume (PV) | Storage abstraction |
| Network | Network Policy / Service | Pod-to-pod communication |

---

## Core Kubernetes Objects

### Pod

A Pod is one or more containers that share storage and network. It's the atomic unit in Kubernetes.

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx:alpine
      ports:
        - containerPort: 80
```

```bash
kubectl apply -f pod.yaml
kubectl get pods
kubectl delete pod nginx-pod
```

> [!NOTE]
> You rarely create Pods directly. Use Deployments instead.

### Deployment

A Deployment manages a set of identical Pods (replicas) and handles updates.

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          ports:
            - containerPort: 80
```

```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl scale deployment web --replicas=5
```

### Service

A Service exposes Pods to the network (like `docker run -p`).

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: LoadBalancer  # or NodePort, ClusterIP
  selector:
    app: web  # Matches pods with this label
  ports:
    - port: 80
      targetPort: 80
```

```bash
kubectl apply -f service.yaml
kubectl get services
```

---

## Common kubectl Commands

| Task | Docker | Kubernetes |
| :--- | :--- | :--- |
| Run container | `docker run nginx` | `kubectl run nginx --image=nginx` |
| List running | `docker ps` | `kubectl get pods` |
| View logs | `docker logs <id>` | `kubectl logs <pod>` |
| Exec into container | `docker exec -it <id> sh` | `kubectl exec -it <pod> -- sh` |
| Scale | `docker service scale` | `kubectl scale deployment` |
| Delete | `docker rm` | `kubectl delete pod` |

---

## Getting Started Locally

### Install Minikube or Docker Desktop Kubernetes

```bash
# Minikube (cross-platform)
minikube start

# Docker Desktop: Enable Kubernetes in settings
```

### Deploy Your First App

```bash
# Create a deployment
kubectl create deployment web --image=nginx:alpine

# Expose it
kubectl expose deployment web --port=80 --type=NodePort

# Get the URL
minikube service web --url
# or
kubectl get services
```

---

## Volumes in Kubernetes

### PersistentVolumeClaim (PVC)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

### Use in Deployment

```yaml
spec:
  containers:
    - name: db
      image: postgres:15
      volumeMounts:
        - mountPath: /var/lib/postgresql/data
          name: db-data
  volumes:
    - name: db-data
      persistentVolumeClaim:
        claimName: db-storage
```

---

## ConfigMaps and Secrets

### ConfigMap (Non-sensitive config)

```bash
kubectl create configmap app-config --from-literal=DEBUG=true
```

### Secret (Sensitive data)

```bash
kubectl create secret generic db-secret --from-literal=password=mysecret
```

### Use in Pod

```yaml
env:
  - name: DEBUG
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: DEBUG
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password
```

---

## Summary

| Kubernetes Object | Purpose |
| :--- | :--- |
| **Pod** | Run containers |
| **Deployment** | Manage replicas and updates |
| **Service** | Network access to pods |
| **ConfigMap** | Non-sensitive configuration |
| **Secret** | Sensitive data |
| **PVC** | Persistent storage |

**Next Chapter:** Optimize your development workflow in **Chapter 15: Docker-Driven Dev Workflow**.
