from pydantic import BaseModel, Field
from enum import Enum

class Transcription(BaseModel):
    site: str = Field(default="")
    directory: str = Field(default="")
    
class TaskStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    