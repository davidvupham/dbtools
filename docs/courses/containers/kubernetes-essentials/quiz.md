# Kubernetes essentials quiz

> **Module:** Kubernetes Essentials | **Type:** Interactive Assessment | **Questions:** 20

Test your Kubernetes knowledge before diving deeper. Select your answer for each question, then click to reveal the correct answer and explanation.

**Instructions:**
1. Read each question and choose your answer (A, B, C, or D)
2. Click "Show Answer" to reveal the correct answer and explanation
3. Keep track of your correct answers
4. Calculate your percentage at the end

---

## Section 1: Core concepts

### Question 1

What is the smallest deployable unit in Kubernetes?

- A) Container
- B) Pod
- C) Deployment
- D) Service

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Pod

**Explanation:** A Pod is the smallest deployable unit. It can contain one or more containers that share storage and network.

</details>

---

### Question 2

Which component is responsible for scheduling pods to nodes?

- A) kubelet
- B) API Server
- C) Scheduler
- D) Controller Manager

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Scheduler

**Explanation:** The Scheduler watches for newly created pods and assigns them to nodes based on resource requirements and constraints.

</details>

---

### Question 3

What is the purpose of a Deployment?

- A) To expose pods to external traffic
- B) To manage a replicated set of pods with rolling updates
- C) To store persistent data
- D) To configure networking

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

To manage a replicated set of pods with rolling updates.

**Explanation:** Deployments manage ReplicaSets, providing declarative updates, rolling updates, and rollback capabilities.

</details>

---

## Section 2: Services and networking

### Question 4

Which Service type provides external access via a cloud provider's load balancer?

- A) ClusterIP
- B) NodePort
- C) LoadBalancer
- D) ExternalName

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

LoadBalancer

**Explanation:** LoadBalancer type provisions a cloud provider's load balancer, providing external access with a single IP address.

</details>

---

### Question 5

What is the DNS name format for a Service named "api" in the "production" namespace?

- A) api-production.cluster
- B) api.production.svc.cluster.local
- C) production-api.svc.local
- D) api.production

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

api.production.svc.cluster.local

**Explanation:** The full DNS name format is `<service>.<namespace>.svc.cluster.local`.

</details>

---

### Question 6

What does a NetworkPolicy with empty podSelector match?

- A) All pods in the namespace
- B) No pods
- C) Only pods without labels
- D) Pods in all namespaces

<details>
<summary>Show Answer</summary>

**Correct Answer: A**

All pods in the namespace.

**Explanation:** An empty podSelector `{}` matches all pods in the namespace where the NetworkPolicy is defined.

</details>

---

## Section 3: Storage

### Question 7

What is the relationship between PV and PVC?

- A) PVC creates PV
- B) PVC requests storage, PV provides it
- C) PV requests storage, PVC provides it
- D) They are the same thing

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

PVC requests storage, PV provides it.

**Explanation:** PersistentVolumeClaim (PVC) is a request for storage. PersistentVolume (PV) is the actual storage resource that satisfies the claim.

</details>

---

### Question 8

Which access mode allows multiple nodes to mount a volume for reading?

- A) ReadWriteOnce
- B) ReadOnlyMany
- C) ReadWriteMany
- D) SingleNodeRead

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

ReadOnlyMany

**Explanation:** ReadOnlyMany (ROX) allows the volume to be mounted read-only by many nodes.

</details>

---

### Question 9

What Kubernetes resource should you use for a database that needs stable network identity?

- A) Deployment
- B) StatefulSet
- C) DaemonSet
- D) ReplicaSet

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

StatefulSet

**Explanation:** StatefulSet provides stable network identities, ordered deployment, and persistent storage - all essential for databases.

</details>

---

## Section 4: Configuration

### Question 10

What is the main difference between ConfigMap and Secret?

- A) ConfigMaps can hold more data
- B) Secrets are stored in etcd, ConfigMaps are not
- C) Secrets are base64 encoded and intended for sensitive data
- D) ConfigMaps can only store strings

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Secrets are base64 encoded and intended for sensitive data.

**Explanation:** Secrets are designed for sensitive data and are base64 encoded. While not encrypted by default, they can be encrypted at rest.

</details>

---

### Question 11

How do you inject a ConfigMap value as an environment variable?

- A) `env.configMapRef`
- B) `valueFrom.configMapKeyRef`
- C) `envFrom.configMap`
- D) `config.envVar`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`valueFrom.configMapKeyRef`

**Explanation:** Use `valueFrom.configMapKeyRef` to inject a specific key from a ConfigMap as an environment variable.

</details>

---

## Section 5: Ingress

### Question 12

What is required for Ingress resources to work?

- A) A LoadBalancer service
- B) An Ingress Controller
- C) NodePort services
- D) External DNS

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

An Ingress Controller

**Explanation:** Ingress resources are just configurations. An Ingress Controller (like nginx-ingress or Traefik) is needed to implement the rules.

</details>

---

### Question 13

What does the `pathType: Prefix` mean in an Ingress rule?

- A) The path must match exactly
- B) The path and any subpaths are matched
- C) The path is treated as a regex
- D) The path is case-insensitive

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

The path and any subpaths are matched.

**Explanation:** `Prefix` means `/api` matches `/api`, `/api/`, `/api/users`, etc.

</details>

---

## Section 6: Helm

### Question 14

What is a Helm Release?

- A) A version of Helm
- B) A chart template
- C) An installed instance of a chart
- D) A repository index

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

An installed instance of a chart.

**Explanation:** A Release is a running instance of a chart with a specific configuration.

</details>

---

### Question 15

Which file contains default values for a Helm chart?

- A) Chart.yaml
- B) values.yaml
- C) templates/defaults.yaml
- D) config.yaml

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

values.yaml

**Explanation:** `values.yaml` contains the default configuration values that can be overridden during installation.

</details>

---

## Section 7: Operations

### Question 16

What does `kubectl rollout undo deployment/api` do?

- A) Deletes the deployment
- B) Stops all pods
- C) Reverts to the previous deployment revision
- D) Scales down to zero replicas

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Reverts to the previous deployment revision.

**Explanation:** `rollout undo` reverts a deployment to its previous revision, useful for quick rollbacks.

</details>

---

### Question 17

Which probe determines if a container should receive traffic?

- A) livenessProbe
- B) readinessProbe
- C) startupProbe
- D) healthProbe

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

readinessProbe

**Explanation:** readinessProbe determines if a container is ready to receive traffic. Failing it removes the pod from service endpoints.

</details>

---

### Question 18

What is the purpose of a PodDisruptionBudget?

- A) To limit pod resources
- B) To schedule pod evictions
- C) To ensure minimum availability during disruptions
- D) To distribute pods across nodes

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

To ensure minimum availability during disruptions.

**Explanation:** PodDisruptionBudget ensures that a minimum number of pods remain available during voluntary disruptions like upgrades.

</details>

---

## Section 8: Architecture

### Question 19

Where is cluster state stored in Kubernetes?

- A) API Server
- B) etcd
- C) Controller Manager
- D) Each node's kubelet

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

etcd

**Explanation:** etcd is the distributed key-value store that stores all cluster state and configuration.

</details>

---

### Question 20

Which component runs on every node and manages containers?

- A) kubelet
- B) Scheduler
- C) API Server
- D) Controller Manager

<details>
<summary>Show Answer</summary>

**Correct Answer: A**

kubelet

**Explanation:** kubelet is the agent that runs on every node, responsible for running containers in pods.

</details>

---

## Score tracker

Use this section to calculate your final score.

### Tally your results

| Section | Questions | Your Correct Answers |
|---------|-----------|---------------------|
| Core Concepts | 1-3 | ___ / 3 |
| Services and Networking | 4-6 | ___ / 3 |
| Storage | 7-9 | ___ / 3 |
| Configuration | 10-11 | ___ / 2 |
| Ingress | 12-13 | ___ / 2 |
| Helm | 14-15 | ___ / 2 |
| Operations | 16-18 | ___ / 3 |
| Architecture | 19-20 | ___ / 2 |
| **Total** | | ___ / 20 |

### Calculate your percentage

**Your Score: ___ / 20 = ____%**

(Divide your correct answers by 20 and multiply by 100)

### How did you do?

| Score | Percentage | Level | Recommendation |
|-------|------------|-------|----------------|
| 18-20 | 90-100% | Expert | Ready for advanced Kubernetes |
| 14-17 | 70-89% | Proficient | Good foundation |
| 10-13 | 50-69% | Developing | Review specific areas |
| Below 10 | Below 50% | Needs Review | Revisit Kubernetes basics |

---

## Next steps

Based on your score:

- **High score**: Explore advanced topics like Operators, Service Mesh
- **Medium score**: Practice with real deployments
- **Lower score**: Review the Kubernetes Essentials materials

Continue learning:
- [CKA/CKAD Certification](https://kubernetes.io/docs/home/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Practical Kubernetes](06-practical-kubernetes.md) | [Course Overview](../course_overview.md) | [OpenShift: Introduction](../openshift/01-openshift-introduction.md) |
