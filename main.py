from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from unisonai import config
import datetime

config.set_api_key("gemini", "Your API Key")

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

# Create enhanced agent with multiple tools
web_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Enhanced Assistant",
    description="Advanced assistant with web search, time, and calculation capabilities",
    tools=[WebSearchTool, TimeTool, CalculatorTool],
    verbose=True,
    history_folder="history",
    # output_file="output.txt"
)

web_agent.unleash(task="What's the current time and can you search for the latest Apple stock price, then calculate what 1000 shares would cost?")