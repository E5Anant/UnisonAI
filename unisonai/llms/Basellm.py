from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseLLM(ABC):
    """
    A base class for interacting with language models.
    
    Attributes:
        messages (List[Dict[str, str]]): A list of messages in the conversation.
        max_history_messages (int): Maximum messages before compression (default: 20)
    """
    USER = "user"
    MODEL = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

    def __init__(self, 
                 messages: Optional[List[Dict[str, str]]] = None,
                 system_prompt: Optional[str] = None,
                 max_history_messages: int = 20) -> None:
        self.messages = messages or []
        self.max_history_messages = max_history_messages
        if system_prompt is not None:
            self.add_message(self.SYSTEM, system_prompt)

    def add_message(self, role: str, content: str) -> None:
        """Append a message with a given role to the conversation."""
        self.messages.append({"role": role, "content": content})
        
        # Auto-compress if exceeds threshold
        if len(self.messages) > self.max_history_messages:
            self.compress_history()

    def compress_history(self, keep_recent: int = 6) -> None:
        """Compress old messages into summary, keeping recent ones intact.
        
        Args:
            keep_recent: Number of recent message pairs to keep uncompressed
        """
        if len(self.messages) <= keep_recent:
            return
        
        # Keep system message, summarize middle, keep recent
        system_msgs = [m for m in self.messages if m["role"] == self.SYSTEM]
        to_compress = self.messages[len(system_msgs):-keep_recent]
        recent_msgs = self.messages[-keep_recent:]
        
        # Create summary of compressed section
        if to_compress:
            summary_content = self._create_summary(to_compress)
            summary_msg = {
                "role": self.SYSTEM,
                "content": f"[Previous conversation summary: {summary_content}]"
            }
            
            # Rebuild messages: system + summary + recent
            self.messages = system_msgs + [summary_msg] + recent_msgs
    
    def _create_summary(self, messages: List[Dict[str, str]]) -> str:
        """Create concise summary of message sequence.
        
        Args:
            messages: Messages to summarize
            
        Returns:
            Concise summary string (max 200 chars)
        """
        # Extract key actions and results
        actions = []
        for msg in messages:
            content = msg["content"]
            # Extract tool names from JSON if present
            if '"tool"' in content:
                try:
                    tool_start = content.find('"tool"') + 8
                    tool_end = content.find('"', tool_start)
                    tool_name = content[tool_start:tool_end]
                    actions.append(tool_name)
                except:
                    pass
        
        if actions:
            summary = f"Used tools: {', '.join(set(actions[:5]))}"
        else:
            # Generic summary
            summary = f"{len(messages)} previous exchanges"
        
        return summary[:200]  # Cap at 200 chars

    def _get_api_messages(self):
        """Return messages with 'tool' role mapped to 'user' for API compatibility.
        
        Providers that natively support the 'tool' role can override this method.
        """
        api_msgs = []
        for msg in self.messages:
            if msg.get("role") == "tool":
                mapped = dict(msg)
                mapped["role"] = self.USER
                api_msgs.append(mapped)
            else:
                api_msgs.append(msg)
        return api_msgs

    @abstractmethod
    def run(self, prompt: str, save_messages: bool = True, input_role: str = None) -> str:
        """
        Run the model with the given prompt.
        
        Subclasses must implement this method.
        """
        pass

    def reset(self) -> None:
        """Reset the conversation messages."""
        self.messages = []