import os
import tempfile
import subprocess
import imageio_ffmpeg as ffmpeg
from fastapi import HTTPException, UploadFile

def save_disk(file: UploadFile) -> str:
    """
    UploadFile をローカルの一時ディレクトリに保存し、ファイルパスを返す関数。
    """
    try:
        temp_dir = tempfile.mkdtemp()  # 一時ディレクトリを作成
        temp_path = os.path.join(temp_dir, file.filename)  # 保存パスを決定
        with open(temp_path, "wb") as out_file:
            out_file.write(file.file.read())  # ファイルを保存
        return temp_path  # 保存したファイルのパスを返す
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

def convert_wav(input_path: str, output_path: str):
    """
    MP4ファイルをWAVフォーマットに同期的に変換する関数。
    """
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
        raise HTTPException(status_code=500, detail=f"FFmpeg failed: {e.stderr.decode()}")

async def mp4_processor(file_path: str) -> dict:
    """
    ローカルに保存された MP4 ファイルを処理し、WAV ファイルに変換する関数。
    変換後、一時ディレクトリ内のMP4ファイルを削除する。
    """
    try:
        sanitized_filename = os.path.basename(file_path)
        file_extension = os.path.splitext(sanitized_filename)[1].lower()
        # WAVファイルならそのまま返す
        if file_extension == ".wav":
            return _read_file(file_path, sanitized_filename)
        
        tmpdir = os.path.dirname(file_path)
        output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
        output_path = os.path.join(tmpdir, output_filename)
        # MP4をWAVに変換
        convert_wav(file_path, output_path)
        # 一時ディレクトリ内のMP4ファイルをすべて削除
        _cleanup_file(file_path, ".mp4", tmpdir)
        # 変換したWAVファイルを読み取る
        return _read_file(output_path, output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

def _read_file(file_path: str, filename: str) -> dict:
    """
    ファイルを読み取り、ファイル名とデータを含む辞書を返す。
    """
    with open(file_path, "rb") as f:
        file_data = f.read()
    return {"file_name": filename, "file_data": file_data}

def _cleanup_file(file_path: str, extension: str, directory: str):
    """
    指定されたファイルとディレクトリ内の特定の拡張子を持つファイルを削除する。
    """
    try:
        os.remove(file_path)
        for filename in os.listdir(directory):
            if filename.endswith(extension):
                os.remove(os.path.join(directory, filename))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean up files: {str(e)}")
