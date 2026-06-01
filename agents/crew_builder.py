import sys
import os
from crewai import Crew, Process

# Add project root to python path for importing Config and Agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Import agents and tasks
from agents.research_agent import research_agent, research_task
from agents.data_analyst_agent import data_analyst_agent, data_analyst_task
from agents.policy_analyst_agent import policy_analyst_agent, policy_analyst_task
from agents.sdg_alignment_agent import sdg_alignment_agent, sdg_alignment_task
from agents.report_writer_agent import report_writer_agent, report_writer_task

def build_sdg_crew() -> Crew:
    """
    Assembles and returns the CrewAI Crew for the SDG Research Agent pipeline.
    """
    # Create the crew
    crew = Crew(
        agents=[
            research_agent,
            data_analyst_agent,
            policy_analyst_agent,
            sdg_alignment_agent,
            report_writer_agent
        ],
        tasks=[
            research_task,
            data_analyst_task,
            policy_analyst_task,
            sdg_alignment_task,
            report_writer_task
        ],
        process=Process.sequential,
        verbose=True
    )
    return crew

if __name__ == "__main__":
    Config.validate()
    print("Building crew...")
    crew = build_sdg_crew()
    print("Crew successfully assembled.")
