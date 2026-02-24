from .llms import Gemini
from .prompts.agent import AGENT_PROMPT
from .prompts.manager import MANAGER_PROMPT
from .prompts.individual import INDIVIDUAL_PROMPT
from .async_helper import run_async_from_sync
import inspect
import re
import ast
import colorama
from colorama import Fore, Style
from typing import Any
import json
import os
import difflib

colorama.init(autoreset=True)


def create_tools(tools: list):
    """Format tools into clear function signatures the LLM can understand."""
    tool_cards = []

    for tool in tools:
        tool_instance = tool if not isinstance(tool, type) else tool()

        # Build a Python-style signature from params
        sig_parts = []
        if hasattr(tool_instance, 'params'):
            for field in tool_instance.params:
                type_str = field.field_type.value
                if field.required:
                    sig_parts.append(f'{field.name}: {type_str}')
                else:
                    default = repr(field.default_value) if field.default_value is not None else "None"
                    sig_parts.append(f'{field.name}: {type_str} = {default}')

        signature = f"{tool_instance.name}({', '.join(sig_parts)})"

        # Build param docs
        param_lines = []
        if hasattr(tool_instance, 'params'):
            for field in tool_instance.params:
                req = "required" if field.required else "optional"
                param_lines.append(f"  - {field.name} ({field.field_type.value}, {req}): {field.description}")

        card = f"{signature}\n  {tool_instance.description}"
        if param_lines:
            card += "\n" + "\n".join(param_lines)
        tool_cards.append(card)

    return "\n\n".join(tool_cards) if tool_cards else "No tools available."


class Agent:
    def __init__(self,
                 llm: Gemini,
                 identity: str,
                 description: str,
                 task: str = "",
                 verbose: bool = True,
                 tools: list[Any] = [],
                 output_file: str = None,
                 history_folder: str = "."):
        self.llm = llm
        self.identity = identity
        self.description = description
        self.task = task
        self.plan = None
        self.output_file = output_file
        self.clan_connected = False

        self.history_folder = history_folder

        self.rawtools = tools
        self.tools = create_tools(tools)
        self.ask_user = False
        self.user_task = None
        self.shared_instruction = None
        self.rawmembers = []
        self.members = ""
        self.clan_name = ""
        self.verbose = verbose

        if not self.clan_connected and self.history_folder != ".":
            os.makedirs(self.history_folder, exist_ok=True)

    # ── Clan helpers ──

    def _get_agent_by_name(self, agent_name: str):
        """Fuzzy-match an agent name from the clan roster."""
        ceo_variations = ["ceo", "manager", "ceo/manager", "ceo-manager", "ceo manager"]
        clean = agent_name.lower().strip()
        for prefix in ["agent ", " agent", "the "]:
            clean = clean.replace(prefix, "")
        if clean in ceo_variations:
            return "CEO/Manager"
        names = [m.identity for m in self.rawmembers]
        names_lower = [n.lower() for n in names]
        if clean in names_lower:
            return names[names_lower.index(clean)]
        matches = difflib.get_close_matches(clean, names_lower, n=1, cutoff=0.6)
        if matches:
            return names[names_lower.index(matches[0])]
        return agent_name

    def send_message(self, agent_name: str, message: str, additional_resource: str = None, sender: str = None):
        """Route a message to another agent in the clan."""
        matched = self._get_agent_by_name(agent_name)
        if self.verbose:
            print(f"{Fore.CYAN}  → message to {Style.BRIGHT}{matched}{Style.RESET_ALL}")

        msg = f"FROM: {sender} | {message}"
        if additional_resource:
            msg += f"\nRESOURCE: {additional_resource}"

        is_manager = matched in ["CEO/Manager", "Manager", "CEO"]
        for member in self.rawmembers:
            if is_manager and member.ask_user:
                member.unleash(msg)
                return f"Message delivered to {matched}."
            elif member.identity == matched:
                member.unleash(msg)
                return f"Message delivered to {matched}."

        return f"Agent '{agent_name}' not found in clan."

    # ── Tool parsing ──

    def extract_all_tool_calls(self, content):
        """Extract all <tool>...</tool> blocks from a response."""
        return [m.strip() for m in re.findall(r"<tool>(.*?)</tool>", content, re.DOTALL)]

    @staticmethod
    def _escape_string_newlines(s: str) -> str:
        """Escape literal newlines *inside* string arguments; replace those outside with spaces."""
        out = []
        i, n = 0, len(s)
        in_str = False
        qchar = None
        while i < n:
            ch = s[i]
            if in_str:
                if ch == '\\' and i + 1 < n:          # keep escape sequences intact
                    out.append(ch + s[i + 1])
                    i += 2
                    continue
                if ch == qchar:                        # closing quote
                    in_str = False
                    out.append(ch)
                elif ch in '\r\n':                     # literal newline → escape it
                    if ch == '\r' and i + 1 < n and s[i + 1] == '\n':
                        i += 1
                    out.append('\\n')
                else:
                    out.append(ch)
            else:
                if ch in '"\'':
                    in_str = True
                    qchar = ch
                    out.append(ch)
                elif ch in '\r\n':                     # outside string → space
                    if ch == '\r' and i + 1 < n and s[i + 1] == '\n':
                        i += 1
                    out.append(' ')
                else:
                    out.append(ch)
            i += 1
        return ''.join(out)

    def _sanitize_tool_call(self, raw: str) -> str:
        """Try multiple repair strategies so ast.parse can handle common LLM quirks.

        Handles: multi-line string args, missing closing paren/quote,
        stray whitespace between arguments, and other minor formatting issues.
        """
        s = raw.strip()

        # 1. Already valid
        try:
            ast.parse(s, mode='eval')
            return s
        except SyntaxError:
            pass

        # 2. Escape newlines inside strings, collapse those outside to spaces
        fixed = self._escape_string_newlines(s)
        try:
            ast.parse(fixed, mode='eval')
            return fixed
        except SyntaxError:
            pass

        # 3. Brute-force collapse all whitespace (lossy for in-string newlines)
        collapsed = ' '.join(s.split())
        try:
            ast.parse(collapsed, mode='eval')
            return collapsed
        except SyntaxError:
            pass

        # 4. Fix missing closing parentheses
        for candidate in (fixed, collapsed):
            diff = candidate.count('(') - candidate.count(')')
            if diff > 0:
                attempt = candidate + ')' * diff
                try:
                    ast.parse(attempt, mode='eval')
                    return attempt
                except SyntaxError:
                    pass

        # 5. Fix missing closing quote + paren
        for q in ('"', "'"):
            for candidate in (fixed, collapsed):
                attempt = candidate + q + ')'
                try:
                    ast.parse(attempt, mode='eval')
                    return attempt
                except SyntaxError:
                    pass

        # 6. Strip markdown backtick wrappers
        stripped = re.sub(r'`([^`]*)`', r'\1', s)
        if stripped != s:
            stripped = self._escape_string_newlines(stripped)
            try:
                ast.parse(stripped, mode='eval')
                return stripped
            except SyntaxError:
                pass

        return s  # give up; let the caller's except clause handle it

    def execute_tool_call(self, tool_call_str):
        """Parse a Python-style function call string and execute it safely."""
        try:
            clean = self._sanitize_tool_call(tool_call_str)
            tree = ast.parse(clean, mode='eval')
            if not isinstance(tree.body, ast.Call):
                return f"Error: not a valid function call."

            func_name = tree.body.func.id if hasattr(tree.body.func, 'id') else str(tree.body.func.attr)
            args = [ast.literal_eval(a) for a in tree.body.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in tree.body.keywords}

            # ── Built-in tools ──
            if func_name == "send_message":
                return self.send_message(
                    kwargs.get("agent_name"), kwargs.get("message"),
                    kwargs.get("additional_resource"), sender=self.identity
                )

            if func_name == "ask_user":
                q = kwargs.get("question", "What would you like?")
                if self.verbose:
                    print(f"{Fore.YELLOW}  ? {q}{Style.RESET_ALL}")
                answer = input(f"{Fore.CYAN}  You: {Style.RESET_ALL}")
                return f"User answered: {answer}"

            if func_name == "pass_result":
                return ("__PASS_RESULT__", kwargs.get("result", ""))

            # ── User-defined tools ──
            for tool in self.rawtools:
                inst = tool if not isinstance(tool, type) else tool()
                if inst.name == func_name:
                    if inspect.iscoroutinefunction(inst._run):
                        return run_async_from_sync(inst._run(*args, **kwargs))
                    return inst._run(*args, **kwargs)

            return f"Error: tool '{func_name}' not found."

        except Exception as e:
            return f"Error: {e}"

    # ── Verbose helpers ──

    def _print_think(self, text):
        print(f"\n{Fore.MAGENTA}<think>{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{text}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}</think>{Style.RESET_ALL}")

    def _print_tool(self, call, result):
        print(f"\n{Fore.GREEN}<tool>{call}</tool>{Style.RESET_ALL}")
        display = str(result) if len(str(result)) < 300 else str(result)[:297] + "..."
        print(f"{Fore.LIGHTBLACK_EX}↳ {display}{Style.RESET_ALL}")

    def _print_answer(self, text):
        print(f"\n{Fore.YELLOW}Response:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{text}{Style.RESET_ALL}")

    # ── Build tool section for prompt ──

    def _build_tools_section(self):
        """Build the full tools section, including built-in clan tools when connected."""
        sections = self.tools if self.tools else "No tools available."
        if self.clan_connected:
            builtins = (
                'send_message(agent_name: string, message: string)\n'
                '  Send a message to another agent in the clan.\n'
                '  - agent_name (string, required): Name of the target agent\n'
                '  - message (string, required): Message content\n\n'
                'pass_result(result: string)\n'
                '  Deliver the final result to the user. Call this when the task is complete.\n'
                '  - result (string, required): The final output to deliver'
            )
            if self.ask_user:
                builtins += (
                    '\n\nask_user(question: string)\n'
                    '  Ask the user a clarifying question.\n'
                    '  - question (string, required): The question to ask'
                )
            if sections and sections != "No tools available.":
                sections = sections + "\n\n" + builtins
            else:
                sections = builtins
        return sections

    # ── Core loop ──

    def unleash(self, task: str):
        self.user_task = task
        folder = self.history_folder

        # Load history
        try:
            with open(f"{folder}/{self.identity}.json", "r", encoding="utf-8") as f:
                data = f.read()
                self.messages = json.loads(data) if data.strip() else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.messages = []

        self.llm.reset()

        # Build system prompt
        tools_section = self._build_tools_section()

        if self.clan_connected:
            template = MANAGER_PROMPT if self.ask_user else AGENT_PROMPT
            system_prompt = template.format(
                identity=self.identity,
                description=self.description,
                task=self.task,
                tools=tools_section,
                user_task=task,
                shared_instruction=self.shared_instruction or "",
                members=self.members,
                plan=self.plan or "",
                clan_name=self.clan_name
            )
        else:
            system_prompt = INDIVIDUAL_PROMPT.format(
                identity=self.identity,
                description=self.description,
                user_task=self.user_task,
                tools=tools_section,
            )

        # Re-init LLM with prompt
        self.llm.__init__(
            messages=self.messages,
            model=self.llm.model,
            temperature=self.llm.temperature,
            system_prompt=system_prompt,
            max_tokens=self.llm.max_tokens,
            verbose=self.llm.verbose,
            api_key=getattr(self.llm, 'api_key', None)
        )

        if self.verbose:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}[{self.identity}]{Style.RESET_ALL} {Fore.BLUE}{task}{Style.RESET_ALL}")

        # ── Agentic loop ──
        max_turns = 10
        current_input = task
        for turn in range(max_turns):
            response = self.llm.run(current_input, save_messages=True)

            # Save history
            try:
                os.makedirs(folder, exist_ok=True)
                with open(f"{folder}/{self.identity}.json", "w", encoding="utf-8") as f:
                    json.dump(self.llm.messages, f, indent=2)
            except Exception:
                pass

            # Show thinking
            if self.verbose:
                think = re.search(r"<think>(.*?)</think>", response, re.DOTALL)
                if think:
                    self._print_think(think.group(1).strip())

            # Extract tool calls
            tool_calls = self.extract_all_tool_calls(response)

            if not tool_calls:
                # No tools → final answer
                answer = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
                if self.verbose:
                    self._print_answer(answer)
                if self.output_file:
                    with open(self.output_file, "w", encoding="utf-8") as f:
                        f.write(answer)
                return answer

            # Execute each tool call
            tool_outputs = []
            for call in tool_calls:
                result = self.execute_tool_call(call)

                # Handle pass_result → terminate immediately
                if isinstance(result, tuple) and result[0] == "__PASS_RESULT__":
                    final = result[1]
                    if self.verbose:
                        self._print_answer(final)
                    if self.output_file:
                        with open(self.output_file, "w", encoding="utf-8") as f:
                            f.write(str(final))
                    return final

                if self.verbose:
                    self._print_tool(call, result)

                tool_outputs.append(f"Tool `{call}` returned:\n{result}")

            # Feed results back
            current_input = "\n\n".join(tool_outputs)

        # Exhausted turns
        if self.verbose:
            print(f"{Fore.RED}Max turns ({max_turns}) reached.{Style.RESET_ALL}")
        return response
