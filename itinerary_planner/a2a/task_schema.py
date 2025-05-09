# itinerary_planner/a2a/task_schema.py

from pydantic import BaseModel
from typing import List, Optional

class Part(BaseModel):
    text: Optional[str] = None

class Message(BaseModel):
    role: str
    parts: List[Part]

class TaskRequest(BaseModel):
    taskId: str
    message: Message