import redis
import os

client= redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0,
                   decode_responses= True)

def get_redis_client() -> redis.Redis:
    return client
