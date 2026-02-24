# Usage Guide

## Prerequisites

- Python 3.10–3.12
- API key for your LLM provider
- `pip install unisonai-sdk`

---

## API Keys

**Option 1 — Environment variable** (recommended):

```bash
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

**Option 2 — Direct**:

```python
from unisonai.llms import Gemini
llm = Gemini(api_key="your-key")
```

---

## Creating Agents

### Minimal Agent

```python
from unisonai import Agent
from unisonai.llms import Gemini

agent = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Assistant",
    description="A helpful AI assistant",
)

result = agent.unleash(task="Explain machine learning briefly")
print(result)
```

### Agent with Tools

```python
from unisonai.tools.tool import tool

@tool(name="calculator", description="Basic math")
def calculator(operation: str, a: float, b: float) -> str:
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b}
    return str(ops.get(operation, "unknown"))

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Math Agent",
    description="An agent with a calculator",
    tools=[calculator()],
    verbose=True,
)

agent.unleash(task="What is 100 * 52?")
```

### Agent Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | BaseLLM | required | LLM provider instance |
| `identity` | str | required | Agent name |
| `description` | str | required | Agent's purpose |
| `task` | str | `""` | Default task (used in clan mode) |
| `verbose` | bool | `True` | Show thinking, tools, and answers |
| `tools` | list | `[]` | Tool instances |
| `output_file` | str | `None` | Save final output to file |
| `history_folder` | str | `"."` | Conversation history directory |

---

## Creating Clans

A Clan coordinates multiple agents on a shared goal.

```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini

researcher = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Researcher",
    description="Gathers info",
    task="Research assigned topics",
)

analyst = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Analyst",
    description="Analyzes data",
    task="Analyze findings",
)

clan = Clan(
    clan_name="Analysis Team",
    manager=researcher,
    members=[researcher, analyst],
    shared_instruction="Researcher gathers info, Analyst interprets it.",
    goal="Analyze the current state of renewable energy",
    output_file="analysis.txt",
)

clan.unleash()
```

### How Clans Work

1. **Planning** — the manager LLM generates a step-by-step plan
2. **Distribution** — the plan is shared with all agents
3. **Execution** — the manager delegates via `send_message(agent_name, message)`
4. **Completion** — the manager replies directly with the final output

### Built-in Clan Functions

These are automatically available to agents inside a Clan:

| Function | Description |
|----------|-------------|
| `send_message(agent_name, message)` | Send a task to another agent |
| `ask_user(question)` | Ask the user a clarifying question (manager only) |

---

## Supported LLM Providers

```python
from unisonai.llms import Gemini, Openai, Anthropic, Cohere, GroqLLM, Mixtral, XAILLM, CerebrasLLM
```

| Provider | Class | Env Variable |
|----------|-------|-------------|
| Google Gemini | `Gemini` | `GEMINI_API_KEY` |
| OpenAI | `Openai` | `OPENAI_API_KEY` |
| Anthropic | `Anthropic` | `ANTHROPIC_API_KEY` |
| Cohere | `Cohere` | `COHERE_API_KEY` |
| Groq | `GroqLLM` | `GROQ_API_KEY` |
| Mixtral | `Mixtral` | `MIXTRAL_API_KEY` |
| xAI | `XAILLM` | `XAI_API_KEY` |
| Cerebras | `CerebrasLLM` | `CEREBRAS_API_KEY` |

### Custom LLM

Extend `BaseLLM` from `unisonai.llms.Basellm`:

```python
from unisonai.llms.Basellm import BaseLLM

class MyLLM(BaseLLM):
    def run(self, prompt: str, save_messages: bool = True) -> str:
        # Call your API here
        ...

    def reset(self):
        self.messages = []
```

---

## Error Handling

```python
try:
    result = agent.unleash(task="Some task")
except Exception as e:
    print(f"Agent failed: {e}")
```

Tool errors are caught automatically and fed back to the LLM for retry.

---

## Best Practices

1. **Keep tools simple** — one tool, one purpose
2. **Use `@tool` decorator** for stateless functions
3. **Use `BaseTool` class** when you need state or complex validation
4. **Set `verbose=True`** during development to see agent reasoning
5. **Give agents clear descriptions** — the LLM uses them to understand capabilities
6. **In clans, keep shared instructions concise** — short, numbered steps work best

