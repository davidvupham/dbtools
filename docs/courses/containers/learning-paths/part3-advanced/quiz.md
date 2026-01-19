# Part 3: Advanced quiz

> **Module:** Part 3 - Advanced | **Type:** Interactive Assessment | **Questions:** 22

Test your advanced container orchestration and operations knowledge. Select your answer for each question, then click to reveal the correct answer and explanation.

**Instructions:**
1. Read each question and choose your answer (A, B, C, or D)
2. Click "Show Answer" to reveal the correct answer and explanation
3. Keep track of your correct answers
4. Calculate your percentage at the end

---

## Section 1: Docker Swarm

### Question 1

What is the minimum recommended number of manager nodes for a production Swarm cluster?

- A) 1
- B) 3
- C) 5
- D) 7

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

3

**Explanation:** 3 manager nodes provide fault tolerance for 1 manager failure. Raft consensus requires a majority, so 3 nodes can tolerate 1 failure, 5 can tolerate 2, and 7 can tolerate 3.

</details>

---

### Question 2

What command creates a service that runs on every node in the cluster?

- A) `docker service create --replicas all`
- B) `docker service create --global`
- C) `docker service create --mode global`
- D) `docker service create --mode=replicated --all-nodes`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`docker service create --mode global`

**Explanation:** The `--mode global` flag creates a global service that runs exactly one task on every node in the swarm.

</details>

---

### Question 3

What does the routing mesh do in Docker Swarm?

- A) Routes traffic between containers on the same node
- B) Load balances external traffic to any node to service tasks
- C) Creates encrypted tunnels between nodes
- D) Manages DNS resolution

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Load balances external traffic to any node to service tasks.

**Explanation:** The routing mesh enables any node in the swarm to accept connections to published ports and route them to healthy service tasks, even if the task isn't running on that node.

</details>

---

## Section 2: Stacks and services

### Question 4

What is NOT supported in Docker Stack files?

- A) deploy configurations
- B) build directives
- C) secrets
- D) networks

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

build directives

**Explanation:** Stack files don't support `build:` directives. You must use pre-built images. This is because stacks are deployed to a cluster where builds would need to happen on multiple nodes.

</details>

---

### Question 5

Which update order starts new tasks before stopping old ones?

- A) start-first
- B) stop-first
- C) parallel
- D) sequential

<details>
<summary>Show Answer</summary>

**Correct Answer: A**

start-first

**Explanation:** `start-first` (the default for services) starts a new task before stopping the old one, ensuring capacity is maintained during updates. `stop-first` stops the old task before starting the new one.

</details>

---

### Question 6

What happens when a rolling update exceeds `max_failure_ratio`?

- A) The update continues
- B) The service stops
- C) The update performs the configured failure_action
- D) An alert is sent

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

The update performs the configured failure_action.

**Explanation:** When the failure ratio exceeds `max_failure_ratio`, the update performs the configured `failure_action` (pause, continue, or rollback).

</details>

---

## Section 3: Security

### Question 7

Which capability should always be dropped in production containers?

- A) NET_BIND_SERVICE
- B) ALL (then add back only what's needed)
- C) CHOWN
- D) SETUID

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

ALL (then add back only what's needed)

**Explanation:** Best practice is to drop ALL capabilities and add back only those specifically required. This follows the principle of least privilege.

</details>

---

### Question 8

What does `--security-opt no-new-privileges:true` do?

- A) Prevents the container from creating new users
- B) Prevents processes from gaining privileges through setuid/setgid
- C) Disables root access
- D) Prevents network access

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Prevents processes from gaining privileges through setuid/setgid.

**Explanation:** `no-new-privileges` prevents processes inside the container from gaining additional privileges through setuid/setgid binaries or file capabilities.

</details>

---

### Question 9

Which is the most secure base image option?

- A) ubuntu:latest
- B) alpine:latest
- C) gcr.io/distroless/static
- D) debian:slim

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

gcr.io/distroless/static

**Explanation:** Distroless images contain only the application and its runtime dependencies, with no shell or package manager, minimizing the attack surface.

</details>

---

## Section 4: Networking

### Question 10

What makes an overlay network "internal"?

- A) It can only be used by Swarm services
- B) It requires authentication
- C) Containers on it cannot access external networks
- D) It's encrypted

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Containers on it cannot access external networks.

**Explanation:** Setting `internal: true` on a network prevents containers connected to it from accessing external networks, including the internet.

</details>

---

### Question 11

Which network driver allows containers to have their own MAC address?

- A) bridge
- B) overlay
- C) macvlan
- D) host

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

macvlan

**Explanation:** Macvlan gives each container its own MAC address, making them appear as physical devices on the network.

</details>

---

### Question 12

What port does VXLAN use for overlay network traffic?

- A) 2377
- B) 7946
- C) 4789
- D) 443

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

4789

**Explanation:** VXLAN (Virtual Extensible LAN) uses UDP port 4789 for overlay network traffic between nodes.

</details>

---

## Section 5: Storage

### Question 13

What is the recommended storage driver for most Linux distributions?

- A) aufs
- B) overlay2
- C) devicemapper
- D) btrfs

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

overlay2

**Explanation:** overlay2 is the recommended storage driver for modern Linux distributions. It's efficient, well-supported, and works on most filesystems.

</details>

---

### Question 14

How do you ensure a database service always runs on the same node for data persistence?

- A) Use a global service
- B) Use placement constraints with node labels
- C) Use replicas: 1
- D) Use bind mounts

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Use placement constraints with node labels.

**Explanation:** Using placement constraints with node labels ensures the service runs on a specific node where its data volume is located.

</details>

---

## Section 6: CI/CD

### Question 15

What is the purpose of multi-stage builds in CI/CD?

- A) To run multiple containers
- B) To deploy to multiple environments
- C) To create smaller production images by separating build and runtime
- D) To run parallel pipelines

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

To create smaller production images by separating build and runtime.

**Explanation:** Multi-stage builds allow you to use full build environments in early stages while copying only necessary artifacts to minimal production images.

</details>

---

### Question 16

In a canary deployment, what percentage of traffic typically goes to the canary first?

- A) 50%
- B) 25%
- C) 5-10%
- D) 1%

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

5-10%

**Explanation:** Canary deployments typically start with 5-10% of traffic to limit blast radius while still getting meaningful feedback.

</details>

---

## Section 7: Monitoring

### Question 17

Which component scrapes metrics from targets in a Prometheus setup?

- A) Alertmanager
- B) Grafana
- C) Prometheus server
- D) Exporters

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Prometheus server

**Explanation:** The Prometheus server scrapes metrics from configured targets. Exporters expose metrics, Grafana visualizes them, and Alertmanager handles alerts.

</details>

---

### Question 18

What deploy mode should cAdvisor use to monitor all nodes?

- A) replicated with high replica count
- B) global
- C) single
- D) daemon

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

global

**Explanation:** Global mode ensures cAdvisor runs on every node in the cluster, collecting container metrics from each.

</details>

---

## Section 8: Orchestration patterns

### Question 19

In a blue-green deployment, what is the "green" environment?

- A) The current production environment
- B) The new version being deployed
- C) The staging environment
- D) The rollback environment

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

The new version being deployed.

**Explanation:** In blue-green deployments, "blue" is typically the current production environment, and "green" is the new version. Traffic is switched from blue to green after verification.

</details>

---

### Question 20

What is the purpose of the `monitor` option in update_config?

- A) To send metrics to Prometheus
- B) To display update progress
- C) To observe task health for a period before continuing
- D) To log update events

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

To observe task health for a period before continuing.

**Explanation:** The `monitor` duration specifies how long to observe tasks after each batch is updated before proceeding to the next batch.

</details>

---

### Question 21

What pattern runs a helper container alongside the main application container?

- A) Ambassador
- B) Sidecar
- C) Adapter
- D) Init container

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Sidecar

**Explanation:** The sidecar pattern adds a helper container that runs alongside and supports the main container, often for logging, monitoring, or proxying.

</details>

---

### Question 22

What is the recommended approach for stateful services in Swarm?

- A) Use replicated mode with many replicas
- B) Pin to specific nodes with persistent volumes
- C) Use global mode
- D) Use ephemeral storage

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Pin to specific nodes with persistent volumes.

**Explanation:** Stateful services should be pinned to specific nodes (using placement constraints) where their persistent storage is located, typically with replicas: 1.

</details>

---

## Score tracker

Use this section to calculate your final score.

### Tally your results

| Section | Questions | Your Correct Answers |
|---------|-----------|---------------------|
| Docker Swarm | 1-3 | ___ / 3 |
| Stacks and Services | 4-6 | ___ / 3 |
| Security | 7-9 | ___ / 3 |
| Networking | 10-12 | ___ / 3 |
| Storage | 13-14 | ___ / 2 |
| CI/CD | 15-16 | ___ / 2 |
| Monitoring | 17-18 | ___ / 2 |
| Orchestration Patterns | 19-22 | ___ / 4 |
| **Total** | | ___ / 22 |

### Calculate your percentage

**Your Score: ___ / 22 = ____%**

(Divide your correct answers by 22 and multiply by 100)

### How did you do?

| Score | Percentage | Level | Recommendation |
|-------|------------|-------|----------------|
| 20-22 | 90-100% | Expert | Ready for production orchestration |
| 16-19 | 73-89% | Proficient | Strong advanced knowledge |
| 12-15 | 55-72% | Developing | Review specific topics |
| Below 12 | Below 55% | Needs Review | Revisit Part 3 materials |

---

## Next steps

Congratulations on completing the advanced section! Consider:

1. **DCA Certification** - Take the Docker Certified Associate exam
2. **Kubernetes** - Explore container orchestration at scale
3. **Real projects** - Apply these concepts to production systems

Continue to: [Kubernetes Essentials](../../kubernetes-essentials/)
