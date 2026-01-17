# OpenShift quiz

> Test your understanding of OpenShift concepts.

---

## Instructions

- Answer all questions before checking solutions
- Each question has one correct answer unless noted
- Aim for 80% or higher to proceed

---

## Questions

### 1. What is the relationship between OpenShift and Kubernetes?

A) OpenShift is an alternative to Kubernetes
B) OpenShift is a distribution of Kubernetes with additional enterprise features
C) Kubernetes is built on top of OpenShift
D) They are completely separate platforms

---

### 2. Which container runtime does OpenShift use?

A) Docker
B) containerd
C) CRI-O
D) rkt

---

### 3. What is the difference between a Project and a Namespace in OpenShift?

A) They are exactly the same thing
B) Projects are enhanced namespaces with additional metadata and defaults
C) Namespaces are more feature-rich than Projects
D) Projects are only for development, Namespaces for production

---

### 4. Which resource is OpenShift's preferred way to expose services externally?

A) Ingress
B) NodePort
C) Route
D) LoadBalancer

---

### 5. What are the three TLS termination types for Routes?

A) SSL, TLS, HTTPS
B) Edge, Passthrough, Re-encrypt
C) External, Internal, Mixed
D) Client, Server, Mutual

---

### 6. What is Source-to-Image (S2I)?

A) A tool for converting Docker images to OCI format
B) A framework for building container images from source code without Dockerfiles
C) A migration tool for moving VMs to containers
D) A image scanning utility

---

### 7. Which command creates a new application from a Git repository using S2I?

A) `oc build nodejs https://github.com/user/app`
B) `oc new-app nodejs:18~https://github.com/user/app`
C) `oc create app --from-git https://github.com/user/app`
D) `oc deploy --source https://github.com/user/app`

---

### 8. What is the purpose of ImageStreams?

A) To stream video content to containers
B) To provide an abstraction layer for container images with automatic triggers
C) To compress images for faster transfer
D) To convert between image formats

---

### 9. What are Security Context Constraints (SCCs)?

A) Network firewall rules
B) Pod security policies specific to OpenShift with granular control
C) Container resource limits
D) User authentication rules

---

### 10. Which SCC is the default for pods in OpenShift?

A) anyuid
B) privileged
C) restricted
D) hostaccess

---

### 11. How do you grant an SCC to a service account?

A) `oc add scc anyuid to sa/my-sa`
B) `oc adm policy add-scc-to-user anyuid -z my-sa`
C) `oc set scc my-sa anyuid`
D) `oc grant scc anyuid my-sa`

---

### 12. What is the Operator pattern?

A) A way to run containers as root
B) Software that manages application lifecycle using custom resources
C) A deployment strategy for blue-green deployments
D) A monitoring solution

---

### 13. Where do you find and install operators in OpenShift?

A) Docker Hub
B) OperatorHub
C) GitHub
D) npm registry

---

### 14. Which resource represents an installed operator?

A) Subscription
B) CatalogSource
C) ClusterServiceVersion (CSV)
D) InstallPlan

---

### 15. What is the difference between OCP and OKD?

A) OCP is open source, OKD is commercial
B) OCP is commercial (Red Hat), OKD is community/open source
C) They are the same product with different names
D) OCP is for development, OKD is for production

---

### 16. Which command shows all resources in the current project?

A) `oc get everything`
B) `oc get all`
C) `oc list resources`
D) `oc show all`

---

### 17. What is the purpose of BuildConfigs?

A) To configure the container runtime
B) To define how container images are built within OpenShift
C) To set up network configurations
D) To manage storage volumes

---

### 18. How do you start a binary build from a local directory?

A) `oc build --dir ./app`
B) `oc start-build my-app --from-dir=./app`
C) `oc create build my-app ./app`
D) `oc upload ./app | oc build`

---

### 19. What is the oc command to get a shell in a running pod?

A) `oc shell my-pod`
B) `oc connect my-pod`
C) `oc rsh my-pod`
D) `oc terminal my-pod`

---

### 20. In Route traffic splitting, what does this configuration do?

```yaml
to:
  kind: Service
  name: app-v1
  weight: 80
alternateBackends:
  - kind: Service
    name: app-v2
    weight: 20
```

A) Sends 80 requests to v1, then 20 to v2
B) Sends 80% of traffic to v1 and 20% to v2
C) Prioritizes v1 with 80ms timeout, v2 with 20ms
D) Limits v1 to 80 connections, v2 to 20

---

### 21. Which network policy allows traffic from the OpenShift router?

A) Allow pods with label `router=true`
B) Allow from namespaceSelector with label `network.openshift.io/policy-group: ingress`
C) Allow from all external IPs
D) Allow from cluster admin namespace

---

### 22. What does DeploymentConfig offer that Deployment doesn't have natively?

A) Rolling updates
B) Built-in image triggers and lifecycle hooks
C) Replica management
D) Pod scheduling

---

### 23. Which is now recommended for new OpenShift applications?

A) DeploymentConfig
B) Deployment (with trigger annotations)
C) ReplicationController
D) Pod

---

### 24. How do you view the webhook URL for a BuildConfig?

A) `oc get webhook bc/my-app`
B) `oc describe bc my-app`
C) `oc show-webhooks my-app`
D) `oc webhook-url my-app`

---

### 25. What is OpenShift Local (formerly CodeReady Containers)?

A) A cloud-hosted OpenShift service
B) A single-node OpenShift cluster for local development
C) A container runtime for local use
D) A web-based IDE

---

---

## Answers

1. **B** - OpenShift is a distribution of Kubernetes with additional enterprise features
2. **C** - CRI-O
3. **B** - Projects are enhanced namespaces with additional metadata and defaults
4. **C** - Route
5. **B** - Edge, Passthrough, Re-encrypt
6. **B** - A framework for building container images from source code without Dockerfiles
7. **B** - `oc new-app nodejs:18~https://github.com/user/app`
8. **B** - To provide an abstraction layer for container images with automatic triggers
9. **B** - Pod security policies specific to OpenShift with granular control
10. **C** - restricted
11. **B** - `oc adm policy add-scc-to-user anyuid -z my-sa`
12. **B** - Software that manages application lifecycle using custom resources
13. **B** - OperatorHub
14. **C** - ClusterServiceVersion (CSV)
15. **B** - OCP is commercial (Red Hat), OKD is community/open source
16. **B** - `oc get all`
17. **B** - To define how container images are built within OpenShift
18. **B** - `oc start-build my-app --from-dir=./app`
19. **C** - `oc rsh my-pod`
20. **B** - Sends 80% of traffic to v1 and 20% to v2
21. **B** - Allow from namespaceSelector with label `network.openshift.io/policy-group: ingress`
22. **B** - Built-in image triggers and lifecycle hooks
23. **B** - Deployment (with trigger annotations)
24. **B** - `oc describe bc my-app`
25. **B** - A single-node OpenShift cluster for local development

---

## Scoring

- **23-25 correct**: Excellent! You're ready for OpenShift work
- **18-22 correct**: Good understanding, review missed topics
- **13-17 correct**: Review the module content again
- **Below 13**: Re-read the module before proceeding

---

## What's next

Return to the main course or explore specific topics in more depth.

Continue to: [../README.md](../README.md)
