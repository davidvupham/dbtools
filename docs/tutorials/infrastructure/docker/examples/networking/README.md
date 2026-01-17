# Networking Examples

Two simple Compose stacks demonstrating bridge and host networking.

## Bridge network (recommended default)

```bash
cd docs/tutorials/docker/examples/networking
# Start services on a user-defined bridge network
docker compose -f compose-bridge.yaml up -d

# Test endpoints
curl -I http://localhost:8080
curl -s http://localhost:5000 | head -n 5

# Service discovery (web -> api)
WEB=$(docker compose -f compose-bridge.yaml ps -q web)
docker exec "$WEB" getent hosts api

# Tear down
docker compose -f compose-bridge.yaml down
```

## Host network (Linux only)

```bash
cd docs/tutorials/docker/examples/networking
# Ensure host port 80 is free; this binds directly to host network
docker compose -f compose-host.yaml up -d

curl -I http://localhost:80

# Tear down
docker compose -f compose-host.yaml down
```

Notes:
- On macOS/Windows (Docker Desktop), `network_mode: host` behaves differently and is not equivalent to Linux host networking.
- For macvlan, see the deep dive guide; it requires network-specific configuration.
