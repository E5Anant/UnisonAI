# UnisonAI Documentation

## Overview

UnisonAI is a lightweight Python framework for building single-agent and multi-agent AI systems with A2A (Agent-to-Agent) communication.

### Key Features

- **Multi-LLM Support** — Gemini, OpenAI, Anthropic, Cohere, Groq, Mixtral, xAI, Cerebras, and custom models via `BaseLLM`
- **Tool System** — `@tool` decorator for simple functions, `BaseTool` class for stateful tools, with type validation
- **Agent + Clan** — one Agent class works standalone or as part of a Clan for multi-agent coordination
- **A2A Messaging** — agents send messages to each other, ask the user questions, and pass final results

## Installation

```bash
pip install unisonai
```

**Requirements:** Python 3.10–3.12, API key for your chosen LLM provider.

### API Keys

Set via environment variable or pass directly:

```bash
export GEMINI_API_KEY="your-key"
```

```python
from unisonai.llms import Gemini
llm = Gemini(api_key="your-key")
```

## Quick Example

```python
from unisonai import Agent
from unisonai.llms import Gemini

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Assistant",
    description="A helpful AI assistant",
)

print(agent.unleash(task="Explain quantum computing in 3 sentences"))
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [quick-start.md](quick-start.md) | 5-minute setup guide |
| [api-reference.md](api-reference.md) | Complete API docs |
| [usage-guide.md](usage-guide.md) | Best practices and patterns |
| [tools-guide.md](tools-guide.md) | Custom tool creation |
| [architecture.md](architecture.md) | System design overview |

## Examples

| File | Description |
|------|-------------|
| [basic_agent.py](../examples/basic_agent.py) | Minimal agent |
| [tool_example.py](../examples/tool_example.py) | `@tool` decorator and `BaseTool` |
| [advanced_tools.py](../examples/advanced_tools.py) | Stateful tools with Agent |
| [single_agent_example.py](../examples/single_agent_example.py) | Agent with multiple tools |
| [clan-agent_example.py](../examples/clan-agent_example.py) | Multi-agent clan |
| [clan_coordination.py](../examples/clan_coordination.py) | Research team coordination |

## Parameter Reference

### Agent

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | BaseLLM | **required** | LLM provider instance |
| `identity` | str | **required** | Agent name |
| `description` | str | **required** | Agent purpose |
| `task` | str | `""` | Default task (used in clan mode) |
| `verbose` | bool | `True` | Print thinking/tool/response output |
| `tools` | list | `[]` | List of tool instances |
| `output_file` | str | `None` | Write final result to file |
| `history_folder` | str | `"."` | Directory for conversation history |

### Clan

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clan_name` | str | **required** | Team name |
| `manager` | Agent | **required** | Coordinating agent |
| `members` | list[Agent] | **required** | All agents including manager |
| `shared_instruction` | str | **required** | Instructions for all agents |
| `goal` | str | **required** | The task to accomplish |
| `history_folder` | str | `"history"` | History directory |
| `output_file` | str | `None` | Write final result to file |
