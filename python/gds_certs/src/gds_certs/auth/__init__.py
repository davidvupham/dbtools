"""
Authentication strategies for CA API clients.

This module provides pluggable authentication mechanisms for the CA client.
"""

from gds_certs.auth.api_key import APIKeyAuth
from gds_certs.auth.base import BaseAuth
from gds_certs.auth.bearer import BearerAuth

__all__ = [
    "APIKeyAuth",
    "BaseAuth",
    "BearerAuth",
]
