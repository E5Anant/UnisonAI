"""
Basic Agent Example — UnisonAI

A minimal example: create an agent and run a single task.
"""

from unisonai import Agent
from unisonai.llms import Gemini

agent = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Assistant",
    description="A helpful AI assistant",
    verbose=True,
)

result = agent.unleash(task="Explain how photosynthesis works in 3 sentences.")
print(result)
