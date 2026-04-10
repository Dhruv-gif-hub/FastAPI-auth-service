from fastapi import FastAPI
from .middleware.logging import RequestLoggingMiddleware

app = FastAPI()

app.add_middleware(RequestLoggingMiddleware)