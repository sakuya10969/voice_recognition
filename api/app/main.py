from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Form,
    Depends,
    Request,
    BackgroundTasks,
    Query
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import traceback
from fastapi.responses import JSONResponse
import aiohttp
from contextlib import asynccontextmanager
import uuid
import logging
from starlette.requests import Request
from typing import Optional

from app.transcribe_audio import AzTranscriptionClient
from app.summary_text import AzOpenAIClient
from app.blob_processor import AzBlobClient
from app.mp4_processor import save_disk, mp4_processor
from app.word_generator import create_word, cleanup_word
from app.sharepoint_processor import SharePointAccessClass

# 環境変数をロード
load_dotenv()

# 環境変数の取得
AZ_SPEECH_KEY = os.getenv("AZ_SPEECH_KEY")
AZ_SPEECH_ENDPOINT = os.getenv("AZ_SPEECH_ENDPOINT")
AZ_OPENAI_KEY = os.getenv("AZ_OPENAI_KEY")
AZ_OPENAI_ENDPOINT = os.getenv("AZ_OPENAI_ENDPOINT")
AZ_BLOB_CONNECTION = os.getenv("AZ_BLOB_CONNECTION")
AZ_CONTAINER_NAME = "container-vr-dev"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリのライフサイクル管理（セッションの作成・破棄）"""
    session = aiohttp.ClientSession()
    app.state.session = session
    app.state.task_status = {}
    app.state.task_transcribed_text = {}
    app.state.task_summarized_text = {}
    yield
    await session.close()

# FastAPIアプリケーションの初期化
app = FastAPI(lifespan=lifespan)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# クラスの依存性を定義する関数
def get_az_blob_client():
    return AzBlobClient(AZ_BLOB_CONNECTION, AZ_CONTAINER_NAME)

def get_az_speech_client(request: Request):
    return AzTranscriptionClient(
        request.app.state.session, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT
    )

def get_az_openai_client():
    return AzOpenAIClient(AZ_OPENAI_KEY, AZ_OPENAI_ENDPOINT)

def get_sp_access():
    return SharePointAccessClass(CLIENT_ID, CLIENT_SECRET, TENANT_ID)

# モデルの定義
class Transcribe(BaseModel):
    site: str
    directory: str

# フォームデータのパース
def parse_form(
    site: Optional[str] = Form(None), directory: Optional[str] = Form(None)
) -> Transcribe:
    return Transcribe(site=site or "", directory=directory or "")


async def process_audio_task(
    task_id: str,
    site_data_dict: Optional[dict],
    az_blob_client: AzBlobClient,
    az_speech_client: AzTranscriptionClient,
    az_openai_client: AzOpenAIClient,
    sp_access: SharePointAccessClass,
    file_path: str,
):
    """音声処理をバックグラウンドで実行"""
    try:
        app.state.task_status[task_id] = "processing"
        # MP4ファイル処理
        wav_data = await mp4_processor(file_path)
        if not wav_data:
            raise ValueError("MP4ファイルの処理に失敗しました")
        file_name = wav_data["file_name"]
        file_data = wav_data["file_data"]
        # Azure Blob Storage にアップロード
        blob_url = await az_blob_client.upload_blob(file_name, file_data)
        # 文字起こし
        transcribed_text = await az_speech_client.transcribe_audio(blob_url)
        if not transcribed_text:
            raise ValueError("文字起こしに失敗しました")
        # 要約処理
        summarized_text = await az_openai_client.summarize_text(transcribed_text)
        # site_data_dictがある場合のみSharePointにアップロード
        if (
            site_data_dict
            and "site" in site_data_dict
            and "directory" in site_data_dict
        ):
            word_file_path = await create_word(transcribed_text, summarized_text)
            sp_access.upload_file(
                site_data_dict["site"],
                site_data_dict["directory"],
                word_file_path,
            )
            await cleanup_word(word_file_path)
        # タスク結果を保存
        app.state.task_transcribed_text[task_id] = transcribed_text
        app.state.task_summarized_text[task_id] = summarized_text
        app.state.task_status[task_id] = "completed"
        # Blobストレージから削除
        await az_blob_client.delete_blob(file_name)
    except Exception as e:
        app.state.task_status[task_id] = "failed"
        app.state.task_transcribed_text[task_id] = f"エラー: {str(e)}"
        app.state.task_summarized_text[task_id] = f"エラー: {str(e)}"
        logger.error(f"タスク {task_id} の処理中にエラー: {str(e)}")
        logger.error(traceback.format_exc())

@app.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks,
    site_data: Optional[Transcribe] = Depends(parse_form),
    file: UploadFile = File(...),
    az_blob_client: AzBlobClient = Depends(get_az_blob_client),
    az_speech_client: AzTranscriptionClient = Depends(get_az_speech_client),
    az_openai_client: AzOpenAIClient = Depends(get_az_openai_client),
    sp_access: SharePointAccessClass = Depends(get_sp_access),
):
    """音声ファイルの文字起こし & 要約をバックグラウンドで処理"""
    task_id = str(uuid.uuid4())
    app.state.task_status[task_id] = "processing"
    app.state.task_transcribed_text[task_id] = None
    app.state.task_summarized_text[task_id] = None
    site_data_dict = site_data.model_dump() if site_data else {}

    try:
        file_path = save_disk(file)
        background_tasks.add_task(
            process_audio_task,
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
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/transcribe/{task_id}")
async def get_transcription_status(task_id: str):
    """タスクの進捗状況を取得"""
    if task_id not in app.state.task_status:
        raise HTTPException(status_code=404, detail="タスクIDが存在しません")
    return {
        "task_id": task_id,
        "status": app.state.task_status[task_id],
        "transcribed_text": app.state.task_transcribed_text[task_id],
        "summarized_text": app.state.task_summarized_text[task_id]
    }

@app.get("/sites")
async def get_sites(sp_access: SharePointAccessClass = Depends(get_sp_access)):
    """
    サイト一覧を取得するエンドポイント
    """
    try:
        return sp_access.get_sites()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サイト取得中にエラーが発生しました: {str(e)}")

@app.get("/directories")
async def get_directories(site_id: str = Query(default=None), sp_access: SharePointAccessClass = Depends(get_sp_access)):
    """
    指定されたサイトIDのディレクトリ一覧を取得するエンドポイント
    """
    try:
        return sp_access.get_folders(site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ディレクトリ取得中にエラーが発生しました: {str(e)}")

@app.get("/subdirectories")
async def get_subdirectories(site_id: str = Query(default=None), directory_id: str = Query(default=None), sp_access: SharePointAccessClass = Depends(get_sp_access)):
    try:
        return sp_access.get_subfolders(site_id, directory_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サブディレクトリ取得中にエラーが発生しました: {str(e)}")
