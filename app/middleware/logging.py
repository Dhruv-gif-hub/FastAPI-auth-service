import os
import logging
import time
from typing import Any
from uuid import uuid4
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# File Handler
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Middleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Any:
        request_id = str(uuid4())
        # time.perf_counter() is used over time.time() for better precision in measuring elapsed time
        start_time = time.perf_counter()
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            f"[{request_id}] START | {method} {url} | IP={client_ip}"
        )
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                f"[{request_id}] ERROR | {method} {url} | {str(e)}"
            )
            raise
        process_time = time.perf_counter() - start_time
        logger.info(
            f"[{request_id}] END | {method} {url} | "
            f"STATUS={response.status_code} | TIME={process_time:.4f}s"
        )
        return response
    

