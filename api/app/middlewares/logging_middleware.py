import logging
import time
from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse, Response

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "-"
    logger.info(
        f"[START] {request.method} {request.url.path} "
        f"from {client_host} "
        f"query={dict(request.query_params)}"
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # レスポンスボディをログに出力（StreamingResponseなどは省略）
        body_for_log = ""
        if isinstance(response, Response) and not isinstance(response, StreamingResponse):
            # Responseクラスの場合のみbodyを取得
            if hasattr(response, "body"):
                try:
                    body_bytes = response.body
                    body_for_log = body_bytes.decode("utf-8", errors="replace")
                    max_log_length = 500
                    if len(body_for_log) > max_log_length:
                        body_for_log = body_for_log[:max_log_length] + "...(truncated)"
                except Exception as e:
                    body_for_log = f"<Failed to decode body: {e}>"
        else:
            body_for_log = "<streaming or unknown response, not logged>"

        logger.info(
            f"[END] {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"from {client_host} "
            f"ProcessTime: {process_time:.3f}s "
            f"Response: {body_for_log}"
        )
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[ERROR] {request.method} {request.url.path} "
            f"from {client_host} "
            f"Error: {e} "
            f"ProcessTime: {process_time:.3f}s"
        )
        raise

def configure_logging(app: FastAPI) -> None:
    """アプリケーションにログミドルウェアを追加"""
    app.middleware("http")(logging_middleware)
