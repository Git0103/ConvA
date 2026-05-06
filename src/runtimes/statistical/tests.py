import scipy.stats as stats
import polars as pl
from typing import Dict, Any, Tuple

class StatisticalTests:
    def __init__(self):
        pass

    def check_assumptions(self, group1: pl.Series, group2: pl.Series) -> Dict[str, Any]:
        """
        Runs industry-standard assumption checks for parametric tests.
        1. Shapiro-Wilk for Normality
        2. Levene's Test for Homoscedasticity (Equal Variance)
        """
        assumptions = {
            "normality": True,
            "equal_variance": True,
            "details": {}
        }
        
        # 1. Normality (Shapiro-Wilk)
        # scipy shapiro requires N >= 3
        if len(group1) >= 3 and len(group2) >= 3:
            stat1, p1 = stats.shapiro(group1.to_list())
            stat2, p2 = stats.shapiro(group2.to_list())
            assumptions["details"]["shapiro_p1"] = p1
            assumptions["details"]["shapiro_p2"] = p2
            if p1 < 0.05 or p2 < 0.05:
                assumptions["normality"] = False
        else:
            assumptions["normality"] = False # Too small
            assumptions["details"]["shapiro_error"] = "Sample size < 3"

        # 2. Equal Variance (Levene)
        stat_l, p_l = stats.levene(group1.to_list(), group2.to_list())
        assumptions["details"]["levene_p"] = p_l
        if p_l < 0.05:
            assumptions["equal_variance"] = False
            
        return assumptions

    def execute_t_test(self, df: pl.DataFrame, target_col: str, group_col: str) -> Dict[str, Any]:
        """
        Executes a rigorous t-test comparing two groups.
        Automatically falls back to Welch's or Mann-Whitney U if assumptions are violated.
        """
        groups = df.partition_by(group_col)
        if len(groups) != 2:
            raise ValueError(f"t-test requires exactly 2 groups. Found {len(groups)}.")
            
        g1 = groups[0][target_col].drop_nulls()
        g2 = groups[1][target_col].drop_nulls()
        
        g1_name = str(groups[0][group_col][0])
        g2_name = str(groups[1][group_col][0])
        
        assumptions = self.check_assumptions(g1, g2)
        
        result = {
            "test_type": "Independent t-test",
            "groups": [g1_name, g2_name],
            "assumptions_met": assumptions,
            "statistic": None,
            "p_value": None,
            "interpretation": ""
        }
        
        # Decision tree for rigorous statistics
        if not assumptions["normality"]:
            result["test_type"] = "Mann-Whitney U (Non-parametric fallback)"
            stat, p = stats.mannwhitneyu(g1.to_list(), g2.to_list())
        elif not assumptions["equal_variance"]:
            result["test_type"] = "Welch's t-test (Unequal variance fallback)"
            stat, p = stats.ttest_ind(g1.to_list(), g2.to_list(), equal_var=False)
        else:
            stat, p = stats.ttest_ind(g1.to_list(), g2.to_list(), equal_var=True)
            
        result["statistic"] = stat
        result["p_value"] = p
        
        if p < 0.05:
            result["interpretation"] = f"Significant difference detected between {g1_name} and {g2_name}."
        else:
            result["interpretation"] = f"No significant difference detected between {g1_name} and {g2_name}."
            
        return result

    def execute_anova(self, df: pl.DataFrame, target_col: str, group_col: str) -> Dict[str, Any]:
        """
        Executes a one-way ANOVA across multiple groups.
        """
        groups = df.partition_by(group_col)
        if len(groups) < 2:
            raise ValueError(f"ANOVA requires at least 2 groups. Found {len(groups)}.")
            
        arrays = [g[target_col].drop_nulls().to_list() for g in groups]
        group_names = [str(g[group_col][0]) for g in groups]
        
        stat, p = stats.f_oneway(*arrays)
        
        return {
            "test_type": "One-way ANOVA",
            "groups": group_names,
            "statistic": stat,
            "p_value": p,
            "interpretation": "Significant differences found among groups." if p < 0.05 else "No significant differences found."
        }
        
    def execute_correlation(self, df: pl.DataFrame, col1: str, col2: str, method: str = 'pearson') -> Dict[str, Any]:
        """
        Executes correlation between two numeric columns.
        """
        data = df.select([col1, col2]).drop_nulls()
        v1 = data[col1].to_list()
        v2 = data[col2].to_list()
        
        if method == 'pearson':
            stat, p = stats.pearsonr(v1, v2)
        elif method == 'spearman':
            stat, p = stats.spearmanr(v1, v2)
        else:
            raise ValueError(f"Unsupported correlation method: {method}")
            
        return {
            "test_type": f"{method.capitalize()} Correlation",
            "columns": [col1, col2],
            "statistic": stat,
            "p_value": p,
            "interpretation": "Significant correlation." if p < 0.05 else "No significant correlation."
        }
