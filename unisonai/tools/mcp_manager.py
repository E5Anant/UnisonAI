"""MCP (Model Context Protocol) manager for UnisonAI.

This module provides the MCPManager class for managing MCP server connections
and converting MCP tools to UnisonAI-compatible BaseTool format.
"""

import asyncio
import atexit
import json
import threading
import time
import uuid
from typing import Dict, List, Optional, Union, Any

from .mcp_errors import MCPConnectionError, MCPConfigurationError, MCPToolExecutionError
from .mcp_client import MCPClient
from .mcp_tool import MCPTool


class MCPManager:
    """Singleton manager for MCP server connections and tool registration."""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MCPManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'clients'):  # Only initialize once
            try:
                import mcp  # noqa
            except ImportError as e:
                raise ImportError(
                    'Could not import mcp. Please install mcp with `pip install -U mcp`.'
                ) from e

            self.clients: Dict[str, MCPClient] = {}
            self.loop = asyncio.new_event_loop()
            self.loop_thread = threading.Thread(target=self._start_loop, daemon=True)
            self.loop_thread.start()

            # Process tracking for cleanup
            self.processes = []
            self._monkey_patch_mcp_process_creation()

    def _monkey_patch_mcp_process_creation(self):
        """Monkey patch MCP process creation for cleanup tracking."""
        try:
            import mcp.client.stdio
            target = mcp.client.stdio._create_platform_compatible_process
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                'MCP integration needs to monkey patch MCP for process cleanup. '
                'Please upgrade MCP to a higher version with `pip install -U mcp`.'
            ) from e

        async def _patched_create_process(*args, **kwargs):
            process = await target(*args, **kwargs)
            self.processes.append(process)
            return process

        mcp.client.stdio._create_platform_compatible_process = _patched_create_process

    def _start_loop(self):
        """Start the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)

        # Set exception handler for MCP SSE connection issues
        def exception_handler(loop, context):
            exception = context.get('exception')
            if exception:
                # Silently handle cross-task exceptions from MCP SSE connections
                if (isinstance(exception, RuntimeError) and
                        'Attempted to exit cancel scope in a different task' in str(exception)):
                    return
                if (isinstance(exception, BaseExceptionGroup) and
                        'Attempted to exit cancel scope in a different task' in str(exception)):
                    return

            # Handle other exceptions normally
            loop.default_exception_handler(context)

        self.loop.set_exception_handler(exception_handler)
        self.loop.run_forever()

    def is_valid_mcp_servers_config(self, config: Dict[str, Any]) -> bool:
        """Validate MCP servers configuration format.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid
            
        Example valid config:
        {
            "mcpServers": {
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
                },
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                }
            }
        }
        """
        # Check if the top-level key "mcpServers" exists and is a dictionary
        if not isinstance(config, dict) or 'mcpServers' not in config:
            return False
        
        mcp_servers = config['mcpServers']
        if not isinstance(mcp_servers, dict):
            return False

        # Check each server configuration
        for server_name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                return False
            
            # Check for command-based configuration
            if 'command' in server_config:
                if not isinstance(server_config['command'], str):
                    return False
                if 'args' not in server_config or not isinstance(server_config['args'], list):
                    return False
            
            # Check for URL-based configuration
            if 'url' in server_config:
                if not isinstance(server_config['url'], str):
                    return False
                if 'headers' in server_config and not isinstance(server_config['headers'], dict):
                    return False
            
            # Environment variables must be a dictionary if present
            if 'env' in server_config and not isinstance(server_config['env'], dict):
                return False

        return True

    def init_config(self, config: Dict[str, Any]) -> List[MCPTool]:
        """Initialize MCP tools from server configuration.
        
        Args:
            config: MCP servers configuration
            
        Returns:
            List of MCPTool objects (BaseTool instances)
            
        Raises:
            MCPConfigurationError: If configuration is invalid
            MCPConnectionError: If initialization fails
        """
        if not self.is_valid_mcp_servers_config(config):
            raise MCPConfigurationError('Invalid MCP servers configuration', config=config)

        # Submit coroutine to event loop and wait for result
        future = asyncio.run_coroutine_threadsafe(
            self._init_config_async(config), 
            self.loop
        )
        
        try:
            return future.result()
        except Exception as e:
            raise MCPConnectionError(f'Failed to initialize MCP tools: {e}', original_error=e)

    async def _init_config_async(self, config: Dict[str, Any]) -> List[MCPTool]:
        """Async implementation of MCP configuration initialization."""
        tools: List[MCPTool] = []
        mcp_servers = config['mcpServers']
        successful_connections = 0
        failed_connections = []
        
        for server_name, server_config in mcp_servers.items():
            try:
                client = MCPClient()
                
                # Connect to the MCP server
                await client.connect_server(server_name, server_config)
                
                # Generate unique client ID
                client_id = f"{server_name}_{uuid.uuid4()}"
                client.client_id = client_id
                self.clients[client_id] = client
                successful_connections += 1
                
                # Convert MCP tools to MCPTool objects
                for mcp_tool in client.tools:
                    # Create tool parameters schema
                    parameters = mcp_tool.inputSchema
                    if 'required' not in parameters:
                        parameters['required'] = []
                    
                    # Ensure schema has required fields
                    required_fields = {'type', 'properties', 'required'}
                    missing_fields = required_fields - parameters.keys()
                    if missing_fields:
                        raise ValueError(f'Missing required schema fields: {missing_fields}')

                    # Clean up parameters to only include standard fields
                    cleaned_parameters = {
                        'type': parameters['type'],
                        'properties': parameters['properties'],
                        'required': parameters['required']
                    }
                    
                    # Create tool name and MCPTool object
                    tool_name = f"{server_name}-{mcp_tool.name}"
                    mcp_tool_obj = MCPTool(
                        name=tool_name,
                        description=mcp_tool.description,
                        parameters=cleaned_parameters,
                        client_id=client_id,
                        mcp_tool_name=mcp_tool.name,
                        mcp_manager=self
                    )
                    tools.append(mcp_tool_obj)

                # Add resource tools if available
                if client.resources:
                    # List resources tool
                    list_resources_tool = MCPTool(
                        name=f"{server_name}-list_resources",
                        description=(
                            'List available resources from the MCP server. '
                            'Resources represent data sources that can be used as context.'
                        ),
                        parameters={'type': 'object', 'properties': {}, 'required': []},
                        client_id=client_id,
                        mcp_tool_name='list_resources',
                        mcp_manager=self
                    )
                    tools.append(list_resources_tool)

                    # Read resource tool
                    read_resource_tool = MCPTool(
                        name=f"{server_name}-read_resource",
                        description=(
                            'Read a specific resource by URI. '
                            'Use list_resources first to discover available URIs.'
                        ),
                        parameters={
                            'type': 'object',
                            'properties': {
                                'uri': {
                                    'type': 'string',
                                    'description': 'The URI of the resource to read'
                                }
                            },
                            'required': ['uri']
                        },
                        client_id=client_id,
                        mcp_tool_name='read_resource',
                        mcp_manager=self
                    )
                    tools.append(read_resource_tool)
                    
            except Exception as e:
                # Log the failed connection but continue with other servers
                failed_connections.append((server_name, str(e)))
                continue
        
        # If no servers connected successfully, raise an error with helpful details
        if successful_connections == 0:
            error_details = []
            for server_name, error in failed_connections:
                error_details.append(f"  - {server_name}: {error}")
            
            error_msg = f"Failed to connect to any MCP servers:\n" + "\n".join(error_details)
            
            # Provide helpful suggestions based on common errors
            if any("No such file or directory" in error for _, error in failed_connections):
                error_msg += "\n\nCommon solutions:"
                if any("uvx" in error for _, error in failed_connections):
                    error_msg += "\n  - Install uvx: pip install uvx"
                if any("npx" in error for _, error in failed_connections):
                    error_msg += "\n  - Install Node.js and npm"
                error_msg += "\n  - Check that MCP server commands are in your PATH"
            
            raise MCPConnectionError(error_msg)
        
        # If some servers failed but others succeeded, just warn
        if failed_connections:
            import warnings
            failed_names = [name for name, _ in failed_connections]
            warnings.warn(
                f"Some MCP servers failed to connect: {', '.join(failed_names)}. "
                f"Continuing with {successful_connections} successful connection(s)."
            )

        return tools

    def shutdown(self):
        """Shutdown the MCP manager and clean up resources."""
        futures = []
        
        # Clean up all clients
        for client_id in list(self.clients.keys()):
            client = self.clients[client_id]
            future = asyncio.run_coroutine_threadsafe(client.cleanup(), self.loop)
            futures.append(future)
            del self.clients[client_id]
        
        # Wait for graceful cleanup
        time.sleep(1)
        
        # Force terminate processes if needed
        if asyncio.all_tasks(self.loop):
            for process in self.processes:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass  # Process may have already exited

        # Stop the event loop
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop_thread.join()


def _cleanup_mcp(_sig_num=None, _frame=None):
    """Cleanup function for MCP manager on exit."""
    if MCPManager._instance is None:
        return
    manager = MCPManager()
    manager.shutdown()


# Register cleanup function
if threading.current_thread() is threading.main_thread():
    atexit.register(_cleanup_mcp)