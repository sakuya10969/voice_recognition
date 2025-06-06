from fastapi import HTTPException
import logging

from app.infrastructure.az_speech import AzSpeechClient

logger = logging.getLogger(__name__)


class AudioTranscriptionService:
    """音声文字起こしを行うサービス"""
    def __init__(self, az_speech_client: AzSpeechClient):
        self._az_speech_client = az_speech_client

    async def transcribe_audio(self, blob_url: str) -> str:
        """音声ファイルを文字起こしする"""
        try:
            job_url = await self._az_speech_client.create_transcription_job(blob_url)
            files_url = await self._az_speech_client.poll_transcription_status(job_url)
            content_url = await self._az_speech_client.get_transcription_result_url(
                files_url
            )
            logger.info(f"content_url: {content_url}")
            return await self._az_speech_client.get_transcription_by_speaker(content_url)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"文字起こしに失敗しました: {str(e)}"
            )
