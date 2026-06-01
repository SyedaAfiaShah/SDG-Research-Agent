import sys
import os
from crewai import Agent, Task

# Add project root to python path for importing Config and Tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from tools.sdg_lookup_tool import sdg_lookup_tool
from tools.rag_tool import rag_tool

# Initialize LLM
llm = Config.get_llm()

# Define Agent
sdg_alignment_agent = Agent(
    role="SDG Framework Specialist",
    goal="Map development research findings to the UN Sustainable Development Goals (SDGs) and target indicators.",
    backstory="You are an expert on the United Nations 2030 Agenda. You know all 17 SDGs, their targets, and indicators "
              "inside out. You specialize in assessing how local development interventions align with global goals, "
              "determining primary and secondary SDG alignments for policy briefs.",
    tools=[sdg_lookup_tool, rag_tool],
    llm=llm,
    verbose=True
)

# Define Task
sdg_alignment_task = Task(
    description="Review the compiled findings and proposed opportunity areas for the query: '{query}'. "
                "Map these findings to the UN Sustainable Development Goals (SDGs). "
                "Identify the primary SDG and secondary SDGs. For each mapped goal, explain the specific connection "
                "and how the proposed policy recommendations will impact its target indicators.",
    expected_output="A structured mapping of SDGs, featuring a primary SDG and secondary SDGs, with a detailed "
                    "impact explanation and target indicator codes for each goal.",
    agent=sdg_alignment_agent
)

if __name__ == "__main__":
    Config.validate()
    print("SDG Alignment Agent and Task initialized successfully.")
