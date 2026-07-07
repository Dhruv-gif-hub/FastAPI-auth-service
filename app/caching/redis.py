from redis.asyncio import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from ..core.config import Settings
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    BusyLoadingError
)

redis_client = Redis(
    host=Settings.host,
    port=Settings.port,
    db=Settings.REDIS_CACHE_DB,
    decode_responses=Settings.decode_responses,
    max_connections=Settings.max_connections,
    socket_connect_timeout=Settings.socket_connect_timeout, # Time to wait for a connection to be established
    socket_timeout=Settings.socket_timeout, # Time to wait for a response after a command is sent
    # Interval to check the health of connections in the pool
    health_check_interval=Settings.health_check_interval, 
    

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