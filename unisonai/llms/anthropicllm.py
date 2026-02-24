import anthropic
import os
from dotenv import load_dotenv
from rich import print
from typing import Type, Optional, List, Dict

load_dotenv()


class Anthropic:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    MODEL = "model"
    TOOL = "tool"

    def __init__(
            self,
            messages: list[dict[str, str]] = [],
            model: str = "claude-3-opus-20240229",
            temperature: float = 0.0,
            system_prompt: str | None = None,
            max_tokens: int = 2048,
            connectors: list[str] = [],
            verbose: bool = False,
            api_key: str | None = None
    ) -> None:
        """
        Initialize the LLM

        Parameters
        ----------
        messages : list[dict[str, str]], optional
            The list of messages, by default []
        model : str, optional
            The model to use, by default "claude-3-opus-20240229"
        temperature : float, optional
            The temperature to use, by default 0.0
        system_prompt : str, optional
            The system prompt to use, by default None
        max_tokens : int, optional
            The max tokens to use, by default 2048
        connectors : list[str], optional
            The list of connectors to use, by default []
        verbose : bool, optional
            The verbose to use, by default False
        api_key : str|None, optional
            The api key to use, by default None

        Examples
        --------
        >>> llm = LLM()
        >>> llm.add_message("User", "Hello, how are you?")
        """
        # Configure API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "No API key provided. Please provide an API key either through:\n"
                "1. The api_key parameter\n"
                "2. ANTHROPIC_API_KEY environment variable"
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.connectors = connectors
        self.verbose = verbose

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

    def run(self, prompt: str, save_messages: bool = True, input_role: str = None) -> str:
        role = input_role if input_role else self.USER
        if save_messages:
            self.add_message(role, prompt)
        """
        Run the LLM

        Parameters
        ----------
        prompt : str
            The prompt to run

        Returns
        -------
        str
            The response

        Examples
        --------
        >>> llm.run("Hello, how are you?")
        "I'm doing well, thank you!"
        """
        self.response = self.client.messages.create(
            model=self.model,
            messages=self._get_api_messages(),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        if save_messages:
            self.add_message(self.MODEL, self.response.content)
        return self.response.content

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the list of messages

        Parameters
        ----------
        role : str
            The role of the message
        content : str
            The content of the message

        Returns
        -------
        None

        Examples
        --------
        >>> llm.add_message("User", "Hello, how are you?")
        >>> llm.add_message("Chatbot", "I'm doing well, thank you!")
        """
        self.messages.append({"role": role, "content": content})

    def __getitem__(self, index) -> dict[str, str] | list[dict[str, str]]:
        """
        Get a message from the list of messages

        Parameters
        ----------
        index : int
            The index of the message to get

        Returns
        -------
        dict
            The message at the specified index

        Examples
        --------
        >>> llm[0]
        {'role': 'User', 'message': 'Hello, how are you?'}
        >>> llm[1]
        {'role': 'Chatbot', 'message': "I'm doing well, thank you!"}

        Raises
        ------
        TypeError
            If the index is not an integer or a slice
        """
        if isinstance(index, slice):
            return self.messages[index]
        elif isinstance(index, int):
            return self.messages[index]
        else:
            raise TypeError("Invalid argument type")

    def __setitem__(self, index, value) -> None:
        """
        Set a message in the list of messages

        Parameters
        ----------
        index : int
            The index of the message to set
        value : dict
            The new message

        Returns
        -------
        None

        Examples
        --------
        >>> llm[0] = {'role': 'User', 'message': 'Hello, how are you?'}
        >>> llm[1] = {'role': 'Chatbot', 'message': "I'm doing well, thank you!"}

        Raises
        ------
        TypeError
            If the index is not an integer or a slice
        """
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


if __name__ == "__main__":
    llm = Anthropic()
    llm.add_message("human", "Hello, how are you?")
    llm.add_message("assistant", "I'm doing well, thank you!")
    print(llm.run("write python code to make snake game"))
