from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from fastapi import HTTPException

class AzBlobClient:
    def __init__(self, az_blob_connection: str, az_container_name: str):
        """Azure Blob Storageクライアントの初期化"""
        self._blob_service_client = BlobServiceClient.from_connection_string(az_blob_connection)
        self._container_client = self._blob_service_client.get_container_client(az_container_name)

    async def upload_blob(self, file_name: str, file_data: bytes) -> str:
        """ファイルをAzure Blob Storageにアップロードする"""
        try:
            blob_client = self._container_client.get_blob_client(blob=file_name)
            blob_client.upload_blob(file_data, overwrite=True)
            return blob_client.url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Blobのアップロードに失敗しました: {str(e)}"
            ) from e

    async def delete_blob(self, blob_name: str) -> None:
        """Azure Blob Storageからファイルを削除する"""
        try:
            self._container_client.delete_blob(blob_name)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Blobの削除に失敗しました: {str(e)}"
            ) from e
