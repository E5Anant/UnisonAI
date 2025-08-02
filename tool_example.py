"""
Enhanced Tool System Example for UnisonAI

This example demonstrates the new ToolParameterType class and enhanced BaseTool class
with strong type validation, error handling, and standardized results.
"""

from unisonai.tools.tool import BaseTool, Field, ToolResult
from unisonai.tools.types import ToolParameterType
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai import config
import json
import statistics

# Configure your API key
# config.set_api_key("gemini", "your-api-key-here")

class DataAnalysisTool(BaseTool):
    """Advanced data analysis tool showcasing the enhanced tool system."""
    
    def __init__(self):
        self.name = "data_analyzer"
        self.description = "Perform statistical analysis on numerical data with customizable operations."
        self.params = [
            Field(
                name="data",
                description="List of numbers to analyze (e.g., [1, 2, 3, 4, 5])",
                field_type=ToolParameterType.LIST,
                required=True
            ),
            Field(
                name="operations",
                description="Statistical operations to perform",
                field_type=ToolParameterType.LIST,
                default_value=["mean", "median"],
                required=False
            ),
            Field(
                name="precision",
                description="Number of decimal places for results",
                field_type=ToolParameterType.INTEGER,
                default_value=2,
                required=False
            ),
            Field(
                name="include_metadata",
                description="Include additional statistics (min, max, count)",
                field_type=ToolParameterType.BOOLEAN,
                default_value=True,
                required=False
            )
        ]
        super().__init__()
    
    def _run(self, data: list, operations: list = ["mean", "median"], precision: int = 2, include_metadata: bool = True) -> dict:
        """Perform statistical analysis on the provided data."""
        if not data or not all(isinstance(x, (int, float)) for x in data):
            raise ValueError("Data must be a list of numbers")
        
        results = {}
        
        # Perform requested operations
        for op in operations:
            if op == "mean":
                results["mean"] = round(statistics.mean(data), precision)
            elif op == "median":
                results["median"] = round(statistics.median(data), precision)
            elif op == "mode":
                try:
                    results["mode"] = statistics.mode(data)
                except statistics.StatisticsError:
                    results["mode"] = "No unique mode"
            elif op == "std":
                if len(data) > 1:
                    results["standard_deviation"] = round(statistics.stdev(data), precision)
                else:
                    results["standard_deviation"] = 0
            elif op == "variance":
                if len(data) > 1:
                    results["variance"] = round(statistics.variance(data), precision)
                else:
                    results["variance"] = 0
        
        # Add metadata if requested
        if include_metadata:
            results["metadata"] = {
                "count": len(data),
                "min": min(data),
                "max": max(data),
                "range": max(data) - min(data),
                "sum": sum(data)
            }
        
        return results

class TextAnalyzerTool(BaseTool):
    """Text analysis tool demonstrating string parameter validation."""
    
    def __init__(self):
        self.name = "text_analyzer"
        self.description = "Analyze text content with various metrics and options."
        self.params = [
            Field(
                name="text",
                description="Text content to analyze",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="include_readability",
                description="Include readability analysis",
                field_type=ToolParameterType.BOOLEAN,
                default_value=False,
                required=False
            ),
            Field(
                name="word_frequency_limit",
                description="Number of most frequent words to show (0 for none)",
                field_type=ToolParameterType.INTEGER,
                default_value=5,
                required=False
            )
        ]
        super().__init__()
    
    def _run(self, text: str, include_readability: bool = False, word_frequency_limit: int = 5) -> dict:
        """Analyze text and return comprehensive metrics."""
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        # Basic text metrics
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        
        results = {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": sentences if sentences > 0 else 1,
            "paragraph_count": paragraphs if paragraphs > 0 else 1,
            "average_word_length": round(sum(len(word) for word in words) / len(words) if words else 0, 2),
            "average_sentence_length": round(len(words) / sentences if sentences > 0 else len(words), 2)
        }
        
        # Word frequency analysis
        if word_frequency_limit > 0:
            from collections import Counter
            word_freq = Counter(word.lower().strip('.,!?;:"()[]{}') for word in words if word.strip('.,!?;:"()[]{}'))
            results["most_frequent_words"] = dict(word_freq.most_common(word_frequency_limit))
        
        # Simple readability (if requested)
        if include_readability:
            # Flesch Reading Ease approximation
            avg_sentence_length = results["average_sentence_length"]
            avg_syllables = sum(max(1, len([c for c in word if c.lower() in 'aeiou'])) for word in words) / len(words) if words else 1
            
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
            
            if flesch_score >= 90:
                readability = "Very Easy"
            elif flesch_score >= 80:
                readability = "Easy" 
            elif flesch_score >= 70:
                readability = "Fairly Easy"
            elif flesch_score >= 60:
                readability = "Standard"
            elif flesch_score >= 50:
                readability = "Fairly Difficult"
            elif flesch_score >= 30:
                readability = "Difficult"
            else:
                readability = "Very Difficult"
            
            results["readability"] = {
                "flesch_score": round(flesch_score, 1),
                "level": readability
            }
        
        return results

def demonstrate_enhanced_tools():
    """Demonstrate the enhanced tool system with validation and error handling."""
    
    print("🔧 Enhanced Tool System Demo")
    print("=" * 50)
    
    # Create tool instances
    data_tool = DataAnalysisTool()
    text_tool = TextAnalyzerTool()
    
    print("\n📊 Tool Schemas:")
    print("Data Analyzer Schema:")
    print(json.dumps(data_tool.get_schema(), indent=2))
    
    print("\nText Analyzer Schema:")
    print(json.dumps(text_tool.get_schema(), indent=2))
    
    print("\n🧪 Tool Execution Examples:")
    
    # Test valid data analysis
    print("\n1. Valid Data Analysis:")
    result = data_tool.run(
        data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        operations=["mean", "median", "std"],
        precision=3,
        include_metadata=True
    )
    print(f"Success: {result.success}")
    print(f"Result: {json.dumps(result.result, indent=2)}")
    
    # Test invalid data (should fail validation)
    print("\n2. Invalid Data (should fail):")
    result = data_tool.run(data="invalid_data")
    print(f"Success: {result.success}")
    print(f"Error: {result.error_message}")
    
    # Test text analysis
    print("\n3. Text Analysis:")
    sample_text = """
    The enhanced tool system in UnisonAI provides robust type validation and error handling.
    It supports multiple parameter types including strings, integers, floats, booleans, lists, and dictionaries.
    This ensures that tools receive the correct data types and can handle errors gracefully.
    """
    
    result = text_tool.run(
        text=sample_text,
        include_readability=True,
        word_frequency_limit=10
    )
    print(f"Success: {result.success}")
    print(f"Result: {json.dumps(result.result, indent=2)}")
    
    print("\n✅ Enhanced Tool System Demo Complete!")

def create_enhanced_agent_example():
    """Create an agent with enhanced tools (requires API key)."""
    try:
        # Uncomment and add your API key to test with an actual agent
        # config.set_api_key("gemini", "your-api-key-here")
        
        agent = Single_Agent(
            llm=Gemini(model="gemini-2.0-flash"),
            identity="Data Analysis Assistant",
            description="AI assistant with enhanced data and text analysis capabilities",
            tools=[DataAnalysisTool(), TextAnalyzerTool()],
            verbose=True
        )
        
        print("\n🤖 Enhanced Agent Created Successfully!")
        print("The agent can now use strongly-typed tools with automatic validation.")
        
        # Example task (uncomment to test with actual API)
        # agent.unleash(task="Analyze this data: [10, 20, 30, 40, 50] and tell me the mean and standard deviation")
        
    except Exception as e:
        print(f"\n⚠️ Agent creation skipped (likely missing API key): {e}")
        print("Add your API key to test the enhanced agent functionality.")

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_enhanced_tools()
    
    # Show agent integration (requires API key)
    create_enhanced_agent_example()
