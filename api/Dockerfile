# ビルド用のステージ
FROM python:3.10-slim AS builder

# 必要なビルドツールとライブラリをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを作成
WORKDIR /app

# Python依存関係をインストール
COPY requirements.txt . 
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 実行用のステージ
FROM python:3.10-slim AS runtime

# 最低限のランタイムライブラリをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi8 \
    libssl3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 必要なファイルをビルドステージからコピー
COPY --from=builder /install /usr/local
COPY . .

# .env ファイルをコンテナにコピー
COPY .env /app/.env

# SSL証明書をコンテナにコピー（ホストからコンテナにマウントする場合は別途volumes設定が必要）
COPY cert.pem /app/cert.pem
COPY key.pem /app/key.pem

# 作業ディレクトリ
WORKDIR /app

# FastAPI が利用するポートを公開
EXPOSE 443

# GunicornとUvicornを使ってSSL対応で起動を設定
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", \
    "--bind", "0.0.0.0:443", \
    "--certfile", "/app/cert.pem", \
    "--keyfile", "/app/key.pem", \
    "--workers", "4", \
    "--threads", "3", \
    "--log-level", "info"]
