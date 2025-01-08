# Python 3.10 ベースイメージを使用
FROM python:3.10-slim

# 作業ディレクトリを作成
WORKDIR /app

# 必要な依存パッケージをインストール（ffmpegを含む）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 必要なPythonライブラリをリストアップしたファイルをコピー
COPY requirements.txt .

# Python依存関係をインストール（キャッシュを使用しない）
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY . .

# FastAPI が利用するポートを公開
EXPOSE 8000

# アプリを起動するコマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
