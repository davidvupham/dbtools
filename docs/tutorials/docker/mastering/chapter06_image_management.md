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
