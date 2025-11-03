# gds_snmp_receiver

gds_snmp_receiver is an SNMP trap receiver used by the GDS notification
stack. It listens for SNMP traps and publishes a normalized alert JSON to a
RabbitMQ queue (by default `alerts`) for downstream processing.

Key goals
---------
- Object-oriented, testable implementation (:class:`SNMPReceiver`).
- Extensive logging to make troubleshooting easier.
- Small, well-documented public API and a lightweight CLI wrapper for
  backwards compatibility with previous entrypoints.

Quickstart
----------
Install dependencies (project-level requirements may already include these):

```bash
# Example using pip (run in a virtualenv)
pip install pysnmp pika
```

Run the receiver (container environments may map host UDP ports differently):

```bash
python -m gds_snmp_receiver.receiver --host 0.0.0.0 --port 162 --rabbit amqp://guest:guest@rabbitmq:5672/ --queue alerts
```

Container notes
---------------
This package provides a package-local `Dockerfile` at `gds_snmp_receiver/Dockerfile`.
Build the image from the package directory to keep the build context small:

```bash
docker build -t gds_snmp_receiver:latest gds_snmp_receiver/
```

The image includes a small `healthcheck.py` which the Dockerfile wires into a `HEALTHCHECK` so orchestrators can probe the container's health. The healthcheck checks for the receiver Python process; it does not attempt to validate RabbitMQ connectivity.


Environment variables
---------------------
All CLI options may be provided via environment variables as well:

- `SNMP_LISTEN_HOST` - host to bind to (default: `0.0.0.0`)
- `SNMP_LISTEN_PORT` - UDP port (default: `162`)
- `RABBIT_URL` - RabbitMQ connection string (default: `amqp://guest:guest@rabbitmq:5672/`)
- `SNMP_QUEUE` - RabbitMQ queue name (default: `alerts`)
- `SNMP_LOG_LEVEL` - logging level (e.g. `DEBUG`, `INFO`)

Design and usage notes
----------------------
- The main API class is :class:`gds_snmp_receiver.SNMPReceiver` which can be
  imported and used programmatically from other Python code. Example:

```python
from gds_snmp_receiver import SNMPReceiver

r = SNMPReceiver(listen_host='0.0.0.0', listen_port=162, rabbit_url='amqp://...')
r.run()
```

- Logging: the package logs to the standard Python logging system. Set
  `SNMP_LOG_LEVEL` or configure the root logger to control verbosity.

- The default RabbitMQ publishing strategy opens a short-lived connection
  per message for simplicity; for high-throughput scenarios consider
  modifying the class to use a persistent connection or connection pool.

Troubleshooting
---------------
- If traps are not received, ensure the UDP port is reachable and the host
  sending traps is pointed to the correct port. Containers often map host
  ports like 1162 -> 162; confirm the mapping.
- Enable `DEBUG` logging to see detailed internal state and error traces:

```bash
SNMP_LOG_LEVEL=DEBUG python -m gds_snmp_receiver.receiver
```

Development notes
-----------------
- The implementation lives in `gds_snmp_receiver/core.py` and the thin CLI
  wrapper is `gds_snmp_receiver/receiver.py`.
- The package is intentionally small to make unit testing of the message
  construction and publishing logic straightforward.

License
-------
See the repository LICENSE for details.
