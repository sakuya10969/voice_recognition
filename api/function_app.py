import azure.functions as func
from fastapi import FastAPI, File, UploadFile, HTTPException
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import azure.functions as func

from transcribe_audio import transcribe_audio
from summary import summarize_text
from blob_processor import upload_blob, delete_blob
from mp4_processor import mp4_processor

fastapi_app = FastAPI()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

az_speech_key = os.getenv("AZ_SPEECH_KEY")
az_speech_endpoint = os.getenv("AZ_SPEECH_ENDPOINT")
az_blob_connection = os.getenv("AZ_BLOB_CONNECTION")
account_name = "strvr010"
container_name = "container-vr-dev"

@fastapi_app.post("/transcribe")
async def main(file: UploadFile = File(...)):
    try:
        response = await mp4_processor(file)
        file_name = response["file_name"]
        file_data = response["file_data"]

        blob_url = await upload_blob(container_name, file_name, az_blob_connection, file_data)
        # urlを元に文字起こしを行う
        display = await transcribe_audio(blob_url, az_speech_key, az_speech_endpoint)
        # 文字起こしされたテキストを要約
        summary_text = await summarize_text(display)
        # 処理が完了したらblob storage内のファイルを該当のwavファイルを削除
        await delete_blob(container_name, file_name, az_blob_connection)

        return summary_text
    except Exception as e:
        logging.error(f"Error during transcription: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process transcription: {str(e)}"
        )

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = func.AsgiFunctionApp(
    app=fastapi_app, 
    http_auth_level=func.AuthLevel.ANONYMOUS, 
)
