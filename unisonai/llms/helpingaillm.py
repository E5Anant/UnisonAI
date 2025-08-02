from HelpingAI import HAI
import os
from dotenv import load_dotenv
from rich import print
from typing import Type, Optional, List, Dict
from unisonai.config import config

load_dotenv()


class HelpingAI:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    MODEL = "assistant"

    def __init__(
            self,
            messages: list[dict[str, str]] = [],
            model: str = "Dhanishtha-2.0-preview",
            temperature: float = 0.7,
            system_prompt: str | None = None,
            max_tokens: int = 2048,
            connectors: list[str] = [],
            verbose: bool = False,
            api_key: str | None = None,
            hide_think: bool = True,
            top_p: float = 0.9,
            frequency_penalty: float = 0.0,
            presence_penalty: float = 0.0
    ) -> None:
        """
        Initialize the HelpingAI LLM

        Parameters
        ----------
        messages : list[dict[str, str]], optional
            The list of messages, by default []
        model : str, optional
            The model to use, by default "Helpingai3-raw"
            Available models: "Helpingai3-raw", "Dhanishtha-2.0-preview"
        temperature : float, optional
            The temperature to use, by default 0.7
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
        hide_think : bool, optional
            Filter out reasoning blocks for Dhanishtha model, by default True
        top_p : float, optional
            Nucleus sampling parameter, by default 0.9
        frequency_penalty : float, optional
            Reduces repetition, by default 0.0
        presence_penalty : float, optional
            Encourages new topics, by default 0.0

        Examples
        --------
        >>> llm = HelpingAI()
        >>> llm.add_message("user", "Hello, how are you?")
        >>> response = llm.run("Tell me about emotional intelligence")
        """
        # Configure API key
        if api_key:
            config.set_api_key('helpingai', api_key)
            self.client = HAI(api_key=api_key)
        else:
            stored_key = config.get_api_key('helpingai')
            if stored_key:
                self.client = HAI(api_key=stored_key)
            elif os.getenv("HAI_API_KEY"):
                config.set_api_key('helpingai', os.getenv("HAI_API_KEY"))
                self.client = HAI(api_key=os.getenv("HAI_API_KEY"))
            else:
                raise ValueError(
                    "No API key provided. Please provide an API key either through:\n"
                    "1. The api_key parameter\n"
                    "2. config.set_api_key('helpingai', 'your-api-key')\n"
                    "3. HAI_API_KEY environment variable\n"
                    "Get your API key from: https://helpingai.co/dashboard"
                )

        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.connectors = connectors
        self.verbose = verbose
        self.hide_think = hide_think
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

        if self.system_prompt is not None:
            self.add_message(self.SYSTEM, self.system_prompt)

    def run(self, prompt: str, save_messages: bool = True) -> str:
        """
        Run the HelpingAI LLM

        Parameters
        ----------
        prompt : str
            The prompt to run
        save_messages : bool, optional
            Whether to save messages to conversation history, by default True

        Returns
        -------
        str
            The response from the model

        Examples
        --------
        >>> llm.run("What makes a good leader?")
        "A good leader combines emotional intelligence with clear communication..."
        """
        if save_messages:
            self.add_message(self.USER, prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                hide_think=self.hide_think
            )
            
            response_content = response.choices[0].message.content
            
            if self.verbose:
                print(f"[HelpingAI Response]: {response_content}")
            
            if save_messages:
                self.add_message(self.MODEL, response_content)
            
            return response_content
            
        except Exception as e:
            error_msg = f"Error calling HelpingAI API: {str(e)}"
            if self.verbose:
                print(f"[HelpingAI Error]: {error_msg}")
            raise Exception(error_msg)

    def stream(self, prompt: str, save_messages: bool = True) -> str:
        """
        Stream responses from HelpingAI in real-time

        Parameters
        ----------
        prompt : str
            The prompt to run
        save_messages : bool, optional
            Whether to save messages to conversation history, by default True

        Returns
        -------
        str
            The complete response from the model

        Examples
        --------
        >>> for chunk in llm.stream("Tell me about empathy"):
        ...     print(chunk, end="")
        """
        if save_messages:
            self.add_message(self.USER, prompt)

        response_content = ""
        
        try:
            for chunk in self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                hide_think=self.hide_think,
                stream=True
            ):
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_content += content
                    if self.verbose:
                        print(content, end="")
            
            if save_messages:
                self.add_message(self.MODEL, response_content)
            
            return response_content
            
        except Exception as e:
            error_msg = f"Error streaming from HelpingAI API: {str(e)}"
            if self.verbose:
                print(f"[HelpingAI Error]: {error_msg}")
            raise Exception(error_msg)

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the list of messages

        Parameters
        ----------
        role : str
            The role of the message (user, assistant, system)
        content : str
            The content of the message

        Returns
        -------
        None

        Examples
        --------
        >>> llm.add_message("user", "Hello, how are you?")
        >>> llm.add_message("assistant", "I'm doing well, thank you!")
        """
        self.messages.append({"role": role, "content": content})

    def __getitem__(self, index) -> dict[str, str] | list[dict[str, str]]:
        """
        Get a message from the list of messages

        Parameters
        ----------
        index : int or slice
            The index of the message to get

        Returns
        -------
        dict or list
            The message(s) at the specified index

        Examples
        --------
        >>> llm[0]
        {'role': 'user', 'content': 'Hello, how are you?'}
        >>> llm[1]
        {'role': 'assistant', 'content': "I'm doing well, thank you!"}

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
        index : int or slice
            The index of the message to set
        value : dict or list
            The new message(s)

        Returns
        -------
        None

        Examples
        --------
        >>> llm[0] = {'role': 'user', 'content': 'Hello, how are you?'}
        >>> llm[1] = {'role': 'assistant', 'content': "I'm doing well, thank you!"}

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
        Reset the conversation messages and system prompt

        Returns
        -------
        None
        """
        self.messages = []
        self.system_prompt = None

    def get_available_models(self) -> list:
        """
        Get list of available models

        Returns
        -------
        list
            List of available model names
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models]
        except Exception as e:
            if self.verbose:
                print(f"[HelpingAI Error]: Could not fetch models: {str(e)}")
            return ["Helpingai3-raw", "Dhanishtha-2.0-preview"]


if __name__ == "__main__":
    # Example usage
    llm = HelpingAI(model="Dhanishtha-2.0-preview", verbose=True)
    llm.add_message("user", "Hello, how are you?")
    llm.add_message("assistant", "I'm doing well, thank you!")
    print(llm.run("Tell me about emotional intelligence in leadership"))