"""
Advanced Tools — UnisonAI

Demonstrates class-based tools with state, multiple params, and
how to wire them into an Agent.
"""

from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.tool import BaseTool, Field, tool
from unisonai.tools.types import ToolParameterType
import statistics


# ── Stateful tool: keeps running totals ─────────────────────────────────

class ExpenseTracker(BaseTool):
    """Track expenses across categories."""

    def __init__(self):
        self.name = "expense_tracker"
        self.description = "Add an expense or get a spending summary"
        self.params = [
            Field(name="action", description="'add' or 'summary'",
                  field_type=ToolParameterType.STRING, required=True),
            Field(name="amount", description="Expense amount (for add)",
                  field_type=ToolParameterType.FLOAT, required=False, default_value=0.0),
            Field(name="category", description="Expense category (for add)",
                  field_type=ToolParameterType.STRING, required=False, default_value="general"),
        ]
        self._expenses = []
        super().__init__()

    def _run(self, action: str, amount: float = 0.0, category: str = "general") -> str:
        if action == "add":
            self._expenses.append({"amount": amount, "category": category})
            total = sum(e["amount"] for e in self._expenses)
            return f"Added ${amount:.2f} to {category}. Running total: ${total:.2f}"
        elif action == "summary":
            if not self._expenses:
                return "No expenses recorded."
            by_cat = {}
            for e in self._expenses:
                by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]
            lines = [f"  {cat}: ${amt:.2f}" for cat, amt in sorted(by_cat.items())]
            total = sum(by_cat.values())
            return "Expenses:\n" + "\n".join(lines) + f"\n  Total: ${total:.2f}"
        return f"Unknown action: {action}"


# ── @tool decorator with multiple params ────────────────────────────────

@tool(name="stats", description="Compute statistics for a list of numbers")
def stats(numbers: list, operation: str = "mean") -> str:
    """Operations: mean, median, stdev, min, max, sum."""
    if not numbers:
        return "Empty list"
    ops = {
        "mean": lambda d: statistics.mean(d),
        "median": lambda d: statistics.median(d),
        "stdev": lambda d: statistics.stdev(d) if len(d) > 1 else 0,
        "min": lambda d: min(d),
        "max": lambda d: max(d),
        "sum": lambda d: sum(d),
    }
    fn = ops.get(operation)
    if fn is None:
        return f"Unknown operation: {operation}. Use: {', '.join(ops)}"
    return f"{operation} = {round(fn(numbers), 4)}"


# ── Use with Agent ──────────────────────────────────────────────────────

if __name__ == "__main__":
    tracker = ExpenseTracker()

    agent = Agent(
        llm=Gemini(model="gemini-2.5-flash"),
        identity="Finance Assistant",
        description="Tracks expenses and computes statistics",
        tools=[tracker, stats()],
        verbose=True,
    )

    result = agent.unleash(
        task="Add these expenses: $45 food, $120 travel, $30 food, $200 hotel. "
             "Then show the summary and compute the mean of all amounts."
    )
    print(result)
