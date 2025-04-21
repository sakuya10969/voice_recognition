import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_process_audio(client, mocker):
    # UUID生成を固定にする
    mocker.patch("app.handlers.audio_processing_handler.uuid.uuid4", return_value="mock-task-id")

    # save_file_temporarily をモック
    mocker.patch("app.handlers.audio_processing_handler.save_file_temporarily", new=AsyncMock(return_value="/tmp/test.wav"))

    # UseCaseの生成をモック
    mock_usecase = AsyncMock()
    mocker.patch("app.handlers.audio_processing_handler._create_audio_usecase", return_value=mock_usecase)

    # Act
    files = {"file": ("dummy.wav", b"dummy content", "audio/wav")}
    response = client.post("/transcription", files=files)

    # Assert
    assert response.status_code == 202
    assert response.json() == {
        "task_id": "mock-task-id",
        "message": "処理を開始しました"
    }
    
def test_get_transcription_status(client, mocker):
    # task_managing_service のモック状態を注入
    mock_service = MagicMock()
    mock_service.status = {"mock-task-id": "Done"}
    mock_service.transcribed_text = {"mock-task-id": "テキスト"}
    mock_service.summarized_text = {"mock-task-id": "要約"}

    app.state.task_managing_service = mock_service

    response = client.get("/transcription/mock-task-id")
    assert response.status_code == 200
    assert response.json() == {
        "task_id": "mock-task-id",
        "status": "Done",
        "transcribed_text": "テキスト",
        "summarized_text": "要約"
    }
