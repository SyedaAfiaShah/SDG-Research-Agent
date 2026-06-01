import sys
import os
from crewai import Agent, Task

# Add project root to python path for importing Config and Tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from tools.rag_tool import rag_tool

# Initialize LLM
llm = Config.get_llm()

# Define Agent
policy_analyst_agent = Agent(
    role="International Development Policy Specialist",
    goal="Identify policy gaps, evaluate implementation challenges, and propose opportunity areas based on literature.",
    backstory="You are a policy analyst with years of experience advising governments and NGOs. You specialize in translating "
              "empirical research and data into actionable policy frameworks. You analyze institutional barriers, policy gaps, "
              "and successful case studies to recommend practical interventions.",
    tools=[rag_tool],
    llm=llm,
    verbose=True
)

# Define Task
policy_analyst_task = Task(
    description="Review the research and statistical data compiled for the query: '{query}'. "
                "Analyze existing policies, best practices, and case studies in the knowledge base. "
                "Identify implementation challenges and policy gaps specific to the target context. "
                "Propose 3 to 5 actionable opportunity areas for intervention.",
    expected_output="A policy landscape summary detailing current gaps and institutional challenges, followed by a list of "
                    "3 to 5 clear, actionable opportunity areas.",
    agent=policy_analyst_agent
)

if __name__ == "__main__":
    Config.validate()
    print("Policy Analyst Agent and Task initialized successfully.")
