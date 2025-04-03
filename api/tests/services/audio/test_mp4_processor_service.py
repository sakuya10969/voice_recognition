import pytest
import tempfile
import os
import subprocess
from fastapi import HTTPException

from api.app.services.audio.mp4_processing_service import MP4ProcessorService

class TestMP4ProcessorService:
    @pytest.fixture
    def service(self):
        return MP4ProcessorService()

    @pytest.fixture
    def temp_wav_file(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"dummy wav data")
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def temp_invalid_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"invalid file")
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.mark.asyncio
    async def test_process_mp4_with_wav(self, service, temp_wav_file):
        """WAVファイルを正常に処理できることを確認するテスト"""
        result = await service.process_mp4(temp_wav_file)
        
        assert result["file_name"].endswith(".wav")
        assert result["file_data"] == b"dummy wav data"

    @pytest.mark.asyncio
    async def test_process_mp4_with_invalid_extension(self, service, temp_invalid_file):
        """不正な拡張子のファイルを処理した場合にエラーとなることを確認するテスト"""
        with pytest.raises(HTTPException) as exc_info:
            await service.process_mp4(temp_invalid_file)
            
        assert exc_info.value.status_code == 400
        assert "サポートされていないファイル形式" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_convert_wav_failure(self, service, monkeypatch):
        """WAV変換が失敗した場合のエラーハンドリングを確認するテスト"""
        def mock_subprocess_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], stderr=b"ffmpeg error")

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)

        with tempfile.NamedTemporaryFile(suffix=".wav") as input_file:
            input_file.write(b"dummy")
            input_file.flush()
            output_path = f"{input_file.name}.out.wav"

            with pytest.raises(HTTPException) as exc_info:
                service._convert_wav(input_file.name, output_path)

            assert exc_info.value.status_code == 500
            assert "FFmpeg failed" in exc_info.value.detail