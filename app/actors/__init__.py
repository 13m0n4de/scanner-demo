import dramatiq

from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

from app.config import CONFIG
from app.utils import CustomJSONEncoder


REDIS_CONFIG = CONFIG['redis']

backend = RedisBackend(url=f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")

broker = RedisBroker(url=f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
broker.declare_queue("default")
broker.add_middleware(Results(backend=backend))

dramatiq.set_broker(broker)
dramatiq.set_encoder(CustomJSONEncoder())


from app.actors.scans import scan_by_masscan

__all__ = (
    "broker",
    "scan_by_masscan",
)
