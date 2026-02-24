from openai import OpenAI
import os
from dotenv import load_dotenv
from rich import print
from typing import Type, Optional

load_dotenv()

class XAILLM:
    USER = "user"
    MODEL = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    def __init__(
            self,
            messages: list[dict[str, str]] = [],
            model: str = "grok-2-latest",  # Updated default model
            temperature: Optional[float] = 0.7,
            system_prompt: Optional[str] = None,
            max_tokens: int = 2048,
            api_key: str | None = None
    ) -> None:
        self.api_key = api_key if api_key else os.getenv("XAI_API_KEY")
        self.client = OpenAI(base_url="https://api.x.ai/v1",api_key=self.api_key)
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens

        if self.system_prompt is not None:
            self.add_message(self.SYSTEM, self.system_prompt)

    def _get_api_messages(self):
        """Return messages with 'tool' role mapped to 'user' for API compatibility."""
        api_msgs = []
        for msg in self.messages:
            if msg.get("role") == "tool":
                mapped = dict(msg)
                mapped["role"] = self.USER
                api_msgs.append(mapped)
            else:
                api_msgs.append(msg)
        return api_msgs

    def run(self, prompt: str, save_messages:bool = True, input_role: str = None) -> str:
        role = input_role if input_role else self.USER
        if save_messages:
            self.add_message(role, prompt)
        response_content = ""
        self.stream = self.client.chat.completions.create(
            model=self.model,
            messages=self._get_api_messages(),
            stream=False,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        for chunk in self.stream:
            if chunk.choices[0].delta.content is not None:
                response_content += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")
        if save_messages:
            self.add_message(self.MODEL, response_content)
        return response_content

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def __getitem__(self, index) -> dict[str, str] | list[dict[str, str]]:
        if isinstance(index, slice):
            return self.messages[index]
        elif isinstance(index, int):
            return self.messages[index]
        else:
            raise TypeError("Invalid argument type")

    def __setitem__(self, index, value) -> None:
        if isinstance(index, slice):
            self.messages[index] = value
        elif isinstance(index, int):
            self.messages[index] = value
        else:
            raise TypeError("Invalid argument type")

    def reset(self) -> None:
        self.messages = []
        self.system_prompt = None

if __name__ == "__main__":
    llm = XAILLM(model="grok-2-latest") 
    while True:
        q = input(">>> ")
        # llm.add_message(GroqLLM.USER, q)
        print("Final Response:")
        print(llm.run(q))
        print()
        # print(llm.messages)
        # llm.reset()  # Reset the instance
        # print(llm.messages)