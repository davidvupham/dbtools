# DCA exam checklist

> **Module:** Certification | **Level:** Advanced | **Time:** 15 minutes

## Use this checklist to track your exam preparation progress.

---

## Domain 1: Orchestration (25%)

### Swarm setup and management

- [ ] Initialize a Swarm cluster
- [ ] Add manager and worker nodes
- [ ] Drain nodes for maintenance
- [ ] Remove nodes from cluster
- [ ] Backup and restore Swarm

### Service management

- [ ] Create services with `docker service create`
- [ ] Scale services up and down
- [ ] Configure rolling updates
- [ ] Perform rollbacks
- [ ] Inspect service logs

### Stacks

- [ ] Deploy stacks with `docker stack deploy`
- [ ] Use compose files for stacks
- [ ] Manage stack services
- [ ] Remove stacks

### Networking in Swarm

- [ ] Create overlay networks
- [ ] Understand routing mesh
- [ ] Configure service discovery
- [ ] Use ingress networking

---

## Domain 2: Image creation and management (20%)

### Dockerfile

- [ ] Write efficient Dockerfiles
- [ ] Use multi-stage builds
- [ ] Understand build cache
- [ ] Use .dockerignore
- [ ] Set ENTRYPOINT vs CMD

### Image operations

- [ ] Build images with `docker build`
- [ ] Tag images appropriately
- [ ] Push to registries
- [ ] Pull from registries
- [ ] Inspect image layers with `docker history`

### Best practices

- [ ] Minimize image layers
- [ ] Use official base images
- [ ] Run as non-root user
- [ ] Handle secrets properly

---

## Domain 3: Installation and configuration (15%)

### Installation

- [ ] Install Docker Engine on Linux
- [ ] Configure Docker to start on boot
- [ ] Upgrade Docker Engine
- [ ] Uninstall Docker Engine

### Daemon configuration

- [ ] Configure /etc/docker/daemon.json
- [ ] Set storage driver
- [ ] Configure logging driver
- [ ] Set default network options
- [ ] Configure registry mirrors

### Namespaces and cgroups

- [ ] Understand namespace isolation
- [ ] Configure user namespaces
- [ ] Understand cgroup limits

---

## Domain 4: Networking (15%)

### Network drivers

- [ ] Bridge networks
- [ ] Overlay networks
- [ ] Host network
- [ ] Macvlan networks
- [ ] None network

### Network operations

- [ ] Create custom networks
- [ ] Connect containers to networks
- [ ] Publish ports
- [ ] Configure DNS
- [ ] Troubleshoot network issues

### Network security

- [ ] Isolate networks
- [ ] Use encrypted overlay networks
- [ ] Configure firewall rules

---

## Domain 5: Security (15%)

### Image security

- [ ] Scan images for vulnerabilities
- [ ] Use Docker Content Trust
- [ ] Sign images
- [ ] Pull from trusted registries

### Runtime security

- [ ] Use read-only containers
- [ ] Drop capabilities
- [ ] Configure seccomp profiles
- [ ] Use AppArmor/SELinux
- [ ] Run as non-root

### Secrets management

- [ ] Create secrets
- [ ] Use secrets in services
- [ ] Rotate secrets
- [ ] Manage secret access

### TLS configuration

- [ ] Configure TLS for daemon
- [ ] Set up client certificates
- [ ] Protect Docker socket

---

## Domain 6: Storage and volumes (10%)

### Volume types

- [ ] Named volumes
- [ ] Bind mounts
- [ ] tmpfs mounts

### Volume operations

- [ ] Create volumes
- [ ] Mount volumes to containers
- [ ] Share volumes between containers
- [ ] Backup and restore volumes

### Storage drivers

- [ ] Understand overlay2
- [ ] Configure storage driver
- [ ] Troubleshoot storage issues

---

## Command reference

### Must-know commands

```bash
# Containers
docker run, start, stop, rm
docker exec, logs, inspect
docker ps, top, stats

# Images
docker build, tag, push, pull
docker images, history, inspect
docker save, load

# Swarm
docker swarm init, join, leave
docker node ls, inspect, update
docker service create, update, scale
docker stack deploy, ls, rm

# Networks
docker network create, ls, inspect
docker network connect, disconnect

# Volumes
docker volume create, ls, inspect, rm

# Security
docker secret create, ls, inspect, rm
docker trust sign, inspect

# System
docker info, version
docker system df, prune
```

### Important flags

```bash
# docker run
-d          # Detached
-it         # Interactive terminal
-p 80:80    # Port mapping
-v vol:/data # Volume mount
--name      # Container name
--network   # Network
-e VAR=val  # Environment variable
--rm        # Remove on exit
-m 512m     # Memory limit
--cpus 2    # CPU limit

# docker service create
--replicas 3        # Number of replicas
--publish 80:80     # Publish port
--network app-net   # Network
--secret mysecret   # Secret
--constraint        # Placement constraint
--update-parallelism # Update parallelism
--update-delay      # Delay between updates
```

---

## Pre-exam checklist

### One week before

- [ ] Review all domains
- [ ] Take full practice exam
- [ ] Identify weak areas
- [ ] Schedule lab time

### Day before

- [ ] Rest well
- [ ] Prepare workspace
- [ ] Test internet connection
- [ ] Review quick reference

### Exam day

- [ ] Valid ID ready
- [ ] Quiet environment
- [ ] Computer meets requirements
- [ ] Browser configured

---

## Good luck!

You've prepared well. Trust your knowledge and take your time with each question.

Remember:
- Read questions carefully
- Eliminate wrong answers
- Flag and return to difficult questions
- Don't change answers unless certain
