import redis
import os

def get_redis_client_zero():
    client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0, decode_responses= True)
    try:
        yield client
    finally:
        client.close()

def get_redis_client_one():
    client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 1, decode_responses= True)
    yield client