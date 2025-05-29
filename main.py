from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool
from unisonai import config

config.set_api_key("gemini", "Your API Key")


web_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Web Explorer",
    description="Web Searcher for multiple queries",
    tools=[WebSearchTool],
    verbose=False,
    history_folder="history",
    output_file="output.txt"
)

web_agent.unleash(task="Find out what is the current price of apple stocks")