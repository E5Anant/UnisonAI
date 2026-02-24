"""
Clan Coordination Example — UnisonAI

A research team of three agents — researcher, analyst, writer —
collaborating on a report via A2A messaging.
"""

from unisonai import Agent, Clan
from unisonai.llms import Gemini
from unisonai.tools.tool import tool


@tool(name="research_tool", description="Gather research findings on a topic")
def research_tool(topic: str, depth: str = "detailed") -> str:
    """Simulated research — returns key findings."""
    return (
        f"Research on '{topic}' ({depth}):\n"
        f"1. {topic} is growing rapidly in recent years.\n"
        f"2. Key players include major tech companies.\n"
        f"3. Regulatory frameworks are still evolving.\n"
        f"4. Adoption is accelerating in healthcare and finance."
    )


@tool(name="analysis_tool", description="Analyze and summarize research data")
def analysis_tool(data: str, analysis_type: str = "qualitative") -> str:
    """Simulated analysis — extracts insights."""
    return (
        f"Analysis ({analysis_type}):\n"
        f"- Strong upward trend identified.\n"
        f"- Key gap: lack of standardized regulations.\n"
        f"- Recommendation: invest in R&D and compliance early."
    )


# ── Agents ──────────────────────────────────────────────────────────────

researcher = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Researcher",
    description="Expert information gatherer",
    task="Research assigned topics thoroughly",
    tools=[research_tool()],
)

analyst = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Analyst",
    description="Data analyst who extracts insights from research",
    task="Analyze research findings and identify patterns",
    tools=[analysis_tool()],
)

writer = Agent(
    llm=Gemini(model="gemini-2.5-flash"),
    identity="Writer",
    description="Technical writer who produces clear reports",
    task="Synthesize research and analysis into a polished report",
)

# ── Clan ────────────────────────────────────────────────────────────────

clan = Clan(
    clan_name="Research Team",
    manager=researcher,
    members=[researcher, analyst, writer],
    shared_instruction=(
        "1. Researcher gathers information.\n"
        "2. Analyst interprets findings.\n"
        "3. Writer produces the final report."
    ),
    goal="Produce a brief report on AI adoption in healthcare.",
    output_file="research_report.txt",
)

clan.unleash()
