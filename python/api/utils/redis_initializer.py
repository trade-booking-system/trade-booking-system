import redis
import os

r

def initialize_redis():
    global r
    r= redis.Redis(host= os.getenv("REDIS_HOST"), port= 6379, db= 0)
