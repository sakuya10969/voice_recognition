import os
import tempfile
import ffmpeg
from fastapi import UploadFile, HTTPException, File


def save_disk_sync(file: UploadFile, destination: str, chunk_size: int = 128 * 1024 * 1024):
    with open(destination, "wb") as out_file:
        while chunk := file.file.read(chunk_size):
            out_file.write(chunk)


def convert_wav(input_path: str, output_path: str):
    try:
        ffmpeg.input(input_path).output(
            output_path,
            ar=16000,
            ac=1,
            sample_fmt="s16",
        ).run(overwrite_output=True)
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")


async def mp4_processor(file: UploadFile = File(...)) -> dict:
    try:
        sanitized_filename = os.path.basename(file.filename)
        file_extension = os.path.splitext(sanitized_filename)[1].lower()

        if file_extension == ".wav":
            wav_data = file.file.read()
            return {"file_name": sanitized_filename, "file_data": wav_data}

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, sanitized_filename)
            output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
            output_path = os.path.join(tmpdir, output_filename)

            save_disk_sync(file, input_path)

            convert_wav(input_path, output_path)

            with open(output_path, "rb") as f:
                wav_data = f.read()

            return {"file_name": output_filename, "file_data": wav_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
