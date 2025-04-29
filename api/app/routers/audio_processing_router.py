from fastapi import APIRouter

from app.handlers.audio_processing_handler import process_audio, get_transcription_status

router = APIRouter()

router.post("/transcription", status_code=202)(process_audio)
router.get("/transcription/{task_id}")(get_transcription_status)
