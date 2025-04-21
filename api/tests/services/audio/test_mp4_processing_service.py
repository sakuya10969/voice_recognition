import pytest
import tempfile
import os
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

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
    def temp_mp4_file(self):
        """テスト用の一時MP4ファイルを提供するフィクスチャ"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"dummy mp4 data")
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
    async def test_process_mp4_with_wav(self, mp4_processing_service, temp_wav_file):
        """WAVファイルを正常に処理できることを確認するテスト"""
        result = await mp4_processing_service.process_mp4(temp_wav_file)
        assert result["file_name"].endswith(".wav")
        assert result["file_data"] == b"dummy wav data"
        mp4_processing_service._convert_wav.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_mp4_with_mp4(self, mp4_processing_service, temp_mp4_file):
        """MP4ファイルを正常に処理できることを確認するテスト"""
        mp4_processing_service._convert_wav.return_value = None
        mp4_processing_service._read_file_async = AsyncMock(return_value={
            "file_name": "test.wav",
            "file_data": b"converted wav data"
        })

        result = await mp4_processing_service.process_mp4(temp_mp4_file)
        assert result["file_name"] == "test.wav"
        assert result["file_data"] == b"converted wav data"
        mp4_processing_service._convert_wav.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_mp4_with_invalid_extension(self, mp4_processing_service, temp_invalid_file):
        """不正な拡張子のファイルを処理した場合にエラーとなることを確認するテスト"""
        with pytest.raises(HTTPException) as exc_info:
            await mp4_processing_service.process_mp4(temp_invalid_file)

        assert exc_info.value.status_code == 500
        assert "サポートされていないファイル形式" in exc_info.value.detail
        mp4_processing_service._convert_wav.assert_not_called()

    @patch("app.services.audio.mp4_processing_service.ffmpeg.get_ffmpeg_exe", return_value="ffmpeg")
    @patch("subprocess.Popen")
    def test_convert_wav_failure(self, mock_popen, mock_get_ffmpeg_exe):
        """WAV変換が失敗した場合のエラーハンドリングを確認するテスト"""
        service = MP4ProcessingService()

        # subprocess.Popenの戻り値をモック
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"ffmpeg error")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        with tempfile.NamedTemporaryFile(suffix=".wav") as input_file:
            input_file.write(b"dummy")
            input_file.flush()
            output_path = f"{input_file.name}.out.wav"

            with pytest.raises(HTTPException) as exc_info:
                service._convert_wav(input_file.name, output_path)

            assert exc_info.value.status_code == 500
            assert "FFmpeg失敗" in exc_info.value.detail
            mock_popen.assert_called_once()

    @pytest.mark.asyncio
    async def test_copy_file(self, mp4_processing_service):
        """ファイルコピー処理のテスト"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as src_file:
            src_file.write(b"test data")
            src_file.flush()
            dst_path = f"{src_file.name}.copy"

            await mp4_processing_service._copy_file(src_file.name, dst_path)

            assert os.path.exists(dst_path)
            with open(dst_path, "rb") as f:
                assert f.read() == b"test data"

            os.remove(dst_path)

    @pytest.mark.asyncio
    async def test_cleanup_file(self, mp4_processing_service):
        """ディレクトリ内のファイルクリーンアップ処理のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            assert os.path.exists(test_file)

            await mp4_processing_service._cleanup_file_async(tmpdir)

            assert not os.path.exists(test_file)

    @pytest.mark.asyncio
    async def test_remove_temp_directory(self, mp4_processing_service):
        """一時ディレクトリ削除処理のテスト"""
        tmpdir = tempfile.mkdtemp()
        assert os.path.exists(tmpdir)

        await mp4_processing_service._remove_temp_directory_async(tmpdir)

        assert not os.path.exists(tmpdir)
