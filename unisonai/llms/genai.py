import os
from dotenv import load_dotenv
from typing import List, Dict
import google.generativeai as genaii
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from unisonai.config import config

load_dotenv()


class Gemini:
    USER = "user"
    MODEL = "model"

    def __init__(self,
                 messages: list[dict[str, str]] = [],
                 model: str = "gemini-2.0-flash",
                 temperature: float = 0.0,
                 system_prompt: str | None = None,
                 max_tokens: int = 2048,
                 connectors: list[str] = [],
                 verbose: bool = False,
                 safety_settings: list = [],
                 api_key: str | None = None
                 ):
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        if safety_settings:
            self.safety_settings = safety_settings

        # Configure API key
        if api_key:
            config.set_api_key('gemini', api_key)
            os.environ["GOOGLE_API_KEY"] = api_key
        else:
            stored_key = config.get_api_key('gemini')
            if stored_key:
                os.environ["GOOGLE_API_KEY"] = stored_key
            elif os.getenv("GEMINI_API_KEY"):
                config.set_api_key('gemini', os.getenv("GEMINI_API_KEY"))
                os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
            else:
                raise ValueError(
                    "No API key provided. Please provide an API key either through:\n"
                    "1. The api_key parameter\n"
                    "2. config.set_api_key('gemini', 'your-api-key')\n"
                    "3. GEMINI_API_KEY environment variable"
                )

        genaii.configure(api_key=os.environ["GOOGLE_API_KEY"])

        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.connectors = connectors
        self.verbose = verbose
        self.client = genaii.GenerativeModel(
            model_name=self.model,
            safety_settings=self.safety_settings,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "response_mime_type": "text/plain",
            }
        )
        if self.system_prompt:
            self.client = genaii.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                    "response_mime_type": "text/plain",
                }
            )

    def run(self, prompt: str, save_messages: bool = True) -> str:
        if save_messages:
            self.add_message(self.USER, prompt)
        self.chat_session = self.client.start_chat(history=self.messages)
        response = self.chat_session.send_message(prompt)
        r = response.text
        if save_messages:
            self.add_message(self.MODEL, r)
        if self.verbose:
            print(r)
        return r

    def add_message(self, role: str, content: str) -> None:
        # Adjusting message structure for Gemini
        self.messages.append({"role": role, "parts": [content]})

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
        """
        Reset the system prompts and messages

        Returns
        -------
        None
        """
        self.messages = []
        self.system_prompt = None
        self.client = genaii.GenerativeModel(
            model_name=self.model,
            safety_settings=self.safety_settings,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "response_mime_type": "text/plain",
            }
        )


if __name__ == "__main__":
    llm = Gemini(system_prompt="Helpful Assistant.", messages=[{'role': 'user', 'parts': [
                 'hello']}, {'role': 'model', 'parts': ['Hi there! How can I help you today?\n']}])
    while True:
        q = input(">>> ")
        answer = llm.run(q)
        print(answer)
        print("Before Reset:", llm.messages)
        llm.reset()
        print("After Reset:", llm.messages)
