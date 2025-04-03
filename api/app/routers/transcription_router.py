from fastapi import APIRouter

from app.handlers.transcription_handler import transcribe_audio, get_transcription_status

router = APIRouter()

router.post("/transcription", status_code=202)(transcribe_audio)
router.get("/transcription/{task_id}")(get_transcription_status)
