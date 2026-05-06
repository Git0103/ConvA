from fastapi import APIRouter, Depends
from src.api.schemas.request import ChatRequest
from src.api.auth import verify_token
from src.orchestration.graph import app_graph
from langchain_core.messages import HumanMessage

router = APIRouter()

@router.post("/chat")
async def process_chat(request: ChatRequest, token: dict = Depends(verify_token)):
    # Convert ChatRequest to initial state for LangGraph
    user_id = token.get("sub", request.user_id)
    
    initial_state = {
        "messages": [HumanMessage(content=request.message.content)],
        "request_data": request.model_dump(),
        "execution_plan": None,
        "analytics_results": {},
        "current_step": "start"
    }
    
    # Invoke workflow
    try:
        final_state = app_graph.invoke(initial_state)
        
        # Extract response
        bot_response = "No response generated."
        if final_state.get("messages"):
            bot_response = final_state["messages"][-1].content
            
        return {
            "status": "success",
            "request_id": request.request_id,
            "message": bot_response,
            "analytics_results": final_state.get("analytics_results")
        }
    except Exception as e:
        raise ValueError(f"Orchestration failed: {str(e)}")
