

<div align="center">
Fork of the OG REPO [UnisonAI](https://github.com/UnisonAI/UnisonAI/)

<img src="https://github.com/UnisonAIInc/UnisonAI/blob/main/assets/UnisonAI_Banner.jpg" alt="UnisonAI Banner" width="100%"/>

</div>

UnisonAI is a flexible and extensible Python framework built on agent to agent (a2a) for building, coordinating,
and scaling multiple AI agents—each powered by the LLM of your choice,
unisonai helps in making individual agents on focused tasks as well as clan-based agent for extensive and complex tasks.

[![GitHub Repo stars](https://img.shields.io/github/stars/UnisonAIInc/UnisonAI)](https://github.com/UnisonAIInc/UnisonAI)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/apache-2-0)

# Table of Content:

- [Overview](#overview)
- [Why UnisonAI?](#why-unisonai)
- [Installation](#installation)
- [Core Components](#core-components)
- [Parameter Reference Tables](#parameter-reference-tables)
- [Usage Examples](#usage-examples)
- [Faq?](#faq)
- [Contributing And License](#contributing-and-license)

## New Features!!!
- **Enhanced Tool System**: Strong type validation with `ToolParameterType` enum, automatic parameter validation, standardized `ToolResult` responses, and comprehensive error handling
- **Type Safety**: All tool parameters are validated against defined types before execution
- **Rich Tool Schemas**: Tools provide detailed schemas for documentation and introspection  
- **Improved Error Handling**: Detailed error messages with metadata for better debugging
- Async Tool Functionality added.

## Overview

UnisonAI is a flexible and extensible Python framework for building, coordinating, and scaling multiple AI agents—each powered by the LLM of your choice.

- **Single_Agent:** For solo, focused tasks.
- **Agent (as part of a Clan):** For teamwork, coordination, and distributed problem-solving.
- **Tool System:** Easily augment agents with custom, pluggable tools (web search, time, APIs, your own logic).

Supports Cohere, Mixtral, Groq, Gemini, Grok, OpenAI, Anthropic, HelpingAI, and any custom model (just extend `BaseLLM`). UnisonAI is designed for real-world, production-grade multi-agent AI applications.

---

## Uses A2A (Agent to Agent) Communication!

<img src="https://github.com/UnisonAIInc/UnisonAI/blob/main/assets/Example.jpg" alt="Example" width="80%"/>

<div><div></div></div>

---

## Why UnisonAI?

<div align="center">

<table>
  <tr>
    <td>🔗 <b>Multi-LLM Support</b><br>Mix and match LLM providers with ease.</td>
    <td>🧩 <b>Modular & Extensible</b><br>Add your own tools, LLMs, and logic.</td>
    <td>🤖 <b>Single or Multi-Agent</b><br>Solo agents or collaborative Clans—your call. With Agent to Agent communication on your supervision</td>
  </tr>
  <tr>
    <td>🛡️ <b>Robust Error Handling</b><br>Built-in JSON/YAML repair & retries.</td>
    <td>📚 <b>Clear Docs & Examples</b><br>Well-documented APIs and quick starts.</td>
    <td>⚡ <b>Production-Ready</b><br>Designed for real-world automation & chatbots.</td>
  </tr>
</table>
</div>

<div align="center">

<img src="https://img.shields.io/badge/Python-%3E=3.10,%3C3.13-blue?style=flat-square" alt="Python Version"/>
<img src="https://img.shields.io/badge/LLM%20Support-Mixtral%2C%20Grok%2C%20Gemini%2C%20OpenAI%2C%20Cohere%2C%20HelpingAI%20%26%20more-orange?style=flat-square" alt="LLM Support"/>
<img src="https://img.shields.io/badge/architecture-Single%20Agent%20%2F%20Clan%20(Multi--Agent)%20A2A%20(Agent%20to%20Agent)-purple?style=flat-square" alt="Architecture"/>
</div>

---

## Installation

> **Requires Python >=3.10, <3.13**

```bash
pip install unisonai
# or
pip3 install unisonai
```

---

## Core Components

<div align="center">

<table>
  <tr>
    <th align="center">Component</th>
    <th align="center">Purpose</th>
    <th align="center">Highlights</th>
  </tr>
  <tr>
    <td><b>Single_Agent</b></td>
    <td>Standalone agent for independent tasks</td>
    <td>
      <ul>
        <li>Own log/history</li>
        <li>Plug in any LLM/tools</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><b>Agent</b></td>
    <td>Works with others in a Clan (team)</td>
    <td>
      <ul>
        <li>Inter-agent messaging</li>
        <li>Tools & role-based prompts</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><b>Clan</b></td>
    <td>Manages a team of Agents (including a leader/manager)</td>
    <td>
      <ul>
        <li>Coordinated planning</li>
        <li>Shared instructions/goals</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><b>Enhanced Tool System</b></td>
    <td>Extend agent capabilities with strongly-typed, validated tools</td>
    <td>
      <ul>
        <li>Type validation with ToolParameterType</li>
        <li>Automatic parameter validation</li>
        <li>Standardized ToolResult responses</li>
        <li>Rich error handling & schemas</li>
      </ul>
    </td>
  </tr>
</table>
</div>

---

## Parameter Reference Tables

### Single_Agent

| Parameter        | Type            | Description                | Default      |
| ---------------- | --------------- | -------------------------- | ------------ |
| `llm`            | BaseLLM/any LLM | LLM for the agent          | **Required** |
| `identity`       | String          | Agent's unique name        | **Required** |
| `description`    | String          | Agent's purpose            | **Required** |
| `verbose`        | Boolean         | Verbose/debug mode         | True         |
| `tools`          | List            | Usable tools               | []           |
| `output_file`    | String          | Output file path           | None         |
| `history_folder` | String          | Directory for logs/history | "history"    |

### Agent

| Parameter     | Type           | Description               | Default      |
| ------------- | -------------- | ------------------------- | ------------ |
| `llm`         | Gemini/any LLM | LLM for the agent         | **Required** |
| `identity`    | String         | Agent's unique name       | **Required** |
| `description` | String         | Responsibilities overview | **Required** |
| `task`        | String         | Agent's core goal/task    | **Required** |
| `verbose`     | Boolean        | Verbose/debug mode        | True         |
| `tools`       | List           | Usable tools              | []           |

### Clan

| Parameter            | Type   | Description                 | Default      |
| -------------------- | ------ | --------------------------- | ------------ |
| `clan_name`          | String | Name of the clan            | **Required** |
| `manager`            | Agent  | Clan manager/leader         | **Required** |
| `members`            | List   | List of Agent instances     | **Required** |
| `shared_instruction` | String | Instructions for all agents | **Required** |
| `goal`               | String | Unified clan objective      | **Required** |
| `history_folder`     | String | Log/history folder          | "history"    |
| `output_file`        | String | Final output file           | None         |

### Tool System

**BaseTool**

| Attribute/Method                 | Description                                          |
| -------------------------------- | ---------------------------------------------------- |
| `name`                           | Tool name (auto-generated from class name)          |
| `description`                    | Tool function summary                                |
| `params`                         | List of Field objects with type validation          |
| `_run(**kwargs)`                 | Tool logic implementation (abstract method)         |
| `run(**kwargs)`                  | Execute tool with validation & error handling       |
| `validate_parameters(kwargs)`    | Validate input parameters against field definitions |
| `get_schema()`                   | Get tool schema for documentation                   |

**Field**

| Attribute       | Description                        | Default                    |
| --------------- | ---------------------------------- | -------------------------- |
| `name`          | Parameter name                     | **Required**               |
| `description`   | Parameter purpose                  | **Required**               |
| `field_type`    | Parameter type (ToolParameterType) | ToolParameterType.STRING   |
| `default_value` | Default value                      | None                       |
| `required`      | Is parameter mandatory?            | True                       |

**ToolParameterType (Enum)**

| Type      | Description                    |
| --------- | ------------------------------ |
| `STRING`  | String/text values             |
| `INTEGER` | Integer numbers                |
| `FLOAT`   | Floating point numbers         |
| `BOOLEAN` | True/False values              |
| `LIST`    | List/array values              |
| `DICT`    | Dictionary/object values       |
| `ANY`     | Any type (fallback)            |

---

## Usage Examples

### Tool Creation

Create custom tools with strong typing and validation:

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
import datetime

class TimeTool(BaseTool):
    """Enhanced time tool with proper field validation."""
    
    def __init__(self):
        self.name = "time_tool"
        self.description = "Get current date and time in specified format with timezone support."
        self.params = [
            Field(
                name="format",
                description="DateTime format string (e.g., '%Y-%m-%d %H:%M:%S')",
                field_type=ToolParameterType.STRING,
                default_value="%Y-%m-%d %H:%M:%S",
                required=False
            ),
            Field(
                name="include_timezone",
                description="Whether to include timezone information",
                field_type=ToolParameterType.BOOLEAN,
                default_value=False,
                required=False
            )
        ]
        super().__init__()
    
    def _run(self, format: str = "%Y-%m-%d %H:%M:%S", include_timezone: bool = False) -> str:
        """Get current time with optional timezone."""
        current_time = datetime.datetime.now()
        
        if include_timezone:
            # Add timezone info if requested
            import time
            timezone = time.tzname[0]
            return f"{current_time.strftime(format)} {timezone}"
        
        return current_time.strftime(format)

class CalculatorTool(BaseTool):
    """Mathematical calculator with type validation."""
    
    def __init__(self):
        self.name = "calculator"
        self.description = "Perform basic mathematical operations on two numbers."
        self.params = [
            Field(
                name="operation",
                description="Math operation: add, subtract, multiply, divide",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="number1",
                description="First number for the operation",
                field_type=ToolParameterType.FLOAT,
                required=True
            ),
            Field(
                name="number2", 
                description="Second number for the operation",
                field_type=ToolParameterType.FLOAT,
                required=True
            )
        ]
        super().__init__()
    
    def _run(self, operation: str, number1: float, number2: float) -> float:
        """Execute mathematical operation."""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
        }
        
        if operation not in operations:
            raise ValueError(f"Unsupported operation: {operation}")
        
        return operations[operation](number1, number2)
```

### Standalone Agent

This is the enhanced code from [`main.py`](https://github.com/UnisonAIInc/UnisonAI/blob/main/main.py) FILE.

```python
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool
from unisonai import config

# Configure API key
config.set_api_key("gemini", "Your API Key")

# Create agent with enhanced tools
web_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Web Explorer",
    description="Advanced web searcher with calculation and time capabilities",
    tools=[WebSearchTool, TimeTool, CalculatorTool],
    history_folder="history",
    output_file="output.txt"
)

# The agent can now use tools with proper validation
web_agent.unleash(task="Find current Apple stock price and calculate the percentage change from last week")
```

---

### Clan-Based Agents

**"This is an enhanced reference from [`main2.py`](https://github.com/UnisonAIInc/UnisonAI/blob/main/main2.py) FILE, check the file for the full complex example."**

```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from unisonai import config

# Configure API key
config.set_api_key("gemini", "Your API Key")

class BudgetTrackerTool(BaseTool):
    """budget tracking with type validation."""
    
    def __init__(self):
        self.name = "budget_tracker"
        self.description = "Track expenses and manage trip budget with detailed reporting."
        self.params = [
            Field(
                name="action",
                description="Action to perform: 'initialize', 'add_expense', 'get_balance'",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="amount",
                description="Amount in INR (required for initialize/add_expense)",
                field_type=ToolParameterType.FLOAT,
                default_value=0.0,
                required=False
            ),
            Field(
                name="category",
                description="Expense category (food, transport, accommodation, activities)",
                field_type=ToolParameterType.STRING,
                default_value="miscellaneous",
                required=False
            ),
            Field(
                name="description",
                description="Detailed description of the expense",
                field_type=ToolParameterType.STRING,
                default_value="",
                required=False
            )
        ]
        self.total_budget = 0
        self.expenses = []
        super().__init__()
    
    def _run(self, action: str, amount: float = 0.0, category: str = "miscellaneous", description: str = "") -> str:
        """Execute budget management actions."""
        if action == "initialize":
            self.total_budget = amount
            self.expenses = []
            return f"Budget initialized with {amount} INR"
        
        elif action == "add_expense":
            expense = {
                "amount": amount,
                "category": category,
                "description": description
            }
            self.expenses.append(expense)
            spent = sum(exp["amount"] for exp in self.expenses)
            remaining = self.total_budget - spent
            return f"Added expense: {amount} INR for {category}. Remaining budget: {remaining} INR"
        
        elif action == "get_balance":
            spent = sum(exp["amount"] for exp in self.expenses)
            remaining = self.total_budget - spent
            breakdown = {}
            for exp in self.expenses:
                cat = exp["category"]
                breakdown[cat] = breakdown.get(cat, 0) + exp["amount"]
            
            report = f"Budget Report:\nTotal: {self.total_budget} INR\nSpent: {spent} INR\nRemaining: {remaining} INR\n"
            report += "Category Breakdown:\n"
            for cat, amt in breakdown.items():
                report += f"  {cat}: {amt} INR\n"
            return report
        
        else:
            raise ValueError(f"Invalid action: {action}")

# Enhanced agents with strongly typed tools
budget_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Budget Manager",
    description="Advanced budget tracking with detailed expense categorization",
    task="Monitor all trip expenses with category-wise breakdown and alerts",
    tools=[BudgetTrackerTool]
)

research_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Specialist", 
    description="Web research with enhanced search capabilities",
    task="Gather comprehensive travel information with cost analysis",
    tools=[WebSearchTool, CalculatorTool]
)

# Create clan with coordination
clan = Clan(
    clan_name="Trip Planning Clan",
    manager=planner_agent,  # Your enhanced clan leader agent
    members=[budget_agent, research_agent /*, ...other enhanced agents*/],
    shared_instruction="Use the tool system for precise budget tracking, calculations, and research. Ensure all tool parameters are validated and results are accurate.",
    goal="Create a detailed 7-day India trip plan with precise budget tracking and real-time calculations",
    history_folder="trip_history",
    output_file="trip_plan.txt"
)

clan.unleash()
```

### Tool Examples

For comprehensive examples of the tool system, see [`tool_example.py`](https://github.com/UnisonAIInc/UnisonAI/blob/main/tool_example.py) which demonstrates:

- Creating tools with strong type validation
- Parameter validation and error handling  
- Tool schema generation and introspection
- ToolResult object handling
- Advanced data analysis and text processing tools

---

## Tool System Features

UnisonAI's tool system provides robust type validation, error handling, and standardized results:

### Key Features

🔒 **Strong Type Validation**: All tool parameters are validated against defined types using `ToolParameterType` enum
🛡️ **Error Handling**: Comprehensive error catching with detailed error messages and metadata
📊 **Standardized Results**: All tools return `ToolResult` objects with success status, results, and metadata
🔧 **Auto-validation**: Parameters are automatically validated before tool execution
📝 **Rich Schemas**: Tools provide detailed schemas for documentation and introspection

### Tool Parameter Types

```python
from unisonai.tools.types import ToolParameterType

# Supported parameter types:
ToolParameterType.STRING    # Text values
ToolParameterType.INTEGER   # Whole numbers  
ToolParameterType.FLOAT     # Decimal numbers
ToolParameterType.BOOLEAN   # True/False values
ToolParameterType.LIST      # Arrays/lists
ToolParameterType.DICT      # Objects/dictionaries
ToolParameterType.ANY       # Any type (fallback)
```

### Tool Result Handling

```python
# All tools return standardized ToolResult objects
result = tool.run(parameter1="value", parameter2=123)

if result.success:
    print(f"Tool executed successfully: {result.result}")
    print(f"Metadata: {result.metadata}")
else:
    print(f"Tool failed: {result.error_message}")
```

### Advanced Tool Example

```python
class DataAnalysisTool(BaseTool):
    """Advanced data analysis with multiple parameter types."""
    
    def __init__(self):
        self.name = "data_analyzer"
        self.description = "Analyze data with statistical operations"
        self.params = [
            Field(
                name="data",
                description="List of numbers to analyze",
                field_type=ToolParameterType.LIST,
                required=True
            ),
            Field(
                name="operations",
                description="Operations to perform (mean, median, mode, std)",
                field_type=ToolParameterType.LIST,
                default_value=["mean"],
                required=False
            ),
            Field(
                name="precision",
                description="Decimal places for results",
                field_type=ToolParameterType.INTEGER,
                default_value=2,
                required=False
            ),
            Field(
                name="include_metadata",
                description="Include additional statistics",
                field_type=ToolParameterType.BOOLEAN,
                default_value=True,
                required=False
            )
        ]
        super().__init__()
    
    def _run(self, data: list, operations: list = ["mean"], precision: int = 2, include_metadata: bool = True) -> dict:
        """Perform statistical analysis on data."""
        import statistics
        
        results = {}
        
        for op in operations:
            if op == "mean":
                results["mean"] = round(statistics.mean(data), precision)
            elif op == "median":
                results["median"] = round(statistics.median(data), precision)
            elif op == "mode":
                try:
                    results["mode"] = statistics.mode(data)
                except:
                    results["mode"] = "No unique mode"
            elif op == "std":
                results["std_dev"] = round(statistics.stdev(data), precision)
        
        if include_metadata:
            results["metadata"] = {
                "count": len(data),
                "min": min(data),
                "max": max(data),
                "range": max(data) - min(data)
            }
        
        return results
```

## Model Context Protocol (MCP) Integration

UnisonAI now supports [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/specification), allowing agents to connect to external tools and services through standardized MCP servers.

### Quick Start

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

### Configuration Options

#### Stdio-based MCP Servers
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

#### HTTP-based MCP Servers
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

### Available MCP Tools

MCP tools are automatically converted to UnisonAI `BaseTool` instances and can be used with any agent. Each MCP server's tools are prefixed with the server name (e.g., `time-get_current_time`).

### Error Handling

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

---

## API Key Configuration

UnisonAI provides a flexible configuration system for managing API keys. You can set API keys in three ways:

1. Using the configuration system:

```python
from unisonai import config

config.set_api_key("gemini", "your-api-key")
config.set_api_key("openai", "your-api-key")
config.set_api_key("anthropic", "your-api-key")
config.set_api_key("helpingai", "your-api-key")
```

or

2. Setting environment variables:

```bash
export GEMINI_API_KEY="your-api-key"
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
export HAI_API_KEY="your-api-key"
```

or

3. Passing the API key directly when initializing the LLM:

```python
llm = Gemini(model="gemini-2.0-flash", api_key="your-api-key")
# or
llm = HelpingAI(model="Dhanishtha-2.0-preview", api_key="your-api-key")
```

The API keys are stored in a JSON file at `~/.unisonai/config.json` for persistence across sessions.

---

## FAQ?

<details>
  <summary><b>What is UnisonAI?</b></summary>
  <p>A Python framework for orchestrating multiple AI agents—each powered by your choice of LLMs, working solo or in teams. Specifically with A2A communication.</p>
</details>

<details>
  <summary><b>Why use a Clan?</b></summary>
  <p>For complex, multi-step, or specialized tasks: divide and conquer with specialized agents, coordinated by a manager.</p>
</details>

<details>
  <summary><b>Can I add my own LLM?</b></summary>
  <p>Yes! Just extend the <code>BaseLLM</code> class and plug in your model.</p>
</details>

<details>
  <summary><b>What are tools?</b></summary>
  <p>Reusable logic/components, built on <code>BaseTool</code>, that agents can call for specialized tasks (e.g., web search, APIs).</p>
</details>

<details>
  <summary><b>How is agent history logged?</b></summary>
  <p>Each agent maintains its own logs/history in the specified directory (default: <code>history/</code>).</p>
</details>

<details>
  <summary><b>What can I build with UnisonAI?</b></summary>
  <p>Chatbots, collaborative planners, research assistants, workflow automation, and more!</p>
</details>

<details>
  <summary><b>How do I manage API keys?</b></summary>
  <p>You can manage API keys through the configuration system, environment variables, or by passing them directly to the LLM. The configuration system stores keys in <code>~/.unisonai/config.json</code> for persistence.</p>
</details>

<details>
  <summary><b>What's new in the tool system?</b></summary>
  <p>The tool system includes: <strong>Strong type validation</strong> with <code>ToolParameterType</code> enum, <strong>automatic parameter validation</strong> before execution, <strong>standardized results</strong> with <code>ToolResult</code> objects, <strong>comprehensive error handling</strong> with detailed messages, and <strong>rich tool schemas</strong> for documentation and introspection.</p>
</details>

<details>
  <summary><b>How do I create tools with type validation?</b></summary>
  <p>Use the <code>BaseTool</code> class with <code>Field</code> objects that specify <code>field_type</code> from <code>ToolParameterType</code> enum. The system automatically validates parameters against these types before execution and returns standardized <code>ToolResult</code> objects.</p>
</details>

<details>
  <summary><b>What happens if tool parameters are invalid?</b></summary>
  <p>The tool system validates all parameters before execution. If validation fails, it returns a <code>ToolResult</code> object with <code>success=False</code> and a detailed error message explaining what went wrong, without executing the tool logic.</p>
</details>

<details>
  <summary><b>Can I use async tools?</b></summary>
  <p>Yes, the tool system supports asynchronous tools. You can define tools with async methods and they will be executed in an async context.</p>
</details>

<details>
  <summary><b>How Can I use the Model Context Protocol (MCP)?</b></summary>
  <p>UnisonAI supports MCP for connecting to external tools and services. You can configure MCP servers in the <code>mcpServers</code> section of the configuration, and use the <code>MCPManager</code> to initialize tools. This allows agents to leverage external capabilities through standardized MCP servers.</p>
</details>
---

## Contributing and License

<div align="center">

<b>Founding-Contributor:</b> <a href="https://github.com/E5Anant">@E5Anant</a> <br/>
<b>Co-Contributors:</b> <a href="https://github.com/AnonymousCoderArtist">@AnonymousCoderArtist</a>
<a href="https://github.com/OEvortex">@OEvortex</a> <br/>

PRs and issues welcome! The project is under the Apache 2.0 License.

<a href="https://github.com/UnisonAIInc/UnisonAI/issues">Open issues</a> •
<a href="https://github.com/UnisonAIInc/UnisonAI/pulls">Submit PRs</a> •
<a href="https://github.com/UnisonAIInc/UnisonAI">Suggest improvements</a>

<br/><br/>

<p>
  <a href="https://github.com/UnisonAIInc/UnisonAI/stargazers">
    <img src="https://img.shields.io/github/stars/UnisonAIInc/UnisonAI?style=for-the-badge" alt="GitHub Repo stars"/>
  </a>
  <a href="https://github.com/UnisonAIInc/UnisonAI/commits/main">
    <img src="https://img.shields.io/github/last-commit/UnisonAIInc/UnisonAI?style=for-the-badge" alt="GitHub last commit"/>
  </a>
</p>

<a href="https://github.com/UnisonAIInc/UnisonAI/blob/main/LICENSE">
  <img src="https://img.shields.io/github/license/UnisonAIInc/UnisonAI?style=for-the-badge" alt="License: Apache 2.0"/>
</a>

</div>

---

<div align="center">
  <b>UnisonAI: Orchestrate the Future of Multi-Agent AI.</b>
</div>
