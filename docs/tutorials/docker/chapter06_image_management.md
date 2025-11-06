# Chapter 6: Managing Images

```bash
# List and inspect
docker image ls
docker image inspect <image>:<tag>
docker image history <image>:<tag>

# Cleanup
docker image prune -f
docker system prune

# Save/Load
docker image save -o myimg.tar <image>:<tag>
docker image load -i myimg.tar

# Tag/push
docker tag myimg:dev USER/myimg:dev
docker push USER/myimg:dev
```

Which images are in use:

```bash
# Show running containers and their images
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
# Count images used by running containers
docker ps --format '{{.Image}}' | sort | uniq -c
```

---

## Maintenance & housekeeping

Disk usage and safe cleanup:

```bash
docker system df                 # high-level disk usage
docker image prune               # remove dangling images
docker image prune -a            # remove all unused images
docker builder prune             # prune build cache
docker system prune              # containers, networks, images, build cache
docker system prune -a --volumes # include images and volumes (destructive!)
```

Tagging strategy:
- Prefer immutable tags per release (e.g., `1.2.3`) and per commit (SHA).
- Update moving tags (`latest`, `1`, `1.2`) only after promotion.
- Keep registry retention policies (e.g., last N versions) to control storage.

Export/import:
```bash
docker image save -o myimg.tar myorg/app:1.2.3
docker image load -i myimg.tar
```
