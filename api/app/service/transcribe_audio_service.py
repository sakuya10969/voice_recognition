from fastapi import HTTPException

from infrastructure.az_speech import AzSpeechClient

class TranscribeAudioService:
    def __init__(self, client: AzSpeechClient):
        self._client = client

    async def transcribe(self, blob_url: str) -> str:
        """音声文字起こしの一連の処理をまとめる"""
        job_url = await self._client.create_transcription_job(blob_url)
        status_data = await self._client.poll_transcription_status(job_url)
        
        file_url = status_data["links"]["files"]
        content_url = await self._extract_first_content_url(file_url)
        return await self._extract_display_text(content_url)

    async def _extract_first_content_url(self, file_url: str) -> str:
        files_data = await self._client.get(file_url)
        try:
            return files_data["values"][0]["links"]["contentUrl"]
        except (KeyError, IndexError):
            raise HTTPException(500, "文字起こしファイルの取得に失敗しました")

    async def _extract_display_text(self, content_url: str) -> str:
        content_data = await self._client.get(content_url)
        try:
            return content_data["combinedRecognizedPhrases"][0]["display"]
        except (KeyError, IndexError):
            raise HTTPException(500, "文字起こし結果の取得に失敗しました")
