from typing import List
from pydantic import BaseModel
from .models import ColumnProfile, SemanticModel
from src.orchestration.llm import get_llm
import os

class LLMSemanticOutput(BaseModel):
    semantic_models: List[SemanticModel]

def infer_semantic_types_with_llm(profiles: List[ColumnProfile]) -> List[SemanticModel]:
    """
    Given a list of column profiles, invoke an LLM to determine their semantic type and 
    associated analytic capabilities.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "mock_key" and api_key != "your-api-key-here":
        try:
            llm = get_llm(provider="openai", model_name="gpt-4o-mini").with_structured_output(LLMSemanticOutput)
            prompt = f"Analyze the following column profiles and determine their semantic_type and analytics_capabilities:\n"
            for p in profiles:
                prompt += f"- {p.model_dump_json()}\n"
            
            result = llm.invoke(prompt)
            return result.semantic_models
        except Exception as e:
            print(f"LLM Semantic Mapping failed, falling back to heuristics: {e}")
    
    # Fallback / Mock heuristics
    semantic_models = []
    for p in profiles:
        semantic_type = "generic_data"
        capabilities = ["descriptive_statistics"]
        
        col_lower = p.column_name.lower()
        if "score" in col_lower or "nps" in col_lower:
            semantic_type = "nps_score"
            capabilities.extend(["nps", "correlation", "regression"])
        elif "region" in col_lower or "department" in col_lower:
            semantic_type = "categorical_group"
            capabilities.extend(["anova", "chi_square"])
        elif p.structural_type.startswith("Float"):
            semantic_type = "continuous_metric"
            capabilities.extend(["regression", "t_test"])
            
        sm = SemanticModel(
            **p.model_dump(),
            semantic_type=semantic_type,
            analytics_capabilities=capabilities
        )
        semantic_models.append(sm)
        
    return semantic_models
