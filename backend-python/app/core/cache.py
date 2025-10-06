import hashlib, json, datetime
import redis
from .config import settings

r = redis.from_url(settings.REDIS_URL)

def make_cache_key(namespace: str, query: dict) -> str:
    payload = json.dumps(query, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return f"{namespace}:{h}"

def get_cache(namespace: str, query: dict):
    key = make_cache_key(namespace, query)
    val = r.get(key)
    if val:
        return json.loads(val)
    return None

def set_cache(namespace: str, query: dict, data, ttl_seconds: int = 604800):
    key = make_cache_key(namespace, query)
    r.setex(key, ttl_seconds, json.dumps(data, ensure_ascii=False))
    return key
