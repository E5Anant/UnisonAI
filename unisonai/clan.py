from .prompts.plan import PLAN_PROMPT
from .agent import Agent
from typing import List
import re
import os
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


class Clan:
    """Coordinate multiple agents to accomplish a shared goal."""

    def __init__(
        self,
        clan_name: str,
        manager: Agent,
        members: List[Agent],
        shared_instruction: str,
        goal: str,
        history_folder: str = "history",
        output_file: str = None,
    ):
        self.clan_name = clan_name
        self.goal = goal
        self.shared_instruction = shared_instruction
        self.manager = manager
        self.members = members
        self.output_file = output_file
        self.history_folder = history_folder

        # Manager is the coordinator
        self.manager.ask_user = True
        os.makedirs(self.history_folder, exist_ok=True)

        if self.output_file is not None:
            open(self.output_file, "w", encoding="utf-8").close()

        # Wire every member into the clan
        formatted_members = ""
        for member in self.members:
            member.clan_connected = True
            member.history_folder = self.history_folder
            member.shared_instruction = self.shared_instruction
            member.user_task = self.goal
            member.output_file = self.output_file
            member.clan_name = self.clan_name

            label = f"{member.identity} (Manager)" if member == self.manager else member.identity
            formatted_members += f"- {label}: {member.description}\n"

            member.members = formatted_members
            member.rawmembers = self.members

        self.formatted_members = formatted_members

    def unleash(self):
        """Plan the work, then hand execution to the manager agent."""
        self.manager.llm.reset()

        # ── Planning phase ──
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Clan: {self.clan_name}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Goal: {self.goal}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}Planning...{Style.RESET_ALL}")

        plan_prompt = (
            PLAN_PROMPT.format(members=self.formatted_members, client_task=self.goal)
            + "\n\nCreate a plan to accomplish this task:\n"
            + self.goal
        )
        response = self.manager.llm.run(plan_prompt)

        # Clean up plan text
        plan_text = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        plan_text = re.sub(r"<[^>]+>", "", plan_text).strip()

        # Display plan concisely
        print(f"\n{Fore.YELLOW}Plan:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{plan_text}{Style.RESET_ALL}")

        # Distribute plan to all members
        self.manager.llm.reset()
        for member in self.members:
            member.plan = plan_text

        # ── Execution phase ──
        print(f"\n{Fore.GREEN}Executing...{Style.RESET_ALL}\n")
        self.manager.unleash(self.goal)
