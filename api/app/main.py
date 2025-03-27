from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Form,
    Depends,
    Request,
    BackgroundTasks,
    Query,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import traceback
import aiohttp
from contextlib import asynccontextmanager
import uuid
import logging
from starlette.requests import Request
from typing import Optional, Dict, Any, List
from enum import Enum

from app.transcribe_audio import AzTranscriptionClient
from app.summary_text import AzOpenAIClient
from app.blob_processor import AzBlobClient
from app.mp4_processor import save_disk, mp4_processor
from app.word_generator import create_word, cleanup_word
from app.sharepoint_processor import SharePointAccessClass

class EnvironmentConfig:
    """環境変数の設定と検証を行うクラス"""
    REQUIRED_VARS = [
        "AZ_SPEECH_KEY", "AZ_SPEECH_ENDPOINT", "AZ_OPENAI_KEY",
        "AZ_OPENAI_ENDPOINT", "AZ_BLOB_CONNECTION", "CLIENT_ID",
        "CLIENT_SECRET", "TENANT_ID"
    ]

    def __init__(self):
        load_dotenv()
        self._load_environment_variables()
        self._validate_environment_variables()

    def _load_environment_variables(self):
        """環境変数を読み込む"""
        for var in self.REQUIRED_VARS:
            setattr(self, var, os.getenv(var))
        self.AZ_CONTAINER_NAME = "container-vr-dev"

    def _validate_environment_variables(self):
        """必須環境変数の存在確認"""
        missing = [var for var in self.REQUIRED_VARS if not getattr(self, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

class TaskStatus(str, Enum):
    """タスクの状態を表す列挙型"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskManager:
    """タスクの状態管理を行うクラス"""
    def __init__(self):
        self.status: Dict[str, TaskStatus] = {}
        self.transcribed_text: Dict[str, Optional[str]] = {}
        self.summarized_text: Dict[str, Optional[str]] = {}

    def initialize_task(self, task_id: str) -> None:
        """新規タスクの初期化"""
        self.status[task_id] = TaskStatus.PROCESSING
        self.transcribed_text[task_id] = None
        self.summarized_text[task_id] = None

    def complete_task(self, task_id: str, transcribed: str, summarized: str) -> None:
        """タスクの完了処理"""
        self.status[task_id] = TaskStatus.COMPLETED
        self.transcribed_text[task_id] = transcribed
        self.summarized_text[task_id] = summarized

    def fail_task(self, task_id: str, error_message: str) -> None:
        """タスクの失敗処理"""
        self.status[task_id] = TaskStatus.FAILED
        error_text = f"エラー: {error_message}"
        self.transcribed_text[task_id] = error_text
        self.summarized_text[task_id] = error_text

class AudioProcessor:
    """音声処理の主要ロジックを扱うクラス"""
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def process_audio(
        self,
        task_id: str,
        site_data_dict: Optional[Dict[str, Any]],
        az_blob_client: AzBlobClient,
        az_speech_client: AzTranscriptionClient,
        az_openai_client: AzOpenAIClient,
        sp_access: SharePointAccessClass,
        file_path: str,
    ) -> None:
        """音声処理のメインロジック"""
        try:
            # MP4処理
            wav_data = await mp4_processor(file_path)
            if not wav_data:
                raise ValueError("MP4ファイルの処理に失敗しました")

            # Blob処理
            blob_url = await az_blob_client.upload_blob(
                wav_data["file_name"], 
                wav_data["file_data"]
            )

            # 文字起こしと要約
            transcribed_text = await self._handle_transcription(
                az_speech_client, 
                blob_url
            )
            summarized_text = await az_openai_client.summarize_text(transcribed_text)

            # SharePoint処理
            await self._handle_sharepoint_upload(
                site_data_dict,
                sp_access,
                transcribed_text,
                summarized_text
            )

            # タスク完了処理
            self.task_manager.complete_task(task_id, transcribed_text, summarized_text)
            await az_blob_client.delete_blob(wav_data["file_name"])

        except Exception as e:
            self._handle_error(task_id, e)

    async def _handle_transcription(
        self, 
        az_speech_client: AzTranscriptionClient, 
        blob_url: str
    ) -> str:
        """文字起こし処理"""
        transcribed_text = await az_speech_client.transcribe_audio(blob_url)
        if not transcribed_text:
            raise ValueError("文字起こしに失敗しました")
        return transcribed_text

    async def _handle_sharepoint_upload(
        self,
        site_data_dict: Optional[Dict[str, Any]],
        sp_access: SharePointAccessClass,
        transcribed_text: str,
        summarized_text: str
    ) -> None:
        """SharePointへのアップロード処理"""
        if site_data_dict and all(k in site_data_dict for k in ["site", "directory"]):
            word_file_path = await create_word(transcribed_text, summarized_text)
            try:
                sp_access.upload_file(
                    site_data_dict["site"],
                    site_data_dict["directory"],
                    word_file_path,
                )
            finally:
                await cleanup_word(word_file_path)

    def _handle_error(self, task_id: str, error: Exception) -> None:
        """エラー処理"""
        self.task_manager.fail_task(task_id, str(error))
        logger.error(f"タスク {task_id} の処理中にエラー: {str(error)}")
        logger.error(traceback.format_exc())

# 設定の初期化
config = EnvironmentConfig()

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    session = aiohttp.ClientSession()
    app.state.session = session
    app.state.task_manager = TaskManager()
    app.state.audio_processor = AudioProcessor(app.state.task_manager)
    yield
    await session.close()

# FastAPIアプリケーションの設定
app = FastAPI(lifespan=lifespan)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依存性注入の設定
def get_az_blob_client() -> AzBlobClient:
    return AzBlobClient(config.AZ_BLOB_CONNECTION, config.AZ_CONTAINER_NAME)

def get_az_speech_client(request: Request) -> AzTranscriptionClient:
    return AzTranscriptionClient(
        request.app.state.session, 
        config.AZ_SPEECH_KEY, 
        config.AZ_SPEECH_ENDPOINT
    )

def get_az_openai_client() -> AzOpenAIClient:
    return AzOpenAIClient(config.AZ_OPENAI_KEY, config.AZ_OPENAI_ENDPOINT)

def get_sp_access() -> SharePointAccessClass:
    return SharePointAccessClass(
        config.CLIENT_ID, 
        config.CLIENT_SECRET, 
        config.TENANT_ID
    )

class Transcribe(BaseModel):
    """文字起こしリクエストのモデル"""
    site: str = Field(default="")
    directory: str = Field(default="")

def parse_form(
    site: Optional[str] = Form(None), 
    directory: Optional[str] = Form(None)
) -> Transcribe:
    """フォームデータのパース"""
    return Transcribe(site=site or "", directory=directory or "")

@app.post("/transcribe", status_code=status.HTTP_202_ACCEPTED)
async def transcribe(
    background_tasks: BackgroundTasks,
    site_data: Optional[Transcribe] = Depends(parse_form),
    file: UploadFile = File(...),
    az_blob_client: AzBlobClient = Depends(get_az_blob_client),
    az_speech_client: AzTranscriptionClient = Depends(get_az_speech_client),
    az_openai_client: AzOpenAIClient = Depends(get_az_openai_client),
    sp_access: SharePointAccessClass = Depends(get_sp_access),
):
    """音声ファイルの文字起こしと要約を開始"""
    task_id = str(uuid.uuid4())
    app.state.task_manager.initialize_task(task_id)
    site_data_dict = site_data.model_dump() if site_data else {}

    try:
        file_path = save_disk(file)
        background_tasks.add_task(
            app.state.audio_processor.process_audio,
            task_id,
            site_data_dict,
            az_blob_client,
            az_speech_client,
            az_openai_client,
            sp_access,
            file_path,
        )
        return {"task_id": task_id, "message": "処理を開始しました"}
    except Exception as e:
        logger.error(f"音声処理エンドポイントでエラー: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

@app.get("/transcribe/{task_id}")
async def get_transcription_status(task_id: str):
    """タスクの進捗状況を取得"""
    if task_id not in app.state.task_manager.status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="タスクIDが存在しません"
        )
    
    return {
        "task_id": task_id,
        "status": app.state.task_manager.status[task_id],
        "transcribed_text": app.state.task_manager.transcribed_text[task_id],
        "summarized_text": app.state.task_manager.summarized_text[task_id]
    }

@app.get("/sites")
async def get_sites(sp_access: SharePointAccessClass = Depends(get_sp_access)):
    """サイト一覧を取得"""
    try:
        return sp_access.get_sites()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サイト取得中にエラーが発生しました: {str(e)}"
        )

@app.get("/directories")
async def get_directories(
    site_id: str = Query(...),
    sp_access: SharePointAccessClass = Depends(get_sp_access)
):
    """指定されたサイトのディレクトリ一覧を取得"""
    try:
        return sp_access.get_folders(site_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ディレクトリ取得中にエラーが発生しました: {str(e)}"
        )

@app.get("/subdirectories")
async def get_subdirectories(
    site_id: str = Query(...),
    directory_id: str = Query(...),
    sp_access: SharePointAccessClass = Depends(get_sp_access)
):
    """指定されたディレクトリのサブディレクトリ一覧を取得"""
    try:
        return sp_access.get_subfolders(site_id, directory_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サブディレクトリ取得中にエラーが発生しました: {str(e)}"
        )
