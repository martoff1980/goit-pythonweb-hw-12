import redis.asyncio as redis
from config import get_settings


# Example of incorrect Redis client initialization:
# redis_client = redis.Redis(
#     host="redis",  # ❌ host не full URL
#     port=6379,
#     decode_responses=True
# )

# redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

_redis_client = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        settings = get_settings() 
        _redis_client = redis.Redis.from_url(settings.REDIS_URL)
    return _redis_client
