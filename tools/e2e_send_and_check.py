#!/usr/bin/env python3
"""
End-to-end SNMP -> RabbitMQ smoke tester.

This script is intended to be run inside the `snmp-sender` container of the
`docker-compose.e2e.yml` stack. It performs the following steps:

1. Wait for RabbitMQ to be reachable on the compose network.
2. Wait for the `alerts` queue to be declared (created by the receiver) or
   proceed after a timeout if the receiver is not declaring the queue.
3. Ensure `snmptrap` is available (install `snmp`/net-snmp via apt if missing).
4. Send an SNMPv2c trap to the `gds-snmp-receiver` service.
5. Poll RabbitMQ and attempt to read a message from the `alerts` queue.

Usage (from repo root):
  docker compose -f docker-compose.e2e.yml run --rm snmp-sender python tools/e2e_send_and_check.py

The script prints progress and exits with code 0 on success (message received)
or non-zero on failure.
"""

import os
import subprocess
import sys
import time
from typing import Optional

RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = os.environ.get("SNMP_QUEUE", "alerts")
RECEIVER_HOST = os.environ.get("RECEIVER_HOST", "gds-snmp-receiver")
RECEIVER_PORT = int(os.environ.get("RECEIVER_PORT", "162"))


def run(cmd: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print(f"> {cmd}")
    return subprocess.run(cmd, shell=True, check=check, text=True, capture_output=capture)


def ensure_snmptrap() -> None:
    """Install net-snmp (snmptrap) if it is not available."""
    try:
        subprocess.run(["snmptrap", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("snmptrap present")
        return
    except OSError:
        print("snmptrap not found; installing net-snmp via apt")

    # Install non-interactively
    run("apt-get update -qq", check=True)
    run("DEBIAN_FRONTEND=noninteractive apt-get install -y -qq snmp", check=True)


def wait_for_rabbit(timeout: int = 60) -> bool:
    """Try to connect to RabbitMQ using pika until success or timeout."""
    print("Waiting for RabbitMQ to accept connections...")
    # Ensure pika is installed in the sender container
    try:
        import pika  # type: ignore
    except Exception:
        print("pika not present in sender container; installing via pip")
        run("pip install --no-cache-dir pika", check=True)

    start = time.time()
    while time.time() - start < timeout:
        try:
            import pika  # type: ignore
        except Exception as e:
            print("RabbitMQ not ready yet:", e)
            time.sleep(1)
    return False


def wait_for_queue(queue: str, timeout: int = 30) -> bool:
    """Wait for queue to be present by checking via pika passive declare."""
    print(
        "Waiting up to {}s for queue '{}' to be declared by the receiver".format(
            timeout, queue
        )
    )
    import pika

    params = pika.URLParameters(RABBIT_URL)
    start = time.time()
    while time.time() - start < timeout:
        try:
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            # passive declare will throw if queue does not exist
            ch.queue_declare(queue=queue, passive=True)
            conn.close()
            print("Queue '{}' exists".format(queue))
            return True
        except pika.exceptions.AMQPError as e:
            # queue not found or connection error
            print("queue not present yet:", e)
            time.sleep(1)
    return False


def send_trap() -> None:
    """Send a simple SNMPv2c trap using snmptrap to the receiver host."""
    # Example OID used: linkDown (1.3.6.1.6.3.1.1.5.3) or use generic
    oid = ".1.3.6.1.6.3.1.1.5.1"
    # Use host only (snmptrap expects host (or host:port) and then varbinds.
    # Using just the service name is usually sufficient on the compose network.
    cmd = f"snmptrap -v 2c -c public {RECEIVER_HOST} '' {oid}"
    print("Sending SNMP trap:", cmd)
    run(cmd, check=True)


def poll_for_message(queue: str, timeout: int = 20) -> Optional[str]:
    print(f"Polling RabbitMQ for messages on '{queue}' for up to {timeout}s")
    import pika

    params = pika.URLParameters(RABBIT_URL)
    start = time.time()
    while time.time() - start < timeout:
        try:
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            method, props, body = ch.basic_get(queue=queue, auto_ack=True)
            conn.close()
            if body:
                print("Message received from queue")
                return body.decode(errors='ignore')
        except Exception as e:
                print("pika poll error:", e)
        time.sleep(1)
    return None


def main() -> int:
    # Step 1: ensure RabbitMQ is reachable
    ok = wait_for_rabbit(timeout=60)
    if not ok:
        print("RabbitMQ did not become reachable within timeout")
        return 2

    # Step 2: wait for the receiver to declare the queue
    q_ok = wait_for_queue(QUEUE_NAME, timeout=30)
    if not q_ok:
            print(
                "Queue '{}' not present after wait; continuing anyway".format(QUEUE_NAME)
            )

    # Step 3: ensure snmptrap available
    ensure_snmptrap()

    # Step 4: send trap
    try:
        send_trap()
    except subprocess.CalledProcessError as e:
        print("Failed to send snmptrap:", e)
        return 3

    # Step 5: poll RabbitMQ for message
    msg = poll_for_message(QUEUE_NAME, timeout=30)
    if msg:
        print("E2E SUCCESS — received message:")
        print(msg)
        return 0
    else:
        print("E2E FAILURE — no message received from RabbitMQ")
        return 4


if __name__ == "__main__":
    sys.exit(main())
