import redis
import os

def get_redis_client():
    client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0, decode_responses= True)
    try:
        yield client
    finally:
        client.close()
