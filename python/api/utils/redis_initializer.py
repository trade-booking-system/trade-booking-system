import redis
import os

r= None

def initialize_redis():
    global r
    r= redis.Redis(host= os.getenv("REDIS_HOST"), port= 6379, db= 0)

def get_redis_client():
    client = redis.Redis(host = os.getenv("REDIS_HOST"), port = 6379, db = 0)
    try:
        yield client
    finally:
        client.close
