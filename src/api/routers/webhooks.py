from fastapi import APIRouter, Request, HTTPException
from src.api.schemas.request import ChatRequest, MessageContent
from src.orchestration.graph import app_graph
from langchain_core.messages import HumanMessage
import uuid
import datetime

router = APIRouter()

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Stubs out a Twilio-style WhatsApp webhook endpoint.
    It takes form data, normalizes it into ChatRequest, and runs the orchestrator.
    """
    form_data = await request.form()
    
    # Twilio sends 'Body' for message content, and 'From' for the sender phone number
    body = form_data.get("Body", "")
    sender = form_data.get("From", "unknown_sender")
    
    if not body:
        raise HTTPException(status_code=400, detail="Missing message body.")
        
    # Normalize to our unified schema
    normalized_request = ChatRequest(
        request_id=str(uuid.uuid4()),
        channel="whatsapp",
        workspace_id="default",
        user_id=str(sender),
        thread_id=str(sender), # Thread tied to sender phone number
        session_id=str(uuid.uuid4()),
        timestamp=datetime.datetime.now().isoformat(),
        message=MessageContent(type="text", content=str(body)),
        attachments=[],
        metadata={"source": "twilio_whatsapp"}
    )
    
    # Trigger graph
    initial_state = {
        "messages": [HumanMessage(content=normalized_request.message.content)],
        "request_data": normalized_request.model_dump(),
        "execution_plan": None,
        "analytics_results": {},
        "current_step": "start"
    }
    
    try:
        final_state = app_graph.invoke(initial_state)
        bot_response = final_state.get("messages")[-1].content if final_state.get("messages") else "No response generated."
        
        # In a real app, you would use Twilio's API to reply. 
        # For now, return the TwiML XML mock or JSON mock.
        return {
            "status": "success",
            "reply": bot_response
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
