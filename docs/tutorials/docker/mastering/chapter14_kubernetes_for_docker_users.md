# Chapter 14: Kubernetes Concepts for Docker Users

- Pods (one or more containers), Deployments, Services
- Container runtimes and images are still used

```yaml
# Minimal Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels: { app: web }
  template:
    metadata: { labels: { app: web } }
    spec:
      containers:
        - name: web
          image: nginxdemos/hello:latest
          ports: [{ containerPort: 80 }]
```

Use this chapter to translate Docker mental models into K8s primitives.
