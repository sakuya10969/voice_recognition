import os
import aiofiles
import tempfile
import ffmpeg
from fastapi import UploadFile, HTTPException


async def save_disk(file: UploadFile, destination: str, chunk_size: int = 128 * 1024 * 1024):
    async with aiofiles.open(destination, "wb") as out_file:
        while chunk := await file.read(chunk_size):
            await out_file.write(chunk)


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


async def mp4_processor(file: UploadFile):
    try:
        sanitized_filename = os.path.basename(file.filename)
        file_extension = os.path.splitext(sanitized_filename)[1].lower()

        if file_extension == ".wav":
            async with aiofiles.open(file.file, "rb") as f:
                wav_data = await f.read()
            return {"file_name": sanitized_filename, "file_data": wav_data}

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, sanitized_filename)
            output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
            output_path = os.path.join(tmpdir, output_filename)

            await save_disk(file, input_path)

            convert_wav(input_path, output_path)

            async with aiofiles.open(output_path, "rb") as f:
                wav_data = await f.read()

            return {"file_name": output_filename, "file_data": wav_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
