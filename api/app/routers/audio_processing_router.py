import uuid
import logging
from typing import Optional, Dict, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    UploadFile,
    File,
    Depends,
    HTTPException,
    status,
    Request,
)
from pydantic import BaseModel

from app.domain.transcription import Transcription
from app.di.parse_form import parse_transcription_form
from app.usecases.audio_processing_usecase import AudioProcessingUseCase
from app.services.audio.mp4_processing_service import MP4ProcessingService
from app.services.word_generating_service import WordGeneratingService
from app.utils.file_handling import save_file_temporarily
from app.domain.transcription import AudioProcessingResponse, TranscriptionStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _create_audio_usecase(request: Request) -> AudioProcessingUseCase:
    """AudioProcessingUseCaseのインスタンスを生成する"""
    az_client_factory = request.app.state.az_client_factory
    return AudioProcessingUseCase(
        task_managing_service=request.app.state.task_managing_service,
        mp4_processing_service=MP4ProcessingService(),
        word_generating_service=WordGeneratingService(),
        az_blob_client=az_client_factory.create_az_blob_client(),
        az_speech_client=az_client_factory.create_az_speech_client(),
        az_openai_client=az_client_factory.create_az_openai_client(),
        ms_sharepoint_client=az_client_factory.create_ms_sharepoint_client(),
    )


async def _handle_audio_operation(
    operation_name: str, operation: callable
) -> Dict[str, Any]:
    """文字起こし操作の共通エラーハンドリング"""
    try:
        return await operation()
    except Exception as e:
        logger.error(f"{operation_name}に失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation_name}に失敗しました: {str(e)}",
        )


@router.post("/transcription", status_code=202, response_model=AudioProcessingResponse)
async def process_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    site_data: Optional[Transcription] = Depends(parse_transcription_form),
):
    """音声ファイルの文字起こしと要約を非同期で実行"""

    async def start_audio_processing():
        task_id = str(uuid.uuid4())
        site_data_dict = site_data.model_dump() if site_data else None
        temp_file_path = await save_file_temporarily(file)

        usecase = _create_audio_usecase(request)
        background_tasks.add_task(
            usecase.execute,
            task_id=task_id,
            site_data=site_data_dict,
            file_path=temp_file_path,
        )

        return AudioProcessingResponse(task_id=task_id, message="処理を開始しました")

    return await _handle_audio_operation("音声処理の開始", start_audio_processing)


@router.get("/transcription/{task_id}", response_model=TranscriptionStatusResponse)
async def get_transcription_status(
    request: Request, task_id: str
):
    """タスクの処理状態と結果を取得"""
    task_managing_service = request.app.state.task_managing_service

    if task_id not in task_managing_service.status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="タスクIDが存在しません"
        )

    return TranscriptionStatusResponse(
        task_id=task_id,
        status=task_managing_service.status[task_id],
        transcribed_text=task_managing_service.transcribed_text[task_id],
        summarized_text=task_managing_service.summarized_text[task_id],
    )
