import os
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from typing import Any
from fastapi import HTTPException
import asyncio
import tempfile
import shutil
from aiofiles import open as aio_open
from aiofiles.os import remove as aio_remove

logger = logging.getLogger(__name__)


class MP4ProcessingService:
    """MP4ファイルをWAVファイルに変換・処理するサービス"""

    async def process_mp4(self, file_path: str) -> dict[str, Any]:
        sanitized_filename = os.path.basename(file_path)
        ext = os.path.splitext(sanitized_filename)[1].lower()

        if ext not in [".mp4", ".wav"]:
            raise HTTPException(status_code=400, detail="サポートされていないファイル形式です。")

        if ext == ".wav":
            return await self._read_file(file_path, sanitized_filename)

        return await self._process_audio_file(file_path, sanitized_filename)

    async def _process_audio_file(self, file_path: str, filename: str) -> dict[str, Any]:
        tmpdir = tempfile.mkdtemp()
        input_path = os.path.join(tmpdir, filename)
        output_filename = f"{os.path.splitext(filename)[0]}.wav"
        output_path = os.path.join(tmpdir, output_filename)

        try:
            await asyncio.to_thread(shutil.copy2, file_path, input_path)
            await asyncio.to_thread(self._convert_wav, input_path, output_path)
            result = await self._read_file(output_path, output_filename)
        except Exception as e:
            logger.error(f"処理エラー: {str(e)}")
            raise HTTPException(status_code=500, detail=f"処理失敗: {str(e)}")
        finally:
            await self._cleanup_directory(tmpdir)

        return result

    def _convert_wav(self, input_path: str, output_path: str) -> None:
        command = [
            ffmpeg.get_ffmpeg_exe(),
            "-i", input_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            "-y", output_path,
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8
        )
        _, stderr = process.communicate()
        if process.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg失敗: {stderr.decode(errors='ignore')}",
            )

    async def _read_file(self, file_path: str, filename: str) -> dict[str, Any]:
        async with aio_open(file_path, "rb") as f:
            data = await f.read()
        return {"file_name": filename, "file_data": data}

    async def _cleanup_directory(self, directory: str) -> None:
        try:
            for fname in os.listdir(directory):
                fpath = os.path.join(directory, fname)
                try:
                    await aio_remove(fpath)
                except Exception as e:
                    logger.warning(f"ファイル削除失敗: {fpath} ({e})")

            await asyncio.to_thread(shutil.rmtree, directory)
        except Exception as e:
            logger.warning(f"一時ディレクトリ削除失敗: {str(e)}")
