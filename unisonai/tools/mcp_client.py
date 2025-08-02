"""MCP (Model Context Protocol) client implementation for UnisonAI.

This module provides the MCPClient class for connecting to and interacting with
MCP servers using various transport methods (stdio, SSE, streamable-http).
"""

import asyncio
import datetime
import json
import threading
import uuid
from contextlib import AsyncExitStack
from typing import Dict, List, Optional, Union, Any

from .mcp_errors import MCPConnectionError, MCPToolExecutionError


class MCPClient:
    """Client for connecting to and interacting with MCP servers."""

    def __init__(self):
        try:
            from mcp import ClientSession
        except ImportError as e:
            raise ImportError(
                'Could not import mcp. Please install mcp with `pip install -U mcp`.'
            ) from e
        
        self.session: Optional[ClientSession] = None
        self.tools: List = []
        self.exit_stack = AsyncExitStack()
        self.resources: bool = False
        self._last_mcp_server_name = None
        self._last_mcp_server = None
        self.client_id = None

    async def connect_server(self, mcp_server_name: str, mcp_server: Dict[str, Any]):
        """Connect to an MCP server and retrieve the available tools.
        
        Args:
            mcp_server_name: Name identifier for the MCP server
            mcp_server: Server configuration dictionary
            
        Raises:
            MCPConnectionError: If connection fails
        """
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.sse import sse_client
        from mcp.client.stdio import stdio_client
        from mcp.client.streamable_http import streamablehttp_client

        # Save parameters for reconnection
        self._last_mcp_server_name = mcp_server_name
        self._last_mcp_server = mcp_server

        try:
            if 'url' in mcp_server:
                # HTTP-based connection (SSE or streamable-http)
                url = mcp_server.get('url')
                sse_read_timeout = mcp_server.get('sse_read_timeout', 300)
                
                if mcp_server.get('type', 'sse') == 'streamable-http':
                    # Streamable HTTP mode
                    self._streams_context = streamablehttp_client(
                        url=url, 
                        sse_read_timeout=datetime.timedelta(seconds=sse_read_timeout)
                    )
                    read_stream, write_stream, get_session_id = await self.exit_stack.enter_async_context(
                        self._streams_context
                    )
                    self._session_context = ClientSession(read_stream, write_stream)
                    self.session = await self.exit_stack.enter_async_context(self._session_context)
                else:
                    # SSE mode
                    headers = mcp_server.get('headers', {'Accept': 'text/event-stream'})
                    self._streams_context = sse_client(url, headers, sse_read_timeout=sse_read_timeout)
                    streams = await self.exit_stack.enter_async_context(self._streams_context)
                    self._session_context = ClientSession(*streams)
                    self.session = await self.exit_stack.enter_async_context(self._session_context)
            else:
                # Stdio-based connection
                server_params = StdioServerParameters(
                    command=mcp_server['command'],
                    args=mcp_server['args'],
                    env=mcp_server.get('env', None)
                )
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                self.stdio, self.write = stdio_transport
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(self.stdio, self.write)
                )

            # Initialize session and get tools
            await self.session.initialize()
            list_tools = await self.session.list_tools()
            self.tools = list_tools.tools
            
            # Check for resources
            try:
                list_resources = await self.session.list_resources()
                if list_resources.resources:
                    self.resources = True
            except Exception:
                pass  # No resources available
                
        except Exception as e:
            raise MCPConnectionError(
                f'Failed to connect to MCP server {mcp_server_name}: {e}',
                server_name=mcp_server_name,
                original_error=e
            )

    async def reconnect(self):
        """Reconnect to the MCP server.
        
        Returns:
            New MCPClient instance with the same configuration
        """
        if self.client_id is None:
            raise RuntimeError(
                'Cannot reconnect: client_id is None. '
                'This usually means the client was not properly registered.'
            )
        
        new_client = MCPClient()
        new_client.client_id = self.client_id
        await new_client.connect_server(self._last_mcp_server_name, self._last_mcp_server)
        return new_client

    async def execute_function(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool function on the MCP server.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Tool execution result as string
            
        Raises:
            MCPToolExecutionError: If tool execution fails
        """
        from mcp.types import TextResourceContents

        # Check if session is alive
        try:
            await self.session.send_ping()
        except Exception as e:
            # Attempt to reconnect
            try:
                from .mcp_manager import MCPManager
                manager = MCPManager()
                if self.client_id is not None:
                    manager.clients[self.client_id] = await self.reconnect()
                    return await manager.clients[self.client_id].execute_function(tool_name, tool_args)
                else:
                    raise MCPToolExecutionError(
                        f"Session reconnect failed: client_id is None",
                        tool_name=tool_name
                    )
            except Exception as e3:
                raise MCPToolExecutionError(
                    f"Session reconnect failed: {e3}",
                    tool_name=tool_name,
                    original_error=e3
                )

        try:
            if tool_name == 'list_resources':
                list_resources = await self.session.list_resources()
                if list_resources.resources:
                    resources_str = '\n\n'.join(str(resource) for resource in list_resources.resources)
                else:
                    resources_str = 'No resources found'
                return resources_str
                
            elif tool_name == 'read_resource':
                uri = tool_args.get('uri')
                if not uri:
                    raise ValueError('URI is required for read_resource')
                
                read_resource = await self.session.read_resource(uri)
                texts = []
                for resource in read_resource.contents:
                    if isinstance(resource, TextResourceContents):
                        texts.append(resource.text)
                
                if texts:
                    return '\n\n'.join(texts)
                else:
                    return 'Failed to read resource'
                    
            else:
                # Execute regular tool
                response = await self.session.call_tool(tool_name, tool_args)
                texts = []
                for content in response.content:
                    if content.type == 'text':
                        texts.append(content.text)
                
                if texts:
                    return '\n\n'.join(texts)
                else:
                    return 'Tool execution completed with no text output'
                    
        except Exception as e:
            raise MCPToolExecutionError(
                f"Failed to execute tool '{tool_name}': {e}",
                tool_name=tool_name,
                original_error=e
            )

    async def cleanup(self):
        """Clean up client resources."""
        try:
            await self.exit_stack.aclose()
        except Exception:
            pass  # Ignore cleanup errors