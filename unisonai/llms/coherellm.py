import cohere
import os
from dotenv import load_dotenv
from rich import print
from typing import Type, Optional, List, Dict
from unisonai.config import config

load_dotenv()


class Cohere:
    USER = "user"
    MODEL = "model"
    SYSTEM = "System"

    def __init__(
            self,
            messages: list[dict[str, str]] = [],
            model: str = "command",
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
            The model to use, by default "command"
        temperature : float, optional
            The temperature to use, by default 0.0
        system_prompt : str, optional
            The system prompt to use, by default ""
        max_tokens : int, optional
            The max tokens to use, by default 2048
        connectors : list[str], optional
            The connectors to use, by default []
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
            config.set_api_key('cohere', api_key)
            self.client = cohere.Client(api_key=api_key)
        else:
            stored_key = config.get_api_key('cohere')
            if stored_key:
                self.client = cohere.Client(api_key=stored_key)
            elif os.getenv("COHERE_API_KEY"):
                config.set_api_key('cohere', os.getenv("COHERE_API_KEY"))
                self.client = cohere.Client(
                    api_key=os.getenv("COHERE_API_KEY"))
            else:
                raise ValueError(
                    "No API key provided. Please provide an API key either through:\n"
                    "1. The api_key parameter\n"
                    "2. config.set_api_key('cohere', 'your-api-key')\n"
                    "3. COHERE_API_KEY environment variable"
                )

        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.connectors = connectors
        self.verbose = verbose

        if self.system_prompt != None:
            self.add_message(self.SYSTEM, self.system_prompt)

    def run(self, prompt: str, save_messages: bool = True) -> str:
        if save_messages:
            self.add_message(self.USER, prompt)
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
        self.stream = self.client.chat_stream(
            model=self.model,
            message=prompt,
            temperature=self.temperature,
            chat_history=self.messages,
            connectors=self.connectors,
            preamble=self.system_prompt,
            max_tokens=self.max_tokens,
        )
        response: str = ""
        for event in self.stream:
            if event.event_type == "text-generation":
                if self.verbose:
                    print(event.text, end='')
                response += event.text
        if save_messages:
            self.add_message(self.MODEL, response)
        return response

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
        self.messages.append({"role": role, "message": content})

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
    llm = Cohere(verbose=False)
    while True:
        q = input(">>> ")
        # llm.add_message(GroqLLM.USER, q)
        print("Final Response:")
        print(llm.run(q))
        print()
        print(llm.messages)
        llm.reset()  # Reset the instance
        print(llm.messages)
