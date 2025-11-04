## Containerization & E2E HOWTO for gds_snmp_receiver

This document captures the containerization approach, build/run commands, the end-to-end (SNMP -> RabbitMQ) test flow, troubleshooting guidance, and recommended next steps. It mirrors the guidance created during the containerization effort and is intended to be stored alongside the repository so contributors can follow exact steps.

### Summary
- Purpose: containerize `gds_snmp_receiver` as a self-contained package with Docker support, provide an end-to-end smoke test that sends an SNMP trap and validates message delivery into RabbitMQ, and document commands and troubleshooting.
- Location: All files are contained within the `gds_snmp_receiver/` directory including Dockerfile, `requirements.txt`, `entrypoint.sh`, `healthcheck.py`, `docker-compose.e2e.yml`, `docker-compose.yml`, and `tools/` directory with E2E test scripts.

### Contract
- Inputs: the `gds_snmp_receiver/` directory with all necessary files for containerization and testing.
- Outputs: a built container image and a deterministic way to exercise SNMP trap -> RabbitMQ publish.
- Error modes: broker unreachable, queue not declared, SNMP trap not delivered, pysnmp compatibility issues.
- Success criteria: the E2E helper returns exit code 0 and prints the message consumed from RabbitMQ.

---

## Build & Run (step-by-step)

1) Build the package-local image

This builds the image from the `gds_snmp_receiver/` directory.

```bash
cd gds_snmp_receiver
docker build -t gds_snmp_receiver:latest .
```

2) Run the receiver standalone (non-privileged host port example)

Map host port 1162 to container UDP 162 so we don't need privileged host ports.

```bash
docker run -d --name gds_snmp_test -p 1162:162/udp gds_snmp_receiver:latest
```

If you need to bind to host UDP 162 (privileged), prefer adding capability rather than running the container as root:

```bash
docker run -d --name gds_snmp_test --cap-add=NET_BIND_SERVICE -p 162:162/udp gds_snmp_receiver:latest
```

3) Start the E2E compose stack (RabbitMQ + receiver + sender)

```bash
cd gds_snmp_receiver
docker compose -f docker-compose.e2e.yml up -d --build
```

This will start:
- `rabbitmq` (rabbitmq:3-management)
- `gds-snmp-receiver` (built from current directory)
- `snmp-sender` (helper used to run the E2E script)

4) Run the E2E helper script (recommended)

The helper runs inside the `snmp-sender` service and performs the following:
- Waits for RabbitMQ to be reachable
- Waits for the `alerts` queue to be present (or times out)
- Ensures `snmptrap` is available (installs net-snmp in the sender container if necessary)
- Sends a trap to `gds-snmp-receiver`
- Polls RabbitMQ for a message (basic_get)

Run it with:

```bash
docker compose -f docker-compose.e2e.yml run --rm snmp-sender python tools/e2e_send_and_check.py
```

Exit codes (from the helper):
- 0: success (message received)
- 2: RabbitMQ unreachable
- 3: failed to send snmptrap
- 4: no message received in poll window

---

## What the e2e helper does (detailed)

- Ensures `pika` is installed in the sender container (pip install if missing).
- Waits for RabbitMQ to accept connections via repeated `BlockingConnection` attempts.
- Waits for the `alerts` queue via a passive `queue_declare(queue=..., passive=True)` (retries until timeout).
- Ensures `snmptrap` (net-snmp) is installed (uses apt in sender container if missing).
- Sends an SNMPv2c trap using `snmptrap -v 2c -c public <RECEIVER_HOST> '' <OID>`.
- Polls `alerts` with `basic_get` until a message is found or timeout.

Notes:
- The compose network allows `snmp-sender` to reach `gds-snmp-receiver` using the service name `gds-snmp-receiver` and port 162.

---

## Dockerfile & entrypoint notes

- Base image: `python:3.11-slim` (example) to keep images minimal.
- Dependencies installed from `gds_snmp_receiver/requirements.txt` (pin versions if you want deterministic builds).
- Non-root runtime user is created and used. If binding privileged ports (162) you must either: run as root or add `--cap-add=NET_BIND_SERVICE` to the container run command.
- ENTRYPOINT is `entrypoint.sh` which does `exec "$@"` so signals are preserved and Python is reaped properly.
- HEALTHCHECK runs a small Python script (e.g., `healthcheck.py`) that checks the receiver process presence.

---

## Environment variables

- `RABBIT_URL` — amqp URL, default: `amqp://guest:guest@rabbitmq:5672/`
- `SNMP_QUEUE` — the queue name the receiver publishes to, default: `alerts`
- `RECEIVER_HOST`/`RECEIVER_PORT` — used by test sender; defaults `gds-snmp-receiver` and `162`.

Adjust via the compose file or `docker run -e ...`.

---

## Known failure modes and fixes

1) No message in RabbitMQ after sending trap
- Cause: receiver hasn't declared the queue or hasn't connected to RabbitMQ yet.
- Fixes:
  - Ensure the receiver declares the queue on AMQP connection: call `ch.queue_declare(queue='alerts', durable=True)` when connection established.
  - Wait longer for RabbitMQ to become available (increase helper's timeout).
  - Confirm trap reached receiver (UDP port mapping) and check container logs.

2) pysnmp import problems
- Cause: pysnmp changed carriers across versions.
- Fix: either include fallback imports in `core.py` (try `pysnmp.carrier.asynsock` then fallback to `pysnmp.carrier.asyncio`) or pin `pysnmp` in requirements.

3) Binding host port 162
- HOST port 162 is privileged; use a non-privileged host port (eg 1162:162/udp), or run the container with `--cap-add=NET_BIND_SERVICE`.

---

## Recommendations (next steps to make E2E deterministic)

1) Have the receiver declare the `alerts` queue immediately after successful AMQP connection.
2) Add a readiness indicator (file or HTTP endpoint) that signals AMQP connected + queue declared; update the e2e helper to wait for it.
3) Pin `pysnmp` and `pika` versions in `gds_snmp_receiver/requirements.txt`.
4) Add a `test-publish` CLI option to the receiver that publishes a sample message for quick smoke tests.
5) Add CI job to build images and run the e2e stack where possible.

---

## Example run sequence (copyable)

```bash
# Build image
docker build -t gds_snmp_receiver:latest gds_snmp_receiver/

# Start E2E stack
docker compose -f docker-compose.e2e.yml up -d --build

# Run e2e helper
docker compose -f docker-compose.e2e.yml run --rm snmp-sender python tools/e2e_send_and_check.py

# View receiver logs
docker compose -f docker-compose.e2e.yml logs gds-snmp-receiver

# Tear down
docker compose -f docker-compose.e2e.yml down
```

---

## Completion summary

What changed: documentation added to `DOCKER_E2E_HOWTO.md` with full build/run/test instructions and troubleshooting. The `tools/e2e_send_and_check.py` script exists in `tools/` and is the helper used by the E2E flow.

If you'd like, I can implement one of the recommended next steps now (make the receiver declare the queue at startup, add a readiness endpoint, or make the e2e helper declare the queue before sending the trap). Tell me which and I'll implement it and re-run the E2E test.
