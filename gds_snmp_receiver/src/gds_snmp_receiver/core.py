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
    - Configurable via SNMPReceiverConfig dataclass

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
import re
import signal
import socket
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Optional
from urllib.parse import urlparse

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

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

# =============================================================================
# Module Constants
# =============================================================================

DEFAULT_LISTEN_HOST = "0.0.0.0"
DEFAULT_LISTEN_PORT = 162
DEFAULT_RABBIT_URL = "amqp://guest:guest@rabbitmq:5672/"
DEFAULT_QUEUE_NAME = "alerts"
DEFAULT_COMMUNITY_STRING = "public"
DEFAULT_READINESS_FILE = "/tmp/gds_snmp_ready"

# Timeout and retry configuration
DEFAULT_RABBITMQ_WAIT_TIMEOUT = 30  # seconds to wait for RabbitMQ at startup
DEFAULT_CONNECTION_TIMEOUT = 10  # seconds for individual connection attempts
DEFAULT_PUBLISH_RETRY_COUNT = 1  # number of retries on publish failure

# Payload limits
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1 MB max payload size

# Port ranges
PRIVILEGED_PORT_MAX = 1023
MIN_PORT = 1
MAX_PORT = 65535


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class SNMPReceiverConfig:
    """Configuration for SNMPReceiver with validation.

    This dataclass provides structured configuration with automatic
    validation on initialization. All parameters have sensible defaults.

    Attributes:
        listen_host: IP address or hostname to bind UDP socket.
        listen_port: UDP port number for SNMP traps.
        rabbit_url: RabbitMQ connection URL in AMQP format.
        queue_name: Name of the RabbitMQ queue to publish to.
        community_string: SNMPv2c community string for authentication.
        readiness_file: Path to write readiness marker file.
        connection_timeout: Timeout for RabbitMQ connection attempts.
        rabbitmq_wait_timeout: Max time to wait for RabbitMQ at startup.

    Example:
        >>> config = SNMPReceiverConfig(
        ...     listen_port=9162,
        ...     community_string="my_secret"
        ... )
        >>> receiver = SNMPReceiver.from_config(config)
    """

    listen_host: str = DEFAULT_LISTEN_HOST
    listen_port: int = DEFAULT_LISTEN_PORT
    rabbit_url: str = DEFAULT_RABBIT_URL
    queue_name: str = DEFAULT_QUEUE_NAME
    community_string: str = DEFAULT_COMMUNITY_STRING
    readiness_file: str = DEFAULT_READINESS_FILE
    connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT
    rabbitmq_wait_timeout: int = DEFAULT_RABBITMQ_WAIT_TIMEOUT
    _validated: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self._validated:
            self.validate()
            object.__setattr__(self, "_validated", True)

    def validate(self) -> None:
        """Validate all configuration parameters.

        Raises:
            ValueError: If any parameter is invalid.
        """
        self._validate_port()
        self._validate_host()
        self._validate_rabbit_url()
        self._validate_queue_name()
        self._validate_timeouts()

    def _validate_port(self) -> None:
        """Validate listen_port is in valid range."""
        if not isinstance(self.listen_port, int):
            raise ValueError(
                f"listen_port must be an integer, got {type(self.listen_port).__name__}"
            )
        if not MIN_PORT <= self.listen_port <= MAX_PORT:
            raise ValueError(
                f"listen_port must be between {MIN_PORT} and {MAX_PORT}, "
                f"got {self.listen_port}"
            )
        if self.listen_port <= PRIVILEGED_PORT_MAX:
            logger.warning(
                "Port %d requires root/admin privileges. Consider using port >= %d",
                self.listen_port,
                PRIVILEGED_PORT_MAX + 1,
            )

    def _validate_host(self) -> None:
        """Validate listen_host is a valid IP or hostname."""
        if not isinstance(self.listen_host, str):
            raise ValueError(
                f"listen_host must be a string, got {type(self.listen_host).__name__}"
            )
        if not self.listen_host:
            raise ValueError("listen_host cannot be empty")

        # Check if it's a valid IP address
        try:
            socket.inet_aton(self.listen_host)
            return
        except socket.error:
            pass

        # Check if it's a valid hostname pattern
        hostname_pattern = re.compile(
            r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        )
        if not hostname_pattern.match(self.listen_host):
            raise ValueError(
                f"listen_host '{self.listen_host}' is not a valid IP address or hostname"
            )

    def _validate_rabbit_url(self) -> None:
        """Validate rabbit_url is a valid AMQP URL."""
        if not isinstance(self.rabbit_url, str):
            raise ValueError(
                f"rabbit_url must be a string, got {type(self.rabbit_url).__name__}"
            )
        if not self.rabbit_url:
            raise ValueError("rabbit_url cannot be empty")

        try:
            parsed = urlparse(self.rabbit_url)
            if parsed.scheme not in ("amqp", "amqps"):
                raise ValueError(
                    f"rabbit_url must use 'amqp://' or 'amqps://' scheme, "
                    f"got '{parsed.scheme}://'"
                )
            if not parsed.hostname:
                raise ValueError("rabbit_url must include a hostname")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid rabbit_url format: {e}") from e

    def _validate_queue_name(self) -> None:
        """Validate queue_name is a valid RabbitMQ queue name."""
        if not isinstance(self.queue_name, str):
            raise ValueError(
                f"queue_name must be a string, got {type(self.queue_name).__name__}"
            )
        if not self.queue_name:
            raise ValueError("queue_name cannot be empty")
        # RabbitMQ queue names can be up to 255 bytes
        if len(self.queue_name.encode("utf-8")) > 255:
            raise ValueError("queue_name exceeds maximum length of 255 bytes")

    def _validate_timeouts(self) -> None:
        """Validate timeout values are positive."""
        if self.connection_timeout <= 0:
            raise ValueError(
                f"connection_timeout must be positive, got {self.connection_timeout}"
            )
        if self.rabbitmq_wait_timeout <= 0:
            raise ValueError(
                f"rabbitmq_wait_timeout must be positive, got {self.rabbitmq_wait_timeout}"
            )


# =============================================================================
# Custom Exceptions
# =============================================================================


class SNMPReceiverError(Exception):
    """Base exception for SNMP receiver errors."""

    pass


class PortBindingError(SNMPReceiverError):
    """Raised when the receiver cannot bind to the specified port."""

    pass


class RabbitMQConnectionError(SNMPReceiverError):
    """Raised when RabbitMQ connection fails."""

    pass


class ConfigurationError(SNMPReceiverError):
    """Raised when configuration is invalid."""

    pass


# =============================================================================
# Main Receiver Class
# =============================================================================


class SNMPReceiver:
    """SNMP trap receiver that publishes normalized alerts to RabbitMQ.

    The receiver maintains a short-lived SNMP dispatcher and a persistent
    pika connection/channel to reduce overhead when publishing multiple
    alerts.

    Attributes:
        listen_host: The host/IP to bind the UDP socket to.
        listen_port: The UDP port to listen on.
        rabbit_url: The AMQP connection URL for RabbitMQ.
        queue_name: The queue to publish messages to.
        community_string: The SNMPv2c community string for authentication.
        readiness_file: Path to the readiness marker file.

    Example:
        >>> receiver = SNMPReceiver(
        ...     listen_port=9162,
        ...     rabbit_url="amqp://user:pass@localhost:5672/"
        ... )
        >>> receiver.run()  # Blocks until stopped
    """

    def __init__(
        self,
        listen_host: str = DEFAULT_LISTEN_HOST,
        listen_port: int = DEFAULT_LISTEN_PORT,
        rabbit_url: str = DEFAULT_RABBIT_URL,
        queue_name: str = DEFAULT_QUEUE_NAME,
        community_string: str = DEFAULT_COMMUNITY_STRING,
        readiness_file: str = DEFAULT_READINESS_FILE,
        connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT,
        rabbitmq_wait_timeout: int = DEFAULT_RABBITMQ_WAIT_TIMEOUT,
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
            community_string: SNMPv2c community string for authentication.
                Default is 'public'. Change for production use.
            readiness_file: Path to write readiness marker file.
                Used by container health checks.
            connection_timeout: Timeout in seconds for RabbitMQ connections.
            rabbitmq_wait_timeout: Max seconds to wait for RabbitMQ at startup.

        Raises:
            ConfigurationError: If any configuration parameter is invalid.

        Note:
            Logging configuration is controlled by GDS_SNMP_LOG_LEVEL
            environment variable. Set to DEBUG for verbose output.
        """
        # Validate configuration
        try:
            config_obj = SNMPReceiverConfig(
                listen_host=listen_host,
                listen_port=int(listen_port),
                rabbit_url=rabbit_url,
                queue_name=queue_name,
                community_string=community_string,
                readiness_file=readiness_file,
                connection_timeout=connection_timeout,
                rabbitmq_wait_timeout=rabbitmq_wait_timeout,
            )
        except ValueError as e:
            raise ConfigurationError(str(e)) from e

        # Store validated configuration
        self.listen_host = config_obj.listen_host
        self.listen_port = config_obj.listen_port
        self.rabbit_url = config_obj.rabbit_url
        self.queue_name = config_obj.queue_name
        self.community_string = config_obj.community_string
        self.readiness_file = config_obj.readiness_file
        self.connection_timeout = config_obj.connection_timeout
        self.rabbitmq_wait_timeout = config_obj.rabbitmq_wait_timeout

        # SNMP engine state
        self._snmp_engine: Optional[engine.SnmpEngine] = None
        self._snmp_transport = None  # UDP transport, set during setup
        self._use_asyncio_backend = False  # pysnmp 7.x uses asyncio

        # Threading control
        self._running = threading.Event()  # Tracks receiver state

        # RabbitMQ connection state (reused across publishes)
        self._pika_conn: Optional[pika.BlockingConnection] = None
        self._pika_ch = None  # pika.BlockingChannel

        self._setup_logging()

        logger.debug(
            "SNMPReceiver(init) host=%s port=%d queue=%s community=%s",
            self.listen_host,
            self.listen_port,
            self.queue_name,
            "***"
            if self.community_string != DEFAULT_COMMUNITY_STRING
            else self.community_string,
        )

    @classmethod
    def from_config(cls, config: SNMPReceiverConfig) -> "SNMPReceiver":
        """Create an SNMPReceiver from a configuration object.

        Args:
            config: A validated SNMPReceiverConfig instance.

        Returns:
            A new SNMPReceiver instance.

        Example:
            >>> config = SNMPReceiverConfig(listen_port=9162)
            >>> receiver = SNMPReceiver.from_config(config)
        """
        return cls(
            listen_host=config.listen_host,
            listen_port=config.listen_port,
            rabbit_url=config.rabbit_url,
            queue_name=config.queue_name,
            community_string=config.community_string,
            readiness_file=config.readiness_file,
            connection_timeout=config.connection_timeout,
            rabbitmq_wait_timeout=config.rabbitmq_wait_timeout,
        )

    def _setup_logging(self) -> None:
        """Configure logging for the receiver."""
        if not logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
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

    # =========================================================================
    # Public API
    # =========================================================================

    def run(self) -> None:
        """Start the SNMP dispatcher and block until stopped.

        This method:
        1. Sets up the SNMP engine and binds to the UDP port
        2. Establishes RabbitMQ connection (with retry)
        3. Registers signal handlers for graceful shutdown
        4. Starts the dispatcher event loop

        Raises:
            PortBindingError: If unable to bind to the specified port.
            SNMPReceiverError: If the dispatcher fails unexpectedly.

        Note:
            Registers SIGINT/SIGTERM handlers for graceful shutdown.
        """
        self._setup_snmp_engine()

        # Ensure we have a pika connection before we start receiving traps.
        # RabbitMQ may take a short while to become ready; retry for a
        # configurable period so the receiver declares its queue and is
        # deterministic for E2E tests.
        waited = 0
        while self._pika_conn is None or self._pika_ch is None:
            self._ensure_pika_connection()
            if self._pika_conn is not None and self._pika_ch is not None:
                # Create a readiness marker file so external test helpers can
                # detect the receiver is ready (AMQP connected and queue declared).
                self._write_readiness_marker()
                break
            if waited >= self.rabbitmq_wait_timeout:
                logger.warning(
                    "Could not establish RabbitMQ connection after %ds, "
                    "continuing without AMQP",
                    self.rabbitmq_wait_timeout,
                )
                break
            waited += 1
            logger.info(
                "Waiting for RabbitMQ to become available (%ds/%ds)",
                waited,
                self.rabbitmq_wait_timeout,
            )
            time.sleep(1)

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(
            "Starting SNMP trap receiver on %s:%d",
            self.listen_host,
            self.listen_port,
        )

        assert self._snmp_engine is not None
        self._running.set()

        # Different pysnmp transport backends require different ways to
        # start the dispatcher.
        if self._use_asyncio_backend:
            self._run_asyncio_dispatcher()
        else:
            self._run_asynsock_dispatcher()

    def _run_asyncio_dispatcher(self) -> None:
        """Run the asyncio-based dispatcher (pysnmp 7.x)."""
        import asyncio

        logger.debug("Using asyncio backend for pysnmp, starting event loop")

        try:
            assert self._snmp_engine is not None
            # Mark dispatcher as having work
            self._snmp_engine.transportDispatcher.jobStarted(1)
            logger.debug("Starting asyncio run_dispatcher on loop")

            # Await the UDP socket binding future explicitly.
            loop = asyncio.get_event_loop()
            logger.debug("Loop running=%s", loop.is_running())

            if hasattr(self, "_snmp_transport") and hasattr(
                self._snmp_transport, "_lport"
            ):
                logger.debug("Awaiting UDP socket binding future")
                loop.run_until_complete(self._snmp_transport._lport)
                logger.debug("UDP socket bound. Loop running=%s", loop.is_running())
            else:
                # Fallback: run loop briefly for other pending tasks
                loop.run_until_complete(asyncio.sleep(0.05))
                logger.debug("Asyncio initialization complete")

            # Now run the dispatcher which blocks and processes traps
            logger.debug("Calling transportDispatcher.run_dispatcher()")
            self._snmp_engine.transportDispatcher.run_dispatcher()
            logger.debug("transportDispatcher.run_dispatcher() returned")

        except Exception as e:
            logger.exception("SNMP asyncio dispatcher error")
            try:
                if self._snmp_engine is not None:
                    self._snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                logger.exception("Error closing asyncio dispatcher")
            raise SNMPReceiverError(f"Dispatcher failed: {e}") from e
        finally:
            self._running.clear()
            logger.info("SNMP receiver stopped (asyncio)")

    def _run_asynsock_dispatcher(self) -> None:
        """Run the asynsock-based dispatcher (pysnmp 6.x)."""
        assert self._snmp_engine is not None
        self._snmp_engine.transportDispatcher.jobStarted(1)

        try:
            self._snmp_engine.transportDispatcher.runDispatcher()
        except Exception as e:
            logger.exception("SNMP dispatcher error")
            try:
                self._snmp_engine.transportDispatcher.closeDispatcher()
            except Exception:
                logger.exception("Error closing dispatcher")
            raise SNMPReceiverError(f"Dispatcher failed: {e}") from e
        finally:
            self._running.clear()
            logger.info("SNMP receiver stopped")

    def stop(self) -> None:
        """Stop the SNMP dispatcher and close RabbitMQ connection.

        This method performs graceful shutdown:
        1. Closes the SNMP transport dispatcher
        2. Closes the RabbitMQ connection
        3. Removes the readiness marker file
        4. Clears the running state

        Safe to call multiple times.
        """
        logger.debug("stop() called")

        if self._snmp_engine is not None:
            try:
                self._snmp_engine.transportDispatcher.closeDispatcher()
                logger.debug("SNMP dispatcher closed")
            except Exception:
                logger.exception("Error closing SNMP dispatcher in stop()")

        # Close pika connection
        if self._pika_conn is not None:
            try:
                self._pika_conn.close()
                logger.debug("Pika connection closed")
            except Exception:
                logger.exception("Error closing pika connection")
            finally:
                self._pika_conn = None
                self._pika_ch = None

        # Remove readiness marker if present
        self._remove_readiness_marker()

        self._running.clear()
        logger.debug("Receiver stopped")

    def is_running(self) -> bool:
        """Check if the receiver is currently running.

        Returns:
            True if the receiver is running, False otherwise.
        """
        return self._running.is_set()

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _write_readiness_marker(self) -> None:
        """Write readiness marker file for health checks."""
        try:
            with open(self.readiness_file, "w") as f:
                f.write("ready\n")
            logger.debug("Wrote readiness marker to %s", self.readiness_file)
        except Exception:
            logger.debug("Could not write readiness marker, continuing")

    def _remove_readiness_marker(self) -> None:
        """Remove readiness marker file if it exists."""
        try:
            if os.path.exists(self.readiness_file):
                os.remove(self.readiness_file)
                logger.debug("Removed readiness marker %s", self.readiness_file)
        except Exception:
            logger.debug("Could not remove readiness marker")

    def _setup_snmp_engine(self) -> None:
        """Configure and initialize the SNMP engine.

        Raises:
            PortBindingError: If unable to bind to the specified port.
        """
        if self._snmp_engine is not None:
            logger.debug("SNMP engine already configured")
            return

        logger.debug("Configuring SNMP engine")
        snmp_engine = engine.SnmpEngine()
        listen_addr = (self.listen_host, self.listen_port)

        # Create the UDP transport; when using asyncio backend, this
        # returns a transport with a pending future for socket binding.
        try:
            transport = udp.UdpTransport().openServerMode(listen_addr)
        except OSError as e:
            error_msg = f"Failed to bind to {self.listen_host}:{self.listen_port}: {e}"
            if e.errno == 13:  # Permission denied
                error_msg += (
                    f". Port {self.listen_port} requires elevated privileges. "
                    f"Use a port >= {PRIVILEGED_PORT_MAX + 1} or run as root."
                )
            elif e.errno == 98:  # Address already in use
                error_msg += ". Port is already in use by another process."
            logger.error(error_msg)
            raise PortBindingError(error_msg) from e

        config.addTransport(
            snmp_engine,
            udp.domainName,
            transport,
        )

        # Configure SNMPv2c community string authentication.
        config.addV1System(snmp_engine, "my-area", self.community_string)

        logger.debug("Registering trap callback: %s", self._trap_callback)
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

        # Inspect dispatcher for socket-related attributes for diagnostics
        try:
            disp = snmp_engine.transportDispatcher
            sock_attrs = [
                a for a in dir(disp) if "sock" in a.lower() or "socket" in a.lower()
            ]
            for a in sock_attrs:
                try:
                    logger.debug("dispatcher.%s=%r", a, getattr(disp, a))
                except Exception:
                    logger.debug("dispatcher.%s=<unreprable>", a)
        except Exception:
            logger.debug("Could not introspect transportDispatcher")

        # Remember which transport backend pysnmp provided
        try:
            self._use_asyncio_backend = _PYSNMP_BACKEND == "asyncio"
        except Exception:
            self._use_asyncio_backend = False

        logger.debug("SNMP engine configured")

    def _trap_callback(
        self,
        _snmpEngine: Any,
        _stateReference: Any,
        _contextEngineId: Any,
        _contextName: Any,
        varBinds: Iterable[Any],
        _cbCtx: Any,
    ) -> None:
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

            # Handle empty varbinds gracefully
            if not var_binds_list:
                logger.warning("Received trap with no varbinds, skipping")
                return

            # Parse trap details from varbinds
            alert_name: Optional[str] = None
            details: dict[str, str] = {}

            # Step 1: Extract all OID-value pairs
            for oid, val in var_binds_list:
                oid_str = str(oid)
                details[oid_str] = str(val)

                # Step 2: Identify the trap type from snmpTrapOID.0
                # Standard OID: 1.3.6.1.6.3.1.1.4.1.0
                if oid_str.endswith(".1.3.6.1.6.3.1.1.4.1.0") or oid_str.endswith(
                    "1.3.6.1.6.3.1.1.4.1.0"
                ):
                    alert_name = str(val)

            # Step 3: Fallback - use first varbind OID if no trap OID found
            if not alert_name and var_binds_list:
                first = var_binds_list[0]
                alert_name = f"snmp:{str(first[0])}"

            # Step 4: Generate unique idempotency key for duplicate detection
            idempotency_id = self.compute_idempotency_from_trap(var_binds_list)

            # Step 5: Build normalized JSON payload
            # Use timezone-aware datetime (no deprecation warning)
            received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            payload = {
                # Unique identifier for this trap instance
                "idempotency_id": idempotency_id,
                # Trap type OID (e.g., "1.3.6.1.6.3.1.1.5.3" for linkDown)
                "alert_name": alert_name,
                # Static source identifier for routing/filtering
                "source": "snmp",
                # ISO 8601 timestamp with UTC timezone
                "received_at": received_at,
                # Complete varbind dictionary (OID → value)
                "raw": details,
                # Human-readable subject line for notifications
                "subject": f"SNMP Trap: {alert_name}",
                # JSON-formatted details for email body/display
                "body_text": json.dumps(details, indent=2),
            }

            logger.debug("Publishing payload id=%s", idempotency_id)
            logger.debug("payload preview: %s", json.dumps(payload)[:1000])

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
            try:
                if self._pika_conn.is_open and self._pika_ch.is_open:
                    return
            except Exception:
                # Connection may be in bad state, proceed to reconnect
                pass

        logger.debug(
            "Establishing pika connection to %s",
            self._redact_url(self.rabbit_url),
        )

        try:
            # Parse AMQP URL into connection parameters with timeout
            params = pika.URLParameters(self.rabbit_url)
            params.socket_timeout = self.connection_timeout
            params.blocked_connection_timeout = self.connection_timeout

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

        except AMQPConnectionError as e:
            logger.warning(
                "RabbitMQ connection failed: %s. Will retry.",
                str(e),
            )
            self._pika_conn = None
            self._pika_ch = None

        except Exception:
            logger.exception("Failed to establish pika connection")
            # Clear connection state on any failure
            self._pika_conn = None
            self._pika_ch = None

    def publish_alert(self, payload: dict) -> bool:
        """Publish alert payload to RabbitMQ with automatic retry.

        This method implements a two-tier error handling strategy:
        1. Attempt publish with existing channel
        2. On failure, reconnect and retry once
        3. On second failure, log error and drop message

        Args:
            payload: Dictionary containing normalized trap data.
                Must include 'idempotency_id' for tracking.

        Returns:
            True if publish succeeded, False if message was dropped.

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
        idempotency_id = payload.get("idempotency_id", "unknown")

        # Check payload size
        payload_json = json.dumps(payload)
        if len(payload_json) > MAX_PAYLOAD_SIZE:
            logger.error(
                "Payload exceeds max size (%d > %d), dropping id=%s",
                len(payload_json),
                MAX_PAYLOAD_SIZE,
                idempotency_id,
            )
            return False

        # Ensure channel exists (lazy initialization)
        if self._pika_ch is None:
            logger.debug("No pika channel, attempting to connect")
            self._ensure_pika_connection()

        # Fail-fast if no channel available after connection attempt
        if self._pika_ch is None:
            logger.error(
                "No RabbitMQ channel available, dropping payload id=%s",
                idempotency_id,
            )
            return False

        # Check channel is still open
        try:
            if not self._pika_ch.is_open:
                logger.debug("Channel closed, reconnecting")
                self._ensure_pika_connection()
                if self._pika_ch is None:
                    logger.error(
                        "Could not reopen channel, dropping payload id=%s",
                        idempotency_id,
                    )
                    return False
        except Exception:
            pass

        try:
            # Log connection state for debugging
            logger.debug(
                "publishing to queue=%s conn=%r ch=%r",
                self.queue_name,
                self._pika_conn,
                self._pika_ch,
            )
            logger.debug("publishing payload (truncated): %s", payload_json[:1000])

            # Publish message to queue
            self._pika_ch.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=payload_json,
                properties=pika.BasicProperties(delivery_mode=2),
            )

            logger.info(
                "Published alert id=%s to queue=%s",
                idempotency_id,
                self.queue_name,
            )
            return True

        except (AMQPConnectionError, AMQPChannelError) as e:
            # First attempt failed - connection issue
            logger.warning("Publish failed (%s), retrying connection", str(e))
            return self._retry_publish(payload, idempotency_id)

        except Exception:
            # First attempt failed - unknown error
            logger.exception("Publish failed, retrying connection")
            return self._retry_publish(payload, idempotency_id)

    def _retry_publish(self, payload: dict, idempotency_id: str) -> bool:
        """Retry publishing after reconnection.

        Args:
            payload: The payload to publish.
            idempotency_id: The payload's idempotency ID for logging.

        Returns:
            True if retry succeeded, False otherwise.
        """
        try:
            self._ensure_pika_connection()

            if self._pika_ch is not None:
                # Retry publish with new connection
                self._pika_ch.basic_publish(
                    exchange="",
                    routing_key=self.queue_name,
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                logger.info(
                    "Published alert after reconnect id=%s",
                    idempotency_id,
                )
                return True
            else:
                logger.error(
                    "No channel after reconnect, dropping payload id=%s",
                    idempotency_id,
                )
                return False

        except Exception:
            # Second attempt failed - give up
            logger.exception("Failed to publish alert after reconnect")
            return False

    @staticmethod
    def compute_idempotency_from_trap(var_binds: Iterable[Any]) -> str:
        """Create an idempotency SHA-256 hex digest for the trap.

        The result is a hex string (64 chars). The current implementation
        includes the current UTC timestamp so ids are unique per-receipt.

        Args:
            var_binds: Iterable of (OID, value) tuples from the trap.

        Returns:
            A 64-character hexadecimal SHA-256 hash string.
        """
        s = "".join(f"{str(x[0])}={str(x[1])};" for x in var_binds)
        # Use timezone-aware datetime (no deprecation warning)
        s += datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    # =========================================================================
    # Utilities
    # =========================================================================

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals (SIGTERM, SIGINT).

        Args:
            signum: The signal number received.
            frame: The current stack frame (unused).
        """
        logger.info("Received signal %s, shutting down", signum)
        try:
            self.stop()
        except Exception:
            logger.exception("Error while stopping receiver")

    @staticmethod
    def _redact_url(url: str) -> str:
        """Redact credentials in a URL for safe logging.

        Args:
            url: The URL potentially containing credentials.

        Returns:
            The URL with credentials replaced by '<redacted>'.

        Example:
            >>> SNMPReceiver._redact_url("amqp://user:pass@host:5672/")
            'amqp://<redacted>@host:5672/'
        """
        try:
            if "://" in url and "@" in url:
                prefix, rest = url.split("://", 1)
                _, host = rest.split("@", 1)
                return f"{prefix}://<redacted>@{host}"
        except Exception:
            pass
        return url
