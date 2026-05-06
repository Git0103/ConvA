import polars as pl
from typing import Dict, Any

def calculate_nps(df: pl.DataFrame, score_column: str) -> Dict[str, Any]:
    """
    Deterministically calculates NPS with hardcoded thresholds.
    Promoters: 9-10
    Passives: 7-8
    Detractors: 0-6
    """
    if score_column not in df.columns:
        raise ValueError(f"Column {score_column} not found in dataset.")
        
    series = df[score_column].drop_nulls()
    total_responses = len(series)
    
    if total_responses == 0:
        return {"metric": "NPS", "score": None, "total_responses": 0}
        
    promoters = series.filter(series >= 9).len()
    passives = series.filter((series >= 7) & (series <= 8)).len()
    detractors = series.filter(series <= 6).len()
    
    nps_score = ((promoters - detractors) / total_responses) * 100
    
    return {
        "metric": "NPS",
        "score": round(nps_score, 2),
        "total_responses": total_responses,
        "breakdown": {
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors
        }
    }

def calculate_csat(df: pl.DataFrame, score_column: str, top_box_threshold: int = 4) -> Dict[str, Any]:
    """
    Calculates CSAT % based on top-box methodology (e.g. 4 or 5 on a 5-point scale).
    """
    if score_column not in df.columns:
        raise ValueError(f"Column {score_column} not found in dataset.")
        
    series = df[score_column].drop_nulls()
    total_responses = len(series)
    
    if total_responses == 0:
        return {"metric": "CSAT", "score": None, "total_responses": 0}
        
    satisfied = series.filter(series >= top_box_threshold).len()
    
    csat_score = (satisfied / total_responses) * 100
    
    return {
        "metric": "CSAT",
        "score": round(csat_score, 2),
        "total_responses": total_responses,
        "satisfied_count": satisfied
    }
