import subprocess

from typing import Dict
from subprocess import CalledProcessError

from app.actors import dramatiq
from app.config import CONFIG


@dramatiq.actor
def run_masscan(config: Dict[str, str]):
    command = [
        part.format(
            binary=CONFIG['binary']['masscan'],
            target=config['target'],
            port_range=config['port_range'],
            rate=config['rate'],
            source_ip=config['source_ip'])
        for part in CONFIG['command']['masscan']]
    run_masscan.logger.info(command)
    # try:
    #     output = subprocess.check_output(command)
    #     print(output)
    # except CalledProcessError:
    #     pass
