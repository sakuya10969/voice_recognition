from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

from app.transcribe_audio import transcribe_audio
from app.summary import summarize_text
from app.blob_processor import upload_blob, delete_blob
from app.mp4_processor import mp4_processor
from app.word_generator import create_word, cleanup_file
from app.sharepoint import SharePointAccessClass

# 環境変数をロード
load_dotenv(dotenv_path="../.env")

# 環境変数
AZ_SPEECH_KEY = os.getenv("AZ_SPEECH_KEY")
AZ_SPEECH_ENDPOINT = os.getenv("AZ_SPEECH_ENDPOINT")
AZ_BLOB_CONNECTION = os.getenv("AZ_BLOB_CONNECTION")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
print(CLIENT_ID)
CONTAINER_NAME = "container-vr-dev"

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPIApp")

# FastAPIアプリケーションの初期化
app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sp_access = SharePointAccessClass(CLIENT_ID, CLIENT_SECRET, TENANT_ID)

@app.post("/transcribe")
async def main(project: str, project_directory: str, file: UploadFile = File(...)) -> str:
    """
    音声ファイルを文字起こしし、要約を返すエンドポイント。
    """
    try:
        # MP4ファイル処理
        response = await mp4_processor(file)
        file_name = response.get("file_name")
        file_data = response.get("file_data")
        # Azure Blob Storage にアップロード
        blob_url = await upload_blob(file_name, file_data, CONTAINER_NAME, AZ_BLOB_CONNECTION)

        try:
            # 音声を文字起こし
            transcribed_text = await transcribe_audio(blob_url, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT)
            # 要約処理
            summarized_text = await summarize_text(transcribed_text)
            # SharepointにWordファイルをアップロード
            word_file_path = await create_word(summarized_text)
            await sp_access.upload_file_to_sharepoint(project, project_directory, word_file_path)
            # 結果を返却
            return summarized_text
        
        finally:
            await delete_blob(file_name, CONTAINER_NAME, AZ_BLOB_CONNECTION)
            await cleanup_file(word_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
    
@app.get("/sites")
async def get_sites():
    """
    サイト一覧を取得するエンドポイント
    """
    try:
        return sp_access.get_sites()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サイト取得中にエラーが発生しました: {str(e)}")

@app.get("/directories")
async def get_directories(site_id: str = Query(...)):
    """
    指定されたサイトIDのディレクトリ一覧を取得するエンドポイント
    """
    try:
        return sp_access.get_folders(site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ディレクトリ取得中にエラーが発生しました: {str(e)}")
