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

# The backend_url is constructed similarly to the broker_url, 
# but it uses a different database index (REDIS_RESULT_DB) for storing task results.
backend_url = (
    f"redis://{Settings.host}:"
    f"{Settings.port}/"
    f"{Settings.REDIS_RESULT_DB}"
)

# Initialize Celery with the application name, broker URL, and backend URL.
# The Celery instance is configured with various settings, including task serialization format, 
# timezone, result expiration time, and connection retry behavior.
celery = Celery(
    "blog_app", # this specifies the name of the Celery application

    broker=broker_url, # this specifies the broker URL for Celery to send and receive messages 

    backend=backend_url
)

# Update Celery configuration settings to specify task serialization format,
# accepted content types, timezone, result expiration time, and connection retry behavior.
# Celery is configured to use JSON for task serialization and result serialization,
# accept only JSON content, operate in UTC timezone, enable UTC support,
# set result expiration time to 3600 seconds (1 hour), retry broker connection on startup,
# and track the start of tasks.
celery.conf.update(

    task_serializer="json", # this specifies that tasks will be serialized in JSON format

    result_serializer="json", # this specifies that results will be serialized in JSON format

    accept_content=["json"], # this specifies that only JSON content will be accepted

    timezone="UTC", # this specifies that the timezone for Celery will be UTC

    enable_utc=True, # this specifies that UTC support will be enabled

    result_expires=3600, # this specifies that the results of tasks will expire after 3600 seconds (1 hour)

    broker_connection_retry_on_startup=True, # this specifies that Celery will retry the broker connection on startup if it fails

    task_track_started=True, # this specifies that Celery will track the start of tasks
)

# @shared_task is a decorator provided by Celery that allows you to define 
# a task that can be executed asynchronously.
@shared_task
def update_post(id, user, blog, post):
    return post.update_blog(id, user, blog)