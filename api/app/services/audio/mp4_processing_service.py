import os
import tempfile
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from typing import Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MP4ProcessingService:
    """MP4ファイルをWAVファイルに変換・処理するサービス"""
    
    async def process_mp4(self, file_path: str) -> Dict[str, Any]:
        """MP4ファイルを処理し、WAVデータを生成する"""
        try:
            sanitized_filename = os.path.basename(file_path)
            file_extension = os.path.splitext(sanitized_filename)[1].lower()
            
            allowed_extensions = ['.mp4', '.wav']
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"サポートされていないファイル形式です。許可される拡張子: {', '.join(allowed_extensions)}"
                )
            
            if file_extension == ".wav":
                return self._read_file(file_path, sanitized_filename)
            
            return await self._process_audio_file(file_path, sanitized_filename)
            
        except Exception as e:
            logger.error(f"MP4ファイルの処理に失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"MP4ファイルの処理に失敗しました: {str(e)}"
            )

    async def _process_audio_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """音声ファイルの変換処理を行う"""
        tmpdir = tempfile.mkdtemp()
        try:
            input_path = os.path.join(tmpdir, filename)
            output_filename = f"{os.path.splitext(filename)[0]}.wav"
            output_path = os.path.join(tmpdir, output_filename)
            
            await self._copy_file(file_path, input_path)
            self._convert_wav(input_path, output_path)
            result = self._read_file(output_path, output_filename)
            self._cleanup_file(input_path, ".mp4", tmpdir)
            
            return result
            
        finally:
            self._remove_temp_directory(tmpdir)

    async def _copy_file(self, src_path: str, dst_path: str) -> None:
        """ファイルをコピーする"""
        with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
            dst.write(src.read())

    def _convert_wav(self, input_path: str, output_path: str) -> None:
        """MP4ファイルをWAVフォーマットに変換する"""
        try:
            command = self._build_ffmpeg_command(input_path, output_path)
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg failed: {e.stderr.decode()}"
            )

    def _build_ffmpeg_command(self, input_path: str, output_path: str) -> list:
        """FFmpegコマンドを構築する"""
        return [
            ffmpeg.get_ffmpeg_exe(),
            "-i", input_path,
            "-ar", "16000",     # サンプリングレート 16kHz
            "-ac", "1",         # モノラルに変換
            "-sample_fmt", "s16", # サンプルフォーマット（16-bit PCM）
            output_path,
        ]

    def _read_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """ファイルを読み取り、ファイル名とデータを含む辞書を返す"""
        with open(file_path, "rb") as f:
            file_data = f.read()
        return {
            "file_name": filename,
            "file_data": file_data
        }

    def _cleanup_file(self, file_path: str, extension: str, directory: str) -> None:
        """ファイルとディレクトリ内の特定拡張子ファイルを削除する"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            for filename in os.listdir(directory):
                if filename.endswith(extension):
                    os.remove(os.path.join(directory, filename))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clean up files: {str(e)}"
            )

    def _remove_temp_directory(self, tmpdir: str) -> None:
        """一時ディレクトリを削除する"""
        try:
            import shutil
            shutil.rmtree(tmpdir)
        except Exception as e:
            logger.warning(f"一時ディレクトリの削除に失敗: {str(e)}")