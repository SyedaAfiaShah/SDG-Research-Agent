import sys
import os
from crewai import Agent, Task

# Add project root to python path for importing Config and Schemas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from schemas.policy_brief import PolicyBrief

# Initialize LLM
llm = Config.get_llm()

# Define Agent
report_writer_agent = Agent(
    role="Policy Brief Writer",
    goal="Synthesize all analyst findings into a formal, structured, and evidence-grounded policy brief.",
    backstory="You are a professional report writer and policy editor. You write clear, concise, and highly persuasive "
              "policy briefs for senior officials and executives. Your writing is strictly objective and grounded "
              "in evidence. You never make claims without citing a source from the research and data provided to you.",
    tools=[],  # Synthesis only
    llm=llm,
    verbose=True
)

# Define Task
report_writer_task = Task(
    description="Synthesize the outputs from the Research, Data Analyst, Policy Analyst, and SDG Alignment agents "
                "regarding the query: '{query}'. "
                "Compile these findings into a cohesive, formal policy brief. "
                "Every single claim, recommendation, or statistic must cite its source (document name, page number, "
                "or API reference). Do not invent any new information or pull external knowledge not provided by prior agents. "
                "Your output must strictly conform to the PolicyBrief Pydantic schema structure.",
    expected_output="A JSON object matching the PolicyBrief Pydantic schema, filled with the synthesized policy brief contents.",
    agent=report_writer_agent,
    output_json=PolicyBrief  # Forces output to conform to PolicyBrief Pydantic schema
)

if __name__ == "__main__":
    Config.validate()
    print("Report Writer Agent and Task initialized successfully.")
