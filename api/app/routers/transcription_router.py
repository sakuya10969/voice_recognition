from fastapi import APIRouter

from app.handlers.transcription_handler import transcribe, get_transcription_status

router = APIRouter()

router.post("/", status_code=202)(transcribe)
router.get("/{task_id}")(get_transcription_status)
