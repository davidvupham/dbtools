# Part 2: Intermediate quiz

> **Module:** Part 2 - Intermediate | **Type:** Interactive Assessment | **Questions:** 22

Test your Docker Compose and intermediate container knowledge. Select your answer for each question, then click to reveal the correct answer and explanation.

**Instructions:**
1. Read each question and choose your answer (A, B, C, or D)
2. Click "Show Answer" to reveal the correct answer and explanation
3. Keep track of your correct answers
4. Calculate your percentage at the end

---

## Section 1: Docker Compose basics

### Question 1

What is the default filename Docker Compose looks for?

- A) docker-compose.yml
- B) compose.yaml
- C) docker.yaml
- D) container.yaml

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

compose.yaml

**Explanation:** Modern Docker Compose uses `compose.yaml` as the default. The older `docker-compose.yml` is still supported for backward compatibility.

</details>

---

### Question 2

Which command shows the merged configuration from multiple compose files?

- A) docker compose show
- B) docker compose merge
- C) docker compose config
- D) docker compose inspect

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

docker compose config

**Explanation:** `docker compose config` displays the final merged configuration after processing all compose files and variable substitution.

</details>

---

### Question 3

What does `docker compose up -d --build` do?

- A) Downloads images and starts containers
- B) Builds images only, doesn't start
- C) Rebuilds images and starts containers in detached mode
- D) Removes and recreates all containers

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Rebuilds images and starts containers in detached mode.

**Explanation:** The `-d` flag runs in detached mode, and `--build` forces a rebuild of images before starting containers.

</details>

---

## Section 2: Service dependencies

### Question 4

What is the correct way to wait for a database to be healthy before starting an API?

- A) `depends_on: [db]`
- B) `depends_on: { db: { condition: service_healthy } }`
- C) `wait_for: db`
- D) `requires: db:healthy`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`depends_on: { db: { condition: service_healthy } }`

**Explanation:** The `condition: service_healthy` ensures the dependent service waits for the health check to pass, not just for the container to start.

</details>

---

### Question 5

Which dependency condition waits for a container to exit successfully?

- A) service_started
- B) service_healthy
- C) service_completed_successfully
- D) service_exited_zero

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

service_completed_successfully

**Explanation:** `service_completed_successfully` is used for init containers or migration tasks that should complete before other services start.

</details>

---

## Section 3: Networking

### Question 6

What does `internal: true` do on a network?

- A) Makes the network only accessible to services in the same compose file
- B) Prevents containers on this network from accessing the internet
- C) Restricts the network to internal Docker communication
- D) Enables internal load balancing

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Prevents containers on this network from accessing the internet.

**Explanation:** Setting `internal: true` on a network prevents containers connected to it from accessing external networks (including the internet), useful for isolating backend services.

</details>

---

### Question 7

How do containers in the same Compose network communicate?

- A) By IP address only
- B) By container ID
- C) By service name
- D) They cannot communicate directly

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

By service name.

**Explanation:** Docker Compose sets up DNS resolution so containers can reach each other using their service names as hostnames.

</details>

---

## Section 4: Volumes

### Question 8

What's the difference between a named volume and a bind mount?

- A) Named volumes are faster
- B) Named volumes are managed by Docker; bind mounts map to host paths
- C) Bind mounts persist data; named volumes don't
- D) There is no difference

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Named volumes are managed by Docker; bind mounts map to host paths.

**Explanation:** Named volumes are managed by Docker in its storage area, while bind mounts directly map a host directory into the container.

</details>

---

### Question 9

What does this volume configuration do?

```yaml
volumes:
  - ./src:/app/src:ro
```

- A) Creates a read-only named volume
- B) Mounts ./src to /app/src as read-only
- C) Copies ./src to /app/src
- D) Creates a symlink from ./src to /app/src

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Mounts ./src to /app/src as read-only.

**Explanation:** This is a bind mount that maps the local `./src` directory to `/app/src` in the container. The `:ro` suffix makes it read-only.

</details>

---

## Section 5: Building images

### Question 10

What does the `target` option do in a build configuration?

- A) Specifies the build output directory
- B) Selects which stage to build in a multi-stage Dockerfile
- C) Sets the target platform (linux/amd64)
- D) Specifies the target image name

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Selects which stage to build in a multi-stage Dockerfile.

**Explanation:** In a multi-stage Dockerfile, `target` allows you to build a specific stage (e.g., `development` or `production`) rather than the final stage.

</details>

---

### Question 11

Which build argument syntax provides a default value if the variable is unset?

- A) `${VAR?default}`
- B) `${VAR:-default}`
- C) `${VAR:default}`
- D) `${VAR||default}`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`${VAR:-default}`

**Explanation:** The `${VAR:-default}` syntax provides a default value if VAR is unset or empty. `${VAR-default}` provides a default only if unset.

</details>

---

## Section 6: Secrets and configuration

### Question 12

Where are secrets mounted inside containers by default?

- A) /etc/secrets/
- B) /secrets/
- C) /run/secrets/
- D) /app/secrets/

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

/run/secrets/

**Explanation:** Docker mounts secrets at `/run/secrets/<secret_name>` inside containers.

</details>

---

### Question 13

What's the recommended way to pass a database password to a container?

- A) Hardcode in compose.yaml
- B) Use environment variable directly
- C) Use a secret file with `_FILE` environment variable convention
- D) Pass as a build argument

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Use a secret file with `_FILE` environment variable convention.

**Explanation:** Using secrets with the `_FILE` suffix convention (e.g., `POSTGRES_PASSWORD_FILE=/run/secrets/db_password`) is the recommended approach as it avoids exposing secrets in environment variables.

</details>

---

## Section 7: Health checks

### Question 14

What does `start_period` in a health check configuration do?

- A) Sets how long to wait before running the first check
- B) Provides a grace period during which failures don't count toward retries
- C) Sets the maximum time the container can take to start
- D) Delays the start of dependent services

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Provides a grace period during which failures don't count toward retries.

**Explanation:** During the `start_period`, health check failures are not counted toward the retry limit, allowing slow-starting applications time to initialize.

</details>

---

### Question 15

Which health check state indicates the container has passed its health check?

- A) running
- B) ready
- C) healthy
- D) started

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

healthy

**Explanation:** The three health states are: `starting` (during start_period), `healthy` (checks passing), and `unhealthy` (checks failing after retries exhausted).

</details>

---

## Section 8: Resource management

### Question 16

What happens when a container exceeds its memory limit?

- A) It is paused
- B) It receives a warning
- C) It is killed (OOM)
- D) Memory is swapped to disk

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

It is killed (OOM).

**Explanation:** When a container exceeds its memory limit, the kernel's OOM (Out of Memory) killer terminates the container. This can be observed with `docker inspect` showing `OOMKilled: true`.

</details>

---

### Question 17

What's the purpose of resource reservations?

- A) To limit maximum resource usage
- B) To guarantee minimum resources for scheduling
- C) To reserve resources for future use
- D) To prevent OOM kills

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

To guarantee minimum resources for scheduling.

**Explanation:** Reservations guarantee that the specified resources are available for the container. They're used for scheduling decisions but don't limit actual usage like limits do.

</details>

---

## Section 9: Image optimization

### Question 18

Which practice most reduces Docker image size?

- A) Using more RUN commands
- B) Adding more COPY instructions
- C) Using multi-stage builds with minimal production base
- D) Using the latest tag

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Using multi-stage builds with minimal production base.

**Explanation:** Multi-stage builds allow you to use a full build environment but copy only the necessary artifacts to a minimal production image.

</details>

---

### Question 19

Why should you order Dockerfile instructions from least to most frequently changed?

- A) It makes the file easier to read
- B) It maximizes build cache utilization
- C) It reduces the number of layers
- D) It's required by Docker

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

It maximizes build cache utilization.

**Explanation:** Docker caches layers, and a changed layer invalidates all subsequent layers. Putting rarely-changed instructions (like installing dependencies) before frequently-changed ones (like copying source code) maximizes cache hits.

</details>

---

## Section 10: Production considerations

### Question 20

Which is NOT a security best practice for production containers?

- A) Running as non-root user
- B) Using read-only filesystem
- C) Using privileged mode for easier debugging
- D) Dropping all capabilities and adding only needed ones

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Using privileged mode for easier debugging.

**Explanation:** Privileged mode should never be used in production as it gives the container full access to the host system, defeating container isolation.

</details>

---

### Question 21

What restart policy should be used for most production services?

- A) always
- B) unless-stopped
- C) on-failure
- D) no

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

unless-stopped

**Explanation:** `unless-stopped` restarts containers automatically after failures or reboots but respects manual stops, making it ideal for most production services.

</details>

---

### Question 22

What does the `stop_grace_period` setting control?

- A) How long to wait before starting a container
- B) Time between SIGTERM and SIGKILL when stopping
- C) Maximum container runtime
- D) Health check timeout

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Time between SIGTERM and SIGKILL when stopping.

**Explanation:** `stop_grace_period` sets how long Docker waits after sending SIGTERM before sending SIGKILL, allowing applications time for graceful shutdown.

</details>

---

## Score tracker

Use this section to calculate your final score.

### Tally your results

| Section | Questions | Your Correct Answers |
|---------|-----------|---------------------|
| Docker Compose Basics | 1-3 | ___ / 3 |
| Service Dependencies | 4-5 | ___ / 2 |
| Networking | 6-7 | ___ / 2 |
| Volumes | 8-9 | ___ / 2 |
| Building Images | 10-11 | ___ / 2 |
| Secrets and Configuration | 12-13 | ___ / 2 |
| Health Checks | 14-15 | ___ / 2 |
| Resource Management | 16-17 | ___ / 2 |
| Image Optimization | 18-19 | ___ / 2 |
| Production Considerations | 20-22 | ___ / 3 |
| **Total** | | ___ / 22 |

### Calculate your percentage

**Your Score: ___ / 22 = ____%**

(Divide your correct answers by 22 and multiply by 100)

### How did you do?

| Score | Percentage | Level | Recommendation |
|-------|------------|-------|----------------|
| 20-22 | 90-100% | Expert | Ready for advanced topics |
| 16-19 | 73-89% | Proficient | Solid intermediate knowledge |
| 12-15 | 55-72% | Developing | Review weak areas |
| Below 12 | Below 55% | Needs Review | Revisit Part 2 materials |

---

## Next steps

Based on your score:

- **Score 80%+**: Continue to [Part 3: Advanced](../part3-advanced/)
- **Score below 80%**: Review the Part 2 materials before proceeding
