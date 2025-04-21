import pytest
from unittest.mock import MagicMock, patch
from app.infrastructure.az_blob import AzBlobClient
from fastapi import HTTPException

@pytest.fixture
def mock_blob_client():
    with patch("app.infrastructure.az_blob.BlobServiceClient") as mock_service:
        mock_instance = MagicMock()
        mock_container = MagicMock()
        mock_blob = MagicMock()

        # モックチェーンの構築
        mock_service.from_connection_string.return_value = mock_instance
        mock_instance.get_container_client.return_value = mock_container
        mock_container.get_blob_client.return_value = mock_blob

        yield {
            "service_mock": mock_service,
            "instance": mock_instance,
            "container": mock_container,
            "blob": mock_blob
        }

@pytest.fixture
def az_blob_client(mock_blob_client):
    return AzBlobClient("fake-connection", "test-container")

@pytest.mark.asyncio
async def test_upload_blob_success(az_blob_client, mock_blob_client):
    mock_blob = mock_blob_client["blob"]
    mock_blob.upload_blob.return_value = None
    mock_blob.url = "https://example.blob.core.windows.net/test/file.txt"

    result = await az_blob_client.upload_blob("file.txt", b"dummy data")

    assert result == "https://example.blob.core.windows.net/test/file.txt"
    mock_blob.upload_blob.assert_called_once_with(b"dummy data", overwrite=True)

@pytest.mark.asyncio
async def test_upload_blob_failure(az_blob_client, mock_blob_client):
    mock_blob = mock_blob_client["blob"]
    mock_blob.upload_blob.side_effect = Exception("Upload failed")

    with pytest.raises(HTTPException) as exc_info:
        await az_blob_client.upload_blob("file.txt", b"data")

    assert "Blobのアップロードに失敗しました" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_delete_blob_success(az_blob_client, mock_blob_client):
    container = mock_blob_client["container"]
    container.delete_blob.return_value = None

    await az_blob_client.delete_blob("file.txt")
    container.delete_blob.assert_called_once_with("file.txt")

@pytest.mark.asyncio
async def test_delete_blob_failure(az_blob_client, mock_blob_client):
    container = mock_blob_client["container"]
    container.delete_blob.side_effect = Exception("Delete failed")

    with pytest.raises(HTTPException) as exc_info:
        await az_blob_client.delete_blob("file.txt")

    assert "Blobの削除に失敗しました" in str(exc_info.value.detail)
