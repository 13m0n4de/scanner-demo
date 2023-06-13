import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app import get_app_config


REDIS_CONFIG = get_app_config()['redis']

broker = RedisBroker(url=f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
broker.declare_queue("default")
dramatiq.set_broker(broker)

from app.actors.masscan import run_masscan

__all__ = (
    "broker",
    "run_masscan",
)
