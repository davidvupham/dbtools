# Kubernetes Controllers

## Introduction
Controllers enable you to run applications more reliably and scalably.

## Deployments
Manages stateless applications. Handles replication and rolling updates.
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
```

## StatefulSets
Manages stateful applications (databases). Ensures stickiness and ordering.

## DaemonSets
Ensures a copy of a Pod runs on all (or some) Nodes. Useful for logging/monitoring agents.
