import asyncio
import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.infrastructure.az_speech import AzSpeechClient

logger = logging.getLogger(__name__)

class TranscrbeAudioService:
    """音声文字起こしを行うサービス"""
    
    def __init__(self, speech_client: AzSpeechClient):
        self.speech_client = speech_client
    
    async def transcribe(self, blob_url: str) -> str:
        """音声ファイルを文字起こしする"""
        try:
            # 文字起こしジョブの作成
            job_id = await self.speech_client.create_transcription_job(blob_url)
            
            # ジョブの完了を待機
            while True:
                status = await self.speech_client.get_transcription_status(job_id)
                if status == "Succeeded":
                    break
                elif status == "Failed":
                    raise HTTPException(
                        status_code=500,
                        detail="文字起こしジョブが失敗しました"
                    )
                await asyncio.sleep(5)  # 5秒待機
            
            # 結果の取得
            result = await self.speech_client.get_transcription_result(job_id)
            
            # 結果の解析
            content_url = self._extract_content_url(result)
            display_text = await self._extract_display_text(content_url)
            
            return display_text
            
        except Exception as e:
            logger.error(f"文字起こしに失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"文字起こしに失敗しました: {str(e)}"
            )
    
    def _extract_content_url(self, result: Dict[str, Any]) -> str:
        """文字起こし結果からコンテンツURLを抽出する"""
        try:
            return result["contentUrls"]["contentUrl"]
        except KeyError:
            raise HTTPException(
                status_code=500,
                detail="文字起こし結果からコンテンツURLを取得できませんでした"
            )
    
    async def _extract_display_text(self, content_url: str) -> str:
        """コンテンツURLから表示テキストを抽出する"""
        try:
            content = await self.speech_client.get_content(content_url)
            return content["displayText"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"表示テキストの取得に失敗しました: {str(e)}"
            ) 