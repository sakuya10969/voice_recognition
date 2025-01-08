from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import os
from dotenv import load_dotenv
from transcribe_audio import transcribe_audio
from summary import summarize_text
from blob_processor import upload_blob, delete_blob
from mp4_processor import mp4_processor

# 環境変数をロード
load_dotenv()

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
async def main(file: UploadFile = File(...)):
    """
    音声ファイルを文字起こしし、要約を返すエンドポイント。
    """
    try:
        logger.info("Processing request...")

        # MP4ファイル処理
        response = await mp4_processor(file)
        file_name = response["file_name"]
        file_data = response["file_data"]

        # Azure Blob Storage にアップロード
        blob_url = await upload_blob(CONTAINER_NAME, file_name, AZ_BLOB_CONNECTION, file_data)
        logger.info(f"Blob uploaded: {blob_url}")

        # 音声を文字起こし
        transcribed_text = await transcribe_audio(
            blob_url, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT
        )
        logger.info(f"Transcribed text: {transcribed_text}")

        # 要約処理
        summarized_text = await summarize_text(transcribed_text)
        logger.info(f"Summarized text: {summarized_text}")

        # 処理後のBlobを削除
        await delete_blob(CONTAINER_NAME, file_name, AZ_BLOB_CONNECTION)
        logger.info(f"Blob deleted: {file_name}")

        # 結果を返却
        return summarized_text

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
