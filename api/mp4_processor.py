import ffmpeg
import os
from tempfile import NamedTemporaryFile

def save_temp(file_bytes: bytes, filename: str)-> str:
    try:
        _, ext = os.path.splitext(filename)

        with NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        return temp_file_path

    except Exception as e:
        raise RuntimeError(f"ファイル保存中にエラーが発生しました: {e}") from e

def convert_wav(input_file_path: str)-> str:
    temp_dir = os.path.dirname(input_file_path)
    output_file_path = os.path.splitext(os.path.basename(input_file_path))[0] + ".wav"
    try:
        ffmpeg.input(input_file_path).output(os.path.join(temp_dir, output_file_path)).run(overwrite_output=True)
        return output_file_path
    except ffmpeg.Error as e:
        raise Exception(f"FFmpeg error: {e.stderr.decode('utf-8')}")
