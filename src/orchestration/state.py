from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from pydantic import BaseModel

class Step(BaseModel):
    step_id: str
    tool: str
    params: Dict[str, Any]

class ExecutionPlan(BaseModel):
    plan_id: str
    intent: str
    steps: List[Step]

class GraphState(TypedDict):
    """
    Represents the state of our conversation and analytics execution.
    """
    messages: Annotated[list, add_messages]
    request_data: Dict[str, Any]
    execution_plan: Optional[ExecutionPlan]
    analytics_results: Dict[str, Any]
    current_step: str
