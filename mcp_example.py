"""
Example: Using Model Context Protocol (MCP) with UnisonAI

This example demonstrates how to integrate MCP servers with UnisonAI agents,
allowing them to use external tools and services through the MCP protocol.
"""

from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools import MCPManager
from unisonai import config

# Example MCP server configuration
# This configuration assumes you have MCP servers available
MCP_CONFIG = {
    "mcpServers": {
        # Example: Time server using uvx (if available)
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=America/New_York"]
        },
        # Example: Fetch server for web requests
        "fetch": {
            "command": "uvx", 
            "args": ["mcp-server-fetch"]
        },
        # Example: File system server
        "filesystem": {
            "command": "uvx",
            "args": ["mcp-server-filesystem", "/tmp"]
        }
        # You can also configure HTTP-based MCP servers:
        # "api_server": {
        #     "url": "http://localhost:8000/mcp",
        #     "headers": {"Authorization": "Bearer your-token"}
        # }
    }
}


def example_mcp_with_single_agent():
    """Example of using MCP tools with a Single_Agent."""
    
    # Configure your Gemini API key
    config.set_api_key("gemini", "YOUR_API_KEY_HERE")
    
    try:
        # Initialize MCP manager and get MCP tools
        mcp_manager = MCPManager()
        mcp_tools = mcp_manager.init_config(MCP_CONFIG)
        
        print(f"Successfully loaded {len(mcp_tools)} MCP tools:")
        for tool in mcp_tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Create an agent with MCP tools
        agent = Single_Agent(
            llm=Gemini(model="gemini-2.0-flash"),
            identity="MCP Assistant",
            description="An AI assistant that can use external tools via MCP",
            tools=mcp_tools,  # Pass MCP tools to the agent
            history_folder="mcp_history",
            output_file="mcp_output.txt"
        )
        
        # Use the agent with MCP capabilities
        agent.unleash(task="What time is it? Also, can you list the available files in /tmp?")
        
    except Exception as e:
        print(f"Error initializing MCP: {e}")
        print("Make sure you have MCP servers installed and configured correctly.")
        print("You can install common MCP servers with: pip install uvx")


def example_mcp_selective_tools():
    """Example of using only specific MCP tools."""
    
    try:
        mcp_manager = MCPManager()
        all_mcp_tools = mcp_manager.init_config(MCP_CONFIG)
        
        # Filter to only use time-related tools
        time_tools = [tool for tool in all_mcp_tools if "time" in tool.name.lower()]
        
        print(f"Using {len(time_tools)} time-related MCP tools:")
        for tool in time_tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # You could now use these tools with an agent
        # agent = Single_Agent(..., tools=time_tools)
        
    except Exception as e:
        print(f"Error: {e}")


def example_mcp_tool_inspection():
    """Example of inspecting MCP tool capabilities."""
    
    try:
        mcp_manager = MCPManager()
        mcp_tools = mcp_manager.init_config(MCP_CONFIG)
        
        print("MCP Tool Details:")
        print("=" * 50)
        
        for tool in mcp_tools:
            print(f"\nTool: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Parameters:")
            
            for param in tool.params:
                print(f"  - {param.name} ({param.field_type.value}): {param.description}")
                if not param.required:
                    print(f"    Optional, default: {param.default_value}")
                else:
                    print(f"    Required")
        
    except Exception as e:
        print(f"Error: {e}")


def example_manual_mcp_tool_usage():
    """Example of manually using MCP tools without an agent."""
    
    try:
        mcp_manager = MCPManager()
        mcp_tools = mcp_manager.init_config(MCP_CONFIG)
        
        # Find a specific tool
        time_tool = None
        for tool in mcp_tools:
            if "time" in tool.name and "get" in tool.name.lower():
                time_tool = tool
                break
        
        if time_tool:
            print(f"Using tool: {time_tool.name}")
            
            # Execute the tool manually
            result = time_tool.run()
            
            if result.success:
                print(f"Tool result: {result.result}")
            else:
                print(f"Tool failed: {result.error_message}")
        else:
            print("No suitable time tool found")
            
    except Exception as e:
        print(f"Error: {e}")


def example_mcp_error_handling():
    """Example of proper error handling with MCP."""
    
    from unisonai.tools import MCPConnectionError, MCPConfigurationError
    
    # Example of invalid configuration
    invalid_config = {
        "mcpServers": {
            "nonexistent": {
                "command": "this-command-does-not-exist",
                "args": ["arg1", "arg2"]
            }
        }
    }
    
    try:
        mcp_manager = MCPManager()
        mcp_tools = mcp_manager.init_config(invalid_config)
        print(f"Loaded {len(mcp_tools)} tools")
        
    except MCPConnectionError as e:
        print(f"MCP Connection Error: {e}")
        print("This is expected for this example with invalid config")
        
    except MCPConfigurationError as e:
        print(f"MCP Configuration Error: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("UnisonAI MCP Integration Examples")
    print("=" * 40)
    
    print("\n1. Basic MCP with Single Agent")
    example_mcp_with_single_agent()
    
    print("\n2. Selective MCP Tools")
    example_mcp_selective_tools()
    
    print("\n3. MCP Tool Inspection") 
    example_mcp_tool_inspection()
    
    print("\n4. Manual MCP Tool Usage")
    example_manual_mcp_tool_usage()
    
    print("\n5. MCP Error Handling")
    example_mcp_error_handling()
    
    print("\nExamples completed!")