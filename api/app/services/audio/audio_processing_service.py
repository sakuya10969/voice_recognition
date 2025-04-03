import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.infrastructure.az_speech import AzSpeechClient
from app.infrastructure.az_blob import AzBlobClient
from app.services.audio.mp4_processing_service import MP4ProcessingService
from app.services.audio.audio_transcription_service import AudioTranscriptionService

logger = logging.getLogger(__name__)

class AudioProcessingService:
    """音声処理を統合的に管理するサービス"""
    
    def __init__(
        self,
        az_speech_client: AzSpeechClient,
        az_blob_client: AzBlobClient,
        mp4_processing_service: MP4ProcessingService,
        audio_transcription_service: AudioTranscriptionService
    ):
        self.az_speech_client = az_speech_client
        self.az_blob_client = az_blob_client
        self.mp4_processing_service = mp4_processing_service
        self.audio_transcription_service = audio_transcription_service

    async def process_audio_file(self, file_path: str) -> Dict[str, Any]:
        """音声ファイルを処理し、Blobストレージにアップロードする"""
        try:
            # MP4の処理
            processed_data = await self.mp4_processing_service.process_mp4(file_path)
            
            # Blobへのアップロード
            blob_url = await self.az_blob_client.upload_blob(
                processed_data["file_name"],
                processed_data["file_data"]
            )

            return {
                "file_name": processed_data["file_name"],
                "blob_url": blob_url
            }

        except Exception as e:
            logger.error(f"音声ファイルの処理に失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"音声ファイルの処理に失敗しました: {str(e)}"
            )

    async def transcribe_audio(self, blob_url: str) -> str:
        """音声ファイルを文字起こしする"""
        try:
            return await self.audio_transcription_service.transcribe_audio(blob_url)

        except Exception as e:
            logger.error(f"文字起こしに失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"文字起こしに失敗しました: {str(e)}"
            )

    async def process_audio(self, file_path: str) -> str:
        """音声ファイルの処理から文字起こしまでを一括で実行する"""
        try:
            # 音声ファイルの処理とアップロード
            audio_data = await self.process_audio_file(file_path)
            
            # 文字起こしの実行
            transcribed_text = await self.transcribe_audio(audio_data["blob_url"])
            
            # 文字起こし完了後、Blobを削除
            await self.az_blob_client.delete_blob(audio_data["file_name"])
            
            return transcribed_text

        except Exception as e:
            logger.error(f"音声処理と文字起こしに失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"音声処理と文字起こしに失敗しました: {str(e)}"
            )
            