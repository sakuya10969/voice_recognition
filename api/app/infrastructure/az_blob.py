from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException

class AzBlobClient:
    """Azure Blob Storageとの通信を担当するクライアントクラス"""

    def __init__(self, connection_string: str, container_name: str) -> None:
        self._blob_service = BlobServiceClient.from_connection_string(connection_string)
        self._container = self._blob_service.get_container_client(container_name)

    async def upload_blob(self, file_name: str, file_data: bytes) -> str:
        """ファイルをBlobストレージにアップロードする"""
        try:
            blob = self._container.get_blob_client(blob=file_name)
            blob.upload_blob(file_data, overwrite=True)
            return blob.url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Blobのアップロードに失敗しました: {str(e)}"
            ) from e

    async def delete_blob(self, blob_name: str) -> None:
        """
        指定されたBlobを削除する"""
        try:
            self._container.delete_blob(blob_name)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Blobの削除に失敗しました: {str(e)}"
            ) from e
