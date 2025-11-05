"""
MongoDB Server Configuration Management Module

This module provides the MongoDBConfiguration class for managing MongoDB server
configuration, including retrieving and modifying server configuration settings
at runtime.

Provides programmatic access to MongoDB server configuration settings such as
logging levels, timeout settings, memory limits, and other runtime-configurable
options.

Reference: https://www.mongodb.com/docs/manual/reference/command/getParameter/
"""

from typing import TYPE_CHECKING, Dict, Any, Optional, List
from pymongo.database import Database
from pymongo.errors import PyMongoError

if TYPE_CHECKING:
    from gds_mongodb.connection import MongoDBConnection


class MongoDBConfiguration:
    """
    Manages retrieval and modification of MongoDB server configuration settings.

    This class provides methods to retrieve individual configuration settings,
    all settings, and filtered sets of settings (runtime vs. startup configurable).
    It also supports modifying runtime-configurable settings.

    Example:
        >>> from gds_mongodb import MongoDBConnection, MongoDBConfiguration
        >>>
        >>> with MongoDBConnection(host='localhost', database='admin') as conn:
        >>>     config = MongoDBConfiguration(conn)
        >>>
        >>>     # Get a single setting
        >>>     log_level = config.get("logLevel")
        >>>     print(f"Log level: {log_level}")
        >>>
        >>>     # Get setting details
        >>>     details = config.get_details("maxBsonObjectSize")
        >>>     if details.get("settable_at_runtime"):
        >>>         print(f"{details['name']} can be changed at runtime")
        >>>
        >>>     # Set a runtime configuration
        >>>     config.set("logLevel", 2)
        >>>
        >>>     # Get all configurations
        >>>     all_settings = config.get_all()
    """

    def __init__(self, connection: "MongoDBConnection"):
        """
        Initialize the configuration manager.

        Args:
            connection: Active MongoDBConnection instance

        Raises:
            ValueError: If connection is None or not connected
        """
        if connection is None:
            raise ValueError("Connection cannot be None")

        self._connection = connection
        self._admin_db: Optional[Database] = None

    def _get_admin_db(self) -> Database:
        """
        Get the admin database for running configuration commands.

        Returns:
            Admin database instance

        Raises:
            RuntimeError: If connection is not established
        """
        if not self._connection.is_connected():
            raise RuntimeError(
                "Connection must be established before accessing configuration"
            )

        if self._admin_db is None:
            self._admin_db = self._connection.get_client().admin

        return self._admin_db

    def get(self, name: str) -> Any:
        """
        Retrieve the value of a single configuration setting.

        Args:
            name: Name of the configuration setting to retrieve

        Returns:
            The configuration value

        Raises:
            ValueError: If name is empty
            PyMongoError: If retrieval fails

        Example:
            >>> log_level = config.get("logLevel")
            >>> print(f"Log level: {log_level}")
        """
        if not name:
            raise ValueError("Configuration name cannot be empty")

        try:
            admin_db = self._get_admin_db()
            result = admin_db.command("getParameter", 1, **{name: 1})

            # Remove metadata fields
            result.pop("ok", None)
            result.pop("$clusterTime", None)
            result.pop("operationTime", None)

            # Return the configuration value
            return result.get(name)

        except PyMongoError as e:
            raise PyMongoError(f"Failed to retrieve configuration '{name}': {str(e)}")

    def get_details(self, name: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a configuration setting.

        Args:
            name: Name of the configuration setting

        Returns:
            Dictionary with keys:
                - name: Configuration name
                - value: Current value
                - settable_at_runtime: Whether it can be set at runtime
                - settable_at_startup: Whether it can be set at startup

        Raises:
            ValueError: If name is empty
            PyMongoError: If retrieval fails

        Example:
            >>> details = config.get_details("maxBsonObjectSize")
            >>> print(f"Value: {details['value']}")
            >>> print(f"Runtime settable: {details.get('settable_at_runtime')}")
        """
        if not name:
            raise ValueError("Configuration name cannot be empty")

        try:
            admin_db = self._get_admin_db()
            result = admin_db.command(
                "getParameter", {"showDetails": True}, **{name: 1}
            )

            param_data = result.get(name, {})

            return {
                "name": name,
                "value": param_data.get("value"),
                "settable_at_runtime": param_data.get("settableAtRuntime"),
                "settable_at_startup": param_data.get("settableAtStartup"),
            }

        except PyMongoError as e:
            raise PyMongoError(
                f"Failed to retrieve configuration details for '{name}': {str(e)}"
            )

    def get_all(self, include_details: bool = False) -> Dict[str, Any]:
        """
        Retrieve all available configuration settings.

        Args:
            include_details: If True, include settableAtRuntime and settableAtStartup info

        Returns:
            Dictionary mapping configuration names to their values (or detail dicts)

        Raises:
            PyMongoError: If retrieval fails

        Example:
            >>> # Get all configuration values
            >>> settings = config.get_all()
            >>> print(f"Log level: {settings['logLevel']}")
            >>>
            >>> # Get all configurations with details
            >>> detailed = config.get_all(include_details=True)
            >>> print(detailed['maxBsonObjectSize'])
        """
        try:
            admin_db = self._get_admin_db()

            if include_details:
                result = admin_db.command(
                    "getParameter", {"showDetails": True, "allParameters": True}
                )
            else:
                result = admin_db.command("getParameter", "*")

            # Remove metadata fields
            result.pop("ok", None)
            result.pop("$clusterTime", None)
            result.pop("operationTime", None)

            return result

        except PyMongoError as e:
            raise PyMongoError(f"Failed to retrieve all configurations: {str(e)}")

    def get_all_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve all configurations as a list of detail dictionaries.

        Returns:
            List of dictionaries, each containing configuration details

        Raises:
            PyMongoError: If retrieval fails

        Example:
            >>> settings = config.get_all_details()
            >>> for setting in settings:
            >>>     if setting.get("settable_at_runtime"):
            >>>         print(f"{setting['name']} can be changed at runtime")
        """
        try:
            all_params = self.get_all(include_details=True)

            setting_list = []
            for name, details in all_params.items():
                if isinstance(details, dict) and "value" in details:
                    setting_list.append(
                        {
                            "name": name,
                            "value": details.get("value"),
                            "settable_at_runtime": details.get("settableAtRuntime"),
                            "settable_at_startup": details.get("settableAtStartup"),
                        }
                    )
                else:
                    # Simple value without details
                    setting_list.append({"name": name, "value": details})

            return setting_list

        except PyMongoError as e:
            raise PyMongoError(f"Failed to retrieve configuration details: {str(e)}")

    def get_runtime_configurable(self) -> Dict[str, Any]:
        """
        Retrieve all configurations that can be set at runtime.

        Note: This feature requires MongoDB 8.0+. For older versions,
        use get_all_details() and filter by settable_at_runtime.

        Returns:
            Dictionary of runtime-settable configurations

        Raises:
            PyMongoError: If retrieval fails or MongoDB version doesn't support this

        Example:
            >>> runtime_settings = config.get_runtime_configurable()
            >>> for name, value in runtime_settings.items():
            >>>     print(f"{name}: {value}")
        """
        try:
            admin_db = self._get_admin_db()
            result = admin_db.command(
                "getParameter", {"allParameters": True, "setAt": "runtime"}
            )

            # Remove metadata fields
            result.pop("ok", None)
            result.pop("$clusterTime", None)
            result.pop("operationTime", None)

            return result

        except PyMongoError as e:
            # Fallback for older MongoDB versions
            if "setAt" in str(e) or "unrecognized" in str(e).lower():
                # Filter manually for older versions
                all_settings = self.get_all_details()
                return {
                    s["name"]: s["value"]
                    for s in all_settings
                    if s.get("settable_at_runtime")
                }
            raise PyMongoError(f"Failed to retrieve runtime configurations: {str(e)}")

    def get_startup_configurable(self) -> Dict[str, Any]:
        """
        Retrieve all configurations that can be set at startup.

        Note: This feature requires MongoDB 8.0+. For older versions,
        use get_all_details() and filter by settable_at_startup.

        Returns:
            Dictionary of startup-settable configurations

        Raises:
            PyMongoError: If retrieval fails or MongoDB version doesn't support this

        Example:
            >>> startup_settings = config.get_startup_configurable()
            >>> for name, value in startup_settings.items():
            >>>     print(f"{name}: {value}")
        """
        try:
            admin_db = self._get_admin_db()
            result = admin_db.command(
                "getParameter", {"allParameters": True, "setAt": "startup"}
            )

            # Remove metadata fields
            result.pop("ok", None)
            result.pop("$clusterTime", None)
            result.pop("operationTime", None)

            return result

        except PyMongoError as e:
            # Fallback for older MongoDB versions
            if "setAt" in str(e) or "unrecognized" in str(e).lower():
                # Filter manually for older versions
                all_settings = self.get_all_details()
                return {
                    s["name"]: s["value"]
                    for s in all_settings
                    if s.get("settable_at_startup")
                }
            raise PyMongoError(f"Failed to retrieve startup configurations: {str(e)}")

    def get_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """
        Get all configurations whose names start with the given prefix.

        Args:
            prefix: Configuration name prefix to filter by

        Returns:
            Dictionary of matching configurations

        Example:
            >>> # Get all replication-related configurations
            >>> repl_settings = config.get_by_prefix("repl")
            >>> for name, value in repl_settings.items():
            >>>     print(f"{name}: {value}")
        """
        if not prefix:
            raise ValueError("Prefix cannot be empty")

        all_settings = self.get_all()
        return {
            name: value
            for name, value in all_settings.items()
            if name.startswith(prefix)
        }

    def search(self, keyword: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for configurations containing the given keyword in their name.

        Args:
            keyword: Keyword to search for in configuration names
            case_sensitive: Whether search should be case-sensitive

        Returns:
            Dictionary of matching configurations

        Example:
            >>> # Find all configurations related to "log"
            >>> log_settings = config.search("log")
            >>> for name, value in log_settings.items():
            >>>     print(f"{name}: {value}")
        """
        if not keyword:
            raise ValueError("Keyword cannot be empty")

        all_settings = self.get_all()

        if case_sensitive:
            return {
                name: value for name, value in all_settings.items() if keyword in name
            }
        else:
            keyword_lower = keyword.lower()
            return {
                name: value
                for name, value in all_settings.items()
                if keyword_lower in name.lower()
            }

    def to_dict(self) -> Dict[str, Any]:
        """
        Export all configurations as a dictionary.

        Returns:
            Dictionary of all configurations
        """
        return self.get_all()

    def set(
        self, name: str, value: Any, comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set a runtime-configurable setting value.

        Warning: Only configurations that are settable at runtime can be modified.
        Check configuration documentation or use get_details() first.

        Args:
            name: Name of the configuration to set
            value: New value for the configuration
            comment: Optional comment for the operation

        Returns:
            Command result dictionary

        Raises:
            ValueError: If name is empty
            PyMongoError: If configuration cannot be set or is startup-only

        Example:
            >>> # Set log level to verbose
            >>> result = config.set("logLevel", 1)
            >>>
            >>> # Set with comment
            >>> result = config.set(
            ...     "cursorTimeoutMillis",
            ...     300000,
            ...     comment="Increase cursor timeout to 5 minutes"
            ... )
        """
        if not name:
            raise ValueError("Configuration name cannot be empty")

        try:
            admin_db = self._get_admin_db()

            command = {"setParameter": 1, name: value}
            if comment:
                command["comment"] = comment

            result = admin_db.command(**command)
            return result

        except PyMongoError as e:
            error_msg = str(e)
            if "settable at startup" in error_msg.lower():
                raise PyMongoError(
                    f"Configuration '{name}' can only be set at startup, "
                    f"not at runtime: {error_msg}"
                )
            raise PyMongoError(f"Failed to set configuration '{name}': {error_msg}")

    def set_multiple(
        self, settings: Dict[str, Any], comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set multiple runtime-configurable settings at once.

        Args:
            settings: Dictionary mapping configuration names to values
            comment: Optional comment for the operation

        Returns:
            Command result dictionary

        Raises:
            ValueError: If settings dict is empty
            PyMongoError: If any configuration cannot be set

        Example:
            >>> settings = {
            ...     "logLevel": 2,
            ...     "cursorTimeoutMillis": 300000,
            ...     "notablescan": False
            ... }
            >>> result = config.set_multiple(settings)
        """
        if not settings:
            raise ValueError("Settings dictionary cannot be empty")

        try:
            admin_db = self._get_admin_db()

            command = {"setParameter": 1, **settings}
            if comment:
                command["comment"] = comment

            result = admin_db.command(**command)
            return result

        except PyMongoError as e:
            raise PyMongoError(f"Failed to set configurations: {str(e)}")

    def reset(self, name: str) -> bool:
        """
        Attempt to reset a configuration to its default value.

        Note: Not all configurations have well-defined defaults. This method
        returns information about typical default values but cannot always
        reset configurations programmatically.

        Args:
            name: Name of the configuration to check for default

        Returns:
            True if default value is known and documented

        Example:
            >>> # Check if configuration has a known default
            >>> if config.reset("logLevel"):
            ...     print("Configuration has documented default value")
        """
        # Common default values for frequently-modified configurations
        defaults = {
            "logLevel": 0,
            "quiet": 0,
            "notablescan": False,
            "cursorTimeoutMillis": 600000,  # 10 minutes
            "ttlMonitorEnabled": True,
        }

        if name in defaults:
            try:
                self.set(name, defaults[name])
                return True
            except PyMongoError:
                return False

        return False

    def __repr__(self) -> str:
        connected = self._connection.is_connected() if self._connection else False
        return f"MongoDBConfiguration(connected={connected})"
