from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import traceback
from fastapi.responses import JSONResponse
import aiohttp
from contextlib import asynccontextmanager
import uuid

from app.transcribe_audio import AzTranscriptionClient
from app.summary_text import AzOpenAIClient
from app.blob_processor import AzBlobClient
from app.mp4_processor import mp4_processor
from app.word_generator import create_word, cleanup_file
from app.sharepoint_processor import SharePointAccessClass

# 環境変数をロード
load_dotenv()
# 環境変数
AZ_SPEECH_KEY = os.getenv("AZ_SPEECH_KEY")
AZ_SPEECH_ENDPOINT = os.getenv("AZ_SPEECH_ENDPOINT")
AZ_OPENAI_KEY = os.getenv("AZ_OPENAI_KEY")
AZ_OPENAI_ENDPOINT = os.getenv("AZ_OPENAI_ENDPOINT")
AZ_BLOB_CONNECTION = os.getenv("AZ_BLOB_CONNECTION")
AZ_CONTAINER_NAME = "container-vr-dev"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

@asynccontextmanager
async def lifespan(app: FastAPI):
    session = aiohttp.ClientSession()
    app.state.session = session
    yield
    await session.close()
# FastAPIアプリケーションの初期化
app = FastAPI(lifespan=lifespan)
task_results = {}
task_status={}
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
    session = request.app.state.session
    return AzTranscriptionClient(session, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT)
def get_az_openai_client():
    return AzOpenAIClient(AZ_OPENAI_KEY, AZ_OPENAI_ENDPOINT)
def get_sp_access():
    return SharePointAccessClass(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
# FastAPI側でのモデルを定義
class Transcribe(BaseModel):
    project: str
    project_directory: str
# クライアントから送信されたフォームデータをjson形式にパースする
def parse_form(
    project: str = Form(...),
    project_directory: str = Form(...)
) -> Transcribe:
    return Transcribe(project=project, project_directory=project_directory)

async def process_audio_task(
    task_id: str,
    project_data_dict: dict,
    az_blob_client: AzBlobClient,
    az_speech_client: AzTranscriptionClient,
    az_openai_client: AzOpenAIClient,
    sp_access: SharePointAccessClass,
    file_name: str,
    file_content: bytes,
):
    """音声処理をバックグラウンドで行い、タスクIDで管理"""
    try:
        task_status[task_id] = "processing"
        # MP4ファイル処理
        wav_data = await mp4_processor(file_name, file_content)
        file_name = wav_data["file_name"]
        file_data = wav_data["file_data"]
        # Azure Blob Storage にアップロード
        blob_url = await az_blob_client.upload_blob(file_name, file_data)
        # 文字起こし
        transcribed_text = await az_speech_client.transcribe_audio(blob_url)
        # 要約処理
        summarized_text = await az_openai_client.summarize_text(transcribed_text)
        # SharePointにWordファイルをアップロード
        word_file_path = await create_word(summarized_text)
        sp_access.upload_file(
            project_data_dict["project"],
            project_data_dict["project_directory"],
            word_file_path,
        )
        # タスク完了後の処理
        task_results[task_id] = summarized_text
        task_status[task_id] = "completed"
        # Blobストレージから削除
        if file_name:
            await az_blob_client.delete_blob(file_name)
    except Exception as e:
        task_status[task_id] = "failed"
        task_results[task_id] = f"Error processing file: {str(e)}"
        print(f"Error processing file for task {task_id}: {str(e)}")

@app.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks,
    project_data: Transcribe = Depends(parse_form),
    file: UploadFile = File(...),
    az_blob_client: AzBlobClient = Depends(get_az_blob_client),
    az_speech_client: AzTranscriptionClient = Depends(get_az_speech_client),
    az_openai_client: AzOpenAIClient = Depends(get_az_openai_client),
    sp_access: SharePointAccessClass = Depends(get_sp_access),
) -> dict:
    """
    音声ファイルを文字起こしし、要約を返すエンドポイント。
    """
    # タスクIDを生成
    task_id = str(uuid.uuid4())
    task_results[task_id] = None
    task_status[task_id] = "queued"
    project_data_dict = project_data.model_dump()
    try:
        file_name = file.filename
        file_content = await file.read()
        # バックグラウンドで処理を実行
        background_tasks.add_task(
            process_audio_task,
            task_id,
            project_data_dict,
            az_blob_client,
            az_speech_client,
            az_openai_client,
            sp_access,
            file_name,
            file_content,
        )
        return {"task_id": task_id, "message": "処理を開始しました"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc(),
            },
        )

@app.get("/transcribe/{task_id}")
async def get_transcription_status(task_id: str):
    """
    タスクの進捗状況または結果を取得するエンドポイント。
    """
    status = task_status[task_id]
    if status == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task_results[task_id],
        }
    return {"task_id": task_id, "status": status}

@app.get("/sites")
async def get_sites(sp_access: SharePointAccessClass = Depends(get_sp_access)):
    """
    サイト一覧を取得するエンドポイント
    """
    try:
        return await sp_access.get_sites()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サイト取得中にエラーが発生しました: {str(e)}")

@app.get("/directories/{site_id}")
async def get_directories(site_id: str, sp_access: SharePointAccessClass = Depends(get_sp_access)):
    """
    指定されたサイトIDのディレクトリ一覧を取得するエンドポイント
    """
    try:
        return await sp_access.get_folders(site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ディレクトリ取得中にエラーが発生しました: {str(e)}")
