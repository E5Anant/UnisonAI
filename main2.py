import datetime
from unisonai import Agent
from unisonai import Clan
from unisonai import BaseTool, Field
from unisonai.tools.websearch import WebSearchTool
from unisonai.llms import Gemini
from unisonai import config

config.set_api_key("gemini", "Your API Key")



# Custom Tool 1: Time Tool
class TimeTool(BaseTool):
    name = "Time Tool"
    description = "Get the current date and time in a specified format."
    params = [Field(name="format", description="The format of the date and time.", default_value="%Y-%m-%d %H:%M:%S", required=True)]

    def _run(format: str = "%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.now().strftime(format)

# Custom Tool 2: Weather Tool (Simulated for this example)
class WeatherTool(BaseTool):
    name = "Weather Tool"
    description = "Get the current weather for a given city in India."
    params = [Field(name="city", description="The city to check weather for.", required=True)]

    def _run(city: str):
        # Simulated weather response (in reality, this would call an API)
        return f"Current weather in {city}: 28°C, partly cloudy (simulated)."

# Custom Tool 3: Budget Tracker Tool
class BudgetTrackerTool(BaseTool):
    name = "Budget Tracker"
    description = "Track and update the remaining budget for the trip."
    params = [
        Field(name="initial_budget", description="The starting budget in INR.", required=True),
        Field(name="expense", description="The amount spent in INR.", default_value=0, required=False)
    ]

    def __init__(self):
        self.remaining_budget = 0

    def _run(self, initial_budget: float, expense: float = 0):
        if expense == 0:
            self.remaining_budget = initial_budget
            return f"Budget initialized at {initial_budget} INR."
        self.remaining_budget -= expense
        return f"Spent {expense} INR. Remaining budget: {self.remaining_budget} INR."

# Custom Tool 4: Transport Cost Estimator
class TransportCostTool(BaseTool):
    name = "Transport Cost Estimator"
    description = "Estimate transportation costs between two cities in India."
    params = [
        Field(name="from_city", description="Starting city.", required=True),
        Field(name="to_city", description="Destination city.", required=True),
        Field(name="mode", description="Mode of transport (train/bus/auto).", default_value="train", required=False)
    ]

    def _run(from_city: str, to_city: str, mode: str = "train"):
        # Simulated costs
        costs = {"train": 200, "bus": 150, "auto": 50}
        cost = costs.get(mode, 200)
        return f"Estimated {mode} cost from {from_city} to {to_city}: {cost} INR (simulated)."

# Agent 1: Time Agent
time_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Time Keeper",
    description="Provide the current date, time, and schedule timing for trip activities.",
    task="Track and report time-related information for the trip.",
    tools=[TimeTool]
)

# Agent 2: Web Search Agent
web_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Web Explorer",
    description="Search the web for travel info, food options, and cultural activities.",
    task="Gather information from the web about destinations, costs, and local experiences.",
    tools=[WebSearchTool]
)

# Agent 3: Weather Agent
weather_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Weather Forecaster",
    description="Check weather conditions for trip destinations.",
    task="Provide weather updates for each day of the trip.",
    tools=[WeatherTool]
)

# Agent 4: Budget Agent
budget_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Budget Manager",
    description="Track and manage the trip budget, ensuring it stays within 10,000 INR.",
    task="Monitor expenses and alert if budget exceeds.",
    tools=[BudgetTrackerTool]
)

# Agent 5: Transport Agent
transport_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Transport Coordinator",
    description="Plan transportation between cities and estimate costs.",
    task="Organize travel logistics between destinations.",
    tools=[TransportCostTool]
)

# Agent 6: Food Agent
food_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Food Critic",
    description="Suggest affordable local food options and eateries for each day.",
    task="Plan meals within budget and recommend where to eat.",
    tools=[WebSearchTool]
)

# Agent 7: Planner Agent (Manager)
planner_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Master Planner",
    description="Coordinate all agents to create a cohesive 7-day trip plan.",
    task="Develop a detailed 7-day trip itinerary for India within 10,000 INR.",
    tools=[]
)

# Create the Clan
clan = Clan(
    manager=planner_agent,
    members=[time_agent, web_agent, weather_agent, budget_agent, transport_agent, food_agent, planner_agent],
    shared_instruction="You are part of a Trip Planning team. Collaborate to create a detailed 7-day trip plan in India with a budget of 10,000 INR. Include daily itineraries, transportation, weather considerations, food options with eatery names, and cultural activities. Ensure the plan is practical and budget-friendly.",
    goal="Plan a 7-day trip across India (Delhi, Agra, Jaipur, Varanasi, Mumbai, Goa, and back) with a budget of 10,000 INR. Provide a detailed breakdown of each day including activities, transportation, food (what to eat and where), and weather updates.",
    history_folder="trip_history",
    clan_name="Ultimate Trip Expert Clan",
    output_file="trip_plan.txt"
)

# Unleash the Clan
clan.unleash()