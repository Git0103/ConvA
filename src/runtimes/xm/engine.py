import polars as pl
from typing import Dict, Any
from .metrics import calculate_nps, calculate_csat

class XMEngine:
    def __init__(self):
        # The XM Engine is mostly functional and stateless in this MVP.
        # It operates directly on dataframes provided by the Tabular Runtime.
        pass
        
    def execute_metric(self, metric_name: str, df: pl.DataFrame, score_column: str) -> Dict[str, Any]:
        """
        Executes a requested XM metric calculation against the dataframe.
        """
        metric_name = metric_name.lower()
        if metric_name == "nps":
            return calculate_nps(df, score_column)
        elif metric_name == "csat":
            return calculate_csat(df, score_column)
        else:
            raise NotImplementedError(f"Metric {metric_name} is not supported yet.")
