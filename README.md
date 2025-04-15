

<div align="center">
Fork of the OG REPO [UnisonAI](https://github.com/UnisonAI/UnisonAI/)

![Logo of UnisonAI](https://github.com/UnisonAI/UnisonAI/blob/main/assets/UnisonAI_Banner.jpg)

[![License: MIT](https://img.shields.io/github/license/UnisonAI/UnisonAI?style=for-the-badge)](https://github.com/UnisonAI/UnisonAI/blob/main/LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/UnisonAI/UnisonAI?style=for-the-badge)](https://github.com/UnisonAI/UnisonAI/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/UnisonAI/UnisonAI?style=for-the-badge)](https://github.com/UnisonAI/UnisonAI/network/members)
[![GitHub issues](https://img.shields.io/github/issues/UnisonAI/UnisonAI?style=for-the-badge)](https://github.com/UnisonAI/UnisonAI/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/UnisonAI/UnisonAI?style=for-the-badge)](https://github.com/UnisonAI/UnisonAI/commits/main)

</div>
The UnisonAI Multi-Agent Framework provides a flexible and extensible environment for creating and coordinating multiple AI agents.

## Table of Contents
- [Overview](#overview)
- [Why UnisonAI?](#why-unisonai)
- [Installation](#installation)
- [Core Components](#core-components)
  - [Single_Agent](#single_agent)
  - [Agent](#agent)
  - [Clan](#clan)
  - [Tool System](#tool-system)
- [Parameter Reference Tables](#parameter-reference-tables)
  - [Single_Agent Parameters](#single_agent-parameters)
  - [Agent Parameters](#agent-parameters)
  - [Clan Parameters](#clan-parameters)
  - [BaseTool and Field](#basetool-and-field)
- [Usage Examples](#usage-examples)
- [FAQ](#faq)
- [Contributing and License](#contributing-and-license)


## Overview

The UnisonAI Multi-Agent Framework provides a flexible and extensible environment for creating and coordinating multiple AI agents. It supports a variety of large language models (LLMs) such as Cohere, Mixtral, Groq, Gemini, Grok, OpenAI, Anthropic, or even your custom LLM (by extending the `BaseLLM` class).

This framework differentiates between two primary agent types:
- **Single_Agent:** Used for standalone tasks. These agents operate independently, making them ideal for one-off or isolated tasks.
- **Agent (Clan Agents):** Designed to work as part of a team within a **Clan**. These agents collaborate under a manager (or leader) to accomplish complex, multi-step projects.

The framework also integrates custom tools to enhance agent capabilities, supporting tasks like web searches, time tracking, and more.


## Why UnisonAI?

UnisonAI is designed with flexibility and scalability in mind. Here are several reasons to choose UnisonAI:

- **Multi-LLM Support:** Seamlessly integrates a variety of LLM providers, giving you the freedom to choose or combine the best models for your needs.
- **Modular Design:** Easily extendable through custom tools and LLM integrations. Use the provided base classes to add your own logic.
- **Hierarchical Collaboration:** Whether you need a standalone agent or a coordinated team (Clan), the framework supports both paradigms.
- **Robust Parsing & Execution:** With built-in error handling (e.g., JSON fixing and YAML parsing), the framework is designed for real-world applications.
- **Ease of Use:** Clear separation of concerns and comprehensive documentation makes it straightforward to implement and extend.


## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. 

First, install UnisonAI using pip:

```shell
pip install unisonai
```
```shell
pip3 install unisonai
``` 

## Core Components

### Single_Agent

**Purpose:**  
The `Single_Agent` class is built to create and execute standalone agents that do not belong to any clan. These agents are ideal for independent tasks, where no inter-agent collaboration is required.

**Key Characteristics:**
- Independent execution.
- Maintains its own history and message logs.

### Agent

**Purpose:**  
The `Agent` class is used to create agents that work within a collaborative environment (a clan). They are designed to communicate with a manager (or CEO) and other agents, sharing plans and tasks.

**Key Characteristics:**
- Collaborative and interactive.
- Uses prompts tailored for agents within a team.
- Incorporates communication methods like sending messages to other agents.
- Supports tools for enhanced functionality.

### Clan

**Purpose:**  
The `Clan` class coordinates multiple `Agent` instances. It assigns a manager to oversee the team and defines a shared instruction set and overall goal.

**Key Characteristics:**
- Groups agents for coordinated task planning.
- Sets a unified goal and shared instructions.
- Manages history and output files for the entire team.

### Tool System

**Purpose:**  
Tools are extensions that agents can call to perform specific tasks. They are built on a common interface using the `BaseTool` class and `Field` class for parameters.

**Key Characteristics:**
- **BaseTool:** An abstract class that requires a `_run` method implementation.
- **Field:** Defines the input parameters for tools, including description, default value, and whether the field is required.

---

## Parameter Reference Tables

### Single_Agent Parameters

| **Parameter**      | **Type**  | **Description**                                                                 | **Default**     |
|--------------------|-----------|---------------------------------------------------------------------------------|-----------------|
| `llm`              | BaseLLM (or any LLM) | The language model instance to be used for task execution.             | _Required_      |
| `identity`         | String    | A unique identifier or name for the agent.                                      | _Required_      |
| `description`      | String    | A short description of the agent’s role or purpose.                             | _Required_      |
| `verbose`          | Boolean   | Flag to toggle verbose output for debugging.                                   | `True`          |
| `tools`            | List      | A list of tools (classes or instances) the agent can use.                        | `[]` (Empty)    |
| `output_file`      | String    | Path to a file where the final output should be saved.                         | `None`          |
| `history_folder`   | String    | Directory for storing history and log files.                                   | `"history"`     |

### Agent Parameters

| **Parameter**      | **Type**  | **Description**                                                                 | **Default**     |
|--------------------|-----------|---------------------------------------------------------------------------------|-----------------|
| `llm`              | Gemini (or any LLM) | The language model instance for the agent.                             | _Required_      |
| `identity`         | String    | Name/identifier for the agent.                                                 | _Required_      |
| `description`      | String    | Brief overview of the agent’s responsibilities.                                | _Required_      |
| `task`             | String    | A base task or goal that the agent should work towards.                        | _Required_      |
| `verbose`          | Boolean   | Determines if detailed logs should be printed.                                 | `True`          |
| `tools`            | List      | Tools available to the agent for task execution.                               | `[]` (Empty)    |

### Clan Parameters

| **Parameter**      | **Type**  | **Description**                                                                 | **Default**     |
|--------------------|-----------|---------------------------------------------------------------------------------|-----------------|
| `clan_name`        | String    | Name of the clan or group.                                                     | _Required_      |
| `manager`          | Agent     | The manager (or leader) of the clan who coordinates the tasks.                 | _Required_      |
| `members`          | List      | A list of `Agent` instances that form the clan.                                | _Required_      |
| `shared_instruction` | String  | Common instructions to be followed by all agents in the clan.                  | _Required_      |
| `goal`             | String    | The overall objective or task for the clan.                                    | _Required_      |
| `history_folder`   | String    | Folder where the clan’s history and logs will be stored.                       | default is `"history"`     |
| `output_file`      | String    | File to save the final consolidated output.                                   | `None`          |

### BaseTool and Field

#### BaseTool

| **Attribute/Method** | **Type** | **Description**                                      |
|----------------------|----------|------------------------------------------------------|
| `name`               | String   | Name of the tool.                                    |
| `description`        | String   | A brief description of what the tool does.           |
| `params`             | List     | List of `Field` objects defining the tool’s inputs.  |
| `_run(**kwargs)`     | Method   | The method that executes the tool's logic.           |

#### Field

| **Attribute**      | **Type**  | **Description**                                                              | **Default** |
|--------------------|-----------|------------------------------------------------------------------------------|-------------|
| `name`             | String    | Parameter name.                                                              | _Required_  |
| `description`      | String    | A description of the parameter’s purpose.                                    | _Required_  |
| `default_value`    | Any       | Default value if no input is provided.                                       | `None`      |
| `required`         | Boolean   | Whether the parameter is mandatory.                                        | `True`      |
| `format()`         | Method    | Returns a formatted string representation of the parameter.                | N/A         |

---

## Usage Examples

### Standalone Agent (Single_Agent)

In [`main.py`](https://github.com/UnisonAI/UnisonAI/blob/main/main.py), a standalone agent is created to perform a web search task:

```python
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool

web_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Web Explorer",
    description="Web Searcher for multiple queries",
    tools=[WebSearchTool],
    history_folder="history",
    output_file="output.txt"
)

web_agent.unleash(task="Find out what is the age of Trump")
```

### Clan-Based Agents

In [`main2.py`](https://github.com/UnisonAI/UnisonAI/blob/main/main2.py), multiple agents are created for a collaborative task (planning a trip) and are managed by a clan:

```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool

# Initialize agents with specific roles
time_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Time Keeper",
    description="Provides current time and scheduling details",
    task="Track time-related info for the trip",
    tools=[TimeTool]
)

web_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Web Explorer",
    description="Searches the web for travel info",
    task="Gather travel info, cultural activities, and costs",
    tools=[WebSearchTool]
)

# Other agents (weather, budget, transport, etc.) are initialized similarly...

# Create the Clan and assign a manager
clan = Clan(
    clan_name="Ultimate Trip Expert Clan",
    manager=planner_agent,  # This is the leader coordinating the plan
    members=[time_agent, web_agent, /* other agents */],
    shared_instruction="Collaborate to plan a budget-friendly 7-day trip in India.",
    goal="Plan a 7-day itinerary across multiple cities with a budget of 10,000 INR",
    history_folder="trip_history",
    output_file="trip_plan.txt"
)

# Unleash the clan to start planning
clan.unleash()
```

---

## FAQ

**Q: What is UnisonAI?**  
A: UnisonAI is a flexible framework that allows you to create and coordinate multiple AI agents using various large language models. It supports both standalone and collaborative (clan-based) agent execution.

**Q: Why should I use the Clan architecture?**  
A: The Clan architecture is ideal for complex tasks that require division of responsibilities. Each agent can specialize (e.g., web search, time tracking, weather updates) while a central manager coordinates efforts to achieve a common goal.

**Q: Can I integrate my own LLM?**  
A: Yes! The framework is designed to support multiple LLM providers. You can extend the `BaseLLM` class to integrate your own models, ensuring flexibility in deployment.

**Q: What are tools and how do they work?**  
A: Tools are modular extensions built on the `BaseTool` class. They enable agents to perform specific operations (e.g., web search, budget tracking) by defining input parameters via the `Field` class and executing logic through the `_run` method.

**Q: How do I track agent history and logs?**  
A: Both `Single_Agent` and `Agent` classes manage history via designated folders (e.g., `"history"`). The logs are stored as JSON files named after each agent's identity.

**Q: What kind of applications can I build?**  
A: The framework is ideal for building chatbots, planning tools, automation workflows, and any system where distributed decision-making and collaboration between multiple AI components are beneficial.

---

## Contributing and License

Founder - [@E5Anant](https://github.com/E5Anant)

Feel free to open issues, submit pull requests, or suggest improvements on the GitHub repository. The project is licensed under the MIT License.
