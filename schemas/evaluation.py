from pydantic import BaseModel, Field

class DimensionScore(BaseModel):
    score: int = Field(description="Score between 1 and 5.")
    justification: str = Field(description="A one-sentence justification for the score.")

class EvaluationResult(BaseModel):
    factual_grounding: DimensionScore
    hallucination_risk: DimensionScore
    sdg_relevance: DimensionScore
    recommendation_quality: DimensionScore
    completeness: DimensionScore
    overall_score: float
    quality_warning: bool
