# OpenShift quiz

> **Module:** OpenShift | **Type:** Interactive Assessment | **Questions:** 25

Test your understanding of OpenShift concepts. Select your answer for each question, then click to reveal the correct answer and explanation.

**Instructions:**
1. Read each question and choose your answer (A, B, C, or D)
2. Click "Show Answer" to reveal the correct answer and explanation
3. Keep track of your correct answers
4. Calculate your percentage at the end

---

## Section 1: OpenShift fundamentals

### Question 1

What is the relationship between OpenShift and Kubernetes?

- A) OpenShift is an alternative to Kubernetes
- B) OpenShift is a distribution of Kubernetes with additional enterprise features
- C) Kubernetes is built on top of OpenShift
- D) They are completely separate platforms

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

OpenShift is a distribution of Kubernetes with additional enterprise features.

**Explanation:** OpenShift is built on top of Kubernetes, adding enterprise features like integrated CI/CD, a developer console, enhanced security, and an operator-based architecture.

</details>

---

### Question 2

Which container runtime does OpenShift use?

- A) Docker
- B) containerd
- C) CRI-O
- D) rkt

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

CRI-O

**Explanation:** OpenShift uses CRI-O, a lightweight container runtime specifically designed for Kubernetes. It's optimized for security and performance.

</details>

---

### Question 3

What is the difference between a Project and a Namespace in OpenShift?

- A) They are exactly the same thing
- B) Projects are enhanced namespaces with additional metadata and defaults
- C) Namespaces are more feature-rich than Projects
- D) Projects are only for development, Namespaces for production

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Projects are enhanced namespaces with additional metadata and defaults.

**Explanation:** Projects wrap Kubernetes namespaces with additional features like default network policies, resource quotas, and RBAC bindings. Every Project is a Namespace, but with OpenShift-specific enhancements.

</details>

---

## Section 2: Routes and networking

### Question 4

Which resource is OpenShift's preferred way to expose services externally?

- A) Ingress
- B) NodePort
- C) Route
- D) LoadBalancer

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Route

**Explanation:** Routes are OpenShift's native way to expose services with HTTP/HTTPS routing, TLS termination, and traffic splitting. While Ingress is supported, Routes offer more features.

</details>

---

### Question 5

What are the three TLS termination types for Routes?

- A) SSL, TLS, HTTPS
- B) Edge, Passthrough, Re-encrypt
- C) External, Internal, Mixed
- D) Client, Server, Mutual

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Edge, Passthrough, Re-encrypt

**Explanation:** Edge terminates TLS at the router. Passthrough sends encrypted traffic directly to the pod. Re-encrypt terminates at the router and re-encrypts to the backend.

</details>

---

### Question 6

In Route traffic splitting, what does this configuration do?

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

- A) Sends 80 requests to v1, then 20 to v2
- B) Sends 80% of traffic to v1 and 20% to v2
- C) Prioritizes v1 with 80ms timeout, v2 with 20ms
- D) Limits v1 to 80 connections, v2 to 20

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Sends 80% of traffic to v1 and 20% to v2.

**Explanation:** The weight values define the percentage of traffic each backend receives. This enables canary deployments and A/B testing.

</details>

---

## Section 3: Source-to-Image (S2I)

### Question 7

What is Source-to-Image (S2I)?

- A) A tool for converting Docker images to OCI format
- B) A framework for building container images from source code without Dockerfiles
- C) A migration tool for moving VMs to containers
- D) An image scanning utility

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

A framework for building container images from source code without Dockerfiles.

**Explanation:** S2I automatically builds container images by injecting source code into a builder image. Developers don't need to write Dockerfiles; the builder handles the build process.

</details>

---

### Question 8

Which command creates a new application from a Git repository using S2I?

- A) `oc build nodejs https://github.com/user/app`
- B) `oc new-app nodejs:18~https://github.com/user/app`
- C) `oc create app --from-git https://github.com/user/app`
- D) `oc deploy --source https://github.com/user/app`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`oc new-app nodejs:18~https://github.com/user/app`

**Explanation:** The `~` syntax tells OpenShift to use the nodejs:18 builder image with the specified Git repository. This creates all necessary resources for the application.

</details>

---

### Question 9

What is the purpose of ImageStreams?

- A) To stream video content to containers
- B) To provide an abstraction layer for container images with automatic triggers
- C) To compress images for faster transfer
- D) To convert between image formats

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

To provide an abstraction layer for container images with automatic triggers.

**Explanation:** ImageStreams track image references and can trigger rebuilds/redeployments when the base image changes. They provide a level of indirection that enables automatic updates.

</details>

---

## Section 4: Security Context Constraints

### Question 10

What are Security Context Constraints (SCCs)?

- A) Network firewall rules
- B) Pod security policies specific to OpenShift with granular control
- C) Container resource limits
- D) User authentication rules

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Pod security policies specific to OpenShift with granular control.

**Explanation:** SCCs control what actions pods can perform and what resources they can access. They're OpenShift's implementation of pod security, more granular than Kubernetes PSPs.

</details>

---

### Question 11

Which SCC is the default for pods in OpenShift?

- A) anyuid
- B) privileged
- C) restricted
- D) hostaccess

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

restricted

**Explanation:** The `restricted` SCC is the default, enforcing that containers run as non-root with a random UID and cannot access host resources. This provides strong isolation by default.

</details>

---

### Question 12

How do you grant an SCC to a service account?

- A) `oc add scc anyuid to sa/my-sa`
- B) `oc adm policy add-scc-to-user anyuid -z my-sa`
- C) `oc set scc my-sa anyuid`
- D) `oc grant scc anyuid my-sa`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`oc adm policy add-scc-to-user anyuid -z my-sa`

**Explanation:** The `-z` flag specifies a service account in the current namespace. This grants the service account permission to use the specified SCC.

</details>

---

## Section 5: Operators

### Question 13

What is the Operator pattern?

- A) A way to run containers as root
- B) Software that manages application lifecycle using custom resources
- C) A deployment strategy for blue-green deployments
- D) A monitoring solution

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Software that manages application lifecycle using custom resources.

**Explanation:** Operators extend Kubernetes with custom resources and controllers that encode operational knowledge. They automate complex application management tasks.

</details>

---

### Question 14

Where do you find and install operators in OpenShift?

- A) Docker Hub
- B) OperatorHub
- C) GitHub
- D) npm registry

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

OperatorHub

**Explanation:** OperatorHub is a catalog of operators integrated into OpenShift. It provides certified, community, and Red Hat operators ready to install.

</details>

---

### Question 15

Which resource represents an installed operator?

- A) Subscription
- B) CatalogSource
- C) ClusterServiceVersion (CSV)
- D) InstallPlan

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

ClusterServiceVersion (CSV)

**Explanation:** The CSV describes the operator's capabilities, requirements, and owned CRDs. It represents the running instance of an operator version.

</details>

---

## Section 6: Builds and deployments

### Question 16

What is the purpose of BuildConfigs?

- A) To configure the container runtime
- B) To define how container images are built within OpenShift
- C) To set up network configurations
- D) To manage storage volumes

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

To define how container images are built within OpenShift.

**Explanation:** BuildConfigs define the build strategy (S2I, Docker, Custom), source location, and output image. They can be triggered manually or automatically by webhooks and image changes.

</details>

---

### Question 17

How do you start a binary build from a local directory?

- A) `oc build --dir ./app`
- B) `oc start-build my-app --from-dir=./app`
- C) `oc create build my-app ./app`
- D) `oc upload ./app | oc build`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`oc start-build my-app --from-dir=./app`

**Explanation:** Binary builds upload local content directly to the build. The `--from-dir` flag uploads the specified directory as the build source.

</details>

---

### Question 18

What does DeploymentConfig offer that Deployment doesn't have natively?

- A) Rolling updates
- B) Built-in image triggers and lifecycle hooks
- C) Replica management
- D) Pod scheduling

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Built-in image triggers and lifecycle hooks.

**Explanation:** DeploymentConfig includes native image change triggers (auto-redeploy on image update) and lifecycle hooks (pre/post deployment actions). Standard Deployments require additional configuration for these.

</details>

---

### Question 19

Which is now recommended for new OpenShift applications?

- A) DeploymentConfig
- B) Deployment (with trigger annotations)
- C) ReplicationController
- D) Pod

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Deployment (with trigger annotations).

**Explanation:** Standard Kubernetes Deployments are now recommended for new applications. They can use annotations like `image.openshift.io/triggers` for image-triggered updates while remaining more portable.

</details>

---

## Section 7: CLI and operations

### Question 20

Which command shows all resources in the current project?

- A) `oc get everything`
- B) `oc get all`
- C) `oc list resources`
- D) `oc show all`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`oc get all`

**Explanation:** `oc get all` displays the main resources (pods, services, deployments, etc.) in the current project. Note that it doesn't show ConfigMaps, Secrets, or other resources.

</details>

---

### Question 21

What is the oc command to get a shell in a running pod?

- A) `oc shell my-pod`
- B) `oc connect my-pod`
- C) `oc rsh my-pod`
- D) `oc terminal my-pod`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`oc rsh my-pod`

**Explanation:** `oc rsh` (remote shell) opens an interactive shell in a running pod. It's equivalent to `kubectl exec -it my-pod -- /bin/sh`.

</details>

---

### Question 22

How do you view the webhook URL for a BuildConfig?

- A) `oc get webhook bc/my-app`
- B) `oc describe bc my-app`
- C) `oc show-webhooks my-app`
- D) `oc webhook-url my-app`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`oc describe bc my-app`

**Explanation:** The `describe` command shows detailed information about the BuildConfig, including webhook URLs that can be used to trigger builds from Git providers.

</details>

---

## Section 8: Network policies and platforms

### Question 23

Which network policy allows traffic from the OpenShift router?

- A) Allow pods with label `router=true`
- B) Allow from namespaceSelector with label `network.openshift.io/policy-group: ingress`
- C) Allow from all external IPs
- D) Allow from cluster admin namespace

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Allow from namespaceSelector with label `network.openshift.io/policy-group: ingress`

**Explanation:** OpenShift labels the router namespace with `network.openshift.io/policy-group: ingress`. NetworkPolicies can use this label to allow ingress traffic from the router.

</details>

---

### Question 24

What is the difference between OCP and OKD?

- A) OCP is open source, OKD is commercial
- B) OCP is commercial (Red Hat), OKD is community/open source
- C) They are the same product with different names
- D) OCP is for development, OKD is for production

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

OCP is commercial (Red Hat), OKD is community/open source.

**Explanation:** OCP (OpenShift Container Platform) is Red Hat's supported commercial product. OKD is the community-supported upstream version, similar to the relationship between RHEL and Fedora.

</details>

---

### Question 25

What is OpenShift Local (formerly CodeReady Containers)?

- A) A cloud-hosted OpenShift service
- B) A single-node OpenShift cluster for local development
- C) A container runtime for local use
- D) A web-based IDE

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

A single-node OpenShift cluster for local development.

**Explanation:** OpenShift Local provides a minimal single-node OpenShift cluster that runs on your local machine. It's designed for development and testing, not production workloads.

</details>

---

## Score tracker

Use this section to calculate your final score.

### Tally your results

| Section | Questions | Your Correct Answers |
|---------|-----------|---------------------|
| OpenShift Fundamentals | 1-3 | ___ / 3 |
| Routes and Networking | 4-6 | ___ / 3 |
| Source-to-Image (S2I) | 7-9 | ___ / 3 |
| Security Context Constraints | 10-12 | ___ / 3 |
| Operators | 13-15 | ___ / 3 |
| Builds and Deployments | 16-19 | ___ / 4 |
| CLI and Operations | 20-22 | ___ / 3 |
| Network Policies and Platforms | 23-25 | ___ / 3 |
| **Total** | | ___ / 25 |

### Calculate your percentage

**Your Score: ___ / 25 = ____%**

(Divide your correct answers by 25 and multiply by 100)

### How did you do?

| Score | Percentage | Level | Recommendation |
|-------|------------|-------|----------------|
| 23-25 | 92-100% | Expert | Ready for OpenShift work |
| 18-22 | 72-91% | Proficient | Good understanding, review missed topics |
| 13-17 | 52-71% | Developing | Review the module content again |
| Below 13 | Below 52% | Needs Review | Re-read the module before proceeding |

---

## Next steps

Based on your score:

- **High score**: Explore OpenShift operator development or certification
- **Medium score**: Practice with OpenShift Local or a sandbox environment
- **Lower score**: Review the OpenShift module materials

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [OpenShift vs Kubernetes](08-openshift-vs-kubernetes.md) | [Course Overview](../course_overview.md) | [Course Overview](../README.md) |
