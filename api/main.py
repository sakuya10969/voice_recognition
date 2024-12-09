from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

from transcribe_audio import transcribe_audio
from summary import summarize_text

app = FastAPI()
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

az_speech_key = os.getenv("AZ_SPEECH_KEY")
az_speech_endpoint = os.getenv("AZ_SPEECH_ENDPOINT")
az_openai_key=os.getenv("AZ_OPENAI_KEY")
az_openai_endpoint=os.getenv("AZ_OPENAI_ENDPOINT")
client_id = os.getenv("CLIENT_ID")
tenant_id = os.getenv("TENANT_ID")
client_secret = os.getenv("CLIENT_SECRET")
drive_id = os.getenv("DRIVE_ID")
folder_path = "voice recognition"

class TranscribeRequest(BaseModel):
    blob_url: str


@app.post("/transcribe")
async def main(request: TranscribeRequest,file: UploadFile = File(...)):
    try:
        file_name = file.filename
        file_content = await file.read()
        
        blob_url = request.blob_url
        display = await transcribe_audio(blob_url, az_speech_key, az_speech_endpoint)
        summary_text = await summarize_text(display)
        return { "文字起こしされたテキスト": display, "要約されたテキスト": summary_text }
    except Exception as e:
        logging.error(f"Error during transcription: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process transcription: {str(e)}"
        )
