# Model Context Protocol (MCP) Integration

UnisonAI now supports [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/specification), allowing agents to connect to external tools and services through standardized MCP servers.

## Quick Start

```python
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools import MCPManager
from unisonai import config

# Configure MCP servers
MCP_CONFIG = {
    "mcpServers": {
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time"]
        },
        "fetch": {
            "command": "uvx", 
            "args": ["mcp-server-fetch"]
        }
    }
}

# Initialize MCP and get tools
mcp_manager = MCPManager()
mcp_tools = mcp_manager.init_config(MCP_CONFIG)

# Use MCP tools with your agent
config.set_api_key("gemini", "your-api-key")
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="MCP Assistant",
    description="AI assistant with MCP capabilities",
    tools=mcp_tools
)

agent.unleash(task="What time is it?")
```

## Configuration Options

### Stdio-based MCP Servers
```python
{
    "mcpServers": {
        "server_name": {
            "command": "command_to_run",
            "args": ["arg1", "arg2"],
            "env": {"ENV_VAR": "value"}  # Optional
        }
    }
}
```

### HTTP-based MCP Servers
```python
{
    "mcpServers": {
        "api_server": {
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": "Bearer token"},  # Optional
            "type": "sse"  # or "streamable-http"
        }
    }
}
```

## Available MCP Tools

MCP tools are automatically converted to UnisonAI `BaseTool` instances and can be used with any agent. Each MCP server's tools are prefixed with the server name (e.g., `time-get_current_time`).

## Error Handling

```python
from unisonai.tools import MCPConnectionError, MCPConfigurationError

try:
    mcp_tools = mcp_manager.init_config(config)
except MCPConnectionError as e:
    print(f"Failed to connect to MCP server: {e}")
except MCPConfigurationError as e:
    print(f"Invalid MCP configuration: {e}")
```

For complete examples, see `mcp_example.py`.