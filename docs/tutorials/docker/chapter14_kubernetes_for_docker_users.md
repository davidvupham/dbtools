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

Expose the Deployment with a Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
  type: NodePort  # or LoadBalancer in cloud
```

Notes:
- `docker run -p 8080:80` → in K8s, create a Service (and Ingress for HTTP).
- `docker logs` → `kubectl logs deployment/web` (or pod name).
- `docker exec` → `kubectl exec -it <pod> -- sh`.
