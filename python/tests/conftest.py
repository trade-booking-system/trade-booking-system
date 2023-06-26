import datetime
import fnmatch
import random
import re

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from api.main import app
from utils.redis_initializer import get_redis_client_zero, get_redis_client_one
import schema

class Channel:
    def __init__(self):
        self.messages = []
        self.handlers = []
    
    def add_handler(self, handler):
        for message in self.messages:
            handler(message)
        self.messages = []
        self.handlers.append(handler)
    
    def add_message(self, message):
        if len(self.handlers) == 0:
            self.messages.append(message)
        else:
            for handler in self.handlers:
                handler(message)

class FakeClient:
    def __init__(self):
        self.data = {}
        self.channels: dict[str, Channel] = {}
    
    def hget(self, name, key):
        return self.data[name][key]
    
    def hset(self, name, key, value):
        if name not in self.data:
            self.data[name] = {}
        self.data[name][key] = value
    
    def hscan_iter(self, name):
        return self.data[name].items()
    
    def scan_iter(self, pattern):
        keys = []
        regex = re.compile(fnmatch.translate(pattern))
        for key in self.data.keys():
            if regex.match(key):
                keys.append(key)
        return keys
    
    def publish(self, channel, message):
        if channel not in self.channels:
            self.channels[channel] = Channel()
        self.channels[channel].add_message(message)
    
    def pubsub(self, ignore_subscribe_messages = True):
        class PubSub:
            def __init__(self, channels):
                self.channels = channels
            
            def subscribe(self, **handlers):
                for channel in handlers:
                    self.channels[channel].add_handler(handlers[channel])
            
            def run_in_thread(self, daemon = True):
                pass
        return PubSub(self.channels)
    
    def _add_channel(self, name):
        self.channels[name] = Channel()

class System:
    web: TestClient
    redis: list[FakeClient]

    def __init__(self, app: FastAPI):
        self.redis = [FakeClient(), FakeClient()]
        app.dependency_overrides[get_redis_client_zero] = lambda: self.redis[0]
        app.dependency_overrides[get_redis_client_one] = lambda: self.redis[1]
        self.web = TestClient(app)

@pytest.fixture()
def test_server() -> System:
    return System(app)

def trade_to_dict(trade: schema.Trade):
    trade_dict = trade.dict()
    for key in ["date", "time"]:
        trade_dict[key] = str(trade_dict[key])
    return trade_dict

def assert_trades_equal(trade1, trade2):
    keys = []
    for key in ["account", "user", "type", "stock_ticker", "amount", "date", "time"]:
        if trade1[key] != trade2[key]:
            keys.append(key)
    assert len(keys) == 0, "keys not equal: " + ", ".join(keys) + f" {keys[0]} {type(trade1[keys[0]])} {type(trade2[keys[0]])}"

def generate_trade(seed: int) -> schema.Trade:
    random_gen = random.Random(seed)
    account = "account" + str(random_gen.randrange(1, 4))
    user = "user" + str(random_gen.randrange(1, 4))
    type = random_gen.choice(["buy", "sell"])
    stock_ticker = random_gen.choice(["ABC", "XYZ", "LMNOP"])
    amount = random_gen.randrange(1, 1000)
    date = datetime.date(random_gen.randrange(1900, 2100), random_gen.randrange(1, 13),
                         random_gen.randrange(1, 29))
    time = datetime.time(random_gen.randrange(0, 24), random_gen.randrange(0, 60),
                         random_gen.randrange(0, 60))
    return schema.Trade(account=account, user=user, type=type, stock_ticker=stock_ticker,
                        amount=amount, date=date, time=time)

def generate_trades(count: int, seed: int) -> list[schema.Trade]:
    trades: list[schema.Trade] = []
    for i in range(count):
        trades.append(generate_trade(seed + i))
    return trades
