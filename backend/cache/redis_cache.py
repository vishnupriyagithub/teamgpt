import redis
import json
import os
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

def init_redis():
  
  global redis_client
  try:
    
    redis_client = redis.from_url(
      
      REDIS_URL,
      decode_responses=True,
      socket_connect_timeout=2,
      socket_timeout = 2
    )
    redis_client.ping()
    logger.info("Redis connected")
  except Exception as e:
    logger.warning(f"Redis connection error: {e}")
    redis_client = None
    

init_redis()

CACHE_TTL_SECONDS = 3600  # 1 hour


def get_cached_answer(key: str):
  
  if not redis_client:
      return None
  try:
    
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None
  except Exception as e:
      logger.warning(f"Redis read error: {e}")
      return None


def set_cached_answer(key: str, value: str, ttl: int=3600):
  if not redis_client:
      return
  try:
    redis_client.setex(
        key,
        CACHE_TTL_SECONDS,
        json.dumps(value)
    )
  except Exception as e:
      logger.warning(f"Redis write error: {e}")
