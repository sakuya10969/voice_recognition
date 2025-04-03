import os
import tempfile
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from typing import Dict, Any
from fastapi import HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor
import shutil

logger = logging.getLogger(__name__)

class MP4ProcessingService:
    """MP4ファイルをWAVファイルに変換・処理するサービス"""
    
    def __init__(self):
        # CPUコア数に応じてワーカー数を調整
        self._executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 2)
    
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
                return await self._read_file_async(file_path, sanitized_filename)
            
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
            
            # ファイルコピーと変換を並列実行
            copy_task = asyncio.create_task(self._copy_file(file_path, input_path))
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._convert_wav,
                input_path,
                output_path
            )
            
            # 両方のタスクの完了を待つ
            await copy_task
            
            result = await self._read_file_async(output_path, output_filename)
            await self._cleanup_file_async(input_path, ".mp4", tmpdir)
            
            return result
            
        finally:
            await self._remove_temp_directory_async(tmpdir)

    async def _copy_file(self, src_path: str, dst_path: str) -> None:
        """ファイルをコピーする（非同期）"""
        await asyncio.get_event_loop().run_in_executor(
            self._executor,
            shutil.copy2,
            src_path,
            dst_path
        )

    def _convert_wav(self, input_path: str, output_path: str) -> None:
        """MP4ファイルをWAVフォーマットに変換する"""
        try:
            command = self._build_ffmpeg_command(input_path, output_path)
            # バッファサイズを増やしてパフォーマンスを改善
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
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
            "-threads", "0",    # 利用可能なすべてのスレッドを使用
            "-preset", "ultrafast",  # エンコード速度を最適化
            output_path,
        ]

    async def _read_file_async(self, file_path: str, filename: str) -> Dict[str, Any]:
        """ファイルを非同期で読み取り、ファイル名とデータを含む辞書を返す"""
        file_data = await asyncio.get_event_loop().run_in_executor(
            self._executor,
            self._read_file_sync,
            file_path
        )
        return {
            "file_name": filename,
            "file_data": file_data
        }

    def _read_file_sync(self, file_path: str) -> bytes:
        """ファイルを同期的に読み取る"""
        with open(file_path, "rb") as f:
            return f.read()

    async def _cleanup_file_async(self, file_path: str, extension: str, directory: str) -> None:
        """ファイルとディレクトリ内の特定拡張子ファイルを非同期で削除する"""
        await asyncio.get_event_loop().run_in_executor(
            self._executor,
            self._cleanup_file_sync,
            file_path,
            extension,
            directory
        )

    def _cleanup_file_sync(self, file_path: str, extension: str, directory: str) -> None:
        """ファイルとディレクトリ内の特定拡張子ファイルを同期的に削除する"""
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

    async def _remove_temp_directory_async(self, tmpdir: str) -> None:
        """一時ディレクトリを非同期で削除する"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                shutil.rmtree,
                tmpdir
            )
        except Exception as e:
            logger.warning(f"一時ディレクトリの削除に失敗: {str(e)}")