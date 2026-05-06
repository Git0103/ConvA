from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class FileAttachment(BaseModel):
    file_id: str
    file_type: str
    file_name: str
    storage_uri: str

class MessageContent(BaseModel):
    type: str
    content: str

class ChatRequest(BaseModel):
    request_id: str
    channel: str
    workspace_id: str
    user_id: str
    thread_id: str
    session_id: str
    timestamp: str
    message: MessageContent
    attachments: Optional[List[FileAttachment]] = []
    metadata: Optional[Dict[str, Any]] = {}
