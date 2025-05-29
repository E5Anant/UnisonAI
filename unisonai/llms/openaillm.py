from openai import OpenAI as OpenAIClient
import os
from dotenv import load_dotenv
from rich import print
from typing import Type, Optional, List, Dict
import openai
from unisonai.config import config

load_dotenv()


class Openai:
    USER = "user"
    MODEL = "model"

    def __init__(self,
                 messages: list[dict[str, str]] = [],
                 model: str = "gpt-3.5-turbo",
                 temperature: float = 0.0,
                 system_prompt: str | None = None,
                 max_tokens: int = 2048,
                 connectors: list[str] = [],
                 verbose: bool = False,
                 api_key: str | None = None
                 ):
        # Configure API key
        if api_key:
            config.set_api_key('openai', api_key)
            openai.api_key = api_key
        else:
            stored_key = config.get_api_key('openai')
            if stored_key:
                openai.api_key = stored_key
            elif os.getenv("OPENAI_API_KEY"):
                config.set_api_key('openai', os.getenv("OPENAI_API_KEY"))
                openai.api_key = os.getenv("OPENAI_API_KEY")
            else:
                raise ValueError(
                    "No API key provided. Please provide an API key either through:\n"
                    "1. The api_key parameter\n"
                    "2. config.set_api_key('openai', 'your-api-key')\n"
                    "3. OPENAI_API_KEY environment variable"
                )

        self.client = OpenAIClient(api_key=openai.api_key)
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.connectors = connectors
        self.verbose = verbose

        if self.system_prompt is not None:
            self.add_message(self.USER, self.system_prompt)

    def run(self, prompt: str, save_messages: bool = True) -> str:
        if save_messages:
            self.add_message(self.USER, prompt)
        response_content = ""
        self.stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
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
    llm = OpenAIClient(model="gpt-3.5-turbo")
    llm.add_message("User", "Hello, how are you?")
    llm.add_message("Chatbot", "I'm doing well, thank you!")
    print(llm.run("Say this is a test"))
