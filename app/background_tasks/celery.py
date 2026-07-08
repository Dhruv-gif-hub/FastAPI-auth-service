from celery import Celery, shared_task
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

celery.conf.update(

    task_serializer="json",

    result_serializer="json",

    accept_content=["json"],

    timezone="UTC",

    enable_utc=True,

    result_expires=3600,

    broker_connection_retry_on_startup=True,

    task_track_started=True,
)

@shared_task
def update_post(id, user, blog, post):
    return post.update_blog(id, user, blog)