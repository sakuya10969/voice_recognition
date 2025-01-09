import os
import tempfile
import ffmpeg
from fastapi import HTTPException


async def save_disk_async(file, destination: str):
    """
    ファイルをディスクに非同期で保存する関数。

    :param file: ファイルオブジェクト
    :param destination: 保存先のパス
    """
    with open(destination, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):  # 非同期で読み込み
            out_file.write(chunk)


def convert_wav_sync(input_path: str, output_path: str):
    """
    MP4ファイルをWAVフォーマットに同期的に変換する関数。

    :param input_path: 入力ファイルのパス
    :param output_path: 出力ファイルのパス
    """
    try:
        ffmpeg.input(input_path).output(
            output_path,
            ar=16000,
            ac=1,
            sample_fmt="s16",
        ).run(overwrite_output=True)
    except ffmpeg.Error as e:
        raise HTTPException(
            status_code=500, detail=f"FFmpeg failed: {e.stderr.decode()}"
        )


async def mp4_processor(file) -> dict:
    """
    MP4ファイルを処理し、WAVファイルに変換する関数。

    :param file: ファイルオブジェクト
    :return: 処理後のファイル名とデータを含む辞書
    """
    try:
        # ファイル名と拡張子を取得
        sanitized_filename = os.path.basename(file.filename)
        file_extension = os.path.splitext(sanitized_filename)[1].lower()

        # WAV形式ならそのまま返す
        if file_extension == ".wav":
            wav_data = await file.read()  # 非同期でデータを読み込む
            return {"file_name": sanitized_filename, "file_data": wav_data}

        # 一時ディレクトリを利用
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, sanitized_filename)
            output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
            output_path = os.path.join(tmpdir, output_filename)

            # ファイルをディスクに保存
            await save_disk_async(file, input_path)

            # MP4をWAVに変換（同期処理）
            convert_wav_sync(input_path, output_path)

            # WAVファイルを読み取る
            with open(output_path, "rb") as f:
                wav_data = f.read()

            return {"file_name": output_filename, "file_data": wav_data}

    except Exception as e:
        # エラーをHTTPExceptionとしてスロー
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
