import uuid
import logging
from typing import Optional

from fastapi import BackgroundTasks, UploadFile, File, Depends, HTTPException, status, Request

from app.models.transcription import Transcription
from app.di.parse_form import parse_transcription_form
from app.usecases.audio_processor_usecase import TranscribeAudioUseCase
from app.services.task_manager_service import TaskManager
from app.infrastructure.az_blob import AzBlobClient
from app.infrastructure.az_speech import AzSpeechClient
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient
from app.services.audio.mp4_processor_service import MP4ProcessorService
from app.services.word_generator_service import WordGeneratorService
from app.utils.file_handler import save_file_temporarily

logger = logging.getLogger(__name__)

def get_transcription_usecase(request: Request) -> TranscribeAudioUseCase:
    """TranscribeAudioUseCaseのインスタンスを生成"""
    task_manager: TaskManager = request.app.state.task_manager
    az_blob_client: AzBlobClient = request.app.state.az_client_factory.create_az_blob_client()
    az_speech_client: AzSpeechClient = request.app.state.az_client_factory.create_az_speech_client()
    az_openai_client: AzOpenAIClient = request.app.state.az_client_factory.create_az_openai_client()
    ms_sharepoint_client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()

    return TranscribeAudioUseCase(
        task_manager=task_manager,
        mp4_processor=MP4ProcessorService(),
        word_generator=WordGeneratorService(),
        az_blob_client=az_blob_client,
        az_speech_client=az_speech_client,
        az_openai_client=az_openai_client,
        ms_sharepoint_client=ms_sharepoint_client
    )

async def transcribe(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    site_data: Optional[Transcription] = Depends(parse_transcription_form),
):
    """音声ファイルの文字起こしと要約を非同期で実行"""
    usecase = get_transcription_usecase(request)

    try:
        task_id = str(uuid.uuid4())
        site_data_dict = site_data.model_dump() if site_data else None
        temp_file_path = await save_file_temporarily(file)

        background_tasks.add_task(
            usecase.execute,
            task_id=task_id,
            site_data=site_data_dict,
            file_path=temp_file_path
        )

        return {
            "task_id": task_id,
            "message": "処理を開始しました"
        }
    except Exception as e:
        logger.error(f"音声処理の開始に失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"処理の開始に失敗しました: {str(e)}"
        )

async def get_transcription_status(request: Request, task_id: str):
    """タスクの処理状態と結果を取得"""
    usecase = get_transcription_usecase(request)

    if task_id not in usecase.task_manager.status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タスクIDが存在しません"
        )

    return {
        "task_id": task_id,
        "status": usecase.task_manager.status[task_id],
        "transcribed_text": usecase.task_manager.transcribed_text[task_id],
        "summarized_text": usecase.task_manager.summarized_text[task_id]
    }
