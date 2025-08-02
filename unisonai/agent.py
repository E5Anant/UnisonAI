import sys  # Added for exiting the process smoothly
from unisonai.llms import Gemini
from unisonai.prompts.agent import AGENT_PROMPT
from unisonai.prompts.manager import MANAGER_PROMPT
from unisonai.async_helper import run_async_from_sync, run_sync_in_executor
import inspect
import re
import yaml
import colorama
from colorama import Fore, Style
from typing import Any
import json
import difflib  # For fuzzy string matching
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


class Agent:
    def __init__(self,
                 llm: Gemini,
                 identity: str,  # Name of the agent
                 description: str,  # Description of the agent
                 task: str,  # A Base Example Task According to agents's work
                 verbose: bool = True,
                 tools: list[Any] = []):
        self.llm = llm
        self.identity = identity
        self.description = description
        self.task = task
        self.plan = None
        self.history_folder = None  # Renamed for consistency
        self.rawtools = tools
        self.tools = create_tools(tools)
        self.ask_user = False
        self.user_task = None
        self.shared_instruction = None
        self.rawmembers = []
        self.members = ""
        self.clan_name = ""
        self.output_file = None
        self.verbose = verbose

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

    def _get_agent_by_name(self, agent_name: str):
        """Find the closest matching agent from rawmembers based on fuzzy name matching."""
        ceo_manager_variations = ["ceo", "manager",
                                  "ceo/manager", "ceo-manager", "ceo manager"]
        agent_name_clean = agent_name.lower().strip()
        for prefix in ["agent ", " agent", "the "]:
            agent_name_clean = agent_name_clean.replace(prefix, "")
        if agent_name_clean in ceo_manager_variations:
            return "CEO/Manager"
        available_agents = [member.identity for member in self.rawmembers]
        available_agents_lower = [agent.lower() for agent in available_agents]
        if agent_name_clean in available_agents_lower:
            index = available_agents_lower.index(agent_name_clean)
            return available_agents[index]
        matches = difflib.get_close_matches(
            agent_name_clean, available_agents_lower, n=1, cutoff=0.6)
        if matches:
            index = available_agents_lower.index(matches[0])
            return available_agents[index]
        return agent_name

    def send_message(self, agent_name: str, message: str, additional_resource: str = None, sender: str = None):
        matched_agent_name = self._get_agent_by_name(agent_name)
        if matched_agent_name != agent_name and self.verbose:
            print(
                f"{Fore.YELLOW}Note: Agent name '{agent_name}' was matched to '{matched_agent_name}'")
        print(Fore.LIGHTCYAN_EX +
              f"Status: Sending message to {matched_agent_name}" + Style.RESET_ALL)
        msg = f"""MESSAGE FROM: {sender}\nMESSAGE TO: {matched_agent_name}\n\n{message}\n\nADDITIONAL RESOURCE:\n{additional_resource}"""
        is_manager_message = matched_agent_name in [
            "CEO/Manager", "Manager", "CEO"]
        for member in self.rawmembers:
            if is_manager_message:
                if member.ask_user:
                    member.unleash(msg)
                else:
                    continue
            elif member.identity == matched_agent_name:
                member.unleash(msg)

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
        # Use history_folder if set; if not, default to current directory
        folder = self.history_folder if self.history_folder is not None else "."
        try:
            with open(f"{folder}/{self.identity}.json", "r", encoding="utf-8") as f:
                history = f.read()
                self.messages = json.loads(history) if history else []
        except FileNotFoundError:
            open(f"{folder}/{self.identity}.json",
                 "w", encoding="utf-8").close()
            self.messages = []
        self.llm.reset()
        if self.tools:
            if self.ask_user:
                self.llm.__init__(
                    messages=self.messages,
                    system_prompt=MANAGER_PROMPT.format(
                        members=self.members,
                        shared_instruction=self.shared_instruction,
                        identity=self.identity,
                        description=self.description,
                        task=self.task,
                        user_task=task,
                        tools=self.tools,
                        plan=self.plan,
                        clan_name=self.clan_name
                    )
                )
            else:
                self.llm.__init__(
                    messages=self.messages,
                    system_prompt=AGENT_PROMPT.format(
                        identity=self.identity,
                        description=self.description,
                        task=self.task,
                        tools=self.tools,
                        user_task=task,
                        shared_instruction=self.shared_instruction,
                        members=self.members,
                        plan=self.plan,
                        clan_name=self.clan_name
                    )
                )
        else:
            if self.ask_user:
                self.llm.__init__(
                    messages=self.messages,
                    system_prompt=MANAGER_PROMPT.format(
                        members=self.members,
                        shared_instruction=self.shared_instruction,
                        identity=self.identity,
                        description=self.description,
                        task=self.task,
                        user_task=task,
                        plan=self.plan,
                        tools="No Provided Tools",
                        clan_name=self.clan_name
                    )
                )
            else:
                self.llm.__init__(
                    messages=self.messages,
                    system_prompt=AGENT_PROMPT.format(
                        identity=self.identity,
                        description=self.description,
                        task=self.task,
                        tools="No Provided Tools",
                        plan=self.plan,
                        user_task=task,
                        shared_instruction=self.shared_instruction,
                        members=self.members,
                        clan_name=self.clan_name
                    )
                )
        print(Fore.LIGHTCYAN_EX + "Status: Evaluating Task...\n")
        response = self.llm.run(task, save_messages=True)
        try:
            with open(f"{folder}/{self.identity}.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.llm.messages, indent=4))
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
            if name == "send_message":
                if isinstance(params, dict) and "agent_name" in params and "message" in params:
                    self.send_message(params["agent_name"], params["message"], params.get(
                        "additional_resource"), sender=self.identity)
                else:
                    print(
                        f"{Fore.RED}Error: Missing required parameters for send_message tool. Need 'agent_name' and 'message'.")
                    print(f"{Fore.RED}Available params: {params}")
            elif name == "ask_user":
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
                            # --- Primary execution path (bound method) ---
                            bound_run_method = tool_instance._run
                            is_async = inspect.iscoroutinefunction(bound_run_method)
                            
                            print(Fore.LIGHTCYAN_EX + f"Status: Executing Tool {'(Async)' if is_async else ''}...\n")
                            
                            if is_async:
                                if isinstance(params, dict):
                                    tool_response = run_async_from_sync(bound_run_method(**params))
                                else:
                                    tool_response = run_async_from_sync(bound_run_method(params))
                            else: # Is a synchronous tool
                                if isinstance(params, dict):
                                    tool_response = bound_run_method(**params)
                                else:
                                    tool_response = bound_run_method(params)

                            print("Tool Response:")
                            print(tool_response)
                            self.unleash(
                                "Here is your tool response:\n\n" + str(tool_response))
                            break
                        
                        except TypeError as e:
                            if ("missing 1 required positional argument: 'self'" in str(e) or
                                    "got multiple values for argument" in str(e) or
                                    "takes 0 positional arguments but 1 was given" in str(e)):
                            # ---- END OF THE FIX ----
                            
                                try:
                                    # --- Fallback execution path (unbound method) ---
                                    unbound_run_method = tool_instance.__class__._run
                                    is_async_unbound = inspect.iscoroutinefunction(unbound_run_method)

                                    print(Fore.LIGHTCYAN_EX + f"Status: Executing Tool (via unbound method) {'(Async)' if is_async_unbound else '(Sync via Executor)'}...\n")

                                    if is_async_unbound:
                                        # Execute async unbound tool
                                        if isinstance(params, dict):
                                            tool_response = run_async_from_sync(unbound_run_method(**params))
                                        else:
                                            tool_response = run_async_from_sync(unbound_run_method(params))
                                    else: 
                                        # Execute sync unbound tool in thread pool
                                        if isinstance(params, dict):
                                            tool_response = run_sync_in_executor(unbound_run_method, **params)
                                        else:
                                            tool_response = run_sync_in_executor(unbound_run_method, params)
                                    
                                    print("Tool Response:")
                                    print(tool_response)
                                    self.unleash(
                                        "Here is your tool response:\n\n" + str(tool_response))
                                    break
                                except Exception as inner_e:
                                    print(
                                        f"{Fore.RED}Failed to execute tool via unbound method: {inner_e}")
                            else:
                                # It's a different TypeError, so report it as a primary error
                                print(f"{Fore.RED}Error executing tool '{name}': {e}")

                        except Exception as e:
                            print(
                                f"{Fore.RED}Error executing tool '{name}': {e}")
        else:
            print(
                Fore.RED + "YAML block found, but it doesn't match the expected format.")
            return response
