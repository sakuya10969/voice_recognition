from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

from app.transcribe_audio import transcribe_audio
from app.summary import summarize_text
from app.blob_processor import upload_blob, delete_blob
from app.mp4_processor import mp4_processor
from app.sharepoint import upload_sharepoint

# 環境変数をロード
load_dotenv(dotenv_path="../.env")

# 環境変数
AZ_SPEECH_KEY = os.getenv("AZ_SPEECH_KEY")
AZ_SPEECH_ENDPOINT = os.getenv("AZ_SPEECH_ENDPOINT")
AZ_BLOB_CONNECTION = os.getenv("AZ_BLOB_CONNECTION")
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


@app.post("/transcribe")
async def main(project_name: str, file: UploadFile = File(...)) -> str:
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

        # 音声を文字起こし
        transcribed_text = await transcribe_audio(blob_url, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT)

        # 要約処理
        summarized_text = await summarize_text(transcribed_text)
        
        # SharepointにWordファイルをアップロード
        await upload_sharepoint(project_name, summarized_text)

        # 処理後のBlobを削除
        await delete_blob(file_name, CONTAINER_NAME, AZ_BLOB_CONNECTION)

        # 結果を返却
        return summarized_text

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
