"""
Vault secret rotation utilities.

This module provides utilities for handling Vault secret rotation schedules,
including cron expression parsing and TTL calculation based on rotation times.
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional, Union

logger = logging.getLogger(__name__)


class CronParser:
    """
    Simple cron expression parser for Vault rotation schedules.
    
    Supports standard 5-field cron format: minute hour day month weekday
    Examples:
        "0 2 * * *" - Daily at 2:00 AM
        "0 2 * * 0" - Weekly on Sunday at 2:00 AM
        "0 2 1 * *" - Monthly on 1st at 2:00 AM
        "0 2 1 1 *" - Yearly on Jan 1st at 2:00 AM
    """
    
    def __init__(self, cron_expression: str):
        """Initialize cron parser with expression."""
        self.expression = cron_expression.strip()
        self.fields = self._parse_expression(self.expression)
        
    def _parse_expression(self, expr: str) -> dict:
        """Parse cron expression into fields."""
        parts = expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expr}. Must have 5 fields.")
            
        return {
            'minute': parts[0],
            'hour': parts[1], 
            'day': parts[2],
            'month': parts[3],
            'weekday': parts[4]
        }
    
    def _parse_field(self, field: str, min_val: int, max_val: int) -> list[int]:
        """Parse a single cron field into list of valid values."""
        if field == '*':
            return list(range(min_val, max_val + 1))
        
        # Handle ranges like "1-5"
        if '-' in field:
            start, end = map(int, field.split('-'))
            return list(range(start, end + 1))
        
        # Handle lists like "1,3,5"
        if ',' in field:
            return [int(x) for x in field.split(',')]
        
        # Handle step values like "*/5" or "2-10/2"
        if '/' in field:
            base, step = field.split('/')
            step = int(step)
            if base == '*':
                values = list(range(min_val, max_val + 1))
            else:
                values = self._parse_field(base, min_val, max_val)
            return [v for v in values if (v - min_val) % step == 0]
        
        # Single value
        return [int(field)]
    
    def next_run_time(self, from_time: Optional[datetime] = None) -> datetime:
        """
        Calculate the next time this cron expression should run.
        
        Args:
            from_time: Calculate next run from this time (defaults to now)
            
        Returns:
            datetime: Next scheduled run time
        """
        if from_time is None:
            from_time = datetime.now()
        
        # Start from the next minute to avoid immediate matches
        next_time = from_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Parse cron fields
        minutes = self._parse_field(self.fields['minute'], 0, 59)
        hours = self._parse_field(self.fields['hour'], 0, 23)
        days = self._parse_field(self.fields['day'], 1, 31)
        months = self._parse_field(self.fields['month'], 1, 12)
        weekdays = self._parse_field(self.fields['weekday'], 0, 6)  # 0=Sunday
        
        # Find next valid time (simple implementation for common cases)
        for _ in range(366 * 24 * 60):  # Max search: 1 year
            if (next_time.minute in minutes and
                next_time.hour in hours and
                next_time.day in days and
                next_time.month in months and
                next_time.weekday() + 1 % 7 in weekdays):  # Convert to Sunday=0
                return next_time
            
            next_time += timedelta(minutes=1)
        
        raise ValueError(f"Could not find next run time for cron: {self.expression}")


def calculate_rotation_ttl(
    last_rotation: Union[str, int, float, datetime],
    rotation_schedule: str,
    buffer_minutes: int = 10,
    current_time: Optional[datetime] = None
) -> int:
    """
    Calculate TTL for a secret based on its rotation schedule.
    
    Args:
        last_rotation: Last rotation time (ISO string, timestamp, or datetime)
        rotation_schedule: Cron expression for rotation schedule
        buffer_minutes: Safety buffer in minutes before rotation (default: 10)
        current_time: Current time for calculation (defaults to now)
        
    Returns:
        int: TTL in seconds until secret should be refreshed
        
    Raises:
        ValueError: If rotation schedule is invalid or times are malformed
    """
    if current_time is None:
        current_time = datetime.now()
    
    # Parse last rotation time
    if isinstance(last_rotation, str):
        try:
            # Try ISO format first
            if last_rotation.endswith('Z'):
                # Handle UTC timezone
                last_rotation_dt = datetime.fromisoformat(last_rotation.replace('Z', '+00:00'))
                # Convert to local time for comparison
                last_rotation_dt = last_rotation_dt.replace(tzinfo=None)
            else:
                last_rotation_dt = datetime.fromisoformat(last_rotation)
                # Remove timezone info if present to work with naive datetime
                if last_rotation_dt.tzinfo is not None:
                    last_rotation_dt = last_rotation_dt.replace(tzinfo=None)
        except ValueError:
            # Try timestamp as string
            last_rotation_dt = datetime.fromtimestamp(float(last_rotation))
    elif isinstance(last_rotation, (int, float)):
        last_rotation_dt = datetime.fromtimestamp(last_rotation)
    elif isinstance(last_rotation, datetime):
        last_rotation_dt = last_rotation
        # Remove timezone info if present to work with naive datetime
        if last_rotation_dt.tzinfo is not None:
            last_rotation_dt = last_rotation_dt.replace(tzinfo=None)
    else:
        raise ValueError(f"Invalid last_rotation format: {type(last_rotation)}")
    
    # Ensure current_time is also naive
    if current_time.tzinfo is not None:
        current_time = current_time.replace(tzinfo=None)
    
    # Parse cron schedule and get next rotation
    try:
        cron = CronParser(rotation_schedule)
        next_rotation = cron.next_run_time(last_rotation_dt)
    except Exception as e:
        logger.error("Failed to parse rotation schedule %s: %s", rotation_schedule, e)
        raise ValueError(f"Invalid rotation schedule: {rotation_schedule}") from e
    
    # Calculate time until rotation with buffer
    time_until_rotation = next_rotation - current_time
    buffer_time = timedelta(minutes=buffer_minutes)
    
    # If we're within buffer time or past rotation, return 0 (needs immediate refresh)
    if time_until_rotation <= buffer_time:
        logger.info(
            "Secret needs immediate refresh: next rotation at %s, current time %s, buffer %d min",
            next_rotation, current_time, buffer_minutes
        )
        return 0
    
    # Return TTL in seconds (minus buffer)
    ttl_seconds = int((time_until_rotation - buffer_time).total_seconds())
    logger.debug(
        "Calculated TTL: %d seconds until rotation at %s (with %d min buffer)",
        ttl_seconds, next_rotation, buffer_minutes
    )
    
    return ttl_seconds


def should_refresh_secret(
    last_rotation: Union[str, int, float, datetime],
    rotation_schedule: str,
    buffer_minutes: int = 10,
    current_time: Optional[datetime] = None
) -> bool:
    """
    Check if a secret should be refreshed based on rotation schedule.
    
    Args:
        last_rotation: Last rotation time
        rotation_schedule: Cron expression for rotation schedule
        buffer_minutes: Safety buffer in minutes before rotation
        current_time: Current time for calculation (defaults to now)
        
    Returns:
        bool: True if secret should be refreshed immediately
    """
    try:
        ttl = calculate_rotation_ttl(
            last_rotation, rotation_schedule, buffer_minutes, current_time
        )
        return ttl <= 0
    except Exception as e:
        logger.warning("Error checking rotation schedule, assuming refresh needed: %s", e)
        return True


def parse_vault_rotation_metadata(vault_response: dict) -> Optional[dict]:
    """
    Parse rotation metadata from Vault response.
    
    Args:
        vault_response: Full response from Vault API
        
    Returns:
        dict: Rotation metadata with keys 'last_rotation', 'schedule', etc.
        None: If no rotation metadata found
    """
    # Check for rotation metadata in various response locations
    metadata = None
    
    # KV v2 metadata location
    if 'data' in vault_response and 'metadata' in vault_response['data']:
        metadata = vault_response['data']['metadata']
    
    # Auth metadata location (for dynamic secrets)
    elif 'auth' in vault_response and 'metadata' in vault_response['auth']:
        metadata = vault_response['auth']['metadata']
    
    # Direct metadata field
    elif 'metadata' in vault_response:
        metadata = vault_response['metadata']
    
    if not metadata:
        return None
    
    # Extract rotation-specific fields
    rotation_info = {}
    
    # Look for common rotation metadata field names
    for field in ['last_rotation', 'last_rotation_time', 'rotation_time']:
        if field in metadata:
            rotation_info['last_rotation'] = metadata[field]
            break
    
    for field in ['rotation_schedule', 'schedule', 'cron_schedule']:
        if field in metadata:
            rotation_info['schedule'] = metadata[field]
            break
    
    # Return None if no rotation fields found
    if not rotation_info:
        return None
    
    logger.debug("Found rotation metadata: %s", rotation_info)
    return rotation_info