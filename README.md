
<div align="center">
  <img src="https://github.com/UnisonaiOrg/UnisonAI/blob/main/assets/UnisonAI.jpg" alt="UnisonAI Banner" width="90%"/>
</div>

# Table of Contents

- [Overview](#overview)
- [Why UnisonAI?](#what-makes-unisonai-special)
- [Installation](#quick-start)
- [Core Components](#core-components)
- [API Keys](#api-key-configuration)
- [Parameter Reference Tables](#documentation-hub)
- [Usage Examples](#usage-examples)
- [FAQ](#faq)
- [Contributing And License](#contributing)


<div align="center">
  <h1>UnisonAI</h1>
  <p><em>Orchestrate the Future of Multi-Agent AI</em></p>
</div>

<p align="center">
  <a href="https://github.com/UnisonaiOrg/UnisonAI/stargazers"><img src="https://img.shields.io/github/stars/UnisonaiOrg/UnisonAI" alt="Stars"/></a>
  <a href="https://github.com/UnisonaiOrg/UnisonAI/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License"/></a>
  <img src="https://img.shields.io/badge/Python-%3E=3.10,%3C3.13-blue?style=flat-square" alt="Python Version"/>
</p>

---

## Overview

UnisonAI is a lightweight Python framework for building single-agent and multi-agent AI systems.

- **Agent** — standalone or part of a clan, with tool integration and conversation history.
- **Clan** — coordinate multiple agents on a shared goal with built-in A2A messaging.
- **Tool System** — create tools with `@tool` decorator or `BaseTool` class; type-validated, standardized results.

Supports **Gemini, OpenAI, Anthropic, Cohere, Groq, Mixtral, xAI, Cerebras**, and any custom model (extend `BaseLLM`).

---

## Quick Start

```bash
pip install unisonai-sdk
```

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

---

## What Makes UnisonAI Special

**Agent-to-Agent (A2A) communication** — agents talk to each other as if they were teammates collaborating on complex tasks.

<div>
  <img src="https://github.com/UnisonaiOrg/UnisonAI/blob/main/assets/Example.jpg" alt="Example" width="60%"/>
</div>

### Perfect For

- **Complex Research** — multiple agents gathering, analyzing, and synthesizing information
- **Workflow Automation** — coordinated agents handling multi-step processes
- **Content Creation** — specialized agents for research, writing, and editing
- **Data Analysis** — distributed agents processing data with different expertise

---

## Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Agent** | Standalone or clan member | Tool integration, history, inter-agent messaging |
| **Clan** | Multi-agent orchestration | Automatic planning, task distribution, A2A communication |
| **Tool System** | Extensible capabilities | `@tool` decorator, `BaseTool` class, type validation |

---

## Usage Examples

### Individual Agent

```python
from unisonai import Agent
from unisonai.llms import Gemini

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Assistant",
    description="An AI assistant for research tasks",
)

agent.unleash(task="Summarize the key benefits of renewable energy")
```

### Agent with Tools

```python
from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.tool import tool

@tool(name="calculator", description="Arithmetic on two numbers")
def calculator(operation: str, a: float, b: float) -> str:
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b else "err"}
    return str(ops.get(operation, "unknown op"))

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Math Helper",
    description="An assistant with a calculator tool",
    tools=[calculator()],
)

agent.unleash(task="What is 1500 * 32?")
```

### Multi-Agent Clan

```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini

researcher = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Researcher",
    description="Gathers information on topics",
    task="Research assigned topics",
)

writer = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Writer",
    description="Writes clear reports from research",
    task="Write polished reports",
)

clan = Clan(
    clan_name="Research Team",
    manager=researcher,
    members=[researcher, writer],
    shared_instruction="Researcher gathers info, Writer produces the report.",
    goal="Write a brief report on AI in healthcare",
    output_file="report.txt",
)

clan.unleash()
```

### Custom Tools

UnisonAI supports two ways to create tools:

#### 1. Decorator-based (Recommended)

```python
from unisonai.tools.tool import tool

@tool(name="calculator", description="Math operations")
def calculator(operation: str, a: float, b: float) -> str:
    if operation == "add":
        return str(a + b)
    elif operation == "multiply":
        return str(a * b)
    return "Unknown operation"
```

#### 2. Class-based (For complex/stateful tools)

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class Calculator(BaseTool):
    def __init__(self):
        self.name = "calculator"
        self.description = "Math operations"
        self.params = [
            Field(name="operation", description="add or multiply",
                  field_type=ToolParameterType.STRING, required=True),
            Field(name="a", description="First number",
                  field_type=ToolParameterType.FLOAT, required=True),
            Field(name="b", description="Second number",
                  field_type=ToolParameterType.FLOAT, required=True),
        ]
        super().__init__()

    def _run(self, operation: str, a: float, b: float) -> float:
        return a + b if operation == "add" else a * b
```

---

## API Key Configuration

1. **Environment Variables**:
   ```bash
   export GEMINI_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   ```

2. **Direct Initialization**:
   ```python
   llm = Gemini(api_key="your-key")
   ```

---

## Documentation Hub

### Getting Started
- **[Quick Start Guide](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/quick-start.md)** — 5-minute setup
- **[Installation](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/README.md#installation)** — Detailed options

### Core Documentation
- **[API Reference](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/api-reference.md)** — Complete API docs
- **[Architecture Guide](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/architecture.md)** — System design
- **[Usage Guidelines](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/usage-guide.md)** — Best practices

### Advanced Features
- **[Tool System Guide](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/tools-guide.md)** — Custom tool creation

### Examples
- **[Basic Agent](https://github.com/UnisonaiOrg/UnisonAI/blob/main/examples/basic_agent.py)** — Minimal agent
- **[Tool Example](https://github.com/UnisonaiOrg/UnisonAI/blob/main/examples/tool_example.py)** — `@tool` decorator & `BaseTool`
- **[Clan Example](https://github.com/UnisonaiOrg/UnisonAI/blob/main/examples/clan-agent_example.py)** — Multi-agent coordination

---

## FAQ

<details>
<summary><b>What is UnisonAI?</b></summary>
Python framework for building and orchestrating AI agents with A2A communication.
</details>

<details>
<summary><b>When should I use a Clan?</b></summary>
For complex, multi-step tasks requiring specialized agents working together.
</details>

<details>
<summary><b>Can I add custom LLMs?</b></summary>
Yes! Extend <code>BaseLLM</code> to integrate any model provider.
</details>

<details>
<summary><b>What are tools?</b></summary>
Reusable components that extend agent capabilities. Create them with the <code>@tool</code> decorator or the <code>BaseTool</code> class.
</details>

<details>
<summary><b>How do I manage API keys?</b></summary>
Use environment variables or pass directly to the LLM constructor.
</details>

---

## Contributing

Author: [Anant Sharma (E5Anant)](https://github.com/E5Anant)

PRs and issues welcome!

<a href="https://github.com/UnisonaiOrg/UnisonAI/issues">Open Issues</a> •
<a href="https://github.com/UnisonaiOrg/UnisonAI/pulls">Submit PRs</a> •
<a href="https://github.com/UnisonaiOrg/UnisonAI">Suggest Features</a>

---


