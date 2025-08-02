from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MemoryTool(BaseTool):
    """Enhanced memory tool for storing and retrieving agent memories with persistence."""
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.name = "memory_tool"
        self.description = "Store and retrieve important information for later use. Useful for maintaining context across conversations."
        self.params = [
            Field(
                name="action",
                description="Action to perform: 'store', 'retrieve', 'list', or 'clear'",
                required=True,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="key",
                description="Unique identifier for the memory item (required for store/retrieve)",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="value",
                description="Information to store (required for store action)",
                required=False,
                field_type=ToolParameterType.STRING
            ),
            Field(
                name="category",
                description="Category/tag for organizing memories",
                default_value="general",
                required=False,
                field_type=ToolParameterType.STRING
            )
        ]
        self.memory_file = memory_file
        self._ensure_memory_file()
        super().__init__()
    
    def _ensure_memory_file(self) -> None:
        """Ensure memory file exists with proper structure."""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({"memories": {}, "metadata": {"created": datetime.now().isoformat()}}, f)
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file."""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading memory: {e}")
            return {"memories": {}, "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_memory(self, memory_data: Dict[str, Any]) -> None:
        """Save memory to file."""
        try:
            memory_data["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            raise RuntimeError(f"Failed to save memory: {e}")
    
    def _run(self, action: str, key: Optional[str] = None, value: Optional[str] = None, 
             category: str = "general") -> str:
        """Execute memory operations."""
        action = action.lower().strip()
        
        if action not in ["store", "retrieve", "list", "clear"]:
            raise ValueError(f"Invalid action: {action}. Must be 'store', 'retrieve', 'list', or 'clear'")
        
        memory_data = self._load_memory()
        
        if action == "store":
            if not key or not value:
                raise ValueError("Both 'key' and 'value' are required for store action")
            
            memory_item = {
                "value": value,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0
            }
            
            memory_data["memories"][key] = memory_item
            self._save_memory(memory_data)
            
            return f"Successfully stored memory item '{key}' in category '{category}'"
        
        elif action == "retrieve":
            if not key:
                raise ValueError("'key' is required for retrieve action")
            
            if key in memory_data["memories"]:
                memory_item = memory_data["memories"][key]
                memory_item["access_count"] += 1
                memory_item["last_accessed"] = datetime.now().isoformat()
                self._save_memory(memory_data)
                
                return f"Retrieved: {memory_item['value']} (Category: {memory_item['category']}, Stored: {memory_item['timestamp']})"
            else:
                return f"No memory found for key: {key}"
        
        elif action == "list":
            memories = memory_data["memories"]
            if not memories:
                return "No memories stored"
            
            result = "Stored memories:\n"
            for mem_key, mem_data in memories.items():
                result += f"- {mem_key}: {mem_data['value'][:50]}{'...' if len(mem_data['value']) > 50 else ''} "
                result += f"(Category: {mem_data['category']})\n"
            
            return result.strip()
        
        elif action == "clear":
            if key:
                # Clear specific memory
                if key in memory_data["memories"]:
                    del memory_data["memories"][key]
                    self._save_memory(memory_data)
                    return f"Cleared memory for key: {key}"
                else:
                    return f"No memory found for key: {key}"
            else:
                # Clear all memories
                memory_data["memories"] = {}
                self._save_memory(memory_data)
                return "Cleared all memories"
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        memory_data = self._load_memory()
        memories = memory_data["memories"]
        
        categories = {}
        total_size = 0
        
        for mem_data in memories.values():
            category = mem_data.get("category", "general")
            categories[category] = categories.get(category, 0) + 1
            total_size += len(mem_data.get("value", ""))
        
        return {
            "total_memories": len(memories),
            "categories": categories,
            "total_size_chars": total_size,
            "memory_file": self.memory_file
        }