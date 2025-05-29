import os
from mistralai import Mistral
from dotenv import load_dotenv
from rich import print
from typing import Optional, List, Dict
import requests
from unisonai.config import config

load_dotenv()


class Mixtral:
    USER = "user"
    MODEL = "model"
    SYSTEM = "system"

    def __init__(
            self,
            messages: list[dict[str, str]] = [],
            model: str = "mistral-large-latest",
            temperature: float = 0.0,
            system_prompt: str | None = None,
            max_tokens: int = 2048,
            connectors: list[str] = [],
            verbose: bool = False,
            api_key: str | None = None
    ) -> None:
        # Configure API key
        if api_key:
            config.set_api_key('mixtral', api_key)
            self.api_key = api_key
        else:
            stored_key = config.get_api_key('mixtral')
            if stored_key:
                self.api_key = stored_key
            elif os.getenv("MISTRAL_API_KEY"):
                config.set_api_key('mixtral', os.getenv("MISTRAL_API_KEY"))
                self.api_key = os.getenv("MISTRAL_API_KEY")
            else:
                raise ValueError(
                    "No API key provided. Please provide an API key either through:\n"
                    "1. The api_key parameter\n"
                    "2. config.set_api_key('mixtral', 'your-api-key')\n"
                    "3. MISTRAL_API_KEY environment variable"
                )

        self.client = Mistral(api_key=self.api_key)
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.connectors = connectors
        self.verbose = verbose

        if self.system_prompt is not None:
            self.add_message(self.SYSTEM, self.system_prompt)

    def run(self, prompt: str, save_messages: bool = True) -> str:
        if save_messages:
            self.add_message(self.USER, prompt)

        response_content = ""
        response = self.client.chat.complete(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            stream=False,
            max_tokens=self.max_tokens,
        )

        response_content = response.choices[0].message.content
        # print(response_content)

        if save_messages:
            self.add_message(self.MODEL, response_content)

        return response_content

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def reset(self) -> None:
        self.messages = []
        self.system_prompt = None


if __name__ == "__main__":
    llm = Mixtral(model="mistral-large-latest")
    while True:
        q = input(">>> ")
        # llm.add_message(GroqLLM.USER, q)
        print("Final Response:")
        print(llm.run(q))
        print()
        # print(llm.messages)
        # llm.reset()  # Reset the instance
        # print(llm.messages)
