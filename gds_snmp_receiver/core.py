"""Object-oriented SNMP trap receiver implementation.

This module provides :class:`SNMPReceiver` which wraps the SNMP engine,
trap handling and RabbitMQ publishing. It focuses on clarity,
testability and rich logging to aid troubleshooting.
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
    """SNMP trap receiver that publishes normalized alerts to RabbitMQ.

    The receiver maintains a short-lived SNMP dispatcher and a persistent
    pika connection/channel to reduce overhead when publishing multiple
    alerts.
    """

    def __init__(
        self,
        listen_host: str = "0.0.0.0",
        listen_port: int = 162,
        rabbit_url: str = "amqp://guest:guest@rabbitmq:5672/",
        queue_name: str = "alerts",
    ) -> None:
        self.listen_host = listen_host
        self.listen_port = int(listen_port)
        self.rabbit_url = rabbit_url
        self.queue_name = queue_name

        self._snmp_engine: Optional[engine.SnmpEngine] = None
        self._running = threading.Event()

        # pika connection + channel for reuse
        self._pika_conn: Optional[pika.BlockingConnection] = None
        # Use a simple attribute for the channel to avoid long annotations
        self._pika_ch = None

        if not logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                )
            )
            logger.addHandler(h)
            logger.setLevel(logging.INFO)

        logger.debug("SNMPReceiver(init) host=%s port=%d queue=%s",
                     self.listen_host, self.listen_port, self.queue_name)

    # Public API
    def run(self) -> None:
        """Start the SNMP dispatcher and block until stopped.

        Registers SIGINT/SIGTERM handlers for graceful shutdown.
        """
        self._setup_snmp_engine()
        self._ensure_pika_connection()

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Starting SNMP trap receiver on %s:%d",
                    self.listen_host, self.listen_port)

        assert self._snmp_engine is not None
        self._snmp_engine.transportDispatcher.jobStarted(1)
        self._running.set()
        try:
            self._snmp_engine.transportDispatcher.runDispatcher()
        except Exception:
            logger.exception("SNMP dispatcher error")
            try:
                self._snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                logger.exception("Error closing dispatcher")
            raise
        finally:
            self._running.clear()
            logger.info("SNMP receiver stopped")

    def stop(self) -> None:
        """Stop the SNMP dispatcher and close RabbitMQ connection."""
        if self._snmp_engine is not None:
            try:
                self._snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                logger.exception("Error closing SNMP dispatcher in stop()")

        # close pika connection
        if self._pika_conn is not None:
            try:
                self._pika_conn.close()
            except Exception:
                logger.exception("Error closing pika connection")
            finally:
                self._pika_conn = None
                self._pika_ch = None

        self._running.clear()

    # Internal helpers
    def _setup_snmp_engine(self) -> None:
        if self._snmp_engine is not None:
            logger.debug("SNMP engine already configured")
            return

        logger.debug("Configuring SNMP engine")
        snmp_engine = engine.SnmpEngine()
        listen_addr = (self.listen_host, self.listen_port)

        config.addTransport(
            snmp_engine,
            udp.domainName,
            udp.UdpTransport().openServerMode(listen_addr),
        )

        ntfrcv.NotificationReceiver(snmp_engine, self._trap_callback)
        self._snmp_engine = snmp_engine
        logger.debug("SNMP engine configured")

    def _trap_callback(self, _snmpEngine: Any, _stateReference: Any,
                       _contextEngineId: Any, _contextName: Any,
                       varBinds: Iterable[Any], _cbCtx: Any) -> None:
        """Callback invoked by pysnmp for incoming traps.

        Converts varbinds into a normalized payload and publishes it.
        """
        try:
            var_binds_list = list(varBinds)
            logger.info("Received SNMP trap (varbinds=%d)",
                        len(var_binds_list))

            alert_name = None
            details: dict[str, str] = {}
            for oid, val in var_binds_list:
                oid_str = str(oid)
                details[oid_str] = str(val)
                if (oid_str.endswith('.1.3.6.1.6.3.1.1.4.1.0') or
                        oid_str.endswith('1.3.6.1.6.3.1.1.4.1.0')):
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

            logger.debug("Publishing payload id=%s", idempotency_id)
            self.publish_alert(payload)
        except Exception:
            logger.exception("Error handling SNMP trap")

    def _ensure_pika_connection(self) -> None:
        """Ensure a live pika connection and channel exist, create if needed.

        The method sets :pyattr:`_pika_conn` and :pyattr:`_pika_ch` on success.
        """
        if self._pika_conn is not None and self._pika_ch is not None:
            if self._pika_conn.is_open:
                return

        try:
            params = pika.URLParameters(self.rabbit_url)
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            ch.queue_declare(queue=self.queue_name, durable=True)
            self._pika_conn = conn
            self._pika_ch = ch
            logger.debug("Established pika connection and channel")
        except Exception:
            logger.exception("Failed to establish pika connection")
            self._pika_conn = None
            self._pika_ch = None

    def publish_alert(self, payload: dict) -> None:
        """Publish the alert payload to RabbitMQ using a persistent channel.

        If the publish fails due to connection issues we attempt to reconnect
        once before giving up.
        """
        if self._pika_ch is None:
            logger.debug("No pika channel, attempting to connect")
            self._ensure_pika_connection()

        if self._pika_ch is None:
            logger.error(
                "No RabbitMQ channel available, dropping payload id=%s",
                payload.get('idempotency_id'),
            )
            return

        try:
            self._pika_ch.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            logger.info('Published alert id=%s to queue=%s',
                        payload.get('idempotency_id'), self.queue_name)
        except Exception:
            logger.exception('Publish failed, retrying connection')
            # try to reconnect once
            try:
                self._ensure_pika_connection()
                if self._pika_ch is not None:
                    self._pika_ch.basic_publish(
                        exchange='',
                        routing_key=self.queue_name,
                        body=json.dumps(payload),
                        properties=pika.BasicProperties(delivery_mode=2),
                    )
                    logger.info('Published alert after reconnect id=%s',
                                payload.get('idempotency_id'))
            except Exception:
                logger.exception('Failed to publish alert after reconnect')

    @staticmethod
    def compute_idempotency_from_trap(var_binds: Iterable[Any]) -> str:
        """Create an idempotency SHA-256 hex digest for the trap.

        The result is a hex string (64 chars). The current implementation
        includes the current UTC timestamp so ids are unique per-receipt.
        """
        s = ''.join(f"{str(x[0])}={str(x[1])};" for x in var_binds)
        s += datetime.utcnow().isoformat()
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    # Utilities
    def _signal_handler(self, signum: int, frame: Any) -> None:
        logger.info("Received signal %s, shutting down", signum)
        try:
            self.stop()
        except Exception:
            logger.exception("Error while stopping receiver")

    @staticmethod
    def _redact_url(url: str) -> str:
        """Redact credentials in a URL for safe logging.

        This is deliberately simple and intended only for log messages.
        """
        try:
            if '://' in url and '@' in url:
                prefix, rest = url.split('://', 1)
                _, host = rest.split('@', 1)
                return f"{prefix}://<redacted>@{host}"
        except Exception:
            pass
        return url
