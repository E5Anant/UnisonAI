from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, Type
from unisonai.tools.types import ToolParameterType
import json
import logging
import inspect

logger = logging.getLogger(__name__)

@dataclass
class Field:
    """Strongly typed field definition for tool parameters."""
    name: str
    description: str
    default_value: Optional[Any] = None
    required: bool = True
    field_type: ToolParameterType = ToolParameterType.STRING

    def __post_init__(self):
        """Validate field configuration after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Field name must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValueError("Field description must be a non-empty string")
        
        # Validate field_type against ToolParameterType enum values
        valid_types = [e.value for e in ToolParameterType]
        if self.field_type not in valid_types:
            raise ValueError(f"Invalid field_type: {self.field_type}. Valid types: {valid_types}")
    
    def validate_value(self, value: Any) -> bool:
        """Validate if a value matches this field's requirements."""
        if value is None:
            return not self.required
        
        # Updated type mapping to match ToolParameterType enum values
        type_mapping = {
            ToolParameterType.STRING: str,
            ToolParameterType.INTEGER: int,
            ToolParameterType.FLOAT: (int, float),  # Allow int for float fields
            ToolParameterType.BOOLEAN: bool,
            ToolParameterType.LIST: list,
            ToolParameterType.DICT: dict,
            ToolParameterType.ANY: object  # Any type is acceptable
        }
        
        expected_type = type_mapping.get(self.field_type)
        if expected_type and self.field_type != ToolParameterType.ANY:
            if not isinstance(value, expected_type):
                logger.error(f"Field {self.name} expects {self.field_type.value} but got {type(value).__name__}")
                return False
        
        # Additional validation for specific types
        if self.field_type == ToolParameterType.INTEGER and isinstance(value, float):
            # Check if float is actually an integer value
            if not value.is_integer():
                logger.error(f"Field {self.name} expects integer but got float with decimal places: {value}")
                return False
        
        return True

    def format(self) -> str:
        """Format field information for display."""
        return f"""
     {self.name}:
       - description: {self.description}
       - type: {self.field_type.value}
       - default_value: {self.default_value}
       - required: {self.required}
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.field_type.value,  # Use enum value for serialization
            "default_value": self.default_value,
            "required": self.required
        }

@dataclass
class ToolResult:
    """Standardized tool execution result."""
    success: bool
    result: Any
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "result": self.result,
            "error_message": self.error_message,
            "metadata": self.metadata
        }

class BaseTool(ABC):
    """Enhanced base class for all tools with strong typing and validation."""
    
    def __init__(self):
        self.name: str = getattr(self, 'name', self.__class__.__name__)
        self.description: str = getattr(self, 'description', '')
        self.params: List[Field] = getattr(self, 'params', [])
        
        # Validate tool configuration
        self._validate_tool_config()
    
    def _validate_tool_config(self) -> None:
        """Validate tool configuration."""
        if not self.name:
            raise ValueError(f"Tool {self.__class__.__name__} must have a name")
        if not self.description:
            raise ValueError(f"Tool {self.name} must have a description")
        if not isinstance(self.params, list):
            raise ValueError(f"Tool {self.name} params must be a list of Field objects")
        
        for param in self.params:
            if not isinstance(param, Field):
                raise ValueError(f"Tool {self.name} params must contain only Field objects")
    
    def validate_parameters(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Validate input parameters against field definitions."""
        try:
            # Check required parameters
            for param in self.params:
                if param.required and param.name not in kwargs:
                    return ToolResult(
                        success=False,
                        result=None,
                        error_message=f"Missing required parameter: {param.name}"
                    )
                
                # Validate parameter types if present
                if param.name in kwargs:
                    if not param.validate_value(kwargs[param.name]):
                        return ToolResult(
                            success=False,
                            result=None,
                            error_message=f"Invalid type for parameter {param.name}: expected {param.field_type.value}, got {type(kwargs[param.name]).__name__}"
                        )
            
            return ToolResult(success=True, result="Parameters validated successfully")
            
        except Exception as e:
            logger.error(f"Parameter validation error in {self.name}: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error_message=f"Parameter validation error: {str(e)}"
            )
    
    def run(self, **kwargs) -> ToolResult:
        """Execute tool with parameter validation and error handling."""
        try:
            # Validate parameters
            validation_result = self.validate_parameters(kwargs)
            if not validation_result.success:
                return validation_result
            
            # Add default values for missing optional parameters
            for param in self.params:
                if param.name not in kwargs and param.default_value is not None:
                    kwargs[param.name] = param.default_value
            
            # Execute the tool
            result = self._run(**kwargs)
            
            return ToolResult(
                success=True,
                result=result,
                metadata={"tool_name": self.name, "parameters": kwargs}
            )
            
        except Exception as e:
            logger.error(f"Tool execution error in {self.name}: {str(e)}")
            return ToolResult(
                success=False,
                result=None,
                error_message=f"Tool execution error: {str(e)}",
                metadata={"tool_name": self.name, "parameters": kwargs}
            )
    
    @abstractmethod
    def _run(self, **kwargs) -> Any:
        """Abstract method to be implemented by concrete tools."""
        raise NotImplementedError("Please implement the _run method")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for documentation and validation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [param.to_dict() for param in self.params]
        }
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"Tool({self.name}): {self.description}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"BaseTool(name='{self.name}', params={len(self.params)})"
    
def tool(name: str, description: str):
    """
    Decorator to convert a function into a BaseTool.
    
    The function's type hints are used to generate the tool's parameters.
    Supported types map to ToolParameterType:
    - str -> STRING
    - int -> INTEGER
    - float -> FLOAT
    - bool -> BOOLEAN
    - list -> LIST
    - dict -> DICT
    - Any -> ANY
    
    Args:
        name: The name of the tool
        description: A brief description of what the tool does
    """
    def decorator(func: Callable) -> Type[BaseTool]:
        # Map python types to ToolParameterType
        type_mapping = {
            str: ToolParameterType.STRING,
            int: ToolParameterType.INTEGER,
            float: ToolParameterType.FLOAT,
            bool: ToolParameterType.BOOLEAN,
            list: ToolParameterType.LIST,
            dict: ToolParameterType.DICT,
            Any: ToolParameterType.ANY
        }
        
        # Inspect function signature
        sig = inspect.signature(func)
        fields = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            # Determine field type
            annotation = param.annotation
            field_type = type_mapping.get(annotation, ToolParameterType.STRING)
            if annotation == inspect.Parameter.empty:
                field_type = ToolParameterType.STRING
                
            # Determine required/default
            default_value = None
            required = True
            if param.default != inspect.Parameter.empty:
                default_value = param.default
                required = False
                
            fields.append(Field(
                name=param_name,
                description=f"Parameter {param_name}",  # Basic description
                field_type=field_type,
                default_value=default_value,
                required=required
            ))

        # Create a dynamic class that inherits from BaseTool
        class DynamicTool(BaseTool):
            def __init__(self):
                self.name = name
                self.description = description
                self.params = fields
                super().__init__()
            
            def _run(self, **kwargs) -> Any:
                return func(**kwargs)
        
        # Return the class, not an instance (Agent instantiates it)
        return DynamicTool
        
    return decorator

if __name__ == "__main__":
    print("=== Testing BaseTool Implementation ===")
    
    # Example 1: Using Class Inheritance
    class CalculatorTool(BaseTool):
        def __init__(self):
            self.name = "calculator"
            self.description = "Performs basic arithmetic operations"
            self.params = [
                Field(name="operation", description="Operation (add, subtract)", field_type=ToolParameterType.STRING),
                Field(name="a", description="First number", field_type=ToolParameterType.FLOAT),
                Field(name="b", description="Second number", field_type=ToolParameterType.FLOAT)
            ]
            super().__init__()
            
        def _run(self, operation: str, a: float, b: float) -> str:
            if operation == "add":
                return str(a + b)
            elif operation == "subtract":
                return str(a - b)
            return "Invalid operation"

    calc = CalculatorTool()
    print("\n[Class Implementation Test]")
    print(f"Tool Name: {calc.name}")
    print(f"Params: {[p.name for p in calc.params]}")
    result = calc.run(operation="add", a=5.0, b=3.0)
    print(f"Result: {result.result}")
    
    # Example 2: Using Decorator
    print("\n=== Testing Decorator Implementation ===")
    
    @tool(
        name="word_counter",
        description="Counts the number of words in a text"
    )
    def count_words(text: str, case_sensitive: bool = False) -> int:
        if not case_sensitive:
            text = text.lower()
        return len(text.split())
    
    # Decorator returns a class, so we instantiate it
    counter_tool = count_words()
    print("\n[Decorator Implementation Test]")
    print(f"Tool Name: {counter_tool.name}")
    print(f"Generated Params: {[p.name for p in counter_tool.params]}")
    
    # Test execution
    res = counter_tool.run(text="Hello world from UnisonAI", case_sensitive=True)
    print(f"Result: {res.result}")
    
    # Verify parameter validation
    fail_res = counter_tool.run(text=123) # Invalid type
    print(f"Validation Failure: {fail_res.error_message}")