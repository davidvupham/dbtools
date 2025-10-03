"""
Custom exception classes for gds_snowflake package
"""


class SnowflakeConnectionError(Exception):
    """Raised when connection to Snowflake fails"""
    
    def __init__(self, message: str, account: str = None):
        super().__init__(message)
        self.account = account


class SnowflakeQueryError(Exception):
    """Raised when query execution fails"""
    
    def __init__(self, message: str, query: str = None):
        super().__init__(message)
        self.query = query


class VaultAuthenticationError(Exception):
    """Raised when Vault authentication fails"""
    
    def __init__(self, message: str, vault_addr: str = None):
        super().__init__(message)
        self.vault_addr = vault_addr


class VaultSecretError(Exception):
    """Raised when secret retrieval from Vault fails"""
    
    def __init__(self, message: str, secret_path: str = None):
        super().__init__(message)
        self.secret_path = secret_path


class SnowflakeConfigurationError(Exception):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, parameter: str = None):
        super().__init__(message)
        self.parameter = parameter
