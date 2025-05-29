from typing import Any
from unisonai.prompts.plan import PLAN_PROMPT
from unisonai.agent import Agent
import re
import os
import colorama
colorama.init(autoreset=True)


def create_members(members: list[Any]):
    formatted_members = """"""
    for member in members:
        formatted_members += f"-{members.index(member)+1}: \n"
        formatted_members += "  ROLE: " + member.identity + "\n"
        formatted_members += "  DESCRIPTION: " + member.description + "\n"
        formatted_members += "  GOAL: " + member.task + "\n"
    return formatted_members


class Clan:
    def __init__(self, clan_name: str, manager: Agent, members: list[Agent], shared_instruction: str, goal: str, history_folder: str = "history", output_file: str = None):
        self.clan_name = clan_name
        self.goal = goal
        self.shared_instruction = shared_instruction
        self.manager = manager
        self.members = members
        self.output_file = output_file
        self.history_folder = history_folder
        self.manager.ask_user = True
        os.makedirs(self.history_folder, exist_ok=True)
        if self.output_file is not None:
            open(self.output_file, "w", encoding="utf-8").close()
        formatted_members = """"""
        for member in self.members:
            member.history_folder = self.history_folder
            member.shared_instruction = self.shared_instruction
            member.user_task = self.goal
            member.output_file = self.output_file
            member.clan_name = self.clan_name
            if member == self.manager:
                formatted_members += f"-MEMBER {member.identity} Post: (Manager/CEO): \n"
                formatted_members += "  NAME: " + member.identity + "\n"
                formatted_members += "  DESCRIPTION: " + member.description + "\n"
                formatted_members += "  GOAL: " + member.task + "\n"
            else:
                formatted_members += f"-MEMBER {member.identity}: \n"
                formatted_members += "  NAME: " + member.identity + "\n"
                formatted_members += "  DESCRIPTION: " + member.description + "\n"
                formatted_members += "  GOAL: " + member.task + "\n"

            member.members = formatted_members
            member.rawmembers = self.members
            self.formatted_members = formatted_members

    def unleash(self):
        self.manager.llm.reset()
        # self.manager.llm.__init__(system_prompt=PLAN_PROMPT.format(members=self.members))
        response = self.manager.llm.run(PLAN_PROMPT.format(
            members=self.formatted_members,
            client_task=self.goal
        ) + "\n\n" + "Make a plan To acomplish this task: \n" + self.goal)
        print(colorama.Fore.LIGHTCYAN_EX+"Status: Planing...\n\n" +
              colorama.Fore.LIGHTYELLOW_EX + response)
        # remove the <think> and </think> and all its content
        response = re.sub(r"<think>(.*?)</think>", "",
                          response, flags=re.DOTALL)
        self.manager.llm.reset()
        for member in self.members:
            member.plan = response

        self.manager.unleash(self.goal)
