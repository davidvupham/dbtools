# Part 1: Beginner Quiz

> **Module:** Part 1 - Beginner | **Type:** Assessment | **Questions:** 30

Test your understanding of container fundamentals. Aim for at least 80% to proceed to Part 2.

---

## Section 1: Container Basics (10 questions)

### Question 1
What is the primary difference between a container and a virtual machine?

- [ ] Containers are faster because they use hardware virtualization
- [x] Containers share the host kernel while VMs include their own kernel
- [ ] VMs can run any operating system, containers cannot
- [ ] Containers require more disk space than VMs

### Question 2
Which command runs a container interactively with a terminal?

- [ ] `docker run nginx`
- [ ] `docker run -d nginx`
- [x] `docker run -it nginx sh`
- [ ] `docker run --terminal nginx`

### Question 3
What does the `-d` flag do in `docker run -d nginx`?

- [ ] Downloads the image first
- [ ] Runs in debug mode
- [x] Runs the container in detached (background) mode
- [ ] Disables networking

### Question 4
How do you stop a running container gracefully?

- [ ] `docker kill mycontainer`
- [x] `docker stop mycontainer`
- [ ] `docker pause mycontainer`
- [ ] `docker remove mycontainer`

### Question 5
What happens to changes made inside a container when it's removed?

- [ ] Changes are automatically saved to the image
- [ ] Changes persist to the next container
- [x] Changes are lost unless volumes are used
- [ ] Changes are backed up automatically

### Question 6
Which command shows only running containers?

- [x] `docker ps`
- [ ] `docker ps -a`
- [ ] `docker list`
- [ ] `docker containers`

### Question 7
What is the purpose of `docker exec`?

- [ ] To create a new container
- [ ] To build an image
- [x] To run a command inside a running container
- [ ] To export a container

### Question 8
How do you remove all stopped containers at once?

- [ ] `docker rm --all`
- [ ] `docker remove stopped`
- [x] `docker container prune`
- [ ] `docker clean containers`

### Question 9
What does `docker logs -f mycontainer` do?

- [ ] Shows the first log entries
- [ ] Filters log output
- [x] Follows log output in real-time
- [ ] Formats logs as JSON

### Question 10
Which restart policy keeps the container running unless manually stopped?

- [ ] `always`
- [x] `unless-stopped`
- [ ] `on-failure`
- [ ] `never-stop`

---

## Section 2: Images (10 questions)

### Question 11
What is the relationship between images and containers?

- [ ] Images are running containers
- [x] Images are templates from which containers are created
- [ ] Containers store images
- [ ] They are the same thing

### Question 12
What does `docker pull python:3.12-slim` do?

- [ ] Creates a new Python container
- [ ] Builds a Python image
- [x] Downloads the Python 3.12 slim image from a registry
- [ ] Updates the local Python installation

### Question 13
Which part of `ghcr.io/myorg/myapp:v1.0` is the tag?

- [ ] `ghcr.io`
- [ ] `myorg`
- [ ] `myapp`
- [x] `v1.0`

### Question 14
Why are image layers important?

- [ ] They make images more secure
- [ ] They allow images to run faster
- [x] They enable efficient storage and caching
- [ ] They are required by OCI standards

### Question 15
What Dockerfile instruction sets the base image?

- [ ] `BASE`
- [x] `FROM`
- [ ] `IMAGE`
- [ ] `IMPORT`

### Question 16
What is the purpose of `.dockerignore`?

- [ ] To ignore Docker commands
- [ ] To skip certain Dockerfile instructions
- [x] To exclude files from the build context
- [ ] To ignore container logs

### Question 17
Which Dockerfile instruction is used to install dependencies?

- [ ] `INSTALL`
- [ ] `GET`
- [x] `RUN`
- [ ] `ADD`

### Question 18
What's the difference between `CMD` and `ENTRYPOINT`?

- [ ] CMD is for building, ENTRYPOINT is for running
- [ ] They are identical
- [x] CMD can be overridden easily, ENTRYPOINT is the fixed executable
- [ ] ENTRYPOINT is deprecated

### Question 19
Why should you copy `requirements.txt` before copying all source code in a Dockerfile?

- [ ] It's required by Docker
- [ ] It makes the image smaller
- [x] It enables caching of the dependency installation layer
- [ ] It prevents security issues

### Question 20
Which image reference is immutable (cannot change)?

- [ ] `nginx:latest`
- [ ] `nginx:1.25`
- [x] `nginx@sha256:abc123...`
- [ ] `nginx:stable`

---

## Section 3: Volumes (5 questions)

### Question 21
What is the main purpose of volumes?

- [ ] To make containers faster
- [ ] To share images between containers
- [x] To persist data beyond container lifecycle
- [ ] To connect containers to networks

### Question 22
What's the difference between named volumes and bind mounts?

- [ ] Named volumes are faster
- [x] Named volumes are managed by Docker; bind mounts use host paths
- [ ] Bind mounts can only be read-only
- [ ] There is no difference

### Question 23
How do you mount a volume as read-only?

- [ ] `-v mydata:/app --readonly`
- [ ] `-v mydata:/app:r`
- [x] `-v mydata:/app:ro`
- [ ] `-v mydata:/app -r`

### Question 24
What command lists all volumes?

- [ ] `docker volume show`
- [x] `docker volume ls`
- [ ] `docker volumes`
- [ ] `docker list volumes`

### Question 25
Where does Podman store rootless volumes by default?

- [ ] `/var/lib/containers/storage/volumes/`
- [x] `~/.local/share/containers/storage/volumes/`
- [ ] `/var/lib/docker/volumes/`
- [ ] `/tmp/containers/volumes/`

---

## Section 4: Networking (5 questions)

### Question 26
What does `-p 8080:80` do in `docker run -p 8080:80 nginx`?

- [ ] Opens port 8080 inside the container
- [x] Maps host port 8080 to container port 80
- [ ] Exposes port 80 to port 8080 range
- [ ] Publishes ports 8080 through 80

### Question 27
Why should you use custom networks instead of the default bridge?

- [ ] Custom networks are faster
- [ ] Custom networks use less memory
- [x] Custom networks provide DNS resolution by container name
- [ ] The default bridge doesn't allow port publishing

### Question 28
How can containers on the same custom network reach each other?

- [x] By container name (automatic DNS)
- [ ] Only by IP address
- [ ] They cannot communicate
- [ ] Only through port publishing

### Question 29
What network type gives a container direct access to the host's network?

- [ ] bridge
- [x] host
- [ ] none
- [ ] direct

### Question 30
What command creates a new custom network?

- [ ] `docker network add mynet`
- [x] `docker network create mynet`
- [ ] `docker create network mynet`
- [ ] `docker network new mynet`

---

## Answer Key

| Question | Answer | Question | Answer |
|----------|--------|----------|--------|
| 1 | B | 16 | C |
| 2 | C | 17 | C |
| 3 | C | 18 | C |
| 4 | B | 19 | C |
| 5 | C | 20 | C |
| 6 | A | 21 | C |
| 7 | C | 22 | B |
| 8 | C | 23 | C |
| 9 | C | 24 | B |
| 10 | B | 25 | B |
| 11 | B | 26 | B |
| 12 | C | 27 | C |
| 13 | D | 28 | A |
| 14 | C | 29 | B |
| 15 | B | 30 | B |

---

## Scoring

| Score | Level | Recommendation |
|-------|-------|----------------|
| 27-30 (90-100%) | Excellent | Ready for Part 2: Intermediate |
| 24-26 (80-89%) | Good | Ready for Part 2, review missed topics |
| 18-23 (60-79%) | Fair | Review Part 1 materials before continuing |
| Below 18 (<60%) | Needs Work | Complete Part 1 exercises and re-read materials |

---

## Next Steps

- **Score 80%+**: Continue to [Part 2: Intermediate](../part2-intermediate/01-docker-compose-basics.md)
- **Score below 80%**: Review the [Part 1 Exercises](exercises/beginner-exercises.md) and re-read relevant sections
