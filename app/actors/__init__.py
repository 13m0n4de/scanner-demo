import dramatiq

from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from dramatiq.worker import Worker

from app.config import CONFIG


REDIS_CONFIG = CONFIG['redis']

backend = RedisBackend(url=f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")

broker = RedisBroker(url=f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
broker.declare_queue("default")
broker.add_middleware(Results(backend=backend))
dramatiq.set_broker(broker)

worker = Worker(broker=broker, queues="default")


from app.actors.scans import run_masscan

__all__ = (
    "broker",
    "run_masscan",
)
