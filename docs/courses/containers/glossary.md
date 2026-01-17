# Glossary

Container and related terminology used throughout this course.

---

## A

### Alpine Linux
A minimal Linux distribution (~5MB) commonly used as a base image for containers due to its small size.

### Attestation
Cryptographic proof about how a container image was built, including build environment and source code origin.

---

## B

### Base Image
The starting point for building a container image, specified by the `FROM` instruction in a Dockerfile.

### Bind Mount
A mapping of a host filesystem path into a container, allowing direct access to host files.

### Bridge Network
The default Docker network driver that creates a private internal network for containers on a single host.

### Buildah
An OCI-compliant tool for building container images without requiring a daemon.

### BuildKit
Docker's modern build backend providing improved performance, caching, and build features.

### Buildx
Docker CLI plugin for extended build capabilities including multi-platform builds.

---

## C

### Cgroups (Control Groups)
Linux kernel feature that limits and isolates resource usage (CPU, memory, I/O) for processes.

### CIS Benchmark
Security configuration guidelines from the Center for Internet Security for Docker and Kubernetes.

### CNI (Container Network Interface)
A specification and libraries for configuring network interfaces in Linux containers.

### Container
A lightweight, isolated runtime environment that packages an application with its dependencies.

### Container Image
A read-only template containing the filesystem and configuration needed to create a container.

### containerd
An industry-standard container runtime used by Docker and Kubernetes.

### Containerfile
Podman's preferred name for a Dockerfile (both formats are compatible).

### Context (Build)
The set of files at a specified path or URL sent to the Docker daemon for building an image.

### Copy-on-Write (CoW)
A strategy where filesystem modifications create new layers instead of modifying existing ones.

---

## D

### Daemon
A background process. Docker uses a daemon (`dockerd`) while Podman is daemonless.

### Daemonless
Architecture where each container runs as a direct child process without a central daemon (Podman).

### Data Volume
A specially-designated directory within containers that persists data and bypasses the union filesystem.

### DCT (Docker Content Trust)
Docker's implementation of image signing using Notary.

### Digest
A content-addressable identifier (SHA256 hash) that uniquely identifies an image.

### Distroless
Container images that contain only the application and its runtime dependencies, without a shell or package manager.

### DOMC (Discrete Option Multiple Choice)
Exam question format where multiple answers may be correct.

### Dockerfile
A text file containing instructions to build a container image.

---

## E

### Entrypoint
The default executable for a container, configured with the `ENTRYPOINT` instruction.

### Ephemeral Container
A temporary container added to a running pod for debugging purposes (Kubernetes).

---

## F

### Fork-Exec
The process model used by Podman where each container is a direct child of the podman command.

---

## G

### Graph Driver
See Storage Driver.

### graphroot
The storage location for Podman images and containers (configurable in storage.conf).

---

## H

### Health Check
A command that Docker runs periodically to verify a container is functioning correctly.

### Host Network
Network mode where containers share the host's network namespace directly.

---

## I

### Image Layer
A read-only filesystem change resulting from a Dockerfile instruction.

### Image Manifest
JSON document describing an image's layers, configuration, and metadata.

### Ingress Network
Swarm's built-in load-balancing network for routing external traffic to services.

---

## J

### JSON-file
Docker's default logging driver that writes container logs to JSON files.

---

## K

### Keep-id
Podman option (`--userns=keep-id`) that maps the container's UID to the host user's UID.

---

## L

### Layer
A set of filesystem changes that, when stacked, form a container image.

### Linux Namespace
Kernel feature that isolates system resources (PID, network, mount, etc.) for containers.

---

## M

### Manifest List
A collection of image manifests for different platforms (architectures) under a single tag.

### MKE (Mirantis Kubernetes Engine)
Formerly Docker Universal Control Plane (UCP), an enterprise container management platform.

### MSR (Mirantis Secure Registry)
Formerly Docker Trusted Registry (DTR), an enterprise container registry.

### MTLS (Mutual TLS)
Two-way authentication where both client and server verify each other's certificates.

### Multi-stage Build
Dockerfile technique using multiple `FROM` instructions to create smaller final images.

---

## N

### Named Volume
A Docker-managed volume with a user-specified name for easy reference.

### Namespace
See Linux Namespace.

### netavark
Podman's modern network stack, replacing CNI plugins.

### Network Driver
Plugin that implements container networking (bridge, overlay, macvlan, etc.).

---

## O

### OCI (Open Container Initiative)
Organization maintaining container format and runtime specifications.

### Orchestration
Automated management of containerized applications including deployment, scaling, and networking.

### Overlay Filesystem
Union filesystem that combines multiple layers into a single view.

### Overlay Network
Multi-host network driver that enables communication between containers across different hosts.

---

## P

### pasta
Podman's userspace network stack for rootless containers (alternative to slirp4netns).

### Pod
A group of containers sharing network and storage namespaces (native in Podman and Kubernetes).

### Port Mapping
Exposing a container port on the host system (`-p host:container`).

### Prune
Command to remove unused containers, images, volumes, or networks.

### Pull
Downloading an image from a registry to local storage.

### Push
Uploading an image from local storage to a registry.

---

## Q

### Quadlet
Systemd generator for running containers as systemd services (Podman).

### Quorum
The minimum number of manager nodes required for a Swarm cluster to function.

---

## R

### Registry
A service for storing and distributing container images.

### Replica
An instance of a service in Docker Swarm or Kubernetes.

### Rootful
Running containers with root privileges (traditional Docker default).

### Rootless
Running containers without root privileges, using user namespaces for isolation.

### runc
The reference implementation of the OCI runtime specification.

### runroot
The runtime storage location for Podman (configurable in storage.conf).

---

## S

### SBOM (Software Bill of Materials)
A list of all components and dependencies in a container image.

### Scratch
A special empty base image for creating minimal containers.

### Secret
Sensitive data (passwords, certificates) managed securely by Docker Swarm or Kubernetes.

### Service
A definition of tasks to execute in a Swarm cluster.

### Sigstore
Open-source project for signing, verifying, and protecting software artifacts.

### Skopeo
Command-line tool for copying and inspecting container images without a daemon.

### slirp4netns
User-mode networking for rootless containers.

### SLSA (Supply-chain Levels for Software Artifacts)
Framework for ensuring the integrity of software artifacts.

### Stack
A collection of services deployed together in Docker Swarm.

### Storage Driver
Plugin that manages how image layers are stored and combined (overlay2, btrfs, etc.).

### subgid
File (`/etc/subgid`) defining subordinate group ID ranges for user namespace mapping.

### subuid
File (`/etc/subuid`) defining subordinate user ID ranges for user namespace mapping.

### Swarm
Docker's native clustering and orchestration solution.

---

## T

### Tag
A human-readable label for an image version (e.g., `nginx:1.25`).

### tmpfs
A temporary filesystem stored in memory, not persisted to disk.

### Trivy
Open-source vulnerability scanner for container images.

---

## U

### UCP (Universal Control Plane)
See MKE.

### UID Mapping
The translation of user IDs between host and container namespaces in rootless mode.

### Union Filesystem
Filesystem that presents multiple directories as a single merged view.

### User Namespace
Linux namespace that maps UIDs/GIDs inside a container to different UIDs/GIDs on the host.

---

## V

### Volume
A mechanism for persisting data generated by containers.

### Volume Driver
Plugin that manages volume storage backends (local, NFS, cloud storage, etc.).

---

## W

### Wasm (WebAssembly)
A binary instruction format enabling near-native performance, now supported in containers.

### Worker Node
A Swarm node that executes tasks assigned by manager nodes.

---

## X

### XDG_RUNTIME_DIR
Environment variable specifying the user's runtime directory, used by rootless Podman.

---

## Y

### YAML
Data serialization format used for Docker Compose and Kubernetes configuration files.

---

## Z

### :z / :Z
SELinux volume labels for shared (:z) or private (:Z) access in Podman/Docker.
