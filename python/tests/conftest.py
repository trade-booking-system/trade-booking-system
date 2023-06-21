import fnmatch
import re
from typing import List

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from api.main import app
from utils.redis_initializer import get_redis_client_zero, get_redis_client_one

class FakeClient:
    def __init__(self):
        self.data = {}
    
    def hget(self, name, key):
        return self.data[name][key]
    
    def hset(self, name, key, value):
        if name not in self.data:
            self.data[name] = {}
        self.data[name][key] = value
    
    def hgetall(self, name):
        return self.data[name]
    
    def keys(self, pattern):
        keys = []
        regex = re.compile(fnmatch.translate(pattern))
        for key in self.data.keys():
            if regex.match(key):
                keys.append(key)
        return keys
    
    def publish(self, channel, message):
        pass

class System:
    web: TestClient
    redis: List[FakeClient]

    def __init__(self, app: FastAPI):
        self.redis = [FakeClient(), FakeClient()]
        app.dependency_overrides[get_redis_client_zero] = lambda: self.redis[0]
        app.dependency_overrides[get_redis_client_one] = lambda: self.redis[1]
        self.web = TestClient(app)

@pytest.fixture()
def test_server() -> System:
    return System(app)
