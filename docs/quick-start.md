# Quick Start Guide

Get running with UnisonAI in under 5 minutes.

## Installation

```bash
pip install unisonai
```

Set your API key:

```bash
export GEMINI_API_KEY="your-key"
```

Or pass it directly: `Gemini(api_key="your-key")`

---

## 1. Single Agent (2 minutes)

```python
from unisonai import Agent
from unisonai.llms import Gemini

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Assistant",
    description="A helpful AI assistant",
)

result = agent.unleash(task="Explain photosynthesis in 3 sentences")
print(result)
```

---

## 2. Agent with Tools (3 minutes)

Use the `@tool` decorator for quick tool creation:

```python
from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.tool import tool

@tool(name="calculator", description="Arithmetic on two numbers")
def calculator(operation: str, a: float, b: float) -> str:
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b}
    return str(ops.get(operation, "unknown"))

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Math Helper",
    description="An assistant with a calculator",
    tools=[calculator()],
)

result = agent.unleash(task="What is 25 * 48?")
print(result)
```

---

## 3. Multi-Agent Clan (5 minutes)

Multiple agents collaborate on a shared goal:

```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini

researcher = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Researcher",
    description="Gathers information",
    task="Research assigned topics",
)

writer = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Writer",
    description="Writes reports from research",
    task="Write a polished report",
)

clan = Clan(
    clan_name="Research Team",
    manager=researcher,
    members=[researcher, writer],
    shared_instruction="Researcher gathers info, Writer produces the report.",
    goal="Write a brief report on AI in education",
    output_file="report.txt",
)

clan.unleash()
```

---

## What Happens Under the Hood

1. **Clan planning** — the manager LLM creates a step-by-step plan.
2. **Task distribution** — the plan is shared with all agents.
3. **Execution** — the manager delegates tasks via `send_message()`.
4. **Final delivery** — the manager calls `pass_result()` to return the output.

---

## Next Steps

- [Tool System Guide](tools-guide.md) — create custom tools
- [Usage Guide](usage-guide.md) — best practices
- [API Reference](api-reference.md) — full parameter docs
- [Examples](../examples/) — runnable code samples
