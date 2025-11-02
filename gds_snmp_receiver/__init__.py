"""gds_snmp_receiver package.

This package provides an object-oriented SNMP trap receiver used by the
notifications stack. The implementation focuses on testability, clear
responsibility separation and extensive logging to make troubleshooting
easier in production or development environments.

Public API
----------
- :class:`SNMPReceiver` - main class for running the receiver.

Example
-------
>>> from gds_snmp_receiver import SNMPReceiver
>>> r = SNMPReceiver()
>>> r.run()
"""

from .core import SNMPReceiver

__all__ = ["SNMPReceiver"]
