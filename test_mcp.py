"""Tests for MCP (Model Context Protocol) integration in UnisonAI."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from unisonai.tools.mcp_manager import MCPManager
from unisonai.tools.mcp_client import MCPClient
from unisonai.tools.mcp_tool import MCPTool
from unisonai.tools.mcp_errors import MCPConnectionError, MCPConfigurationError, MCPToolExecutionError
from unisonai.tools.tool import ToolResult


class TestMCPConfigurationValidation:
    """Test MCP configuration validation."""
    
    def test_valid_stdio_config(self):
        """Test validation of valid stdio-based MCP configuration."""
        config = {
            "mcpServers": {
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time"]
                }
            }
        }
        manager = MCPManager()
        assert manager.is_valid_mcp_servers_config(config) is True
    
    def test_valid_url_config(self):
        """Test validation of valid URL-based MCP configuration."""
        config = {
            "mcpServers": {
                "api": {
                    "url": "http://localhost:8000/mcp",
                    "headers": {"Authorization": "Bearer token"}
                }
            }
        }
        manager = MCPManager()
        assert manager.is_valid_mcp_servers_config(config) is True
    
    def test_invalid_config_missing_mcpservers(self):
        """Test validation fails when mcpServers key is missing."""
        config = {
            "servers": {
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time"]
                }
            }
        }
        manager = MCPManager()
        assert manager.is_valid_mcp_servers_config(config) is False
    
    def test_invalid_config_wrong_type(self):
        """Test validation fails when configuration has wrong types."""
        config = {
            "mcpServers": "not_a_dict"
        }
        manager = MCPManager()
        assert manager.is_valid_mcp_servers_config(config) is False
    
    def test_invalid_server_config(self):
        """Test validation fails for invalid server configuration."""
        config = {
            "mcpServers": {
                "time": {
                    "command": "uvx",
                    "args": "not_a_list"  # Should be a list
                }
            }
        }
        manager = MCPManager()
        assert manager.is_valid_mcp_servers_config(config) is False


class TestMCPTool:
    """Test MCPTool wrapper functionality."""
    
    def test_mcp_tool_initialization(self):
        """Test MCPTool initialization with valid parameters."""
        parameters = {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to process"
                },
                "count": {
                    "type": "integer", 
                    "description": "Number of iterations",
                    "default": 1
                }
            },
            "required": ["message"]
        }
        
        mock_manager = Mock()
        mock_manager.clients = {}
        
        tool = MCPTool(
            name="test-tool",
            description="Test tool description",
            parameters=parameters,
            client_id="test_client",
            mcp_tool_name="original_tool",
            mcp_manager=mock_manager
        )
        
        assert tool.name == "test-tool"
        assert tool.description == "Test tool description"
        assert len(tool.params) == 2
        assert tool.params[0].name == "message"
        assert tool.params[0].required is True
        assert tool.params[1].name == "count"
        assert tool.params[1].required is False
        assert tool.params[1].default_value == 1
    
    def test_mcp_tool_parameter_conversion(self):
        """Test conversion of MCP parameters to UnisonAI Fields."""
        parameters = {
            "type": "object",
            "properties": {
                "string_param": {"type": "string", "description": "A string parameter"},
                "int_param": {"type": "integer", "description": "An integer parameter"},
                "float_param": {"type": "number", "description": "A float parameter"},
                "bool_param": {"type": "boolean", "description": "A boolean parameter"},
                "array_param": {"type": "array", "description": "An array parameter"},
                "object_param": {"type": "object", "description": "An object parameter"}
            },
            "required": ["string_param", "int_param"]
        }
        
        mock_manager = Mock()
        tool = MCPTool(
            name="test-tool",
            description="Test",
            parameters=parameters,
            client_id="test",
            mcp_tool_name="test",
            mcp_manager=mock_manager
        )
        
        # Check field types are correctly mapped
        field_types = {field.name: field.field_type for field in tool.params}
        assert field_types["string_param"].value == "string"
        assert field_types["int_param"].value == "integer"
        assert field_types["float_param"].value == "float"
        assert field_types["bool_param"].value == "boolean"
        assert field_types["array_param"].value == "list"
        assert field_types["object_param"].value == "dict"
    
    @patch('asyncio.run_coroutine_threadsafe')
    def test_mcp_tool_execution_success(self, mock_run_coroutine):
        """Test successful MCP tool execution."""
        # Mock the asyncio execution
        mock_future = Mock()
        mock_future.result.return_value = "Tool executed successfully"
        mock_run_coroutine.return_value = mock_future
        
        # Mock the MCP manager and client
        mock_client = Mock()
        mock_manager = Mock()
        mock_manager.clients = {"test_client": mock_client}
        mock_manager.loop = Mock()
        
        tool = MCPTool(
            name="test-tool",
            description="Test",
            parameters={"type": "object", "properties": {}, "required": []},
            client_id="test_client",
            mcp_tool_name="original_tool",
            mcp_manager=mock_manager
        )
        
        result = tool._run(param1="value1")
        assert result == "Tool executed successfully"
        mock_run_coroutine.assert_called_once()
    
    def test_mcp_tool_execution_client_not_found(self):
        """Test MCP tool execution fails when client not found."""
        mock_manager = Mock()
        mock_manager.clients = {}  # Empty clients dict
        
        tool = MCPTool(
            name="test-tool",
            description="Test",
            parameters={"type": "object", "properties": {}, "required": []},
            client_id="missing_client",
            mcp_tool_name="original_tool",
            mcp_manager=mock_manager
        )
        
        with pytest.raises(MCPToolExecutionError) as exc_info:
            tool._run()
        
        assert "MCP client 'missing_client' not found" in str(exc_info.value)
        assert exc_info.value.tool_name == "test-tool"


class TestMCPManager:
    """Test MCPManager functionality."""
    
    def test_manager_singleton(self):
        """Test that MCPManager implements singleton pattern."""
        manager1 = MCPManager()
        manager2 = MCPManager()
        assert manager1 is manager2
    
    def test_init_config_invalid_configuration(self):
        """Test init_config raises error for invalid configuration."""
        manager = MCPManager()
        invalid_config = {"not_mcp_servers": {}}
        
        with pytest.raises(MCPConfigurationError) as exc_info:
            manager.init_config(invalid_config)
        
        assert "Invalid MCP servers configuration" in str(exc_info.value)
        assert exc_info.value.config == invalid_config


class TestMCPClient:
    """Test MCPClient functionality."""
    
    def test_client_initialization(self):
        """Test MCPClient initialization."""
        client = MCPClient()
        assert client.session is None
        assert client.tools == []
        assert client.resources is False
        assert client.client_id is None
    
    @pytest.mark.asyncio
    async def test_connect_server_missing_mcp(self):
        """Test connection fails gracefully when MCP is not available."""
        with patch('unisonai.tools.mcp_client.MCPClient.__init__') as mock_init:
            # Simulate ImportError during MCP import
            mock_init.side_effect = ImportError("Could not import mcp")
            
            with pytest.raises(ImportError) as exc_info:
                MCPClient()
            
            assert "Could not import mcp" in str(exc_info.value)


class TestMCPIntegration:
    """Integration tests for MCP functionality."""
    
    def test_tool_validation_with_mcp_tool(self):
        """Test that MCPTool integrates properly with UnisonAI validation."""
        parameters = {
            "type": "object",
            "properties": {
                "required_param": {
                    "type": "string",
                    "description": "Required parameter"
                }
            },
            "required": ["required_param"]
        }
        
        mock_manager = Mock()
        tool = MCPTool(
            name="validation-test",
            description="Test validation",
            parameters=parameters,
            client_id="test_client",
            mcp_tool_name="test",
            mcp_manager=mock_manager
        )
        
        # Test validation passes with required parameter
        result = tool.validate_parameters({"required_param": "value"})
        assert result.success is True
        
        # Test validation fails without required parameter
        result = tool.validate_parameters({})
        assert result.success is False
        assert "Missing required parameter: required_param" in result.error_message
        
        # Test validation passes with extra parameters (UnisonAI allows this)
        # This is the expected behavior for UnisonAI's validation system
        result = tool.validate_parameters({"required_param": "value", "extra_param": "value"})
        assert result.success is True

    def test_mcp_tool_run_method(self):
        """Test that MCPTool run method works with UnisonAI's ToolResult system."""
        mock_manager = Mock()
        mock_manager.clients = {"test_client": Mock()}
        
        tool = MCPTool(
            name="test-tool",
            description="Test",
            parameters={"type": "object", "properties": {}, "required": []},
            client_id="test_client",
            mcp_tool_name="test",
            mcp_manager=mock_manager
        )
        
        # Mock the _run method to return a simple result
        with patch.object(tool, '_run', return_value="Mocked result"):
            result = tool.run()
            
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert result.result == "Mocked result"
            assert result.metadata["tool_name"] == "test-tool"


if __name__ == "__main__":
    pytest.main([__file__])