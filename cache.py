import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def get_cached_link(short_code: str):
    return redis_client.get(f"link:{short_code}")

def set_cached_link(short_code: str, original_url: str, ttl: int = 3600):
    redis_client.setex(f"link:{short_code}", ttl, original_url)

def delete_cached_link(short_code: str):
    redis_client.delete(f"link:{short_code}")