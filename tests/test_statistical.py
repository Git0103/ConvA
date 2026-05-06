import polars as pl
from src.runtimes.statistical.tests import StatisticalTests

def test_execute_t_test_fallback():
    engine = StatisticalTests()
    # Less than 3 samples per group triggers fallback
    df = pl.DataFrame({
        "group": ["A", "A", "B", "B"],
        "value": [10, 12, 100, 105]
    })
    
    res = engine.execute_t_test(df, "value", "group")
    # Since n=2, Shapiro fails, forcing Mann-Whitney U
    assert not res["assumptions_met"]["normality"]
    assert res["test_type"] == "Mann-Whitney U (Non-parametric fallback)"
    assert res["p_value"] is not None
