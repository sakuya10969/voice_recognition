from fastapi import HTTPException
from service.transcribe_audio_service import TranscribeAudioService

class TranscribeAudioUseCase:
    def __init__(self, service: TranscribeAudioService):
        self._service = service

    async def execute(self, blob_url: str) -> str:
        try:
            return await self._service.transcribe(blob_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文字起こし中にエラー: {str(e)}")
