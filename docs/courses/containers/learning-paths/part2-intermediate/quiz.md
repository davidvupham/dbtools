# Part 2 intermediate quiz

> Test your Docker Compose and intermediate container knowledge.

---

## Section 1: Docker Compose basics

### Question 1

What is the default filename Docker Compose looks for?

- [ ] docker-compose.yml
- [x] compose.yaml
- [ ] docker.yaml
- [ ] container.yaml

**Explanation:** Modern Docker Compose uses `compose.yaml` as the default. The older `docker-compose.yml` is still supported for backward compatibility.

---

### Question 2

Which command shows the merged configuration from multiple compose files?

- [ ] docker compose show
- [ ] docker compose merge
- [x] docker compose config
- [ ] docker compose inspect

**Explanation:** `docker compose config` displays the final merged configuration after processing all compose files and variable substitution.

---

### Question 3

What does `docker compose up -d --build` do?

- [ ] Downloads images and starts containers
- [ ] Builds images only, doesn't start
- [x] Rebuilds images and starts containers in detached mode
- [ ] Removes and recreates all containers

**Explanation:** The `-d` flag runs in detached mode, and `--build` forces a rebuild of images before starting containers.

---

## Section 2: Service dependencies

### Question 4

What is the correct way to wait for a database to be healthy before starting an API?

- [ ] `depends_on: [db]`
- [x] `depends_on: { db: { condition: service_healthy } }`
- [ ] `wait_for: db`
- [ ] `requires: db:healthy`

**Explanation:** The `condition: service_healthy` ensures the dependent service waits for the health check to pass, not just for the container to start.

---

### Question 5

Which dependency condition waits for a container to exit successfully?

- [ ] service_started
- [ ] service_healthy
- [x] service_completed_successfully
- [ ] service_exited_zero

**Explanation:** `service_completed_successfully` is used for init containers or migration tasks that should complete before other services start.

---

## Section 3: Networking

### Question 6

What does `internal: true` do on a network?

- [ ] Makes the network only accessible to services in the same compose file
- [x] Prevents containers on this network from accessing the internet
- [ ] Restricts the network to internal Docker communication
- [ ] Enables internal load balancing

**Explanation:** Setting `internal: true` on a network prevents containers connected to it from accessing external networks (including the internet), useful for isolating backend services.

---

### Question 7

How do containers in the same Compose network communicate?

- [ ] By IP address only
- [ ] By container ID
- [x] By service name
- [ ] They cannot communicate directly

**Explanation:** Docker Compose sets up DNS resolution so containers can reach each other using their service names as hostnames.

---

## Section 4: Volumes

### Question 8

What's the difference between a named volume and a bind mount?

- [ ] Named volumes are faster
- [x] Named volumes are managed by Docker; bind mounts map to host paths
- [ ] Bind mounts persist data; named volumes don't
- [ ] There is no difference

**Explanation:** Named volumes are managed by Docker in its storage area, while bind mounts directly map a host directory into the container.

---

### Question 9

What does this volume configuration do?
```yaml
volumes:
  - ./src:/app/src:ro
```

- [ ] Creates a read-only named volume
- [x] Mounts ./src to /app/src as read-only
- [ ] Copies ./src to /app/src
- [ ] Creates a symlink from ./src to /app/src

**Explanation:** This is a bind mount that maps the local `./src` directory to `/app/src` in the container. The `:ro` suffix makes it read-only.

---

## Section 5: Building images

### Question 10

What does the `target` option do in a build configuration?

- [ ] Specifies the build output directory
- [x] Selects which stage to build in a multi-stage Dockerfile
- [ ] Sets the target platform (linux/amd64)
- [ ] Specifies the target image name

**Explanation:** In a multi-stage Dockerfile, `target` allows you to build a specific stage (e.g., `development` or `production`) rather than the final stage.

---

### Question 11

Which build argument syntax provides a default value if the variable is unset?

- [ ] `${VAR?default}`
- [x] `${VAR:-default}`
- [ ] `${VAR:default}`
- [ ] `${VAR||default}`

**Explanation:** The `${VAR:-default}` syntax provides a default value if VAR is unset or empty. `${VAR-default}` provides a default only if unset.

---

## Section 6: Secrets and configuration

### Question 12

Where are secrets mounted inside containers by default?

- [ ] /etc/secrets/
- [ ] /secrets/
- [x] /run/secrets/
- [ ] /app/secrets/

**Explanation:** Docker mounts secrets at `/run/secrets/<secret_name>` inside containers.

---

### Question 13

What's the recommended way to pass a database password to a container?

- [ ] Hardcode in compose.yaml
- [ ] Use environment variable directly
- [x] Use a secret file with `_FILE` environment variable convention
- [ ] Pass as a build argument

**Explanation:** Using secrets with the `_FILE` suffix convention (e.g., `POSTGRES_PASSWORD_FILE=/run/secrets/db_password`) is the recommended approach as it avoids exposing secrets in environment variables.

---

## Section 7: Health checks

### Question 14

What does `start_period` in a health check configuration do?

- [ ] Sets how long to wait before running the first check
- [x] Provides a grace period during which failures don't count toward retries
- [ ] Sets the maximum time the container can take to start
- [ ] Delays the start of dependent services

**Explanation:** During the `start_period`, health check failures are not counted toward the retry limit, allowing slow-starting applications time to initialize.

---

### Question 15

Which health check state indicates the container has passed its health check?

- [ ] running
- [ ] ready
- [x] healthy
- [ ] started

**Explanation:** The three health states are: `starting` (during start_period), `healthy` (checks passing), and `unhealthy` (checks failing after retries exhausted).

---

## Section 8: Resource management

### Question 16

What happens when a container exceeds its memory limit?

- [ ] It is paused
- [ ] It receives a warning
- [x] It is killed (OOM)
- [ ] Memory is swapped to disk

**Explanation:** When a container exceeds its memory limit, the kernel's OOM (Out of Memory) killer terminates the container. This can be observed with `docker inspect` showing `OOMKilled: true`.

---

### Question 17

What's the purpose of resource reservations?

- [ ] To limit maximum resource usage
- [x] To guarantee minimum resources for scheduling
- [ ] To reserve resources for future use
- [ ] To prevent OOM kills

**Explanation:** Reservations guarantee that the specified resources are available for the container. They're used for scheduling decisions but don't limit actual usage like limits do.

---

## Section 9: Image optimization

### Question 18

Which practice most reduces Docker image size?

- [ ] Using more RUN commands
- [ ] Adding more COPY instructions
- [x] Using multi-stage builds with minimal production base
- [ ] Using the latest tag

**Explanation:** Multi-stage builds allow you to use a full build environment but copy only the necessary artifacts to a minimal production image.

---

### Question 19

Why should you order Dockerfile instructions from least to most frequently changed?

- [ ] It makes the file easier to read
- [x] It maximizes build cache utilization
- [ ] It reduces the number of layers
- [ ] It's required by Docker

**Explanation:** Docker caches layers, and a changed layer invalidates all subsequent layers. Putting rarely-changed instructions (like installing dependencies) before frequently-changed ones (like copying source code) maximizes cache hits.

---

## Section 10: Production considerations

### Question 20

Which is NOT a security best practice for production containers?

- [ ] Running as non-root user
- [ ] Using read-only filesystem
- [x] Using privileged mode for easier debugging
- [ ] Dropping all capabilities and adding only needed ones

**Explanation:** Privileged mode should never be used in production as it gives the container full access to the host system, defeating container isolation.

---

### Question 21

What restart policy should be used for most production services?

- [ ] always
- [x] unless-stopped
- [ ] on-failure
- [ ] no

**Explanation:** `unless-stopped` restarts containers automatically after failures or reboots but respects manual stops, making it ideal for most production services.

---

### Question 22

What does the `stop_grace_period` setting control?

- [ ] How long to wait before starting a container
- [x] Time between SIGTERM and SIGKILL when stopping
- [ ] Maximum container runtime
- [ ] Health check timeout

**Explanation:** `stop_grace_period` sets how long Docker waits after sending SIGTERM before sending SIGKILL, allowing applications time for graceful shutdown.

---

## Scoring

| Score | Rating |
|-------|--------|
| 20-22 | Expert - Ready for advanced topics |
| 16-19 | Proficient - Solid intermediate knowledge |
| 12-15 | Developing - Review weak areas |
| Below 12 | Needs review - Revisit Part 2 materials |

---

## What's next

If you scored well, proceed to Part 3: Advanced Container Concepts.

Continue to: [../part3-advanced/](../part3-advanced/)
