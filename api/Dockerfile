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
WORKDIR /api

# 必要なPython依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 実行用のステージ
FROM python:3.10-slim AS runtime

# 必要な最低限のランタイムライブラリをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi8 \
    libssl3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 必要なファイルをビルドステージからコピー
COPY --from=builder /install /usr/local

# ソースコードをコンテナにコピー
COPY ./app /api/app
COPY requirements.txt /api/
COPY .env /api/.env
COPY cert.pem /api/cert.pem
COPY key.pem /api/key.pem

# 作業ディレクトリを設定
WORKDIR /api

# FastAPIが利用するポートを公開
EXPOSE 443

# GunicornとUvicornを使ってSSL対応で起動を設定
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", \
    "--bind", "0.0.0.0:443", \
    "--certfile", "/api/cert.pem", \
    "--keyfile", "/api/key.pem", \
    "--workers", "4", \
    "--threads", "3", \
    "--timeout", "3600", \
    "--log-level", "info"]
