import os
import tempfile
import ffmpeg


def save_disk_sync(file, destination: str, chunk_size: int = 128 * 1024 * 1024):
    """
    ファイルをディスクに保存する関数。

    :param file: ファイルオブジェクト
    :param destination: 保存先のパス
    :param chunk_size: 一度に読み取るデータ量（デフォルト: 128MB）
    """
    with open(destination, "wb") as out_file:
        while chunk := file.read(chunk_size):
            out_file.write(chunk)


def convert_wav(input_path: str, output_path: str):
    """
    MP4ファイルをWAVフォーマットに変換する関数。

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
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")


def mp4_processor(file) -> dict:
    """
    MP4ファイルを処理し、WAVファイルに変換する関数。

    :param file: ファイルオブジェクト
    :return: 処理後のファイル名とデータを含む辞書
    """
    try:
        # ファイル名をサニタイズして拡張子を取得
        sanitized_filename = os.path.basename(file.filename)
        file_extension = os.path.splitext(sanitized_filename)[1].lower()

        # 入力が既にWAV形式の場合、そのまま返す
        if file_extension == ".wav":
            wav_data = file.read()
            return {"file_name": sanitized_filename, "file_data": wav_data}

        # 一時ディレクトリを利用してファイルを処理
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, sanitized_filename)
            output_filename = os.path.splitext(sanitized_filename)[0] + ".wav"
            output_path = os.path.join(tmpdir, output_filename)

            # ファイルを一時ディレクトリに保存
            save_disk_sync(file, input_path)

            # MP4をWAVに変換
            convert_wav(input_path, output_path)

            # 変換されたWAVファイルを読み取る
            with open(output_path, "rb") as f:
                wav_data = f.read()

            return {"file_name": output_filename, "file_data": wav_data}

    except Exception as e:
        # エラーをそのままRuntimeErrorとしてスロー
        raise RuntimeError(f"Failed to process file: {str(e)}")
