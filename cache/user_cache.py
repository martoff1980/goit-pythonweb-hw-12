from .redis_client import get_redis_client
import json


async def cache_user(user):
    """Заносимо користувача в Redis"""
    key = f"user:{user.id}"
    user_data = {"id": user.id, "email": user.email, "is_active": user.is_active}
    redis = await get_redis_client()
    await redis.set(key, json.dumps(user_data), ex=3600)  # TTL 1 час


async def get_cached_user(user_id: int):
    """Беремо користувача з Redis"""
    key = f"user:{user_id}"
    data = await get_redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def delete_user_cache(user_id: int):
    await get_redis_client.delete(f"user:{user_id}")
