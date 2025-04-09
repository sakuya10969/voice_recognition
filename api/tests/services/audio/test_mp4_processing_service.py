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
    async def test_process_mp4_with_wav(self, mp4_processing_service: MP4ProcessingService, temp_wav_file: str):
        """WAVファイルを正常に処理できることを確認するテスト"""
        # テストの実行
        result = await mp4_processing_service.process_mp4(temp_wav_file)
        
        # 結果の検証
        assert result["file_name"].endswith(".wav")
        assert result["file_data"] == b"dummy wav data"
        mp4_processing_service._convert_wav.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_mp4_with_mp4(self, mp4_processing_service: MP4ProcessingService, temp_mp4_file: str):
        """MP4ファイルを正常に処理できることを確認するテスト"""
        # モックの設定
        mp4_processing_service._convert_wav.return_value = None
        mp4_processing_service._read_file_async = AsyncMock(return_value={
            "file_name": "test.wav",
            "file_data": b"converted wav data"
        })

        # テストの実行
        result = await mp4_processing_service.process_mp4(temp_mp4_file)
        
        # 結果の検証
        assert result["file_name"] == "test.wav"
        assert result["file_data"] == b"converted wav data"
        mp4_processing_service._convert_wav.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_mp4_with_invalid_extension(self, mp4_processing_service: MP4ProcessingService, temp_invalid_file: str):
        """不正な拡張子のファイルを処理した場合にエラーとなることを確認するテスト"""
        # テストの実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await mp4_processing_service.process_mp4(temp_invalid_file)
            
        assert exc_info.value.status_code == 500
        assert "サポートされていないファイル形式" in exc_info.value.detail
        mp4_processing_service._convert_wav.assert_not_called()

    @patch('subprocess.Popen')
    async def test_convert_wav_failure(self, mock_popen: MagicMock, mp4_processing_service: MP4ProcessingService):
        """WAV変換が失敗した場合のエラーハンドリングを確認するテスト"""
        # モックの設定
        mock_process = MagicMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b"ffmpeg error"))
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

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
            mock_popen.assert_called_once()

    @pytest.mark.asyncio
    async def test_copy_file(self, mp4_processing_service: MP4ProcessingService):
        """ファイルコピー処理のテスト"""
        # テスト用の一時ファイルの作成
        with tempfile.NamedTemporaryFile(suffix=".txt") as src_file:
            src_file.write(b"test data")
            src_file.flush()
            
            dst_path = f"{src_file.name}.copy"
            
            # テストの実行
            await mp4_processing_service._copy_file(src_file.name, dst_path)
            
            # 結果の検証
            assert os.path.exists(dst_path)
            with open(dst_path, "rb") as f:
                assert f.read() == b"test data"
            
            # 後片付け
            os.remove(dst_path)

    @pytest.mark.asyncio
    async def test_cleanup_file(self, mp4_processing_service: MP4ProcessingService):
        """ファイルクリーンアップ処理のテスト"""
        # テスト用の一時ディレクトリとファイルの作成
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            
            # テストの実行
            await mp4_processing_service._cleanup_file_async(test_file, ".txt", tmpdir)
            
            # 結果の検証
            assert not os.path.exists(test_file)

    @pytest.mark.asyncio
    async def test_remove_temp_directory(self, mp4_processing_service: MP4ProcessingService):
        """一時ディレクトリ削除処理のテスト"""
        # テスト用の一時ディレクトリの作成
        tmpdir = tempfile.mkdtemp()
        
        # テストの実行
        await mp4_processing_service._remove_temp_directory_async(tmpdir)
        
        # 結果の検証
        assert not os.path.exists(tmpdir)