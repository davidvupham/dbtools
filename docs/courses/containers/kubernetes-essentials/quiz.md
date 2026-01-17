# Kubernetes essentials quiz

> Test your Kubernetes knowledge before diving deeper.

---

## Section 1: Core concepts

### Question 1

What is the smallest deployable unit in Kubernetes?

- [ ] Container
- [x] Pod
- [ ] Deployment
- [ ] Service

**Explanation:** A Pod is the smallest deployable unit. It can contain one or more containers that share storage and network.

---

### Question 2

Which component is responsible for scheduling pods to nodes?

- [ ] kubelet
- [ ] API Server
- [x] Scheduler
- [ ] Controller Manager

**Explanation:** The Scheduler watches for newly created pods and assigns them to nodes based on resource requirements and constraints.

---

### Question 3

What is the purpose of a Deployment?

- [ ] To expose pods to external traffic
- [x] To manage a replicated set of pods with rolling updates
- [ ] To store persistent data
- [ ] To configure networking

**Explanation:** Deployments manage ReplicaSets, providing declarative updates, rolling updates, and rollback capabilities.

---

## Section 2: Services and networking

### Question 4

Which Service type provides external access via a cloud provider's load balancer?

- [ ] ClusterIP
- [ ] NodePort
- [x] LoadBalancer
- [ ] ExternalName

**Explanation:** LoadBalancer type provisions a cloud provider's load balancer, providing external access with a single IP address.

---

### Question 5

What is the DNS name format for a Service named "api" in the "production" namespace?

- [ ] api-production.cluster
- [x] api.production.svc.cluster.local
- [ ] production-api.svc.local
- [ ] api.production

**Explanation:** The full DNS name format is `<service>.<namespace>.svc.cluster.local`.

---

### Question 6

What does a NetworkPolicy with empty podSelector match?

- [x] All pods in the namespace
- [ ] No pods
- [ ] Only pods without labels
- [ ] Pods in all namespaces

**Explanation:** An empty podSelector `{}` matches all pods in the namespace where the NetworkPolicy is defined.

---

## Section 3: Storage

### Question 7

What is the relationship between PV and PVC?

- [ ] PVC creates PV
- [x] PVC requests storage, PV provides it
- [ ] PV requests storage, PVC provides it
- [ ] They are the same thing

**Explanation:** PersistentVolumeClaim (PVC) is a request for storage. PersistentVolume (PV) is the actual storage resource that satisfies the claim.

---

### Question 8

Which access mode allows multiple nodes to mount a volume for reading?

- [ ] ReadWriteOnce
- [x] ReadOnlyMany
- [ ] ReadWriteMany
- [ ] SingleNodeRead

**Explanation:** ReadOnlyMany (ROX) allows the volume to be mounted read-only by many nodes.

---

### Question 9

What Kubernetes resource should you use for a database that needs stable network identity?

- [ ] Deployment
- [x] StatefulSet
- [ ] DaemonSet
- [ ] ReplicaSet

**Explanation:** StatefulSet provides stable network identities, ordered deployment, and persistent storage - all essential for databases.

---

## Section 4: Configuration

### Question 10

What is the main difference between ConfigMap and Secret?

- [ ] ConfigMaps can hold more data
- [ ] Secrets are stored in etcd, ConfigMaps are not
- [x] Secrets are base64 encoded and intended for sensitive data
- [ ] ConfigMaps can only store strings

**Explanation:** Secrets are designed for sensitive data and are base64 encoded. While not encrypted by default, they can be encrypted at rest.

---

### Question 11

How do you inject a ConfigMap value as an environment variable?

- [ ] `env.configMapRef`
- [x] `valueFrom.configMapKeyRef`
- [ ] `envFrom.configMap`
- [ ] `config.envVar`

**Explanation:** Use `valueFrom.configMapKeyRef` to inject a specific key from a ConfigMap as an environment variable.

---

## Section 5: Ingress

### Question 12

What is required for Ingress resources to work?

- [ ] A LoadBalancer service
- [x] An Ingress Controller
- [ ] NodePort services
- [ ] External DNS

**Explanation:** Ingress resources are just configurations. An Ingress Controller (like nginx-ingress or Traefik) is needed to implement the rules.

---

### Question 13

What does the `pathType: Prefix` mean in an Ingress rule?

- [ ] The path must match exactly
- [x] The path and any subpaths are matched
- [ ] The path is treated as a regex
- [ ] The path is case-insensitive

**Explanation:** `Prefix` means `/api` matches `/api`, `/api/`, `/api/users`, etc.

---

## Section 6: Helm

### Question 14

What is a Helm Release?

- [ ] A version of Helm
- [ ] A chart template
- [x] An installed instance of a chart
- [ ] A repository index

**Explanation:** A Release is a running instance of a chart with a specific configuration.

---

### Question 15

Which file contains default values for a Helm chart?

- [ ] Chart.yaml
- [x] values.yaml
- [ ] templates/defaults.yaml
- [ ] config.yaml

**Explanation:** `values.yaml` contains the default configuration values that can be overridden during installation.

---

## Section 7: Operations

### Question 16

What does `kubectl rollout undo deployment/api` do?

- [ ] Deletes the deployment
- [ ] Stops all pods
- [x] Reverts to the previous deployment revision
- [ ] Scales down to zero replicas

**Explanation:** `rollout undo` reverts a deployment to its previous revision, useful for quick rollbacks.

---

### Question 17

Which probe determines if a container should receive traffic?

- [ ] livenessProbe
- [x] readinessProbe
- [ ] startupProbe
- [ ] healthProbe

**Explanation:** readinessProbe determines if a container is ready to receive traffic. Failing it removes the pod from service endpoints.

---

### Question 18

What is the purpose of a PodDisruptionBudget?

- [ ] To limit pod resources
- [ ] To schedule pod evictions
- [x] To ensure minimum availability during disruptions
- [ ] To distribute pods across nodes

**Explanation:** PodDisruptionBudget ensures that a minimum number of pods remain available during voluntary disruptions like upgrades.

---

## Section 8: Architecture

### Question 19

Where is cluster state stored in Kubernetes?

- [ ] API Server
- [x] etcd
- [ ] Controller Manager
- [ ] Each node's kubelet

**Explanation:** etcd is the distributed key-value store that stores all cluster state and configuration.

---

### Question 20

Which component runs on every node and manages containers?

- [x] kubelet
- [ ] Scheduler
- [ ] API Server
- [ ] Controller Manager

**Explanation:** kubelet is the agent that runs on every node, responsible for running containers in pods.

---

## Scoring

| Score | Rating |
|-------|--------|
| 18-20 | Expert - Ready for advanced Kubernetes |
| 14-17 | Proficient - Good foundation |
| 10-13 | Developing - Review specific areas |
| Below 10 | Needs review - Revisit Kubernetes basics |

---

## Next steps

Based on your score:

- **High score:** Explore advanced topics like Operators, Service Mesh
- **Medium score:** Practice with real deployments
- **Lower score:** Review the Kubernetes Essentials materials

Continue learning:
- [CKA/CKAD Certification](https://kubernetes.io/docs/home/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
