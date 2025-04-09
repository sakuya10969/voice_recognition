from fastapi import HTTPException

from app.infrastructure.az_speech import AzSpeechClient

class AudioTranscriptionService:
    """音声文字起こしを行うサービス"""
    
    def __init__(self, az_speech_client: AzSpeechClient):
        self._az_speech_client = az_speech_client
    
    async def transcribe_audio(self, blob_url: str) -> str:
        """音声ファイルを文字起こしする"""
        try:
            return await self._execute_transcription(blob_url)
        except Exception as e:
            self._handle_error(e)

    async def _execute_transcription(self, blob_url: str) -> str:
        """文字起こし処理を実行する"""
        job_url = await self._az_speech_client.create_transcription_job(blob_url)
        files_url = await self._az_speech_client.poll_transcription_status(job_url)
        content_url = await self._az_speech_client.get_transcription_result(files_url)
        print(f"content_url: {content_url}")
        return await self._az_speech_client.get_transcription_display(content_url)

    def _handle_error(self, error: Exception) -> None:
        """エラー処理を行う"""
        raise HTTPException(
            status_code=500,
            detail=f"文字起こしに失敗しました: {str(error)}"
        )