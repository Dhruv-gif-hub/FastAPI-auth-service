from celery import Celery, shared_task
from ..core.config import Settings

# Broker URL and Backend URL for Celery using Redis
# The broker URL is used by Celery to send and receive messages, 
# while the backend URL is used to store the results of tasks. 
# Both URLs are constructed using the host, port, 
# and database settings defined in the Settings class.
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

# Initialize Celery with the application name, broker URL, and backend URL.
# The Celery instance is configured with various settings, including task serialization format, 
# timezone, result expiration time, and connection retry behavior.
celery = Celery(
    "blog_app",

    broker=broker_url,

    backend=backend_url
)

# Update Celery configuration settings to specify task serialization format,
# accepted content types, timezone, result expiration time, and connection retry behavior.
# Celery is configured to use JSON for task serialization and result serialization,
# accept only JSON content, operate in UTC timezone, enable UTC support,
# set result expiration time to 3600 seconds (1 hour), retry broker connection on startup,
# and track the start of tasks.
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

# This is a shared Celery task that updates a blog post. It takes the post ID, user, blog,
# and post data as arguments and calls the `update_blog` method 
# of the post object to perform the update operation. 
# The result of the update operation is returned.
@shared_task
def update_post(id, user, blog, post):
    return post.update_blog(id, user, blog)