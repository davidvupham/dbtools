# Chapter 8: Docker Networking

- Modes: none, bridge (default), host (Linux), macvlan (advanced).
- Prefer user‑defined bridge for isolation and service discovery.

```bash
# Create and use a user-defined network
docker network create app-net
docker run -d --name api --network app-net myorg/api:1.0
docker run -d --name web --network app-net -p 8080:80 myorg/web:1.0
```

See deep dive: `docs/tutorials/docker/networking_deep_dive.md`

Examples: `docs/tutorials/docker/examples/networking/`
