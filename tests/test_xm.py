import polars as pl
from src.runtimes.xm.metrics import calculate_nps

def test_calculate_nps_perfect():
    # 3 promoters, 0 passives, 0 detractors -> 100 NPS
    df = pl.DataFrame({"nps_score": [9, 10, 9]})
    res = calculate_nps(df, "nps_score")
    assert res["score"] == 100.0
    assert res["total_responses"] == 3

def test_calculate_nps_mixed():
    # 1 promoter (10), 1 passive (8), 2 detractors (0, 6) -> (1 - 2) / 4 * 100 = -25.0
    df = pl.DataFrame({"nps_score": [10, 8, 0, 6]})
    res = calculate_nps(df, "nps_score")
    assert res["score"] == -25.0
    assert res["breakdown"]["promoters"] == 1
    assert res["breakdown"]["passives"] == 1
    assert res["breakdown"]["detractors"] == 2

def test_calculate_nps_missing_values():
    # 1 promoter (9), 1 null, 1 detractor (5)
    df = pl.DataFrame({"nps_score": [9, None, 5]})
    res = calculate_nps(df, "nps_score")
    # Should drop nulls: 1 promoter, 1 detractor -> 0 NPS
    assert res["score"] == 0.0
    assert res["total_responses"] == 2
