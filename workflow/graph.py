import sys
import os
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Add project root to python path for importing Config, Agents, and Tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from workflow.state import WorkflowState
from agents.research_agent import research_agent, research_task
from agents.data_analyst_agent import data_analyst_agent, data_analyst_task
from agents.policy_analyst_agent import policy_analyst_agent, policy_analyst_task
from agents.sdg_alignment_agent import sdg_alignment_agent, sdg_alignment_task
from agents.report_writer_agent import report_writer_agent, report_writer_task

from crewai import Crew

# Node 1: run_research
def run_research(state: WorkflowState):
    print("\n--- Node: Run Research ---")
    query = state["query"]
    retry_count = state.get("retry_count", 0)
    
    # If retry count > 0, expand the query instruction
    if retry_count > 0:
        query_input = f"{query} (Retry with broader search terms, verify literature, check academic/arXiv fallbacks)"
    else:
        query_input = query
        
    print(f"Executing Research Agent for query: '{query_input}' (Retry count: {retry_count})")
    
    crew = Crew(agents=[research_agent], tasks=[research_task], verbose=True)
    result = crew.kickoff(inputs={"query": query_input})
    
    raw_output = result.raw
    insufficient = "insufficient_evidence=True" in raw_output or "insufficient_evidence\": true" in raw_output.lower()
    
    return {
        "research_output": raw_output,
        "insufficient_evidence": insufficient,
        "retry_count": retry_count + 1
    }

# Node 3: run_data_analysis
def run_data_analysis(state: WorkflowState):
    print("\n--- Node: Run Data Analysis ---")
    # Feed previous findings to analyst context
    query_input = f"{state['query']}\n\n[Research Agent Findings]:\n{state['research_output']}"
    
    crew = Crew(agents=[data_analyst_agent], tasks=[data_analyst_task], verbose=True)
    result = crew.kickoff(inputs={"query": query_input})
    
    return {
        "data_analysis_output": result.raw
    }

# Node 4: run_policy_analysis
def run_policy_analysis(state: WorkflowState):
    print("\n--- Node: Run Policy Analysis ---")
    query_input = (
        f"{state['query']}\n\n"
        f"[Research Findings]:\n{state['research_output']}\n\n"
        f"[Data Analysis]:\n{state['data_analysis_output']}"
    )
    
    crew = Crew(agents=[policy_analyst_agent], tasks=[policy_analyst_task], verbose=True)
    result = crew.kickoff(inputs={"query": query_input})
    
    return {
        "policy_analysis_output": result.raw
    }

# Node 5: run_sdg_alignment
def run_sdg_alignment(state: WorkflowState):
    print("\n--- Node: Run SDG Alignment ---")
    query_input = (
        f"{state['query']}\n\n"
        f"[Research Findings]:\n{state['research_output']}\n\n"
        f"[Data Analysis]:\n{state['data_analysis_output']}\n\n"
        f"[Policy Analysis]:\n{state['policy_analysis_output']}"
    )
    
    crew = Crew(agents=[sdg_alignment_agent], tasks=[sdg_alignment_task], verbose=True)
    result = crew.kickoff(inputs={"query": query_input})
    
    return {
        "sdg_alignment_output": result.raw
    }

# Node 6: human_checkpoint
def human_checkpoint(state: WorkflowState):
    print("\n--- Node: Human Checkpoint ---")
    # We do not set human_approved here anymore; the UI will update the state.
    return {}

# Node 7: run_report_writer
def run_report_writer(state: WorkflowState):
    print("\n--- Node: Run Report Writer ---")
    query_input = (
        f"Query: {state['query']}\n\n"
        f"=== RESEARCH FINDINGS ===\n{state['research_output']}\n\n"
        f"=== DATA ANALYSIS ===\n{state['data_analysis_output']}\n\n"
        f"=== POLICY ANALYSIS ===\n{state['policy_analysis_output']}\n\n"
        f"=== SDG ALIGNMENT ===\n{state['sdg_alignment_output']}\n"
    )
    
    crew = Crew(agents=[report_writer_agent], tasks=[report_writer_task], verbose=True)
    result = crew.kickoff(inputs={"query": query_input})
    
    # Parse Pydantic output JSON
    import json
    policy_brief_dict = {}
    try:
        if result.json:
            if isinstance(result.json, dict):
                policy_brief_dict = result.json
            elif isinstance(result.json, str):
                policy_brief_dict = json.loads(result.json)
            else:
                # Could be a Pydantic model
                try:
                    policy_brief_dict = result.json.model_dump()
                except AttributeError:
                    try:
                        policy_brief_dict = dict(result.json)
                    except Exception:
                        policy_brief_dict = json.loads(str(result.json))
        else:
            # Fallback to parsing raw text
            policy_brief_dict = json.loads(result.raw)
    except Exception as e:
        print(f"Error parsing report writer JSON: {e}")
        # Try to find JSON block in raw output
        raw = result.raw
        try:
            start_idx = raw.find("{")
            end_idx = raw.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                policy_brief_dict = json.loads(raw[start_idx:end_idx])
            else:
                policy_brief_dict = {"error": "Failed to parse JSON", "raw": raw}
        except Exception as ex:
            policy_brief_dict = {"error": f"Failed to parse JSON: {ex}", "raw": raw}
            
    # Ensure it is a dictionary
    if isinstance(policy_brief_dict, str):
        try:
            policy_brief_dict = json.loads(policy_brief_dict)
        except Exception:
            pass
            
    return {
        "policy_brief": policy_brief_dict
    }

# Node 8: run_evaluation
def run_evaluation(state: WorkflowState):
    print("\n--- Node: Run Evaluation ---")
    from evaluation.evaluator import evaluate_brief
    
    context = (
        f"=== RESEARCH FINDINGS ===\n{state['research_output']}\n\n"
        f"=== DATA ANALYSIS ===\n{state['data_analysis_output']}\n\n"
        f"=== POLICY ANALYSIS ===\n{state['policy_analysis_output']}\n\n"
        f"=== SDG ALIGNMENT ===\n{state['sdg_alignment_output']}\n"
    )
    
    result = evaluate_brief(
        query=state["query"],
        context=context,
        brief=state["policy_brief"]
    )
    
    return {
        "evaluation_result": result.model_dump()
    }

# Build LangGraph Workflow
workflow = StateGraph(WorkflowState)

# Add Nodes
workflow.add_node("run_research", run_research)
workflow.add_node("run_data_analysis", run_data_analysis)
workflow.add_node("run_policy_analysis", run_policy_analysis)
workflow.add_node("run_sdg_alignment", run_sdg_alignment)
workflow.add_node("human_checkpoint", human_checkpoint)
workflow.add_node("run_report_writer", run_report_writer)
workflow.add_node("run_evaluation", run_evaluation)

# Add Edges
workflow.add_edge(START, "run_research")

# Check evidence quality
def check_evidence(state: WorkflowState):
    if state.get("insufficient_evidence") and state.get("retry_count", 0) <= 1:
        print("\n[Router] Insufficient evidence. Routing back to Research Node...")
        return "insufficient"
    print("\n[Router] Sufficient evidence or retry limit reached. Proceeding to Data Analysis...")
    return "sufficient"

workflow.add_conditional_edges(
    "run_research",
    check_evidence,
    {
        "insufficient": "run_research",
        "sufficient": "run_data_analysis"
    }
)

workflow.add_edge("run_data_analysis", "run_policy_analysis")
workflow.add_edge("run_policy_analysis", "run_sdg_alignment")
workflow.add_edge("run_sdg_alignment", "human_checkpoint")

# Check human approval
def check_human_approval(state: WorkflowState):
    if state.get("human_approved"):
        print("\n[Router] Human approved findings. Proceeding to Report Writer Node...")
        return "approved"
    print("\n[Router] Human rejected findings. Restarting research loop...")
    return "rejected"

workflow.add_conditional_edges(
    "human_checkpoint",
    check_human_approval,
    {
        "approved": "run_report_writer",
        "rejected": "run_research"
    }
)

workflow.add_edge("run_report_writer", "run_evaluation")
workflow.add_edge("run_evaluation", END)

# Compile graph with memory checkpointing and interrupt
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["run_report_writer"])

if __name__ == "__main__":
    Config.validate()
    print("LangGraph workflow compiled successfully.")
