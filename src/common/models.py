from pydantic import BaseModel
from typing import Dict, Any

class AnalysisResult(BaseModel):
    status: str
    data: Dict[str, Any]
