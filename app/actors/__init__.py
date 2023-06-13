import logging

import dramatiq

from dramatiq.brokers.redis import RedisBroker

from app.config import CONFIG


REDIS_CONFIG = CONFIG['redis']

broker = RedisBroker(url=f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
broker.declare_queue("default")
dramatiq.set_broker(broker)


from app.actors.scans import run_masscan

__all__ = (
    "broker",
    "run_masscan",
)
