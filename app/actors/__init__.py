import dramatiq

from dramatiq.brokers.rabbitmq import RabbitmqBroker

from app.config import get_app_config

RABBITMQ_CONFIG = get_app_config()['rabbitmq']

rabbitmq_broker = RabbitmqBroker(
    url=(
        f"amqp://{RABBITMQ_CONFIG['user']}:{RABBITMQ_CONFIG['password']}"
        f"@{RABBITMQ_CONFIG['host']}:{RABBITMQ_CONFIG['port']}/{RABBITMQ_CONFIG['vhost']}"
    ))
dramatiq.set_broker(rabbitmq_broker)


from app.actors.masscan import run_masscan

__all__ = (
    "run_masscan",
)
