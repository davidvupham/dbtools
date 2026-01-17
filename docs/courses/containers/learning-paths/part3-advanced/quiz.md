# Part 3 advanced quiz

> Test your advanced container orchestration and operations knowledge.

---

## Section 1: Docker Swarm

### Question 1

What is the minimum recommended number of manager nodes for a production Swarm cluster?

- [ ] 1
- [x] 3
- [ ] 5
- [ ] 7

**Explanation:** 3 manager nodes provide fault tolerance for 1 manager failure. Raft consensus requires a majority, so 3 nodes can tolerate 1 failure, 5 can tolerate 2, and 7 can tolerate 3.

---

### Question 2

What command creates a service that runs on every node in the cluster?

- [ ] `docker service create --replicas all`
- [ ] `docker service create --global`
- [x] `docker service create --mode global`
- [ ] `docker service create --mode=replicated --all-nodes`

**Explanation:** The `--mode global` flag creates a global service that runs exactly one task on every node in the swarm.

---

### Question 3

What does the routing mesh do in Docker Swarm?

- [ ] Routes traffic between containers on the same node
- [x] Load balances external traffic to any node to service tasks
- [ ] Creates encrypted tunnels between nodes
- [ ] Manages DNS resolution

**Explanation:** The routing mesh enables any node in the swarm to accept connections to published ports and route them to healthy service tasks, even if the task isn't running on that node.

---

## Section 2: Stacks and services

### Question 4

What is NOT supported in Docker Stack files?

- [ ] deploy configurations
- [x] build directives
- [ ] secrets
- [ ] networks

**Explanation:** Stack files don't support `build:` directives. You must use pre-built images. This is because stacks are deployed to a cluster where builds would need to happen on multiple nodes.

---

### Question 5

Which update order starts new tasks before stopping old ones?

- [x] start-first
- [ ] stop-first
- [ ] parallel
- [ ] sequential

**Explanation:** `start-first` (the default for services) starts a new task before stopping the old one, ensuring capacity is maintained during updates. `stop-first` stops the old task before starting the new one.

---

### Question 6

What happens when a rolling update exceeds `max_failure_ratio`?

- [ ] The update continues
- [ ] The service stops
- [x] The update performs the configured failure_action
- [ ] An alert is sent

**Explanation:** When the failure ratio exceeds `max_failure_ratio`, the update performs the configured `failure_action` (pause, continue, or rollback).

---

## Section 3: Security

### Question 7

Which capability should always be dropped in production containers?

- [ ] NET_BIND_SERVICE
- [x] ALL (then add back only what's needed)
- [ ] CHOWN
- [ ] SETUID

**Explanation:** Best practice is to drop ALL capabilities and add back only those specifically required. This follows the principle of least privilege.

---

### Question 8

What does `--security-opt no-new-privileges:true` do?

- [ ] Prevents the container from creating new users
- [x] Prevents processes from gaining privileges through setuid/setgid
- [ ] Disables root access
- [ ] Prevents network access

**Explanation:** `no-new-privileges` prevents processes inside the container from gaining additional privileges through setuid/setgid binaries or file capabilities.

---

### Question 9

Which is the most secure base image option?

- [ ] ubuntu:latest
- [ ] alpine:latest
- [x] gcr.io/distroless/static
- [ ] debian:slim

**Explanation:** Distroless images contain only the application and its runtime dependencies, with no shell or package manager, minimizing the attack surface.

---

## Section 4: Networking

### Question 10

What makes an overlay network "internal"?

- [ ] It can only be used by Swarm services
- [ ] It requires authentication
- [x] Containers on it cannot access external networks
- [ ] It's encrypted

**Explanation:** Setting `internal: true` on a network prevents containers connected to it from accessing external networks, including the internet.

---

### Question 11

Which network driver allows containers to have their own MAC address?

- [ ] bridge
- [ ] overlay
- [x] macvlan
- [ ] host

**Explanation:** Macvlan gives each container its own MAC address, making them appear as physical devices on the network.

---

### Question 12

What port does VXLAN use for overlay network traffic?

- [ ] 2377
- [ ] 7946
- [x] 4789
- [ ] 443

**Explanation:** VXLAN (Virtual Extensible LAN) uses UDP port 4789 for overlay network traffic between nodes.

---

## Section 5: Storage

### Question 13

What is the recommended storage driver for most Linux distributions?

- [ ] aufs
- [x] overlay2
- [ ] devicemapper
- [ ] btrfs

**Explanation:** overlay2 is the recommended storage driver for modern Linux distributions. It's efficient, well-supported, and works on most filesystems.

---

### Question 14

How do you ensure a database service always runs on the same node for data persistence?

- [ ] Use a global service
- [x] Use placement constraints with node labels
- [ ] Use replicas: 1
- [ ] Use bind mounts

**Explanation:** Using placement constraints with node labels ensures the service runs on a specific node where its data volume is located.

---

## Section 6: CI/CD

### Question 15

What is the purpose of multi-stage builds in CI/CD?

- [ ] To run multiple containers
- [ ] To deploy to multiple environments
- [x] To create smaller production images by separating build and runtime
- [ ] To run parallel pipelines

**Explanation:** Multi-stage builds allow you to use full build environments in early stages while copying only necessary artifacts to minimal production images.

---

### Question 16

In a canary deployment, what percentage of traffic typically goes to the canary first?

- [ ] 50%
- [ ] 25%
- [x] 5-10%
- [ ] 1%

**Explanation:** Canary deployments typically start with 5-10% of traffic to limit blast radius while still getting meaningful feedback.

---

## Section 7: Monitoring

### Question 17

Which component scrapes metrics from targets in a Prometheus setup?

- [ ] Alertmanager
- [ ] Grafana
- [x] Prometheus server
- [ ] Exporters

**Explanation:** The Prometheus server scrapes metrics from configured targets. Exporters expose metrics, Grafana visualizes them, and Alertmanager handles alerts.

---

### Question 18

What deploy mode should cAdvisor use to monitor all nodes?

- [ ] replicated with high replica count
- [x] global
- [ ] single
- [ ] daemon

**Explanation:** Global mode ensures cAdvisor runs on every node in the cluster, collecting container metrics from each.

---

## Section 8: Orchestration patterns

### Question 19

In a blue-green deployment, what is the "green" environment?

- [ ] The current production environment
- [x] The new version being deployed
- [ ] The staging environment
- [ ] The rollback environment

**Explanation:** In blue-green deployments, "blue" is typically the current production environment, and "green" is the new version. Traffic is switched from blue to green after verification.

---

### Question 20

What is the purpose of the `monitor` option in update_config?

- [ ] To send metrics to Prometheus
- [ ] To display update progress
- [x] To observe task health for a period before continuing
- [ ] To log update events

**Explanation:** The `monitor` duration specifies how long to observe tasks after each batch is updated before proceeding to the next batch.

---

### Question 21

What pattern runs a helper container alongside the main application container?

- [ ] Ambassador
- [x] Sidecar
- [ ] Adapter
- [ ] Init container

**Explanation:** The sidecar pattern adds a helper container that runs alongside and supports the main container, often for logging, monitoring, or proxying.

---

### Question 22

What is the recommended approach for stateful services in Swarm?

- [ ] Use replicated mode with many replicas
- [x] Pin to specific nodes with persistent volumes
- [ ] Use global mode
- [ ] Use ephemeral storage

**Explanation:** Stateful services should be pinned to specific nodes (using placement constraints) where their persistent storage is located, typically with replicas: 1.

---

## Scoring

| Score | Rating |
|-------|--------|
| 20-22 | Expert - Ready for production orchestration |
| 16-19 | Proficient - Strong advanced knowledge |
| 12-15 | Developing - Review specific topics |
| Below 12 | Needs review - Revisit Part 3 materials |

---

## Next steps

Congratulations on completing the advanced section! Consider:

1. **DCA Certification** - Take the Docker Certified Associate exam
2. **Kubernetes** - Explore container orchestration at scale
3. **Real projects** - Apply these concepts to production systems

Continue to: [../../kubernetes-essentials/](../../kubernetes-essentials/)
