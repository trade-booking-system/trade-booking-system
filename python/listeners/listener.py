from utils.redis_initializer import get_redis_client
from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread
import signal
import os

class listener_base(ABC):
    def __init__(self, client= get_redis_client()):
        self.queue= Queue()
        self.client= client
        self.sub= self.client.pubsub(ignore_subscribe_messages= True)
        self.sub.subscribe(**self.get_handlers())
        self.queue_processor_thread= Thread(target= self.process_queue, daemon= True)

    def start(self):
        self.thread= self.sub.run_in_thread()
        self.startup()
        self.queue_processor_thread.start()
        signal.signal(signal.SIGTERM, self.termination_handler)

    def process_queue(self):
        while True:
            func, args= self.queue.get()
            func(*args)
            self.queue.task_done()

    def termination_handler(self, signum, frame):
        self.thread.stop()
        self.thread.join()
        self.queue.join()
        self.sub.close()
        self.client.close()

    def startup(self):
        mode= os.getenv("RECOVERY_MODE")
        if mode == "rebuild":
            self.rebuild()
        elif mode == "recover":
            self.recover()

    @abstractmethod
    def rebuild():
        pass

    @abstractmethod
    def recover():
        pass

    @abstractmethod
    def get_handlers() -> dict[str, any]:
        pass
