import sys
import argparse
import uuid
import json

# Force UTF-8 encoding for stdout and stderr on Windows to avoid cp1252 encoding crashes
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from config import Config

def main():
    print("=== SDG Research Agent CLI (Phase 1 Testing) ===")
    
    # Parse query inputs
    parser = argparse.ArgumentParser(description="Run the SDG Research Agent LangGraph workflow.")
    parser.add_argument(
        "--query", 
        type=str, 
        default="digital divide in rural Pakistan",
        help="The sustainability research query to analyze."
    )
    args = parser.parse_args()
    
    # Validate configurations
    try:
        Config.validate()
        print("Configuration validated successfully.")
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Import the workflow graph
    print("Loading LangGraph workflow...")
    from workflow.graph import app
    
    # Initialize the workflow state keys as specified
    initial_state = {
        "query": args.query,
        "research_output": "",
        "insufficient_evidence": False,
        "data_analysis_output": "",
        "policy_analysis_output": "",
        "sdg_alignment_output": "",
        "human_approved": False,
        "policy_brief": {},
        "evaluation_result": {},
        "error": None,
        "retry_count": 0
    }
    
    # Execution thread configuration
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\nStarting workflow invocation (Thread ID: {thread_id})...")
    try:
        final_state = app.invoke(initial_state, config)
        print("\n=== Workflow Run Completed ===")
        
        # Display key indicators
        print(f"\nFinal State Details:")
        print(f"  Insufficient Evidence Flag: {final_state.get('insufficient_evidence')}")
        print(f"  Retry Count: {final_state.get('retry_count')}")
        print(f"  Human Approved Flag: {final_state.get('human_approved')}")
        
        brief = final_state.get("policy_brief", {})
        print(f"\nGenerated Policy Brief Summary:")
        print(f"  Primary SDG: SDG {brief.get('primary_sdg', 'N/A')}")
        print(f"  Executive Summary: {brief.get('executive_summary', 'N/A')[:150]}...")
        print(f"  Evidence Quality Flag: {brief.get('evidence_quality_flag', 'N/A')}")
        
        # Display evaluation metrics
        eval_res = final_state.get("evaluation_result", {})
        print(f"\nLLM-as-Judge Evaluation Report:")
        print(f"  Score: {eval_res.get('score', 0.0)}")
        print(f"  Passed Validation: {eval_res.get('passed', False)}")
        print(f"  Factual Citations Count: {eval_res.get('factual_citations_count', 0)}")
        print("  Feedback Suggestions:")
        for idx, item in enumerate(eval_res.get("feedback", []), 1):
            print(f"    {idx}. {item}")
            
        # Write brief JSON to a log file for user inspect
        log_dir = "data"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "policy_brief_output.json")
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2)
        print(f"\nFull Policy Brief JSON written successfully to: [policy_brief_output.json](file:///{os.path.abspath(log_file).replace(chr(92), '/')})")
        
    except Exception as e:
        print(f"Workflow execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
