from fastapi import FastAPI, File, UploadFile, HTTPException
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

from transcribe_audio import transcribe_audio
from summary import summarize_text
from upload_blob import upload_blob

app = FastAPI()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

az_speech_key = os.getenv("AZ_SPEECH_KEY")
az_speech_endpoint = os.getenv("AZ_SPEECH_ENDPOINT")
az_openai_key=os.getenv("AZ_OPENAI_KEY")
az_openai_endpoint=os.getenv("AZ_OPENAI_ENDPOINT")
az_blob_connection = os.getenv("AZ_BLOB_CONNECTION")
client_id = os.getenv("CLIENT_ID")
tenant_id = os.getenv("TENANT_ID")
client_secret = os.getenv("CLIENT_SECRET")
drive_id = os.getenv("DRIVE_ID")
folder_path = "voice recognition"
account_name="strvr010"
container_name="container-vr-dev"

@app.post("/transcribe")
async def main(file: UploadFile = File(...)):
    try:
        file_name = file.filename
        file_data = await file.read()
        
        blob_url = upload_blob(az_blob_connection, container_name, file_name, file_data)
        # urlを元に文字起こしを行う
        display = await transcribe_audio(blob_url, az_speech_key, az_speech_endpoint)
        # 文字起こしされたテキストを要約
        summary_text = await summarize_text(display)
        return summary_text
    except Exception as e:
        logging.error(f"Error during transcription: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process transcription: {str(e)}"
        )
