import polars as pl
from typing import Dict, Any, List

class ValidationEngine:
    def __init__(self):
        pass

    def validate_dataset(self, df: pl.DataFrame) -> Dict[str, Any]:
        """
        Generates a data quality report focusing on missingness.
        """
        report = {
            "total_rows": df.height,
            "total_columns": df.width,
            "missingness": {},
            "requires_user_action": False,
            "user_action_prompt": ""
        }
        
        cols_with_missing = []
        
        for col_name in df.columns:
            null_count = df[col_name].null_count()
            if null_count > 0:
                missing_pct = round((null_count / df.height) * 100, 2)
                report["missingness"][col_name] = {
                    "null_count": null_count,
                    "missing_percentage": missing_pct
                }
                cols_with_missing.append(col_name)
                
        if cols_with_missing:
            report["requires_user_action"] = True
            report["user_action_prompt"] = (
                f"The dataset has missing data in columns: {', '.join(cols_with_missing)}. "
                "How would you like to handle this? Options: [pairwise deletion, listwise deletion, imputation (mean/median/mode)]."
            )
            
        return report
