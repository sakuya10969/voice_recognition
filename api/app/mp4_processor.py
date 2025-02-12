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
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg failed: {e.stderr}")

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
            with open(file_path, "rb") as f:
                file_data = f.read()
            return {"file_name": sanitized_filename, "file_data": file_data}
        # 一時ディレクトリのパスを取得
        tmpdir = os.path.dirname(file_path)
        output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
        output_path = os.path.join(tmpdir, output_filename)
        # MP4をWAVに変換
        convert_wav(file_path, output_path)
        # 変換後のMP4ファイルを削除
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete original MP4 file: {str(e)}"
            )
        # 一時ディレクトリ内のMP4ファイルをすべて削除
        try:
            for filename in os.listdir(tmpdir):
                file_path = os.path.join(tmpdir, filename)
                if file_path.endswith(".mp4"):
                    os.remove(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to clean up temp directory: {str(e)}"
            )
        # 変換したWAVファイルを読み取る
        with open(output_path, "rb") as f:
            wav_data = f.read()
        return {"file_name": output_filename, "file_data": wav_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
