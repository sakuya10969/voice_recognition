import azure.functions as func
import logging
import json
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from transcribe_audio import transcribe_audio
from summary import summarize_text
from blob_processor import upload_blob, delete_blob
from mp4_processor import mp4_processor
from azure.functions import HttpRequest, HttpResponse

# 環境変数をロード
load_dotenv()

# 環境変数
AZ_SPEECH_KEY = os.getenv("AZ_SPEECH_KEY")
AZ_SPEECH_ENDPOINT = os.getenv("AZ_SPEECH_ENDPOINT")
AZ_BLOB_CONNECTION = os.getenv("AZ_BLOB_CONNECTION")
CONTAINER_NAME = "container-vr-dev"

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AzureFunctionApp")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="transcribe")
async def main(req: HttpRequest) -> HttpResponse:
    """
    Azure Functions HTTPトリガー用のエンドポイント処理。
    """
    try:
        logger.info("Processing request...")

        # ファイル取得
        file = req.files.get("file")
        if not file:
            return HttpResponse("File not provided", status_code=400)

        # MP4ファイル処理
        response = mp4_processor(file)
        file_name = response["file_name"]
        file_data = response["file_data"]

        # Azure Blob Storage にアップロード
        blob_url = upload_blob(CONTAINER_NAME, file_name, AZ_BLOB_CONNECTION, file_data)
        logger.info(f"Blob uploaded: {blob_url}")

        # 音声を文字起こし
        transcribed_text = await transcribe_audio(blob_url, AZ_SPEECH_KEY, AZ_SPEECH_ENDPOINT)
        logger.info(f"Transcribed text: {transcribed_text}")

        # 要約処理
        summarized_text = await summarize_text(transcribed_text)
        logger.info(f"Summarized text: {summarized_text}")

        # 処理後のBlobを削除
        delete_blob(CONTAINER_NAME, file_name, AZ_BLOB_CONNECTION)
        logger.info(f"Blob deleted: {file_name}")

        # 結果を返却
        return HttpResponse(
            body=summarized_text,
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
