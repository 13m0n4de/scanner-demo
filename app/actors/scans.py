from typing import Dict

from app.actors import dramatiq
from app.config import CONFIG


@dramatiq.actor(store_results=True)
def run_masscan(config: Dict[str, str]) -> str:
    command = [
        part.format(
            binary=CONFIG['binary']['masscan'],
            target=config['target'],
            port_range=config['port_range'],
            rate=config['rate'],
            source_ip=config['source_ip'])
        for part in CONFIG['command']['masscan']]
    run_masscan.logger.info(command)
    return ''.join(command)
