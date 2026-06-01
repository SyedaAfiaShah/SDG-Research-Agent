from typing import TypedDict, Dict, Any, Optional

class WorkflowState(TypedDict):
    query: str
    research_output: str
    insufficient_evidence: bool
    data_analysis_output: str
    policy_analysis_output: str
    sdg_alignment_output: str
    human_approved: bool
    policy_brief: Dict[str, Any]
    evaluation_result: Dict[str, Any]
    error: Optional[str]
    # Internal trackers (helper keys)
    retry_count: int
