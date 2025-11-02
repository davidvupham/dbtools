#!/usr/bin/env python3
"""Small CLI wrapper around :class:`gds_snmp_receiver.SNMPReceiver`.

This script keeps the original module-level entrypoint but delegates all
behaviour to :class:`gds_snmp_receiver.SNMPReceiver` so the implementation
is object-oriented and easier to maintain.
"""
from __future__ import annotations

import argparse
import os
import logging
from typing import Optional

from .core import SNMPReceiver


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="gds_snmp_receiver CLI")
    parser.add_argument("--host", default=os.environ.get("SNMP_LISTEN_HOST", "0.0.0.0"), help="Host/interface to listen on")
    parser.add_argument("--port", type=int, default=int(os.environ.get("SNMP_LISTEN_PORT", 162)), help="UDP port to listen on")
    parser.add_argument("--rabbit", default=os.environ.get("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/"), help="RabbitMQ URL")
    parser.add_argument("--queue", default=os.environ.get("SNMP_QUEUE", "alerts"), help="RabbitMQ queue name")
    parser.add_argument("--log-level", default=os.environ.get("SNMP_LOG_LEVEL", "INFO"), help="Logging level")

    args = parser.parse_args(argv)

    # Configure root logging according to the CLI option
    numeric_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(level=numeric_level, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    receiver = SNMPReceiver(listen_host=args.host, listen_port=args.port, rabbit_url=args.rabbit, queue_name=args.queue)
    receiver.run()


if __name__ == "__main__":
    main()
