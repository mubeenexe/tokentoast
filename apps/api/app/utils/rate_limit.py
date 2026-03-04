from fastapi import Request, HTTPException, status
from app.core.config import settings
from app.core.redis import get_redis

RATE_LIMIT_LOGIN_KEY = "ratelimit:login"
RATE_LIMIT_REGISTER_KEY = "ratelimit:register"
RATE_LIMIT_FORGOT_PASSWORD_KEY = "ratelimit:forgot_password"
WINDOW_SECONDS = 60


async def _increment_with_fallback(key: str) -> int | None:
    """
    Increment a Redis key, but fail open (no rate limit)
    if Redis is unavailable (useful in local dev).
    """
    try:
        redis = await get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, WINDOW_SECONDS)
        return count
    except Exception:
        # If Redis is down or misconfigured, skip rate limiting
        # instead of raising a 500 error.
        return None


async def rate_limit_login(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    key = f"{RATE_LIMIT_LOGIN_KEY}:{ip}"
    count = await _increment_with_fallback(key)
    if count is None:
        return
    if count > settings.RATE_LIMIT_LOGIN_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )


async def rate_limit_register(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    key = f"{RATE_LIMIT_REGISTER_KEY}:{ip}"
    count = await _increment_with_fallback(key)
    if count is None:
        return
    if count > settings.RATE_LIMIT_REGISTER_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Try again later.",
        )


async def rate_limit_forgot_password(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    key = f"{RATE_LIMIT_FORGOT_PASSWORD_KEY}:{ip}"
    count = await _increment_with_fallback(key)
    if count is None:
        return
    if count > settings.RATE_LIMIT_FORGOT_PASSWORD_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Try again later.",
        )
