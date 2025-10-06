import time
import redis
from fastapi import HTTPException, status
from .config import settings
r = redis.from_url(settings.REDIS_URL)

def allow_request(key: str, limit: int, window_seconds: int = 60) -> bool:
    now = int(time.time())
    bucket = f"rate:{key}:{now // window_seconds}"
    cnt = r.incr(bucket)
    if cnt == 1:
        r.expire(bucket, window_seconds)
    return cnt <= limit

def enforce_quota(user_key: str, limit_per_minute: int = 60):
    if not allow_request(user_key, limit_per_minute, 60):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

def inc_overpass_count(user_key: str):
    day_key = f"quota:overpass:{user_key}:{time.strftime('%Y-%m-%d')}"
    total = r.incr(day_key)
    if total == 1:
        r.expire(day_key, 86400)
    return total
