from fastapi import HTTPException, Request, status
from ..caching.redis import redis_client

class rate_limiter:
    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        redis_client = redis_client
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(self, request: Request):
        client_ip = request.client.host

        key = f"rate_limit:{client_ip}"

        current_count = await self.redis.incr(key)

        if current_count == 1:
            await self.redis.expire(
                key,
                self.window_seconds
            )

        if current_count > self.max_requests:

            ttl = await self.redis.ttl(key)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds."
            )











"""
rate_limiter_storage = {}

def rate_limiter(limit: int, window_seconds: int):
    async def limiter(request: Request):
        client_ip = request.client.host

        now = time.perf_counter()
        if client_ip not in rate_limiter_storage:
            rate_limiter_storage[client_ip] = []

        rate_limiter_storage[client_ip] = [
            timestamp for timestamp in rate_limiter_storage[client_ip]
            if timestamp > now - window_seconds
        ]

        if len(rate_limiter_storage[client_ip]) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Try again later."
            )
        rate_limiter_storage[client_ip].append(now)

    return limiter
"""