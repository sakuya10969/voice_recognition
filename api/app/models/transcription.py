from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class Transcription(BaseModel):
    site: str = Field(default="")
    directory: str = Field(default="")


class TaskStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioProcessingResponse(BaseModel):
    """音声処理のレスポンスデータ"""
    task_id: str
    message: str


class TranscriptionStatusResponse(BaseModel):
    """文字起こし状態のレスポンスデータ"""
    task_id: str
    status: str
    transcribed_text: Optional[str]
    summarized_text: Optional[str]
