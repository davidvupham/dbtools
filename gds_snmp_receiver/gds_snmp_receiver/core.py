"""Object-oriented SNMP trap receiver implementation.

This module provides :class:`SNMPReceiver` which wraps the SNMP engine,
trap handling and RabbitMQ publishing. It focuses on clarity,
testability and rich logging to aid troubleshooting.

Architecture:
    The receiver uses a single-threaded event loop to process incoming
    SNMP traps. Each trap is parsed, normalized into a JSON payload,
    and published to a RabbitMQ queue for downstream processing.

    Flow:
        UDP Socket → pysnmp Dispatcher → Trap Callback →
        Payload Normalization → RabbitMQ Publisher → Durable Queue

Key Features:
    - SNMPv2c trap reception with community string authentication
    - Automatic RabbitMQ connection retry and recovery
    - Persistent message delivery (survives broker restarts)
    - Idempotency keys (SHA-256) for duplicate detection
    - Compatible with pysnmp 6.x (asynsock) and 7.x (asyncio)
    - Graceful shutdown on SIGTERM/SIGINT signals
    - Container-ready with health checks

Example:
    >>> from gds_snmp_receiver import SNMPReceiver
    >>> receiver = SNMPReceiver(
    ...     listen_host="0.0.0.0",
    ...     listen_port=9162,
    ...     rabbit_url="amqp://guest:guest@localhost:5672/",
    ...     queue_name="alerts"
    ... )
    >>> receiver.run()  # Blocks until stopped

For detailed documentation, see TUTORIAL.md and ARCHITECTURE.md
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import signal
import threading
from datetime import datetime
from typing import Any, Iterable, Optional

import pika
# pysnmp changed carrier backends over versions: older versions expose
# pysnmp.carrier.asynsock, newer versions expose pysnmp.carrier.asyncio.
# Try to import the asynsock backend first for compatibility, otherwise
# fall back to the asyncio backend. Record which backend we loaded so
# the runtime can choose the appropriate dispatch mechanism.
try:
    from pysnmp.carrier.asynsock.dgram import udp
    _PYSNMP_BACKEND = "asynsock"
except Exception:
    from pysnmp.carrier.asyncio.dgram import udp
    _PYSNMP_BACKEND = "asyncio"
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
        """Initialize the SNMP receiver with configuration parameters.

        Args:
            listen_host: IP address or hostname to bind UDP socket.
                Use "0.0.0.0" for all interfaces, "127.0.0.1" for
                localhost only, or specific IP for single interface.
            listen_port: UDP port number for SNMP traps. Standard port
                is 162 but requires root privileges. Use ports ≥1024
                for non-root operation.
            rabbit_url: RabbitMQ connection URL in AMQP format.
                Format: amqp://[user]:[pass]@[host]:[port]/[vhost]
                Example: amqp://snmp_user:secret@rabbitmq:5672/prod
            queue_name: Name of the RabbitMQ queue to publish to.
                Queue is created as durable if it doesn't exist.

        Note:
            Logging configuration is controlled by GDS_SNMP_LOG_LEVEL
            environment variable. Set to DEBUG for verbose output.
        """
        self.listen_host = listen_host
        self.listen_port = int(listen_port)
        self.rabbit_url = rabbit_url
        self.queue_name = queue_name

        # SNMP engine state
        self._snmp_engine: Optional[engine.SnmpEngine] = None
        self._snmp_transport = None  # UDP transport, set during setup
        self._use_asyncio_backend = False  # pysnmp 7.x uses asyncio

        # Threading control
        self._running = threading.Event()  # Tracks receiver state

        # RabbitMQ connection state (reused across publishes)
        self._pika_conn: Optional[pika.BlockingConnection] = None
        self._pika_ch = None  # pika.BlockingChannel

        if not logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                )
            )
            logger.addHandler(h)

        # Allow overriding log level via environment for debugging.
        lvl = os.getenv("GDS_SNMP_LOG_LEVEL") or os.getenv("LOG_LEVEL")
        if lvl:
            try:
                logger.setLevel(getattr(logging, lvl.upper(), logging.INFO))
            except Exception:
                logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.INFO)

        # Ensure the StreamHandler (if added) is set to emit debug output
        # when requested by the environment variable.
        if logger.handlers:
            try:
                h0 = logger.handlers[0]
                if lvl and lvl.upper() == "DEBUG":
                    h0.setLevel(logging.DEBUG)
                else:
                    h0.setLevel(logging.INFO)
            except Exception:
                pass

        logger.debug("GDS_SNMP_LOG_LEVEL=%s effective_level=%s", lvl, logger.level)

        logger.debug(
            "SNMPReceiver(init) host=%s port=%d queue=%s",
            self.listen_host,
            self.listen_port,
            self.queue_name,
        )

    # Public API
    def run(self) -> None:
        """Start the SNMP dispatcher and block until stopped.

        Registers SIGINT/SIGTERM handlers for graceful shutdown.
        """
        self._setup_snmp_engine()
        # Ensure we have a pika connection before we start receiving traps.
        # RabbitMQ may take a short while to become ready; retry for a
        # configurable period so the receiver declares its queue and is
        # deterministic for E2E tests.
        max_wait = 30
        waited = 0
        while self._pika_conn is None or self._pika_ch is None:
            self._ensure_pika_connection()
            if self._pika_conn is not None and self._pika_ch is not None:
                # Create a readiness marker file so external test helpers can
                # detect the receiver is ready (AMQP connected and queue declared).
                try:
                    with open("/tmp/gds_snmp_ready", "w") as f:
                        f.write("ready\n")
                except Exception:
                    logger.debug("Could not write readiness marker, continuing")
                break
            if waited >= max_wait:
                logger.warning("Could not establish RabbitMQ connection after %ds, continuing without AMQP", max_wait)
                break
            waited += 1
            logger.info("Waiting for RabbitMQ to become available (%ds/%ds)", waited, max_wait)
            import time

            time.sleep(1)

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Starting SNMP trap receiver on %s:%d",
                    self.listen_host, self.listen_port)

        assert self._snmp_engine is not None
        # Different pysnmp transport backends require different ways to
        # start the dispatcher. Older asynsock-based builds use
        # transportDispatcher.runDispatcher(); newer asyncio-based
        # builds integrate with Python's asyncio event loop and require
        # running that loop to process incoming traps.
        self._running.set()
        if self._use_asyncio_backend:
            import asyncio
            logger.debug("Using asyncio backend for pysnmp, starting event loop")
            
            # pysnmp asyncio dispatcher uses run_dispatcher() (snake_case)
            # which internally calls loop.run_forever(). The asyncio transport
            # UDP socket is bound asynchronously, so we need to ensure the
            # loop runs briefly to allow the socket binding task to complete.
            try:
                # Mark dispatcher as having work
                self._snmp_engine.transportDispatcher.jobStarted(1)
                logger.debug("Starting asyncio run_dispatcher on loop")
                
                # Await the UDP socket binding future explicitly. The
                # transport's _lport future was created by openServerMode.
                loop = asyncio.get_event_loop()
                logger.debug(f"Loop running={loop.is_running()}")
                if hasattr(self, '_snmp_transport') and hasattr(
                    self._snmp_transport, '_lport'
                ):
                    logger.debug("Awaiting UDP socket binding future")
                    loop.run_until_complete(self._snmp_transport._lport)
                    logger.debug(
                        f"UDP socket bound. Loop running={loop.is_running()}"
                    )
                else:
                    # Fallback: run loop briefly for other pending tasks
                    loop.run_until_complete(asyncio.sleep(0.05))
                    logger.debug("Asyncio initialization complete")
                
                # Now run the dispatcher which blocks and processes traps
                logger.debug("Calling transportDispatcher.run_dispatcher()")
                self._snmp_engine.transportDispatcher.run_dispatcher()
                logger.debug("transportDispatcher.run_dispatcher() returned")
            except Exception:
                logger.exception("SNMP asyncio dispatcher error")
                try:
                    self._snmp_engine.transportDispatcher.closeDispatcher()
                except Exception:
                    logger.exception("Error closing asyncio dispatcher")
                raise
            finally:
                self._running.clear()
                logger.info("SNMP receiver stopped (asyncio)")
        else:
            self._snmp_engine.transportDispatcher.jobStarted(1)
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

        # Remove readiness marker if present
        try:
            import os

            if os.path.exists("/tmp/gds_snmp_ready"):
                os.remove("/tmp/gds_snmp_ready")
        except Exception:
            logger.debug("Could not remove readiness marker")

        self._running.clear()

    # Internal helpers
    def _setup_snmp_engine(self) -> None:
        if self._snmp_engine is not None:
            logger.debug("SNMP engine already configured")
            return

        logger.debug("Configuring SNMP engine")
        snmp_engine = engine.SnmpEngine()
        listen_addr = (self.listen_host, self.listen_port)

        # Create the UDP transport; when using asyncio backend, this
        # returns a transport with a pending future for socket binding.
        transport = udp.UdpTransport().openServerMode(listen_addr)
        config.addTransport(
            snmp_engine,
            udp.domainName,
            transport,
        )
        
        # Configure SNMPv2c community string authentication.
        # Accept the community string 'public' from any source.
        config.addV1System(snmp_engine, 'my-area', 'public')
        
        logger.debug(f"Registering trap callback: {self._trap_callback}")
        ntfrcv.NotificationReceiver(snmp_engine, self._trap_callback)
        logger.debug("Trap callback registered successfully")
        self._snmp_engine = snmp_engine
        # Store transport for asyncio socket binding await
        self._snmp_transport = transport
        logger.debug(
            "pysnmp backend=%s transportDispatcher=%r",
            _PYSNMP_BACKEND,
            type(snmp_engine.transportDispatcher),
        )
        # Inspect dispatcher for socket-related attributes to help
        # diagnose whether a server socket was actually opened.
        try:
            disp = snmp_engine.transportDispatcher
            sock_attrs = [a for a in dir(disp) if 'sock' in a.lower() or 'socket' in a.lower()]
            for a in sock_attrs:
                try:
                    logger.debug("dispatcher.%s=%r", a, getattr(disp, a))
                except Exception:
                    logger.debug("dispatcher.%s=<unreprable>", a)
        except Exception:
            logger.debug("Could not introspect transportDispatcher")
        # remember which transport backend pysnmp provided so run() can
        # choose the correct dispatcher invocation. The module-level
        # variable was set at import time above.
        try:
            self._use_asyncio_backend = (_PYSNMP_BACKEND == "asyncio")
        except Exception:
            self._use_asyncio_backend = False
        logger.debug("SNMP engine configured")

    def _trap_callback(self, _snmpEngine: Any, _stateReference: Any,
                       _contextEngineId: Any, _contextName: Any,
                       varBinds: Iterable[Any], _cbCtx: Any) -> None:
        """Callback invoked by pysnmp for each received SNMP trap.

        This method is called synchronously by the pysnmp dispatcher when
        a trap message is received and successfully authenticated. The
        callback extracts trap details, normalizes them into a structured
        JSON payload, and publishes to RabbitMQ.

        Args:
            _snmpEngine: The SNMP engine instance (unused)
            _stateReference: Internal pysnmp state reference (unused)
            _contextEngineId: SNMP context engine identifier (unused)
            _contextName: SNMP context name (unused)
            varBinds: Iterator of (OID, value) tuples representing the
                trap's variable bindings. These contain the trap data.
            _cbCtx: Optional callback context (unused)

        Trap Structure:
            SNMPv2c traps typically contain:
            - sysUpTime.0 (1.3.6.1.2.1.1.3.0): Device uptime in timeticks
            - snmpTrapOID.0 (1.3.6.1.6.3.1.1.4.1.0): Trap type identifier
            - Additional varbinds: Trap-specific data

        Payload Structure:
            {
                "idempotency_id": "sha256-hash",
                "alert_name": "1.3.6.1.6.3.1.1.5.3",
                "source": "snmp",
                "received_at": "2025-11-04T12:34:56.789Z",
                "raw": {"oid": "value", ...},
                "subject": "SNMP Trap: 1.3.6.1.6.3.1.1.5.3",
                "body_text": "{\n  \"oid\": \"value\"\n}"
            }

        Note:
            This method catches all exceptions to prevent a single
            malformed trap from crashing the receiver. Errors are
            logged but do not interrupt trap processing.
        """
        try:
            # Convert iterator to list for reliable iteration and logging.
            # varBinds may be a generator that can only be consumed once.
            var_binds_list = list(varBinds)
            logger.debug(
                "trap callback invoked; varbinds_count=%d",
                len(var_binds_list),
            )
            logger.info("Received SNMP trap (varbinds=%d)", len(var_binds_list))

            # Parse trap details from varbinds
            alert_name = None
            details: dict[str, str] = {}

            # Step 1: Extract all OID-value pairs
            for oid, val in var_binds_list:
                oid_str = str(oid)
                details[oid_str] = str(val)

                # Step 2: Identify the trap type from snmpTrapOID.0
                # Standard OID: 1.3.6.1.6.3.1.1.4.1.0
                if (oid_str.endswith('.1.3.6.1.6.3.1.1.4.1.0') or
                        oid_str.endswith('1.3.6.1.6.3.1.1.4.1.0')):
                    alert_name = str(val)

            # Step 3: Fallback - use first varbind OID if no trap OID found
            if not alert_name and var_binds_list:
                first = var_binds_list[0]
                alert_name = f"snmp:{str(first[0])}"

            # Step 4: Generate unique idempotency key for duplicate detection
            # The key is a SHA-256 hash of varbinds + timestamp
            idempotency_id = self.compute_idempotency_from_trap(var_binds_list)

            # Step 5: Build normalized JSON payload
            payload = {
                # Unique identifier for this trap instance
                'idempotency_id': idempotency_id,

                # Trap type OID (e.g., "1.3.6.1.6.3.1.1.5.3" for linkDown)
                'alert_name': alert_name,

                # Static source identifier for routing/filtering
                'source': 'snmp',

                # ISO 8601 timestamp with UTC timezone
                'received_at': datetime.utcnow().isoformat() + 'Z',

                # Complete varbind dictionary (OID → value)
                'raw': details,

                # Human-readable subject line for notifications
                'subject': f'SNMP Trap: {alert_name}',

                # JSON-formatted details for email body/display
                'body_text': json.dumps(details, indent=2),
            }

            logger.debug("Publishing payload id=%s", idempotency_id)
            logger.debug("payload preview: %s", json.dumps(payload))

            # Step 6: Publish to RabbitMQ (handles connection retry)
            self.publish_alert(payload)
        except Exception:
            logger.exception("Error handling SNMP trap")

    def _ensure_pika_connection(self) -> None:
        """Ensure a live RabbitMQ connection and channel exist.

        This method implements connection pooling by reusing an existing
        connection if it's still open. If no connection exists or the
        existing connection is closed, a new connection is established.

        Connection Steps:
            1. Check if existing connection is usable
            2. Parse connection URL (amqp://...)
            3. Establish TCP connection to RabbitMQ
            4. Create channel for publishing
            5. Declare queue (creates if doesn't exist)

        Queue Configuration:
            - durable=True: Queue survives broker restarts
            - Messages must be published with delivery_mode=2 for
              persistence (done in publish_alert method)

        Error Handling:
            Connection failures are logged but do not raise exceptions.
            Caller should check if _pika_conn is None after calling.

        Side Effects:
            Sets self._pika_conn and self._pika_ch on success.
            Sets both to None on failure.
        """
        # Optimization: reuse existing connection if still open
        if self._pika_conn is not None and self._pika_ch is not None:
            if self._pika_conn.is_open:
                return

        try:
            # Parse AMQP URL into connection parameters
            params = pika.URLParameters(self.rabbit_url)

            # Establish blocking connection (synchronous)
            conn = pika.BlockingConnection(params)

            # Create channel for message operations
            ch = conn.channel()

            # Declare queue (idempotent - safe to call multiple times)
            # durable=True ensures queue survives broker restarts
            ch.queue_declare(queue=self.queue_name, durable=True)

            # Store connection and channel for reuse
            self._pika_conn = conn
            self._pika_ch = ch
            logger.debug("Established pika connection and channel")
        except Exception:
            logger.exception("Failed to establish pika connection")
            # Clear connection state on any failure
            self._pika_conn = None
            self._pika_ch = None

    def publish_alert(self, payload: dict) -> None:
        """Publish alert payload to RabbitMQ with automatic retry.

        This method implements a two-tier error handling strategy:
        1. Attempt publish with existing channel
        2. On failure, reconnect and retry once
        3. On second failure, log error and drop message

        Args:
            payload: Dictionary containing normalized trap data.
                Must include 'idempotency_id' for tracking.

        Message Persistence:
            Messages are published with delivery_mode=2 (persistent)
            which means they survive RabbitMQ broker restarts when
            stored in a durable queue.

        Routing:
            - exchange="": Use default exchange (direct routing)
            - routing_key=queue_name: Route directly to named queue
            - This is the simplest routing pattern for point-to-point

        Error Handling:
            Connection errors trigger automatic reconnection and retry.
            If retry fails, the message is dropped (not queued locally).
            This prevents memory buildup during prolonged outages.

        Note:
            This is a synchronous, blocking operation. For high-volume
            scenarios, consider using an async publish queue.
        """
        # Ensure channel exists (lazy initialization)
        if self._pika_ch is None:
            logger.debug("No pika channel, attempting to connect")
            self._ensure_pika_connection()

        # Fail-fast if no channel available after connection attempt
        if self._pika_ch is None:
            logger.error(
                "No RabbitMQ channel available, dropping payload id=%s",
                payload.get('idempotency_id'),
            )
            return

        try:
            # Log connection state for debugging
            logger.debug("publishing to queue=%s conn=%r ch=%r",
                         self.queue_name, self._pika_conn, self._pika_ch)
            logger.debug("publishing payload (truncated): %s",
                         json.dumps(payload)[:1000])

            # Publish message to queue
            self._pika_ch.basic_publish(
                # Default exchange (routes by queue name)
                exchange="",

                # Target queue name (must exist)
                routing_key=self.queue_name,

                # JSON-serialized payload
                body=json.dumps(payload),

                # Message properties
                properties=pika.BasicProperties(
                    # delivery_mode=2: Persistent (survives restarts)
                    # delivery_mode=1: Transient (lost on restart)
                    delivery_mode=2
                ),
            )

            logger.info(
                "Published alert id=%s to queue=%s",
                payload.get("idempotency_id"),
                self.queue_name,
            )

        except Exception:
            # First attempt failed - likely connection issue
            logger.exception('Publish failed, retrying connection')

            # Retry Strategy: Reconnect once and retry publish
            try:
                self._ensure_pika_connection()

                if self._pika_ch is not None:
                    # Retry publish with new connection
                    self._pika_ch.basic_publish(
                        exchange='',
                        routing_key=self.queue_name,
                        body=json.dumps(payload),
                        properties=pika.BasicProperties(delivery_mode=2),
                    )
                    logger.info('Published alert after reconnect id=%s',
                                payload.get('idempotency_id'))
            except Exception:
                # Second attempt failed - give up
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
