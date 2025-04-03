import pytest
import tempfile
import os
import subprocess
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from app.services.audio.mp4_processing_service import MP4ProcessingService

class TestMP4ProcessingService:
    @pytest.fixture
    def mp4_processing_service(self):
        """MP4ProcessingServiceのモックを提供するフィクスチャ"""
        service = MP4ProcessingService()
        service._convert_wav = AsyncMock()
        return service

    @pytest.fixture
    def temp_wav_file(self):
        """テスト用の一時WAVファイルを提供するフィクスチャ"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"dummy wav data")
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def temp_invalid_file(self):
        """テスト用の不正な拡張子のファイルを提供するフィクスチャ"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"invalid file")
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.mark.asyncio
    async def test_process_mp4_with_wav(self, mp4_processing_service: MP4ProcessingService, temp_wav_file: str):
        """WAVファイルを正常に処理できることを確認するテスト"""
        # テストの実行
        result = await mp4_processing_service.process_mp4(temp_wav_file)
        
        # 結果の検証
        assert result["file_name"].endswith(".wav")
        assert result["file_data"] == b"dummy wav data"
        mp4_processing_service._convert_wav.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_mp4_with_invalid_extension(self, mp4_processing_service: MP4ProcessingService, temp_invalid_file: str):
        """不正な拡張子のファイルを処理した場合にエラーとなることを確認するテスト"""
        # テストの実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await mp4_processing_service.process_mp4(temp_invalid_file)
            
        assert exc_info.value.status_code == 400
        assert "サポートされていないファイル形式" in exc_info.value.detail
        mp4_processing_service._convert_wav.assert_not_called()

    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_convert_wav_failure(self, mock_run: AsyncMock, mp4_processing_service: MP4ProcessingService):
        """WAV変換が失敗した場合のエラーハンドリングを確認するテスト"""
        # モックの設定
        mock_run.side_effect = subprocess.CalledProcessError(1, ["ffmpeg"], stderr=b"ffmpeg error")

        # テスト用の一時ファイルの作成
        with tempfile.NamedTemporaryFile(suffix=".wav") as input_file:
            input_file.write(b"dummy")
            input_file.flush()
            output_path = f"{input_file.name}.out.wav"

            # テストの実行と検証
            with pytest.raises(HTTPException) as exc_info:
                await mp4_processing_service._convert_wav(input_file.name, output_path)

            assert exc_info.value.status_code == 500
            assert "FFmpeg failed" in exc_info.value.detail
            mock_run.assert_called_once()