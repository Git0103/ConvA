from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class DistributionMetrics(BaseModel):
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    mean: Optional[float] = None
    std_dev: Optional[float] = None

class ColumnProfile(BaseModel):
    column_name: str
    structural_type: str
    nullable: bool
    null_count: int
    total_count: int
    cardinality: Optional[int] = None
    distribution: Optional[DistributionMetrics] = None

class SemanticModel(ColumnProfile):
    semantic_type: str = "unknown"
    analytics_capabilities: List[str] = Field(default_factory=list)

class TableProfile(BaseModel):
    table_name: str
    row_count: int
    columns: Dict[str, SemanticModel]
