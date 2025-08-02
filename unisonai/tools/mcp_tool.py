"""MCP (Model Context Protocol) tool wrapper for UnisonAI BaseTool integration."""

import asyncio
from typing import Any, Dict, List

from .tool import BaseTool, Field, ToolResult
from .types import ToolParameterType
from .mcp_errors import MCPToolExecutionError


class MCPTool(BaseTool):
    """Wrapper class that adapts MCP tools to UnisonAI BaseTool interface."""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any], 
                 client_id: str, mcp_tool_name: str, mcp_manager):
        """Initialize MCP tool wrapper.
        
        Args:
            name: Tool name for UnisonAI
            description: Tool description
            parameters: MCP tool parameters schema
            client_id: MCP client identifier
            mcp_tool_name: Original MCP tool name
            mcp_manager: Reference to MCPManager instance
        """
        self.name = name
        self.description = description
        self.client_id = client_id
        self.mcp_tool_name = mcp_tool_name
        self.mcp_manager = mcp_manager
        
        # Convert MCP parameters to UnisonAI Field objects
        self.params = self._convert_mcp_parameters_to_fields(parameters)
        
        # Call parent constructor after setting required attributes
        super().__init__()
    
    def _convert_mcp_parameters_to_fields(self, mcp_parameters: Dict[str, Any]) -> List[Field]:
        """Convert MCP parameter schema to UnisonAI Field objects.
        
        Args:
            mcp_parameters: MCP tool parameters in JSON schema format
            
        Returns:
            List of Field objects for UnisonAI tool validation
        """
        fields = []
        properties = mcp_parameters.get('properties', {})
        required_params = mcp_parameters.get('required', [])
        
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'string')
            param_description = param_info.get('description', f'Parameter {param_name}')
            param_default = param_info.get('default')
            is_required = param_name in required_params
            
            # Map JSON schema types to UnisonAI ToolParameterType
            type_mapping = {
                'string': ToolParameterType.STRING,
                'integer': ToolParameterType.INTEGER,
                'number': ToolParameterType.FLOAT,
                'boolean': ToolParameterType.BOOLEAN,
                'array': ToolParameterType.LIST,
                'object': ToolParameterType.DICT
            }
            
            field_type = type_mapping.get(param_type, ToolParameterType.STRING)
            
            field = Field(
                name=param_name,
                description=param_description,
                default_value=param_default,
                required=is_required,
                field_type=field_type
            )
            fields.append(field)
        
        return fields
    
    def _run(self, **kwargs) -> str:
        """Execute the MCP tool with given arguments.
        
        Args:
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result as string
            
        Raises:
            MCPToolExecutionError: If tool execution fails
        """
        # Get the MCP client
        if self.client_id not in self.mcp_manager.clients:
            raise MCPToolExecutionError(
                f"MCP client '{self.client_id}' not found",
                tool_name=self.name
            )
        
        client = self.mcp_manager.clients[self.client_id]
        
        # Execute the tool asynchronously
        future = asyncio.run_coroutine_threadsafe(
            client.execute_function(self.mcp_tool_name, kwargs),
            self.mcp_manager.loop
        )
        
        try:
            return future.result()
        except Exception as e:
            raise MCPToolExecutionError(
                f"Failed to execute MCP tool '{self.name}': {e}",
                tool_name=self.name,
                original_error=e
            )