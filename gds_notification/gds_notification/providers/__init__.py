"""
Notification provider adapters.

This module provides a pluggable provider architecture for sending notifications
through various channels including email (SMTP), MIR3 emergency notifications,
PagerDuty incident management, and future providers.
"""

from gds_notification.providers.base import (
    NotificationProvider,
    NotificationResult,
    NotificationStatus,
)
from gds_notification.providers.mir3 import MIR3Provider
from gds_notification.providers.pagerduty import PagerDutyProvider
from gds_notification.providers.smtp import SMTPProvider

__all__ = [
    "NotificationProvider",
    "NotificationResult",
    "NotificationStatus",
    "SMTPProvider",
    "MIR3Provider",
    "PagerDutyProvider",
]
