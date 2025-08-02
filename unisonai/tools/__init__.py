"""
UnisonAI Tools Module

This module provides a comprehensive set of tools for AI agents with strong typing,
validation, and error handling.
"""

from .tool import BaseTool, Field, ToolResult
from .types import ToolParameterType
from .websearch import WebSearchTool
from .memory import MemoryTool
from .rag import RAGTool

# MCP (Model Context Protocol) support
from .mcp_manager import MCPManager
from .mcp_tool import MCPTool
from .mcp_errors import MCPError, MCPConnectionError, MCPToolExecutionError, MCPConfigurationError

__all__ = [
    "BaseTool", 
    "Field", 
    "ToolResult",
    "WebSearchTool", 
    "MemoryTool", 
    "RAGTool",
    "ToolParameterType",
    # MCP support
    "MCPManager",
    "MCPTool",
    "MCPError",
    "MCPConnectionError", 
    "MCPToolExecutionError",
    "MCPConfigurationError"
]