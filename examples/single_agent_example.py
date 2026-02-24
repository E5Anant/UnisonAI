"""
Single Agent with Tools — UnisonAI

Shows an agent using class-based tools to answer a multi-part question.
"""

import datetime
from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.tool import BaseTool, Field, tool
from unisonai.tools.types import ToolParameterType


@tool(name="current_time", description="Get the current date and time")
def current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current date/time in the given format."""
    return datetime.datetime.now().strftime(format)


@tool(name="calculator", description="Basic arithmetic on two numbers")
def calculator(operation: str, a: float, b: float) -> str:
    """Operations: add, subtract, multiply, divide."""
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: division by zero",
    }
    return str(ops.get(operation, f"Unknown: {operation}"))


agent = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Assistant",
    description="A helpful assistant with time and math tools",
    tools=[current_time(), calculator()],
    verbose=True,
)

result = agent.unleash(
    task="What time is it right now? Also, how much is 1000 shares at $150 each?"
)
print(result)
