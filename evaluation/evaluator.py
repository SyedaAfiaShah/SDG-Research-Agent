import os
import sys
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Add project root to python path for importing Config, Schemas, and Prompts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from schemas.evaluation import DimensionScore, EvaluationResult
from evaluation.prompts import EVALUATION_PROMPT

# Intermediate Pydantic schema for structured LLM response output
class LLMEvalOutput(BaseModel):
    factual_grounding: DimensionScore = Field(description="Evaluation of factual grounding.")
    hallucination_risk: DimensionScore = Field(description="Evaluation of hallucination risk.")
    sdg_relevance: DimensionScore = Field(description="Evaluation of SDG relevance.")
    recommendation_quality: DimensionScore = Field(description="Evaluation of recommendation quality.")
    completeness: DimensionScore = Field(description="Evaluation of completeness.")

def evaluate_brief(query: str, context: str, brief: dict) -> EvaluationResult:
    """
    Evaluates a generated PolicyBrief JSON against the raw agent outputs (context)
    and query across 5 dimensions.
    Returns an EvaluationResult Pydantic model.
    """
    load_dotenv()
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    # Initialize the LLM
    try:
        llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.0
        )
        
        # Request structured output matching LLMEvalOutput
        structured_llm = llm.with_structured_output(LLMEvalOutput)
        
        # Format the brief JSON
        import json
        brief_str = json.dumps(brief, indent=2)
        
        # Render prompt
        prompt = EVALUATION_PROMPT.format(
            query=query,
            context=context,
            brief=brief_str
        )
        
        # Invoke LLM
        raw_eval = structured_llm.invoke(prompt)
        
        # Extract individual scores
        scores = [
            raw_eval.factual_grounding.score,
            raw_eval.hallucination_risk.score,
            raw_eval.sdg_relevance.score,
            raw_eval.recommendation_quality.score,
            raw_eval.completeness.score
        ]
        
        # Compute metrics
        overall_score = float(sum(scores) / len(scores))
        quality_warning = overall_score < 3.0
        
        # Build and return the final EvaluationResult
        return EvaluationResult(
            factual_grounding=raw_eval.factual_grounding,
            hallucination_risk=raw_eval.hallucination_risk,
            sdg_relevance=raw_eval.sdg_relevance,
            recommendation_quality=raw_eval.recommendation_quality,
            completeness=raw_eval.completeness,
            overall_score=overall_score,
            quality_warning=quality_warning
        )
        
    except Exception as e:
        print(f"Error in LLM-as-Judge evaluation: {e}")
        # Return fallback EvaluationResult on exception
        fallback_score = DimensionScore(score=3, justification=f"Fallback score due to evaluation error: {e}")
        return EvaluationResult(
            factual_grounding=fallback_score,
            hallucination_risk=fallback_score,
            sdg_relevance=fallback_score,
            recommendation_quality=fallback_score,
            completeness=fallback_score,
            overall_score=3.0,
            quality_warning=False
        )

if __name__ == "__main__":
    Config.validate()
    print("Testing Evaluator Module...")
    
    mock_query = "digital divide in Pakistan"
    mock_context = "Research indicates Punjab and Sindh 3G/4G broadband expansion helped household income by 7% (World Bank, 2022)."
    mock_brief = {
        "query": mock_query,
        "executive_summary": "Summary of digital divide",
        "key_findings": ["Punjab household income increased by 7% (World Bank, 2022)"],
        "statistical_evidence": ["Punjab household income increased by 7% (World Bank, 2022)"],
        "policy_recommendations": [
            {
                "title": "Broadband Subsidy",
                "description": "Establish USF subsidies for broadband access in rural Punjab.",
                "priority": "HIGH",
                "implementation_timeframe": "Short-term"
            }
        ],
        "sdg_mappings": [
            {
                "sdg_number": 9,
                "sdg_name": "Industry, Innovation and Infrastructure",
                "relevance_explanation": "Direct connection to expanding digital infrastructure.",
                "expected_impact": "Increase rural internet penetration."
            }
        ],
        "primary_sdg": 9,
        "references": [
            {
                "title": "Digital Inclusion in Rural Pakistan",
                "source": "World Bank",
                "year": 2022,
                "url": None
            }
        ],
        "evidence_quality_flag": "SUFFICIENT"
    }
    
    res = evaluate_brief(mock_query, mock_context, mock_brief)
    print("\nResult type:", type(res))
    print("Factual Grounding:", res.factual_grounding.score, "-", res.factual_grounding.justification)
    print("Hallucination Risk:", res.hallucination_risk.score, "-", res.hallucination_risk.justification)
    print("SDG Relevance:", res.sdg_relevance.score, "-", res.sdg_relevance.justification)
    print("Recommendation Quality:", res.recommendation_quality.score, "-", res.recommendation_quality.justification)
    print("Completeness:", res.completeness.score, "-", res.completeness.justification)
    print("Overall Score:", res.overall_score)
    print("Quality Warning:", res.quality_warning)
