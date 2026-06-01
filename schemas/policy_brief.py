from pydantic import BaseModel
from typing import List

class SDGMapping(BaseModel):
    sdg_number: int
    sdg_name: str
    relevance_explanation: str
    expected_impact: str

class PolicyRecommendation(BaseModel):
    title: str
    description: str
    priority: str  # HIGH / MEDIUM / LOW
    implementation_timeframe: str  # Short-term / Medium-term / Long-term

class Reference(BaseModel):
    title: str
    source: str
    year: int | None
    url: str | None

class PolicyBrief(BaseModel):
    query: str
    executive_summary: str
    key_findings: List[str]
    statistical_evidence: List[str]
    policy_recommendations: List[PolicyRecommendation]
    sdg_mappings: List[SDGMapping]
    primary_sdg: int
    references: List[Reference]
    evidence_quality_flag: str  # SUFFICIENT / INSUFFICIENT
