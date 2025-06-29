import sys  # Added for exiting the process smoothly
from unisonai.llms import Gemini
from unisonai.prompts.individual import INDIVIDUAL_PROMPT
import re
import yaml
import colorama
from colorama import Fore, Style
from typing import Any
import json
import os
colorama.init(autoreset=True)


def create_tools(tools: list):
    formatted_tools = ""
    if tools:
        for tool in tools:
            # Instantiate the tool if it is provided as a class
            tool_instance = tool if not isinstance(tool, type) else tool()
            formatted_tools += f"-TOOL{tools.index(tool)+1}: \n"
            formatted_tools += "  NAME: " + tool_instance.name + "\n"
            formatted_tools += "  DESCRIPTION: " + tool_instance.description + "\n"
            formatted_tools += "  PARAMS: "
            fields = tool_instance.params
            for field in fields:
                formatted_tools += field.format()
    else:
        formatted_tools = None

    return formatted_tools


class Single_Agent:
    def __init__(self,
                 llm: Gemini,
                 identity: str,
                 description: str,
                 verbose: bool = True,
                 tools: list[Any] = [],
                 output_file: str = None,
                 history_folder: str = "history"):
        self.llm = llm
        self.identity = identity
        self.history_folder = history_folder
        self.description = description
        self.rawtools = tools
        self.tools = create_tools(tools)
        self.ask_user = False
        self.output_file = output_file
        self.verbose = verbose
        if history_folder:
            os.makedirs(history_folder, exist_ok=True)

    def _parse_and_fix_json(self, json_str: str):
        """Parses JSON string and attempts to fix common errors."""
        json_str = json_str.strip()
        if not json_str.startswith("{") or not json_str.endswith("}"):
            json_str = json_str[json_str.find("{"): json_str.rfind("}") + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}JSON Error:{Style.RESET_ALL} {e}")
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r"{\s*,", "{", json_str)
            json_str = re.sub(r"\s*,\s*", ",", json_str)
            try:
                return [json_str]
            except json.JSONDecodeError as e:
                return f"Error: Could not parse JSON - {e}"

    def _ensure_dict_params(self, params_data):
        """Ensures params is a dictionary by parsing it if it's a string."""
        if isinstance(params_data, str):
            params_data = params_data.strip()
            try:
                return json.loads(params_data)
            except json.JSONDecodeError as e:
                print(f"{Fore.YELLOW}JSON parsing error: {e}")
                try:
                    parsed = yaml.safe_load(params_data)
                    if isinstance(parsed, dict):
                        return parsed
                    else:
                        return {"value": parsed}
                except yaml.YAMLError:
                    print(f"{Fore.RED}YAML parsing failed; returning raw text")
                    return {"raw_input": params_data}
        elif params_data is None:
            return {}
        return params_data

    def unleash(self, task: str):
        self.user_task = task
        # Use history_folder if set; if not, default to current directory
        if self.history_folder:
            folder = self.history_folder if self.history_folder is not None else "."
            try:
                with open(f"{folder}/{self.identity}.json", "r", encoding="utf-8") as f:
                    history = f.read()
                    self.messages = json.loads(history) if history else []
            except FileNotFoundError:
                open(f"{folder}/{self.identity}.json",
                     "w", encoding="utf-8").close()
                self.messages = []
        else:
            self.messages = []
        self.llm.reset()
        if self.tools:
            self.llm.__init__(
                messages=self.messages,
                model=self.llm.model,  # Preserve the model
                temperature=self.llm.temperature,  # Preserve temperature
                system_prompt=INDIVIDUAL_PROMPT.format(
                    identity=self.identity,
                    description=self.description,
                    user_task=self.user_task,
                    tools=self.tools,
                ),
                max_tokens=self.llm.max_tokens,  # Preserve max_tokens
                verbose=self.llm.verbose,  # Preserve verbose
                api_key=self.llm.client.api_key if hasattr(self.llm, 'client') and hasattr(self.llm.client, 'api_key') else None  # Preserve the API key
            )
        else:
            self.llm.__init__(
                messages=self.messages,
                model=self.llm.model,  # Preserve the model
                temperature=self.llm.temperature,  # Preserve temperature
                system_prompt=INDIVIDUAL_PROMPT.format(
                    identity=self.identity,
                    description=self.description,
                    user_task=self.user_task,
                    tools="No Provided Tools",
                ),
                max_tokens=self.llm.max_tokens,  # Preserve max_tokens
                verbose=self.llm.verbose,  # Preserve verbose
                api_key=self.llm.client.api_key if hasattr(self.llm, 'client') and hasattr(self.llm.client, 'api_key') else None  # Preserve the API key
            )
        print(Fore.LIGHTCYAN_EX + "Status: Evaluating Task...\n")
        response = self.llm.run(task, save_messages=True)
        try:
            if self.history_folder:
                with open(f"{folder}/{self.identity}.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(self.llm.messages, indent=4))
            else:
                pass
        except Exception as e:
            print(e)
        if self.verbose:
            print("Response:")
            print(response)
        yaml_blocks = re.findall(r"```yml(.*?)```", response, flags=re.DOTALL)
        if not yaml_blocks:
            yaml_blocks = re.findall(
                r"```yaml(.*?)```", response, flags=re.DOTALL)
        if not yaml_blocks:
            return response
        yaml_content = yaml_blocks[0].strip()
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            print(f"{Fore.RED}Error parsing YAML: {e}")
            return response
        if "thoughts" in data and "name" in data and "params" in data:
            thoughts = data["thoughts"]
            name = data["name"]
            params_raw = data["params"]
            params = self._ensure_dict_params(params_raw)
            if len(thoughts) > 150:
                thoughts = f"{thoughts[:120]}..."
            print(f"{Fore.MAGENTA}Thoughts: {thoughts}\n{Fore.GREEN}Using Tool ({name})\n{Fore.LIGHTYELLOW_EX}Params: {params}")
            if name == "ask_user":
                if isinstance(params, dict) and "question" in params:
                    print("QUESTION: " + params["question"])
                    self.unleash(input("You: "))
                else:
                    question = str(
                        params) if params else "What would you like to say?"
                    print("QUESTION: " + question)
                    self.unleash(input("You: "))
            elif name == "pass_result":
                if isinstance(params, dict) and "result" in params:
                    print("RESULT: " + str(params["result"]))
                else:
                    print("RESULT: " + str(params))
                while True:
                    decision = input(
                        "Does this result meet your requirements? (y/n): ")
                    if decision.lower() == "y":
                        print("Result accepted. Ending process smoothly.")
                        if self.output_file:
                            with open(self.output_file, "w", encoding="utf-8") as file:
                                file.write(
                                    str(params["result"]) or str(params))
                        sys.exit(0)
                    elif decision.lower() == "n":
                        tweaks = input("What tweaks would you like to make? ")
                        self.unleash(tweaks)
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")
            else:
                # Execute the tool by first ensuring we have an instance.
                for tool in self.rawtools:
                    tool_instance = tool if not isinstance(
                        tool, type) else tool()
                    if tool_instance.name.lower() == name.lower():
                        try:
                            if isinstance(params, dict):
                                tool_response = tool_instance._run(**params)
                            else:
                                tool_response = tool_instance._run()
                            print(Fore.LIGHTCYAN_EX +
                                  "Status: Executing Tool...\n")
                            print("Tool Response:")
                            print(tool_response)
                            self.unleash(
                                "Here is your tool response:\n\n" + str(tool_response))
                            break
                        except TypeError as e:
                            print(
                                f"{Fore.RED}TypeError when executing tool '{name}': {e}")
                            # Check for errors related to missing self or duplicate parameters.
                            if ("missing 1 required positional argument: 'self'" in str(e) or
                                    "got multiple values for argument" in str(e)):
                                try:
                                    print(
                                        f"{Fore.LIGHTCYAN_EX}Status: Executing Tool (via unbound method)...\n")
                                    # Call the unbound _run method from the class so that self is not passed twice.
                                    tool_response = tool_instance.__class__._run(
                                        **params)
                                    print("Tool Response:")
                                    print(tool_response)
                                    self.unleash(
                                        "Here is your tool response:\n\n" + str(tool_response))
                                    break
                                except Exception as inner_e:
                                    print(
                                        f"{Fore.RED}Failed to execute tool via unbound method: {inner_e}")
                        except Exception as e:
                            print(
                                f"{Fore.RED}Error executing tool '{name}': {e}")
        else:
            print(
                Fore.RED + "YAML block found, but it doesn't match the expected format.")
            return response
