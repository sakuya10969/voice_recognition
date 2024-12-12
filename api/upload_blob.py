from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException

async def upload_blob(container_name: str, blob_name: str, blob_connection: str, file_data: bytes)-> str:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(blob_connection)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(file_data, overwrite=True)
        return blob_client.url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))