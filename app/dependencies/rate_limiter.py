import time
from fastapi import Request, HTTPException, status

rate_limiter_storage = {}

# Custome rate limiter dependency

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