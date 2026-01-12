# Getting Started with Podman

This tutorial will guide you through the basics of using Podman to run containers, build images, and manage Pods.

**Prerequisites:**

* Podman installed on your system ([Installation Guide](../../how-to/podman/install-podman-rhel.md)).

## 1. Running Your First Container

Let's pull and run a simple web server.

```bash
podman run -dt -p 8080:80 --name my-nginx nginx:alpine
```

* `-d`: Detached mode (run in background).
* `-t`: Allocate a pseudo-TTY.
* `-p 8080:80`: Map host port 8080 to container port 80.
* `--name`: Give it a friendly name.

**Verify it works:**
Open your browser to `http://localhost:8080` or curl it:

```bash
curl http://localhost:8080
```

## 2. Building an Image

Create a file named `Containerfile` (or `Dockerfile`) with the following content:

```dockerfile
FROM registry.access.redhat.com/ubi9/ubi:latest
RUN dnf install -y python3
CMD ["python3", "-m", "http.server", "8000"]
```

**Build the image:**

```bash
podman build -t my-python-app .
```

* `--tag` (`-t`): Name your image.
* `.`: Build context (current directory).

**Run your new image:**

```bash
podman run -dt -p 8000:8000 my-python-app
```

Check with `curl http://localhost:8000`.

## 3. Working with Pods

One of Podman's unique features is the ability to manage Pods locally. Let's create a Pod that contains a database and a
web frontend.

**Create a Pod:**
We expose port 8081 on the Pod itself.

```bash
podman pod create --name my-app-pod -p 8081:80
```

**Run containers inside the Pod:**

1. **Database (PostgreSQL):**

    ```bash
    podman run -dt --pod my-app-pod -e POSTGRES_PASSWORD=secret postgres:alpine
    ```

2. **Web Server (Adminer - Database UI):**

    ```bash
    podman run -dt --pod my-app-pod adminer
    ```

**Explain:** Since both containers are in the same Pod, they share `localhost`. Adminer can talk to Postgres on `localhost:5432`!

**Access the application:**
Go to `http://localhost:8081`. Log in with:

* System: PostgreSQL
* Server: localhost
* Username: postgres
* Password: secret

## 4. Cleanup

Stop and remove the Pod (which handles all containers inside it):

```bash
podman pod stop my-app-pod
podman pod rm my-app-pod
```

Clean up individual containers:

```bash
podman stop my-nginx my-python-app
podman rm my-nginx my-python-app
```
