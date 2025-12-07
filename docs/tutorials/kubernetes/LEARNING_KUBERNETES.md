# Learning Kubernetes on WSL: A Hands-on Guide

This guide is designed to help you learn Kubernetes concepts by doing, specifically tailored for a generic Windows Subsystem for Linux (WSL) environment.

## 1. Prerequisites & Installation

Before we dive into concepts, let's get your environment ready. You need two main tools:

1. **Docker**: The foundation. You should have Docker Desktop for Windows installed and integrated with your WSL distro, or Docker Engine installed directly in WSL.
2. **kubectl**: The command-line tool for interacting with Kubernetes clusters.
3. **Kind (Kubernetes in Docker)**: A tool for running local Kubernetes clusters using Docker container "nodes".

### Installing Tools in WSL

Run the following commands in your WSL terminal to install `kubectl` and `kind`.

#### 1. Install kubectl

```bash
# Download the latest stable release
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Clean up
rm kubectl

# Verify installation
kubectl version --client
```

#### 2. Install Kind

```bash
# Download Kind for AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64

# Make it executable
chmod +x ./kind

# Move to your path
sudo mv ./kind /usr/local/bin/kind

# Verify installation
kind --version
```

## 2. Core Concepts: The "What" and "Why"

* **Cluster**: A set of worker machines, called nodes, that run containerized applications.
* **Pod**: The smallest deployable unit in Kubernetes. A Pod usually contains one application container (like your Docker container).
* **Deployment**: Manages your Pods. It ensures the specified number of Pod "replicas" are running. If a Pod dies, the Deployment starts a new one.
* **Service**: An abstract way to expose an application running on a set of Pods as a network service. Since Pods die and get new IPs, Services give you a stable address to hit.

## 3. Hands-on: Your First Cluster

Now, let's create a cluster.

```bash
kind create cluster --name learn-k8s
```

Check if your cluster is running:

```bash
kubectl cluster-info
kubectl get nodes
```

## 4. Exercise: Hello World

 We will deploy a simple Nginx web server.

### Step 1: Create the Deployment

Save the following as `docs/tutorials/kubernetes/hello-world/deployment.yaml` (or use the file provided in this repo).

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2
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
        ports:
        - containerPort: 80
```

Apply it:

```bash
kubectl apply -f docs/tutorials/kubernetes/hello-world/deployment.yaml
```

Check your pods:

```bash
kubectl get pods -w
# Press Ctrl+C to stop watching when they are 'Running'
```

### Step 2: Expose it with a Service

Pods are ephemeral. Let's create a Service to access them. Save this as `service.yaml`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30007
```

Apply it:

```bash
kubectl apply -f docs/tutorials/kubernetes/hello-world/service.yaml
```

### Step 3: Accessing the Service

In a typical cloud setup, `LoadBalancer` type services give you a real IP. In `kind` on WSL, we can use `kubectl port-forward` to easily access our service.

```bash
# Forward local port 8080 to the service port 80
kubectl port-forward service/nginx-service 8080:80
```

Now open your browser to `http://localhost:8080`. You should see the "Welcome to nginx!" page.

## 5. Cleanup

To delete the cluster when you are done:

```bash
kind delete cluster --name learn-k8s
```
