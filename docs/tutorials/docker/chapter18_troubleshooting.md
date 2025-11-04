# Chapter 18: Troubleshooting & Debugging

- Logs/events/stats: `docker logs -f`, `docker events`, `docker stats`
- Exec into containers: `docker exec -it <name> sh`
- Inspect everything: `docker inspect <name-or-id>`
- Port issues: verify `-p host:container` and app binds to `0.0.0.0`
- Mount issues: check user IDs, SELinux/AppArmor labels

Cleanup helpers:

```bash
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker image prune -f
```
