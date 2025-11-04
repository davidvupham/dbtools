# Chapter 7: Container Management

- Logs and exec:

```bash
docker logs -f <name>
docker exec -it <name> sh
```

- Inspect, stats, health:

```bash
docker inspect <name>
docker stats
```

- Restart policies:

```bash
docker run --restart=on-failure:3 myimage:tag
```
