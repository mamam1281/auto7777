import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def set_user_streak(user_id: int, count: int, ttl: int = 86400):
    key = f"user:{user_id}:streak_count"
    redis_client.set(key, count, ex=ttl)
    return key

def get_user_streak(user_id: int):
    key = f"user:{user_id}:streak_count"
    return redis_client.get(key)

def invalidate_user_streak(user_id: int):
    key = f"user:{user_id}:streak_count"
    redis_client.delete(key)
    return key

def get_ttl(key: str):
    return redis_client.ttl(key)

def cache_hit_rate():
    info = redis_client.info()
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    if hits + misses == 0:
        return 0.0
    return hits / (hits + misses)
