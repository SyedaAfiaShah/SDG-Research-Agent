import sys
import os
from crewai import Agent, Task

# Add project root to python path for importing Config and Tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from tools.rag_tool import rag_tool
from tools.world_bank_tool import world_bank_tool
from tools.semantic_scholar_tool import semantic_scholar_tool

# Initialize LLM
llm = Config.get_llm()

# Define Agent
research_agent = Agent(
    role="Senior Development Research Analyst",
    goal="Retrieve and synthesize evidence from local literature and external API databases on development queries.",
    backstory="You are a seasoned international development researcher. Your specialty is fact-finding and evidence-gathering. "
              "You search public literature, databases, and policy papers, evaluating the quality of source materials "
              "and systematically citing evidence to support policy-making.",
    tools=[rag_tool, world_bank_tool, semantic_scholar_tool],
    llm=llm,
    verbose=True
)

# Define Task
research_task = Task(
    description="Given the query: '{query}', retrieve 5 to 8 relevant pieces of evidence from the local knowledge base "
                "and external APIs (World Bank, Academic Search). "
                "You must evaluate and explicitly flag the quality of each evidence piece as HIGH, MEDIUM, or LOW. "
                "Citations must include the document title/source and page number/year. "
                "If fewer than 3 HIGH quality sources are found, you must explicitly flag 'insufficient_evidence=True' in your output.",
    expected_output="A structured summary of collected evidence. Each evidence piece must have its source citation "
                    "and a quality flag (HIGH/MEDIUM/LOW). If applicable, state if 'insufficient_evidence=True'.",
    agent=research_agent
)

if __name__ == "__main__":
    Config.validate()
    print("Research Agent and Task initialized successfully.")
