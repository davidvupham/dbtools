# Part 1: Beginner quiz

> **Module:** Part 1 - Beginner | **Type:** Interactive Assessment | **Questions:** 30

Test your understanding of container fundamentals. Select your answer for each question, then click to reveal the correct answer and explanation. Track your score as you go!

**Instructions:**
1. Read each question and choose your answer (A, B, C, or D)
2. Click "Show Answer" to reveal the correct answer and explanation
3. Keep track of your correct answers
4. Calculate your percentage at the end

---

## Section 1: Container basics (10 questions)

### Question 1

What is the primary difference between a container and a virtual machine?

- A) Containers are faster because they use hardware virtualization
- B) Containers share the host kernel while VMs include their own kernel
- C) VMs can run any operating system, containers cannot
- D) Containers require more disk space than VMs

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Containers share the host kernel while VMs include their own kernel.

**Explanation:** Containers are lightweight because they share the host's operating system kernel, while VMs include a complete operating system with its own kernel. This makes containers faster to start and more resource-efficient.

</details>

---

### Question 2

Which command runs a container interactively with a terminal?

- A) `docker run nginx`
- B) `docker run -d nginx`
- C) `docker run -it nginx sh`
- D) `docker run --terminal nginx`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`docker run -it nginx sh`

**Explanation:** The `-i` flag keeps STDIN open for interactive input, and `-t` allocates a pseudo-TTY (terminal). Together with a shell command like `sh`, you get an interactive terminal session inside the container.

</details>

---

### Question 3

What does the `-d` flag do in `docker run -d nginx`?

- A) Downloads the image first
- B) Runs in debug mode
- C) Runs the container in detached (background) mode
- D) Disables networking

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Runs the container in detached (background) mode.

**Explanation:** The `-d` (detached) flag runs the container in the background and prints the container ID. Without this flag, the container runs in the foreground and takes over your terminal.

</details>

---

### Question 4

How do you stop a running container gracefully?

- A) `docker kill mycontainer`
- B) `docker stop mycontainer`
- C) `docker pause mycontainer`
- D) `docker remove mycontainer`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`docker stop mycontainer`

**Explanation:** `docker stop` sends a SIGTERM signal to allow graceful shutdown, then SIGKILL after a timeout. `docker kill` immediately sends SIGKILL without allowing graceful shutdown.

</details>

---

### Question 5

What happens to changes made inside a container when it's removed?

- A) Changes are automatically saved to the image
- B) Changes persist to the next container
- C) Changes are lost unless volumes are used
- D) Changes are backed up automatically

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Changes are lost unless volumes are used.

**Explanation:** Containers have a writable layer, but this layer is ephemeral. When the container is removed, all changes in the writable layer are lost. To persist data, you must use volumes or bind mounts.

</details>

---

### Question 6

Which command shows only running containers?

- A) `docker ps`
- B) `docker ps -a`
- C) `docker list`
- D) `docker containers`

<details>
<summary>Show Answer</summary>

**Correct Answer: A**

`docker ps`

**Explanation:** `docker ps` shows only running containers. Add `-a` to see all containers including stopped ones. There is no `docker list` or `docker containers` command.

</details>

---

### Question 7

What is the purpose of `docker exec`?

- A) To create a new container
- B) To build an image
- C) To run a command inside a running container
- D) To export a container

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

To run a command inside a running container.

**Explanation:** `docker exec` executes a new command in an already running container. It's commonly used for debugging, like `docker exec -it mycontainer sh` to get a shell.

</details>

---

### Question 8

How do you remove all stopped containers at once?

- A) `docker rm --all`
- B) `docker remove stopped`
- C) `docker container prune`
- D) `docker clean containers`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`docker container prune`

**Explanation:** `docker container prune` removes all stopped containers. Similar prune commands exist for images, volumes, and networks. You can also use `docker system prune` to clean up multiple resource types at once.

</details>

---

### Question 9

What does `docker logs -f mycontainer` do?

- A) Shows the first log entries
- B) Filters log output
- C) Follows log output in real-time
- D) Formats logs as JSON

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Follows log output in real-time.

**Explanation:** The `-f` (follow) flag streams new log output in real-time, similar to `tail -f`. Press Ctrl+C to stop following.

</details>

---

### Question 10

Which restart policy keeps the container running unless manually stopped?

- A) `always`
- B) `unless-stopped`
- C) `on-failure`
- D) `never-stop`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`unless-stopped`

**Explanation:** `unless-stopped` restarts the container automatically unless it was manually stopped. `always` would also restart after manual stops when the Docker daemon restarts. `on-failure` only restarts on non-zero exit codes.

</details>

---

## Section 2: Images (10 questions)

### Question 11

What is the relationship between images and containers?

- A) Images are running containers
- B) Images are templates from which containers are created
- C) Containers store images
- D) They are the same thing

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Images are templates from which containers are created.

**Explanation:** An image is a read-only template containing the application and its dependencies. A container is a running instance of an image, with its own writable layer on top.

</details>

---

### Question 12

What does `docker pull python:3.12-slim` do?

- A) Creates a new Python container
- B) Builds a Python image
- C) Downloads the Python 3.12 slim image from a registry
- D) Updates the local Python installation

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Downloads the Python 3.12 slim image from a registry.

**Explanation:** `docker pull` downloads an image from a container registry (Docker Hub by default). The `:3.12-slim` part is the tag, specifying a particular version of the image.

</details>

---

### Question 13

Which part of `ghcr.io/myorg/myapp:v1.0` is the tag?

- A) `ghcr.io`
- B) `myorg`
- C) `myapp`
- D) `v1.0`

<details>
<summary>Show Answer</summary>

**Correct Answer: D**

`v1.0`

**Explanation:** In an image reference: `ghcr.io` is the registry, `myorg` is the namespace/organization, `myapp` is the repository name, and `v1.0` (after the colon) is the tag.

</details>

---

### Question 14

Why are image layers important?

- A) They make images more secure
- B) They allow images to run faster
- C) They enable efficient storage and caching
- D) They are required by OCI standards

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

They enable efficient storage and caching.

**Explanation:** Layers allow Docker to cache and reuse unchanged layers across images and builds. Only changed layers need to be rebuilt or downloaded, making builds faster and reducing storage and bandwidth usage.

</details>

---

### Question 15

What Dockerfile instruction sets the base image?

- A) `BASE`
- B) `FROM`
- C) `IMAGE`
- D) `IMPORT`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`FROM`

**Explanation:** The `FROM` instruction specifies the base image for the build. Every Dockerfile must start with a `FROM` instruction (except for scratch builds or ARG before FROM).

</details>

---

### Question 16

What is the purpose of `.dockerignore`?

- A) To ignore Docker commands
- B) To skip certain Dockerfile instructions
- C) To exclude files from the build context
- D) To ignore container logs

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

To exclude files from the build context.

**Explanation:** `.dockerignore` prevents specified files from being sent to the Docker daemon during builds. This speeds up builds and prevents accidentally including sensitive files (like `.git`, `node_modules`, or secrets) in images.

</details>

---

### Question 17

Which Dockerfile instruction is used to install dependencies?

- A) `INSTALL`
- B) `GET`
- C) `RUN`
- D) `ADD`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`RUN`

**Explanation:** `RUN` executes commands during the build process. It's used to install packages, create directories, download files, and perform any other setup needed in the image.

</details>

---

### Question 18

What's the difference between `CMD` and `ENTRYPOINT`?

- A) CMD is for building, ENTRYPOINT is for running
- B) They are identical
- C) CMD can be overridden easily, ENTRYPOINT is the fixed executable
- D) ENTRYPOINT is deprecated

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

CMD can be overridden easily, ENTRYPOINT is the fixed executable.

**Explanation:** `ENTRYPOINT` defines the main executable that always runs. `CMD` provides default arguments that can be easily overridden. They're often used together: ENTRYPOINT for the command, CMD for default arguments.

</details>

---

### Question 19

Why should you copy `requirements.txt` before copying all source code in a Dockerfile?

- A) It's required by Docker
- B) It makes the image smaller
- C) It enables caching of the dependency installation layer
- D) It prevents security issues

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

It enables caching of the dependency installation layer.

**Explanation:** By copying `requirements.txt` and installing dependencies before copying source code, Docker can cache the dependency layer. Source code changes frequently, but dependencies don't. This order prevents reinstalling all dependencies on every code change.

</details>

---

### Question 20

Which image reference is immutable (cannot change)?

- A) `nginx:latest`
- B) `nginx:1.25`
- C) `nginx@sha256:abc123...`
- D) `nginx:stable`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`nginx@sha256:abc123...`

**Explanation:** Tags like `latest`, `1.25`, or `stable` can be updated to point to different images. Only digest references (`@sha256:...`) are immutable and guaranteed to always reference the exact same image content.

</details>

---

## Section 3: Volumes (5 questions)

### Question 21

What is the main purpose of volumes?

- A) To make containers faster
- B) To share images between containers
- C) To persist data beyond container lifecycle
- D) To connect containers to networks

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

To persist data beyond container lifecycle.

**Explanation:** Volumes store data outside the container's filesystem, so the data survives container removal. They're essential for databases, file uploads, and any data that needs to persist.

</details>

---

### Question 22

What's the difference between named volumes and bind mounts?

- A) Named volumes are faster
- B) Named volumes are managed by Docker; bind mounts use host paths
- C) Bind mounts can only be read-only
- D) There is no difference

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Named volumes are managed by Docker; bind mounts use host paths.

**Explanation:** Named volumes are stored in Docker's storage area and managed by Docker. Bind mounts map a specific host directory into the container. Named volumes are more portable; bind mounts are useful for development when you need to share source code.

</details>

---

### Question 23

How do you mount a volume as read-only?

- A) `-v mydata:/app --readonly`
- B) `-v mydata:/app:r`
- C) `-v mydata:/app:ro`
- D) `-v mydata:/app -r`

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

`-v mydata:/app:ro`

**Explanation:** The `:ro` suffix makes the mount read-only. The container can read files but not write to them. This is useful for sharing configuration or static content that shouldn't be modified.

</details>

---

### Question 24

What command lists all volumes?

- A) `docker volume show`
- B) `docker volume ls`
- C) `docker volumes`
- D) `docker list volumes`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`docker volume ls`

**Explanation:** `docker volume ls` lists all volumes. Similar to other Docker commands: `docker container ls`, `docker image ls`, `docker network ls`.

</details>

---

### Question 25

Where does Podman store rootless volumes by default?

- A) `/var/lib/containers/storage/volumes/`
- B) `~/.local/share/containers/storage/volumes/`
- C) `/var/lib/docker/volumes/`
- D) `/tmp/containers/volumes/`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`~/.local/share/containers/storage/volumes/`

**Explanation:** Podman in rootless mode stores data in the user's home directory at `~/.local/share/containers/`. Root Podman uses `/var/lib/containers/`. Docker uses `/var/lib/docker/`.

</details>

---

## Section 4: Networking (5 questions)

### Question 26

What does `-p 8080:80` do in `docker run -p 8080:80 nginx`?

- A) Opens port 8080 inside the container
- B) Maps host port 8080 to container port 80
- C) Exposes port 80 to port 8080 range
- D) Publishes ports 8080 through 80

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

Maps host port 8080 to container port 80.

**Explanation:** The format is `HOST:CONTAINER`. Traffic to the host's port 8080 is forwarded to port 80 inside the container. This allows accessing services inside containers from outside.

</details>

---

### Question 27

Why should you use custom networks instead of the default bridge?

- A) Custom networks are faster
- B) Custom networks use less memory
- C) Custom networks provide DNS resolution by container name
- D) The default bridge doesn't allow port publishing

<details>
<summary>Show Answer</summary>

**Correct Answer: C**

Custom networks provide DNS resolution by container name.

**Explanation:** Containers on custom networks can reach each other by name (automatic DNS). The default bridge requires using IP addresses or legacy `--link` flags. Custom networks also provide better isolation.

</details>

---

### Question 28

How can containers on the same custom network reach each other?

- A) By container name (automatic DNS)
- B) Only by IP address
- C) They cannot communicate
- D) Only through port publishing

<details>
<summary>Show Answer</summary>

**Correct Answer: A**

By container name (automatic DNS).

**Explanation:** Docker provides built-in DNS for custom networks. Containers can resolve each other by container name or network alias, making it easy to connect services without hardcoding IP addresses.

</details>

---

### Question 29

What network type gives a container direct access to the host's network?

- A) bridge
- B) host
- C) none
- D) direct

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

host

**Explanation:** The `host` network mode removes network isolation—the container shares the host's network namespace. The container's ports are directly accessible on the host without port mapping.

</details>

---

### Question 30

What command creates a new custom network?

- A) `docker network add mynet`
- B) `docker network create mynet`
- C) `docker create network mynet`
- D) `docker network new mynet`

<details>
<summary>Show Answer</summary>

**Correct Answer: B**

`docker network create mynet`

**Explanation:** `docker network create` creates a new network. By default, it creates a bridge network. Use `--driver` to specify other types like overlay for Swarm.

</details>

---

## Score tracker

Use this section to calculate your final score.

### Tally your results

| Section | Questions | Your Correct Answers |
|---------|-----------|---------------------|
| Container Basics | 1-10 | ___ / 10 |
| Images | 11-20 | ___ / 10 |
| Volumes | 21-25 | ___ / 5 |
| Networking | 26-30 | ___ / 5 |
| **Total** | | ___ / 30 |

### Calculate your percentage

**Your Score: ___ / 30 = ____%**

(Divide your correct answers by 30 and multiply by 100)

### How did you do?

| Score | Percentage | Level | Recommendation |
|-------|------------|-------|----------------|
| 27-30 | 90-100% | Excellent | Ready for Part 2: Intermediate |
| 24-26 | 80-89% | Good | Ready for Part 2, review missed topics |
| 18-23 | 60-79% | Fair | Review Part 1 materials before continuing |
| Below 18 | Below 60% | Needs Work | Complete Part 1 exercises and re-read materials |

---

## Next steps

- **Score 80%+**: Continue to [Part 2: Intermediate](../part2-intermediate/01-docker-compose-basics.md)
- **Score below 80%**: Review the [Part 1 Exercises](exercises/beginner-exercises.md) and re-read relevant sections
