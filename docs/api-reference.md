# API Reference

## Agent

### Constructor

```python
Agent(
    llm: BaseLLM,          # LLM provider instance (required)
    identity: str,          # Agent name (required)
    description: str,       # Agent purpose (required)
    task: str = "",         # Default task (used in clan mode)
    verbose: bool = True,   # Print thinking/tool/response output
    tools: list = [],       # List of tool instances
    output_file: str = None,      # Save final result to file
    history_folder: str = ".",    # Conversation history directory
)
```

### Methods

#### `unleash(task: str) -> str`

Execute a task. Returns the final answer as a string.

```python
result = agent.unleash(task="Explain quantum computing")
```

---

## Clan

### Constructor

```python
Clan(
    clan_name: str,              # Team name (required)
    manager: Agent,              # Coordinating agent (required)
    members: list[Agent],        # All agents including manager (required)
    shared_instruction: str,     # Instructions for all agents (required)
    goal: str,                   # The task to accomplish (required)
    history_folder: str = "history",  # History directory
    output_file: str = None,          # Save final result to file
)
```

### Methods

#### `unleash()`

Plan the work and hand execution to the manager.

```python
clan.unleash()
```

### Built-in Functions (available inside clans)

| Function | Available To | Description |
|----------|-------------|-------------|
| `send_message(agent_name, message)` | All agents | Send a task to another agent |
| `ask_user(question)` | Manager only | Ask user a clarifying question |

---

## Tool System

### `@tool` Decorator

```python
from unisonai.tools.tool import tool

@tool(name="my_tool", description="What it does")
def my_tool(param: str) -> str:
    return f"Result: {param}"

# Instantiate for use with Agent
agent = Agent(..., tools=[my_tool()])
```

### `BaseTool` Class

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class MyTool(BaseTool):
    def __init__(self):
        self.name = "my_tool"
        self.description = "What it does"
        self.params = [
            Field(name="param", description="A parameter",
                  field_type=ToolParameterType.STRING, required=True),
        ]
        super().__init__()

    def _run(self, param: str) -> str:
        return f"Result: {param}"
```

### Field

```python
Field(
    name: str,                    # Parameter name
    description: str,             # Description
    field_type: ToolParameterType = STRING,  # Type
    required: bool = True,        # Required?
    default_value: Any = None,    # Default value
)
```

### ToolParameterType

| Value | Python Type |
|-------|-------------|
| `STRING` | str |
| `INTEGER` | int |
| `FLOAT` | float |
| `BOOLEAN` | bool |
| `LIST` | list |
| `DICT` | dict |
| `ANY` | any |

### ToolResult

Returned by `tool_instance.run()`:

| Property | Type | Description |
|----------|------|-------------|
| `success` | bool | Whether execution succeeded |
| `result` | Any | Return value |
| `error_message` | str | Error message if failed |
| `metadata` | dict | Execution metadata |

---

## LLM Providers

### Available Providers

| Class | Module | Env Variable |
|-------|--------|-------------|
| `Gemini` | `unisonai.llms` | `GEMINI_API_KEY` |
| `Openai` | `unisonai.llms` | `OPENAI_API_KEY` |
| `Anthropic` | `unisonai.llms` | `ANTHROPIC_API_KEY` |
| `Cohere` | `unisonai.llms` | `COHERE_API_KEY` |
| `GroqLLM` | `unisonai.llms` | `GROQ_API_KEY` |
| `Mixtral` | `unisonai.llms` | `MIXTRAL_API_KEY` |
| `XAILLM` | `unisonai.llms` | `XAI_API_KEY` |
| `CerebrasLLM` | `unisonai.llms` | `CEREBRAS_API_KEY` |

### Common LLM Parameters

```python
llm = Gemini(
    model="gemini-2.5-flash",   # Model name
    temperature=0.0,             # Creativity (0.0–1.0)
    max_tokens=2048,             # Max response length
    api_key="your-key",          # API key (or use env var)
)
```

### Custom LLM

```python
from unisonai.llms.Basellm import BaseLLM

class MyLLM(BaseLLM):
    def run(self, prompt: str, save_messages: bool = True) -> str:
        # Your API call here
        ...

    def reset(self):
        self.messages = []
```
