# Tool System Guide

UnisonAI provides two ways to create tools: the `@tool` decorator (recommended) and the `BaseTool` class.

---

## Method 1: `@tool` Decorator

Best for simple, stateless functions. Parameters are inferred from type hints.

```python
from unisonai.tools.tool import tool

@tool(name="calculator", description="Arithmetic on two numbers")
def calculator(operation: str, a: float, b: float) -> str:
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: division by zero",
    }
    return str(ops.get(operation, f"Unknown: {operation}"))
```

### Usage with Agent

```python
from unisonai import Agent
from unisonai.llms import Gemini

agent = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Math Helper",
    description="Calculator assistant",
    tools=[calculator()],   # Note: call it to get an instance
)

agent.unleash(task="What is 25 * 48?")
```

### Multiple Decorator Tools

```python
@tool(name="word_count", description="Count words in text")
def word_count(text: str) -> str:
    return str(len(text.split()))

@tool(name="uppercase", description="Convert text to uppercase")
def uppercase(text: str) -> str:
    return text.upper()

agent = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Text Helper",
    description="Text processing assistant",
    tools=[word_count(), uppercase()],
)
```

---

## Method 2: `BaseTool` Class

Best for tools with state, complex logic, or multiple parameters with validation.

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class UnitConverter(BaseTool):
    def __init__(self):
        self.name = "unit_converter"
        self.description = "Convert between measurement units"
        self.params = [
            Field(name="value", description="Number to convert",
                  field_type=ToolParameterType.FLOAT, required=True),
            Field(name="from_unit", description="Source unit",
                  field_type=ToolParameterType.STRING, required=True),
            Field(name="to_unit", description="Target unit",
                  field_type=ToolParameterType.STRING, required=True),
        ]
        super().__init__()

    def _run(self, value: float, from_unit: str, to_unit: str) -> str:
        conversions = {
            ("km", "miles"): lambda v: v * 0.621371,
            ("miles", "km"): lambda v: v * 1.60934,
            ("C", "F"): lambda v: v * 9/5 + 32,
        }
        fn = conversions.get((from_unit, to_unit))
        if fn is None:
            return f"Unsupported: {from_unit} -> {to_unit}"
        return f"{value} {from_unit} = {round(fn(value), 2)} {to_unit}"
```

### Stateful Tools

Class-based tools can maintain state across calls:

```python
class ExpenseTracker(BaseTool):
    def __init__(self):
        self.name = "expense_tracker"
        self.description = "Track expenses"
        self.params = [
            Field(name="action", description="'add' or 'summary'",
                  field_type=ToolParameterType.STRING, required=True),
            Field(name="amount", description="Expense amount",
                  field_type=ToolParameterType.FLOAT, required=False, default_value=0.0),
            Field(name="category", description="Expense category",
                  field_type=ToolParameterType.STRING, required=False, default_value="general"),
        ]
        self._expenses = []
        super().__init__()

    def _run(self, action: str, amount: float = 0.0, category: str = "general") -> str:
        if action == "add":
            self._expenses.append({"amount": amount, "category": category})
            return f"Added ${amount:.2f} to {category}"
        elif action == "summary":
            total = sum(e["amount"] for e in self._expenses)
            return f"Total: ${total:.2f} across {len(self._expenses)} items"
        return f"Unknown action: {action}"
```

---

## Parameter Types

| Type | ToolParameterType | Python Type |
|------|-------------------|-------------|
| String | `STRING` | `str` |
| Integer | `INTEGER` | `int` |
| Float | `FLOAT` | `float` |
| Boolean | `BOOLEAN` | `bool` |
| List | `LIST` | `list` |
| Dictionary | `DICT` | `dict` |
| Any | `ANY` | any |

---

## Field Definition

```python
Field(
    name="param_name",           # Parameter name
    description="What it does",  # Description for the LLM
    field_type=ToolParameterType.STRING,  # Type
    required=True,               # Required or optional
    default_value=None,          # Default if optional
)
```

---

## ToolResult

All tool `run()` calls return a `ToolResult`:

```python
result = my_tool.run(param="value")

result.success        # bool — did it succeed?
result.result         # Any — the return value
result.error_message  # str — error message if failed
result.metadata       # dict — execution metadata
```

---

## How Tools Work with Agents

1. The agent's system prompt includes tool signatures (generated automatically).
2. The LLM wraps tool calls in `<tool>...</tool>` XML tags.
3. The agent parses the call safely using `ast.parse()` — no `eval()`.
4. Tool results are fed back to the LLM for the next reasoning step.
5. The loop continues until the LLM gives a final answer or reaches max turns.

---

## Tips

- **Always instantiate tools** — pass `calculator()` not `calculator` to the tools list.
- **Return strings** from `_run()` when possible — LLMs handle text best.
- **Use `@tool` for 90% of cases** — it's simpler and less boilerplate.
- **Use `BaseTool` when you need state** (e.g., tracking data across calls).
- **Keep tool names short and descriptive** — the LLM uses them to decide which tool to call.
