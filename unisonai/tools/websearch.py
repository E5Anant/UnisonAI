from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from duckduckgo_search import DDGS
from googlesearch import search as netsearch
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Enhanced web search tool with robust error handling and validation."""
    
    def __init__(self):
        self.name = "web_search"
        self.description = "Search the web for current information. Useful for answering questions about recent events, facts, and general knowledge."
        self.params = [
            Field(
                name="query", 
                description="The search query string. Be specific for better results.", 
                required=True,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="max_results",
                description="Maximum number of search results to return (1-10)",
                default_value=3,
                required=False,
                field_type=ToolParameterType.INTEGER
            )
        ]
        super().__init__()

    def _run(self, query: str, max_results: int = 3) -> str:
        """Execute web search with multiple fallback methods."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        if max_results < 1 or max_results > 10:
            max_results = 3
            logger.warning(f"max_results clamped to {max_results}")
        
        output = ""
        search_successful = False
        
        # Method 1: Try Google Search first
        try:
            logger.info(f"Searching via Google for: {query}")
            results = list(netsearch(query, advanced=True, num_results=max_results))
            
            if results:
                logger.info(f"Google search returned {len(results)} results")
                output += "=== Google Search Results ===\n\n"
                for i, result in enumerate(results):
                    output += f"{i+1}. \nTitle: {result.title}\n"
                    output += f"Description: {result.description}\n"
                    output += f"Source: {result.url}\n\n"
                search_successful = True
            else:
                logger.warning("Google search returned no results")
                
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
        
        # Method 2: Fallback to DuckDuckGo if Google fails
        if not search_successful:
            try:
                logger.info(f"Trying DuckDuckGo search for: {query}")
                ddg = DDGS()
                ddg_results = ddg.text(query, max_results=max_results)
                
                if ddg_results:
                    logger.info(f"DuckDuckGo search returned {len(ddg_results)} results")
                    output += "=== DuckDuckGo Search Results ===\n\n"
                    for i, result in enumerate(ddg_results):
                        output += f"{i+1}. \nTitle: {result.get('title', 'No Title')}\n"
                        output += f"Body: {result.get('body', 'No Description')}\n"
                        output += f"Source: {result.get('href', 'No URL')}\n\n"
                    search_successful = True
                else:
                    logger.warning("DuckDuckGo search returned no results")
                    
            except Exception as e:
                logger.error(f"DuckDuckGo search failed: {str(e)}")
        
        if not search_successful:
            raise RuntimeError(f"All search methods failed for query: {query}")
        
        return output.strip()
    
    def get_usage_examples(self) -> List[Dict[str, Any]]:
        """Get usage examples for this tool."""
        return [
            {
                "description": "Search for current news",
                "parameters": {"query": "latest news about artificial intelligence 2024"}
            },
            {
                "description": "Search with custom result count",
                "parameters": {"query": "Python programming tutorial", "max_results": 5}
            },
            {
                "description": "Search for specific information",
                "parameters": {"query": "climate change effects 2024 statistics"}
            }
        ]