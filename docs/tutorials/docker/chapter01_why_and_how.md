# Chapter 1: The Why and How of Docker

Docker packages apps and their dependencies into portable containers so they run the same anywhere. Containers are lighter than virtual machines because they share the host kernel while isolating processes, filesystems, and networks.

- Why Docker:
  - Eliminate “works on my machine” drift
  - Ship environments with the app
  - Faster startup than VMs, smaller footprints, better density
- Core concepts:
  - Images: immutable templates
  - Containers: running instances of images
  - Registries: storage for images

Try it:

```bash
# Sanity check
docker version
# Hello from a container
docker run --rm hello-world
```

What Docker isn’t:
- Not a full VM (no separate kernel)
- Not a config management tool (focus is packaging/runtime)
- Not a perfect security boundary—harden and apply least privilege
