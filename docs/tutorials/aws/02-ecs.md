# AWS ECS (Elastic Container Service)

## Introduction
ECS is a fully managed container orchestration service. It is often simpler than Kubernetes.

## Key Components

### Clusters
A logical grouping of tasks or services. Can run on EC2 instances or Fargate (serverless).

### Task Definitions
The blueprint for your application. Similar to a Docker Compose file. Defines image, CPU/memory, ports.

### Services
Maintains a specified number of instances of a Task Definition. Handles restarting failed tasks.

### Load Balancing
ECS services can integrate with Application Load Balancers (ALB) to distribute traffic.
