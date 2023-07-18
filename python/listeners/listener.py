from utils.redis_initializer import get_redis_client
from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread
import signal

class listener_base(ABC):
    def __init__(self):
        self.queue= Queue()
        self.client= get_redis_client()
        self.sub= self.client.pubsub(ignore_subscribe_messages= True)
        for channel, handler in self.get_handlers().items():
            self.sub.subscribe(**{channel: handler}, args= (self.client))
        self.thread= self.sub.run_in_thread()
        self.startup()
        queue_processor_thread= Thread(target= self.process_queue, daemon= True)
        queue_processor_thread.start()
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

    @abstractmethod
    def get_handlers() -> dict[str, any]:
        pass

    @abstractmethod
    def startup(self):
        pass
