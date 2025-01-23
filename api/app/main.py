from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
import traceback
from fastapi.exceptions import RequestValidationError

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

logger = logging.getLogger("uvicorn.error")

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
# SharePointアクセスクラスの初期化
sp_access = SharePointAccessClass(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
# FastAPI側でのモデルを定義
# class Transcribe(BaseModel):
#     project: str
#     project_directory: str
# クライアントから送信されたフォームデータをjson形式にパースする
# def parse_form(
#     project: str = Form(...),
#     project_directory: str = Form(...)
# ) -> Transcribe:
#     return Transcribe(project=project, project_directory=project_directory)

@app.post("/transcribe")
async def main(
    # project_data: Transcribe = Depends(parse_form), 
    file: UploadFile = File(...)
    ) -> str:
    """
    音声ファイルを文字起こしし、要約を返すエンドポイント。
    """
    # project_data_dict = project_data.model_dump()
    try:
        # ログ: リクエストデータの受信を記録
        # logger.info(f"Received request with project: {project_data.project}, directory: {project_data.project_directory}")
        # MP4ファイル処理
        response = await mp4_processor(file)
        file_name = response.get("file_name")
        file_data = response.get("file_data")
        # ログ: ファイル処理結果を記録
        logger.info(f"File processed: {file_name}")
        # Azure Blob Storage にアップロード
        blob_url = await upload_blob(file_name, file_data, CONTAINER_NAME, AZ_BLOB_CONNECTION)
        # ログ: Blobアップロード成功
        logger.info(f"Uploaded to Azure Blob: {blob_url}")

        try:
            # 音声を文字起こし
            transcribed_text = await transcribe_audio(blob_url, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT)
            logger.info("Audio transcription completed.")
            # 要約処理
            summarized_text = await summarize_text(transcribed_text)
            logger.info("Text summarization completed.")

            # SharePointにWordファイルをアップロード
            # word_file_path = await create_word(summarized_text)
            # sp_access.upload_file(project_data_dict["project"], project_data_dict["project_directory"], word_file_path)
            # logger.info(f"Uploaded Word file to SharePoint: {word_file_path}")

            return summarized_text

        finally:
            await delete_blob(file_name, CONTAINER_NAME, AZ_BLOB_CONNECTION)
            # await cleanup_file(word_file_path)

    except RequestValidationError as ve:
        logger.error("Validation error occurred.")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=422,
            detail={"error": "Validation failed", "details": ve.errors()},
        )
    except Exception as e:
        logger.error("Unhandled exception occurred.")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "traceback": traceback.format_exc()},
        )

@app.get("/sites")
async def get_sites():
    """
    サイト一覧を取得するエンドポイント
    """
    try:
        return sp_access.get_sites()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サイト取得中にエラーが発生しました: {str(e)}")

@app.get("/directories/{site_id}")
async def get_directories(site_id: str):
    """
    指定されたサイトIDのディレクトリ一覧を取得するエンドポイント
    """
    try:
        return sp_access.get_folders(site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ディレクトリ取得中にエラーが発生しました: {str(e)}")
