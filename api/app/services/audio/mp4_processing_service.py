import os
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from typing import Dict, Any
from fastapi import HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiofiles import open as aio_open
from aiofiles.os import remove as aio_remove, rmdir as aio_rmdir
import tempfile
import shutil

logger = logging.getLogger(__name__)

class MP4ProcessingService:
    """MP4ファイルをWAVファイルに変換・処理するサービス"""

    def __init__(self):
        # I/Oバウンド処理のため、コア数の2倍を使用
        self._executor = ThreadPoolExecutor(max_workers=(os.cpu_count() or 2) * 2)

    async def process_mp4(self, file_path: str) -> Dict[str, Any]:
        try:
            sanitized_filename = os.path.basename(file_path)
            ext = os.path.splitext(sanitized_filename)[1].lower()

            if ext not in ['.mp4', '.wav']:
                raise HTTPException(status_code=400, detail="サポートされていないファイル形式です。")

            if ext == '.wav':
                return await self._read_file_async(file_path, sanitized_filename)

            return await self._process_audio_file(file_path, sanitized_filename)

        except Exception as e:
            logger.error(f"処理エラー: {str(e)}")
            raise HTTPException(status_code=500, detail=f"処理失敗: {str(e)}")

    async def _process_audio_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        tmpdir = tempfile.mkdtemp()
        try:
            input_path = os.path.join(tmpdir, filename)
            output_filename = f"{os.path.splitext(filename)[0]}.wav"
            output_path = os.path.join(tmpdir, output_filename)

            # ファイルコピー → ffmpeg変換
            await self._copy_file(file_path, input_path)
            await self._convert_wav_async(input_path, output_path)
            result = await self._read_file_async(output_path, output_filename)
            await self._cleanup_file_async(tmpdir)
            return result

        finally:
            await self._remove_temp_directory_async(tmpdir)

    async def _copy_file(self, src_path: str, dst_path: str) -> None:
        await asyncio.get_event_loop().run_in_executor(
            self._executor, shutil.copy2, src_path, dst_path
        )

    async def _convert_wav_async(self, input_path: str, output_path: str) -> None:
        await asyncio.get_event_loop().run_in_executor(
            self._executor, self._convert_wav, input_path, output_path
        )

    def _convert_wav(self, input_path: str, output_path: str) -> None:
        try:
            command = [
                ffmpeg.get_ffmpeg_exe(),
                "-i", input_path,
                "-vn",  # 映像なし
                "-map", "a",  # 音声ストリームのみ
                "-ar", "16000",
                "-ac", "1",
                "-sample_fmt", "s16",
                "-f", "wav",
                "-threads", "0",
                "-preset", "ultrafast",
                "-y", output_path
            ]
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, stderr=stderr)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"FFmpeg失敗: {e.stderr.decode(errors='ignore')}")

    async def _read_file_async(self, file_path: str, filename: str) -> Dict[str, Any]:
        async with aio_open(file_path, 'rb') as f:
            data = await f.read()
        return {"file_name": filename, "file_data": data}

    async def _cleanup_file_async(self, directory: str) -> None:
        for fname in os.listdir(directory):
            fpath = os.path.join(directory, fname)
            try:
                await aio_remove(fpath)
            except Exception as e:
                logger.warning(f"削除失敗: {fpath} ({e})")

    async def _remove_temp_directory_async(self, tmpdir: str) -> None:
        try:
            await asyncio.get_event_loop().run_in_executor(self._executor, shutil.rmtree, tmpdir)
        except Exception as e:
            logger.warning(f"一時ディレクトリ削除失敗: {str(e)}")