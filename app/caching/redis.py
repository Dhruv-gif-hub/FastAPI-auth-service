from redis.asyncio import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    BusyLoadingError
)

redis_client = Redis(
    host="localhost",
    port=6379,

    decode_responses=True,

    max_connections=100,

    socket_connect_timeout=5, # Time to wait for a connection to be established

    socket_timeout=5, # Time to wait for a response after a command is sent

    health_check_interval=30, # Interval to check the health of connections in the pool

    retry=Retry(
        ExponentialBackoff(
            base=0.1,
            cap=10
        ),
        retries=5
    ),

    retry_on_error=[
        ConnectionError,
        TimeoutError,
        BusyLoadingError
    ]
)