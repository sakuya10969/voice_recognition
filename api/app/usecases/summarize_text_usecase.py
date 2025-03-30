from fastapi import HTTPException

from app.services.summarize_text_service import SummarizeTextService

class SummarizeTextUseCase:
    def __init__(self, service: SummarizeTextService):
        self._service = service

    async def execute(self, text: str) -> str:
        try:
            return await self._service.summarize(text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"要約中にエラー: {str(e)}")
