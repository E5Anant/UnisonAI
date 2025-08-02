"""MCP (Model Context Protocol) specific error classes for UnisonAI."""


class MCPError(Exception):
    """Base exception for MCP-related errors."""
    pass


class MCPConnectionError(MCPError):
    """Raised when MCP server connection fails."""
    
    def __init__(self, message: str, server_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.server_name = server_name
        self.original_error = original_error


class MCPToolExecutionError(MCPError):
    """Raised when MCP tool execution fails."""
    
    def __init__(self, message: str, tool_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.original_error = original_error


class MCPConfigurationError(MCPError):
    """Raised when MCP server configuration is invalid."""
    
    def __init__(self, message: str, config: dict = None):
        super().__init__(message)
        self.config = config