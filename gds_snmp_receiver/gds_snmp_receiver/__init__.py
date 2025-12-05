"""gds_snmp_receiver package.

This package provides an object-oriented SNMP trap receiver used by the
notifications stack. The implementation focuses on testability, clear
responsibility separation and extensive logging to make troubleshooting
easier in production or development environments.

Public API
----------
- :class:`SNMPReceiver` - main class for running the receiver.
- :class:`SNMPReceiverConfig` - configuration dataclass.
- :class:`SNMPReceiverError` - base exception class.
- :class:`PortBindingError` - raised when port binding fails.
- :class:`ConfigurationError` - raised when configuration is invalid.

Example
-------
>>> from gds_snmp_receiver import SNMPReceiver
>>> r = SNMPReceiver()
>>> r.run()

Or with configuration:
>>> from gds_snmp_receiver import SNMPReceiver, SNMPReceiverConfig
>>> config = SNMPReceiverConfig(listen_port=9162)
>>> r = SNMPReceiver.from_config(config)
>>> r.run()
"""

from .core import (
    SNMPReceiver,
    SNMPReceiverConfig,
    SNMPReceiverError,
    PortBindingError,
    ConfigurationError,
    RabbitMQConnectionError,
)

__all__ = [
    "SNMPReceiver",
    "SNMPReceiverConfig",
    "SNMPReceiverError",
    "PortBindingError",
    "ConfigurationError",
    "RabbitMQConnectionError",
]
