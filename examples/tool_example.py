"""
Tool Example — UnisonAI

Two ways to create tools:
1. @tool decorator — best for simple, stateless functions
2. BaseTool class — best for tools with state or complex logic
"""

from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.tool import BaseTool, Field, tool
from unisonai.tools.types import ToolParameterType


# ── Method 1: @tool decorator (recommended for most cases) ──────────────

@tool(name="calculator", description="Perform arithmetic on two numbers")
def calculator(operation: str, a: float, b: float) -> str:
    """Supports add, subtract, multiply, divide."""
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: division by zero",
    }
    return str(ops.get(operation, f"Unknown operation: {operation}"))


@tool(name="word_count", description="Count words in a text string")
def word_count(text: str) -> str:
    """Returns the word count of the given text."""
    return str(len(text.split()))


# ── Method 2: BaseTool class (for stateful / complex tools) ─────────────

class UnitConverter(BaseTool):
    """Convert between common measurement units."""

    def __init__(self):
        self.name = "unit_converter"
        self.description = "Convert a value between measurement units"
        self.params = [
            Field(name="value", description="Numeric value to convert",
                  field_type=ToolParameterType.FLOAT, required=True),
            Field(name="from_unit", description="Source unit (e.g. km, miles, kg, lbs, C, F)",
                  field_type=ToolParameterType.STRING, required=True),
            Field(name="to_unit", description="Target unit",
                  field_type=ToolParameterType.STRING, required=True),
        ]
        super().__init__()

    def _run(self, value: float, from_unit: str, to_unit: str) -> str:
        conversions = {
            ("km", "miles"): lambda v: v * 0.621371,
            ("miles", "km"): lambda v: v * 1.60934,
            ("kg", "lbs"): lambda v: v * 2.20462,
            ("lbs", "kg"): lambda v: v * 0.453592,
            ("C", "F"): lambda v: v * 9 / 5 + 32,
            ("F", "C"): lambda v: (v - 32) * 5 / 9,
        }
        fn = conversions.get((from_unit, to_unit))
        if fn is None:
            return f"Unsupported conversion: {from_unit} -> {to_unit}"
        return f"{value} {from_unit} = {round(fn(value), 2)} {to_unit}"


# ── Use with an Agent ───────────────────────────────────────────────────

if __name__ == "__main__":
    agent = Agent(
        llm=Gemini(model="gemini-2.5-flash"),
        identity="Utility Assistant",
        description="An assistant with calculator and unit conversion tools",
        tools=[calculator(), UnitConverter()],
        verbose=True,
    )

    result = agent.unleash(
        task="What is 25 * 48? Also convert 100 km to miles."
    )
    print(result)
