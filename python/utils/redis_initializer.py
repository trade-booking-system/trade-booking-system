import redis
import os

def get_redis_client():
    return redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0,
                       decode_responses= True)
