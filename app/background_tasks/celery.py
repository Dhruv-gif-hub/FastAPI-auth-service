from celery import Celery
from ..core.config import Settings

broker_url = (
    f"redis://{Settings.host}:"
    f"{Settings.port}/"
    f"{Settings.REDIS_BROKER_DB}"
)

backend_url = (
    f"redis://{Settings.host}:"
    f"{Settings.port}/"
    f"{Settings.REDIS_RESULT_DB}"
)


celery = Celery(
    "blog_app",

    broker=broker_url,

    backend=backend_url
)