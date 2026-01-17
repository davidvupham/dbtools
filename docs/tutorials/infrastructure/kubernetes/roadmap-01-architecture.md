# Kubernetes Architecture

## Introduction
Kubernetes (K8s) is the industry standard for container orchestration.

## Core Components

### Master Node (Control Plane)
- **API Server**: The entry point for all REST commands.
- **Etcd**: Key-value store for cluster data.
- **Scheduler**: Assigns pods to nodes.
- **Controller Manager**: Maintains cluster state.

### Worker Node
- **Kubelet**: Ensures containers are running in a Pod.
- **Kube-proxy**: Network proxy.
- **Container Runtime**: Docker or containerd.

### Fundamental Resources
- **Pod**: The smallest deployable unit. One or more containers.
- **Service**: Network abstraction over a set of Pods.
- **Namespace**: Virtual cluster inside a physical cluster.
