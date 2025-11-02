#!/usr/bin/env python3
"""Object-oriented SNMP trap receiver implementation.

This module exposes the :class:`SNMPReceiver` class which encapsulates the
SNMP engine, trap handling, and RabbitMQ publishing behavior.

Design notes
------------
- The class is small and focused: initialization, starting, stopping and
  processing traps. This makes it easier to unit test and to embed inside
  other applications.
- Extensive logging is included at DEBUG/INFO/ERROR levels to aid
  troubleshooting.

Configuration
-------------
All configuration may be provided via parameters when constructing
:class:`SNMPReceiver` or via environment variables. See the README for
examples.
"""
from __future__ import annotations

import hashlib
import json
import logging
import signal
import threading
from datetime import datetime
from typing import Any, Iterable, Optional

import pika
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv

logger = logging.getLogger("gds_snmp_receiver")


class SNMPReceiver:
    """SNMP Trap receiver that publishes normalized alerts to RabbitMQ.

    Parameters
    ----------
    listen_host:
        Host interface to bind the SNMP UDP listener to. Defaults to
        ``'0.0.0.0'``.
    listen_port:
        UDP port to listen on. Defaults to 162.
    rabbit_url:
        AMQP connection URL for RabbitMQ (passed to ``pika.URLParameters``).
    queue_name:
        Name of the RabbitMQ queue to publish alerts to (durable queue).

    Example
    -------
    >>> r = SNMPReceiver(rabbit_url='amqp://guest:guest@localhost:5672/')
    >>> r.run()
    """

    def __init__(
        self,
        listen_host: str = "0.0.0.0",
        listen_port: int = 162,
        rabbit_url: str = "amqp://guest:guest@rabbitmq:5672/",
        queue_name: str = "alerts",
    ) -> None:
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.rabbit_url = rabbit_url
        self.queue_name = queue_name

        self._snmp_engine: Optional[engine.SnmpEngine] = None
        self._running = threading.Event()

        # Configure module-level logger only if not configured by app
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        logger.debug(
            "SNMPReceiver __init__ listen=%s:%d rabbit_url=%s queue=%s",
            self.listen_host,
            self.listen_port,
            self._redact_url(self.rabbit_url),
            self.queue_name,
        )

    # -----------------
    # Public helpers
    # -----------------
    def run(self) -> None:
        """Start the SNMP dispatcher and block until stopped.

        This method registers signal handlers for SIGINT and SIGTERM so the
        receiver can be stopped cleanly using Ctrl-C or container termination.
        """
        self._setup_snmp_engine()

        # register signal handlers which call stop()
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start dispatcher
        logger.info("Starting SNMP trap receiver on %s:%s", self.listen_host, self.listen_port)
        self._snmp_engine.transportDispatcher.jobStarted(1)
        self._running.set()
        try:
            # This will block until dispatcher stops or an exception occurs
            self._snmp_engine.transportDispatcher.runDispatcher()
        except Exception:
            logger.exception("SNMP transport dispatcher terminated with error")
            try:
                self._snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                logger.exception("Error closing SNMP dispatcher after failure")
            raise
        finally:
            self._running.clear()
            logger.info("SNMP receiver has stopped")

    def stop(self) -> None:
        """Stop the SNMP receiver dispatcher gracefully.

        This attempts to close the underlying transport dispatcher if present.
        Calling stop() when the receiver is not running is a no-op.
        """
        if not self._snmp_engine:
            logger.debug("stop() called but no SNMP engine is configured")
            return

        try:
            logger.info("Stopping SNMP receiver")
            self._snmp_engine.transportDispatcher.closeDispatcher()
        except Exception:
            logger.exception("Failed to close SNMP transport dispatcher")
        finally:
            self._running.clear()

    # -----------------
    # Internal helpers
    # -----------------
    def _setup_snmp_engine(self) -> None:
        if self._snmp_engine is not None:
            logger.debug("SNMP engine already configured")
            return

        logger.debug("Configuring SNMP engine")
        snmp_engine = engine.SnmpEngine()

        listen_addr = (self.listen_host, int(self.listen_port))
        config.addTransport(
            snmp_engine,
            udp.domainName,
            udp.UdpTransport().openServerMode(listen_addr),
        )

        # Attach callback - bound method is accepted by pysnmp
        ntfrcv.NotificationReceiver(snmp_engine, self._trap_callback)

        self._snmp_engine = snmp_engine
        logger.debug("SNMP engine configured and notification receiver attached")

    def _trap_callback(self, snmpEngine: Any, stateReference: Any, contextEngineId: Any, contextName: Any, varBinds: Iterable[Any], cbCtx: Any) -> None:
        """Handle an incoming SNMP trap and publish a normalized alert.

        This method is intentionally defensive: it logs detailed debug
        information and guards the publishing logic so a failure does not
        crash the SNMP dispatcher.
        """
        try:
            var_binds_list = list(varBinds)
            logger.info("Received SNMP trap with %d varbinds", len(var_binds_list))

            alert_name = None
            details = {}
            for oid, val in var_binds_list:
                oid_str = str(oid)
                details[oid_str] = str(val)
                # common trap OID for trap identity
                if oid_str.endswith('.1.3.6.1.6.3.1.1.4.1.0') or oid_str.endswith('1.3.6.1.6.3.1.1.4.1.0'):
                    alert_name = str(val)

            if not alert_name and var_binds_list:
                first = var_binds_list[0]
                alert_name = f"snmp:{str(first[0])}"

            idempotency_id = self.compute_idempotency_from_trap(var_binds_list)

            payload = {
                'idempotency_id': idempotency_id,
                'alert_name': alert_name,
                'source': 'snmp',
                'received_at': datetime.utcnow().isoformat() + 'Z',
                'raw': details,
                'subject': f'SNMP Trap: {alert_name}',
                'body_text': json.dumps(details, indent=2),
            }

            logger.debug("Publishing alert payload: %s", payload)
            self.publish_alert(payload)
        except Exception:
            logger.exception("Error handling SNMP trap")

    def publish_alert(self, payload: dict) -> None:
        """Publish the alert payload to RabbitMQ.

        This implementation uses a short-lived connection per message which is
        simple and robust for low-to-moderate throughput. If you need higher
        performance consider connection pooling or a persistent connection.
        """
        try:
            params = pika.URLParameters(self.rabbit_url)
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            ch.queue_declare(queue=self.queue_name, durable=True)
            ch.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            conn.close()
            logger.info('Published alert to queue id=%s', payload.get('idempotency_id'))
        except Exception:
            logger.exception('Failed to publish alert to RabbitMQ')

    @staticmethod
    def compute_idempotency_from_trap(var_binds: Iterable[Any]) -> str:
        """Create an idempotency hash for a trap.

        The current implementation includes a timestamp to preserve the original
        behaviour where each trap receives a unique id. If you require
        deterministic idempotency across retries, remove the timestamp.
        """
        s = ''.join(f"{str(x[0])}={str(x[1])};" for x in var_binds)
        # Keep behaviour consistent with prior implementation by including time
        s += datetime.utcnow().isoformat()
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    # -----------------
    # Utilities
    # -----------------
    def _signal_handler(self, signum: int, frame: Any) -> None:
        logger.info("Received signal %s, shutting down receiver", signum)
        try:
            self.stop()
        except Exception:
            logger.exception("Error while stopping receiver after signal")

    @staticmethod
    def _redact_url(url: str) -> str:
        """Redact credentials in a URL for safe logging.

        This is intentionally simple and not a full URL parser – good enough
        for log messages. For more robust behavior use urllib.parse.
        """
        try:
            # quick and dirty redact: replace ://<user>:<pass>@ with ://<redacted>@
            if '://' in url and '@' in url:
                prefix, rest = url.split('://', 1)
                creds, host = rest.split('@', 1)
                return f"{prefix}://<redacted>@{host}"
        except Exception:
            pass
        return url
