import sys
import os
from crewai import Agent, Task

# Add project root to python path for importing Config and Tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from tools.rag_tool import rag_tool
from tools.world_bank_tool import world_bank_tool

# Initialize LLM
llm = Config.get_llm()

# Define Agent
data_analyst_agent = Agent(
    role="Quantitative Development Data Analyst",
    goal="Extract statistics, quantitative trends, and empirical findings relevant to development policy queries.",
    backstory="You are a data analyst specializing in international development statistics. You have a keen eye for numbers, "
              "metrics, and quantitative indicators. You extract and cross-reference data from policy reports, "
              "World Bank indices, and census databases, ensuring each statistic has a clear source and year.",
    tools=[rag_tool, world_bank_tool],
    llm=llm,
    verbose=True
)

# Define Task
data_analyst_task = Task(
    description="Analyze the research findings collected for the query: '{query}'. "
                "Extract all relevant statistics, quantitative metrics, numerical trends, and quantitative findings. "
                "For each data point, you must cite the source and year. Identify any data gaps or missing metrics.",
    expected_output="A bullet-pointed list of statistical findings, each containing the numerical value, the indicator description, "
                    "the source, and the year. Include a section pointing out any identified data gaps.",
    agent=data_analyst_agent
)

if __name__ == "__main__":
    Config.validate()
    print("Data Analyst Agent and Task initialized successfully.")
