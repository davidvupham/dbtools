# Chapter 6: Managing Images

Once you've built images, you need to manage them: inspect, tag, push to registries, and clean up unused ones.

## Listing and Filtering Images

```bash
# List all local images
docker images

# Filter by repository name
docker images nginx

# Show only image IDs (useful for scripting)
docker images -q

# Show dangling images (untagged, intermediate layers)
docker images -f "dangling=true"
```

---

## Inspecting Images

### View History (Layers)

See what commands built the image:

```bash
docker history nginx:alpine
```

**Output:**

```
IMAGE          CREATED        CREATED BY                                      SIZE
3b25b682ea82   2 weeks ago    /bin/sh -c #(nop)  CMD ["nginx" "-g" "daemon…   0B
<missing>      2 weeks ago    /bin/sh -c #(nop)  EXPOSE 80                    0B
...
```

### Get Detailed Metadata

```bash
docker inspect nginx:alpine

# Extract specific fields
docker inspect nginx:alpine --format '{{.Os}}/{{.Architecture}}'
# Output: linux/amd64

docker inspect nginx:alpine --format '{{json .Config.Env}}' | jq .
```

---

## Tagging Images

Tags are how you version and organize images. The format is `repository:tag`.

```bash
# Tag a local image for Docker Hub
docker tag myapp:latest yourusername/myapp:1.0.0

# Tag for a private registry
docker tag myapp:latest registry.company.com/team/myapp:1.0.0

# Create multiple tags for the same image
docker tag myapp:latest yourusername/myapp:latest
docker tag myapp:latest yourusername/myapp:1.0
```

> [!TIP]
> Use semantic versioning (`major.minor.patch`) for production images.

---

## Pushing and Pulling Images

### Push to a Registry

```bash
# Login first
docker login

# Push the tagged image
docker push yourusername/myapp:1.0.0
```

### Pull from a Registry

```bash
# Pull a specific version
docker pull yourusername/myapp:1.0.0

# Pull from a private registry
docker pull registry.company.com/team/myapp:1.0.0
```

---

## Saving and Loading Images (Offline Transfer)

Need to move images without a registry (air-gapped environments)?

```bash
# Save image to a tar file
docker save -o myapp.tar myapp:1.0.0

# Load image from a tar file
docker load -i myapp.tar
```

---

## Cleaning Up Images

Images accumulate over time. Clean them up regularly.

```bash
# Remove a specific image
docker rmi myapp:old-version

# Remove all dangling images (untagged intermediates)
docker image prune

# Remove ALL unused images (not just dangling)
docker image prune -a

# Nuclear option: remove everything unused (containers, networks, images)
docker system prune -a
```

> [!WARNING]
> `docker system prune -a` removes **all** unused images, not just dangling ones. Use with caution.

---

## Finding Which Images Are in Use

Before pruning, you might want to know what's actually running:

```bash
# List images used by running containers
docker ps --format '{{.Image}}' | sort | uniq

# List images used by ALL containers (including stopped)
docker ps -a --format '{{.Image}}' | sort | uniq
```

---

## Summary

| Task | Command |
| :--- | :--- |
| List images | `docker images` |
| Inspect image | `docker inspect <image>` |
| View layers | `docker history <image>` |
| Tag image | `docker tag <source> <target>` |
| Push to registry | `docker push <image>` |
| Pull from registry | `docker pull <image>` |
| Save to file | `docker save -o file.tar <image>` |
| Load from file | `docker load -i file.tar` |
| Remove image | `docker rmi <image>` |
| Prune unused | `docker image prune -a` |

**Next Chapter:** Learn how to manage running containers in **Chapter 7: Container Management**.
