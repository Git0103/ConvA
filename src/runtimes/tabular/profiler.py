import polars as pl
from typing import Dict
from .models import ColumnProfile, DistributionMetrics

def profile_dataframe(df: pl.DataFrame) -> Dict[str, ColumnProfile]:
    profiles = {}
    row_count = df.height
    
    for col_name in df.columns:
        series = df[col_name]
        dtype = str(series.dtype)
        null_count = series.null_count()
        nullable = null_count > 0
        
        profile = ColumnProfile(
            column_name=col_name,
            structural_type=dtype,
            nullable=nullable,
            null_count=null_count,
            total_count=row_count
        )
        
        # Profile specific types
        if series.dtype in pl.NUMERIC_DTYPES:
            # Avoid calculating cardinality for floats unless requested, but we can do min/max easily
            profile.distribution = DistributionMetrics(
                min_val=series.min(),
                max_val=series.max(),
                mean=series.mean(),
                std_dev=series.std()
            )
            if series.dtype in pl.INTEGER_DTYPES:
                profile.cardinality = series.n_unique()
                
        elif series.dtype in [pl.Utf8, pl.Categorical, pl.Boolean]:
            profile.cardinality = series.n_unique()
            
        profiles[col_name] = profile
        
    return profiles
