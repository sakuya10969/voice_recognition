from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import logging

from app.dependencies.az_client import (
    get_az_blob_client,
    get_az_speech_client, 
    get_az_openai_client,
    get_sp_access
)
from app.infrastructure.az_blob import AzBlobClient
from app.infrastructure.az_speech import AzSpeechClient
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient
from app.services.task_manager_service import TaskManager
from app.services.mp4_processor_service import MP4ProcessorService
from app.services.word_generator_service import WordGeneratorService
from api.app.usecases.transcribe_audio_usecase import TranscribeAudioUseCase
from api.app.models.transcription import Transcribe
from app.utils.file_handler import save_file_temporarily

router = APIRouter()
logger = logging.getLogger(__name__)

def get_transcribe_usecase(
    request: Request,
    blob_client: AzBlobClient = Depends(get_az_blob_client),
    speech_client: AzSpeechClient = Depends(get_az_speech_client),
    openai_client: AzOpenAIClient = Depends(get_az_openai_client),
    sharepoint_client: MsSharePointClient = Depends(get_sp_access),
) -> TranscribeAudioUseCase:
    """TranscribeAudioUseCaseの依存性注入"""
    task_manager: TaskManager = request.app.state.task_manager
    mp4_processor = MP4ProcessorService()
    word_generator = WordGeneratorService()
    
    return TranscribeAudioUseCase(
        task_manager=task_manager,
        mp4_processor=mp4_processor,
        word_generator=word_generator,
        blob_client=blob_client,
        speech_client=speech_client,
        openai_client=openai_client,
        sharepoint_client=sharepoint_client
    )

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def transcribe(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    site_data: Optional[Transcribe] = None,
    request: Request = None,
    usecase: TranscribeAudioUseCase = Depends(get_transcribe_usecase),
):
    """音声ファイルの文字起こしと要約を非同期で実行するエンドポイント"""
    task_id = str(uuid.uuid4())
    site_data_dict = site_data.model_dump() if site_data else {}

    try:
        temp_file_path = await save_file_temporarily(file)
        background_tasks.add_task(
            usecase.execute,
            task_id=task_id,
            site_data=site_data_dict,
            file_path=temp_file_path,
        )
        return {
            "task_id": task_id,
            "message": "処理を開始しました"
        }
    except Exception as e:
        logger.error(f"音声処理の開始に失敗: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"処理の開始に失敗しました: {str(e)}"}
        )

@router.get("/{task_id}")
async def get_transcription_status(task_id: str, request: Request):
    """タスクの処理状態と結果を取得するエンドポイント"""
    task_manager: TaskManager = request.app.state.task_manager
    
    if task_id not in task_manager.status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タスクIDが存在しません"
        )
        
    return {
        "task_id": task_id,
        "status": task_manager.status[task_id],
        "transcribed_text": task_manager.transcribed_text[task_id],
        "summarized_text": task_manager.summarized_text[task_id]
    }
