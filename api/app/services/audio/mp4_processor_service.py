import os
import tempfile
import subprocess
import logging
import imageio_ffmpeg as ffmpeg
from typing import Dict, Any
from pathlib import Path
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MP4ProcessorService:
    """MP4ファイルの処理を行うサービス"""
    
    async def process_mp4(self, file_path: str) -> Dict[str, Any]:
        """MP4ファイルを処理し、WAVデータを生成する"""
        try:
            sanitized_filename = os.path.basename(file_path)
            file_extension = os.path.splitext(sanitized_filename)[1].lower()
            
            # WAVファイルならそのまま返す
            if file_extension == ".wav":
                return self._read_file(file_path, sanitized_filename)
            
            # 出力パスの設定
            tmpdir = os.path.dirname(file_path)
            output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
            output_path = os.path.join(tmpdir, output_filename)
            
            # MP4をWAVに変換
            self._convert_wav(file_path, output_path)
            
            # 一時ディレクトリ内のMP4ファイルを削除
            self._cleanup_file(file_path, ".mp4", tmpdir)
            
            # 変換したWAVファイルを読み取る
            return self._read_file(output_path, output_filename)
            
        except Exception as e:
            logger.error(f"MP4ファイルの処理に失敗: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"MP4ファイルの処理に失敗しました: {str(e)}"
            )

    def _convert_wav(self, input_path: str, output_path: str) -> None:
        """MP4ファイルをWAVフォーマットに変換する"""
        try:
            ffmpeg_path = ffmpeg.get_ffmpeg_exe()
            command = [
                ffmpeg_path,
                "-i",
                input_path,
                "-ar",
                "16000",  # サンプリングレート 16kHz
                "-ac",
                "1",  # モノラルに変換
                "-sample_fmt",
                "s16",  # サンプルフォーマット（16-bit PCM）
                output_path,
            ]
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg failed: {e.stderr.decode()}"
            )

    def _read_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """ファイルを読み取り、ファイル名とデータを含む辞書を返す"""
        with open(file_path, "rb") as f:
            file_data = f.read()
        return {
            "file_name": filename,
            "file_data": file_data
        }

    def _cleanup_file(self, file_path: str, extension: str, directory: str) -> None:
        """指定されたファイルとディレクトリ内の特定の拡張子を持つファイルを削除する"""
        try:
            os.remove(file_path)
            for filename in os.listdir(directory):
                if filename.endswith(extension):
                    os.remove(os.path.join(directory, filename))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clean up files: {str(e)}"
            )