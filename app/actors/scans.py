import subprocess

from typing import Dict

from app.actors import dramatiq
from app.config import CONFIG


@dramatiq.actor(store_results=True)
def run_masscan(config: Dict[str, str]) -> str:
    command = []
    config['binary'] = CONFIG['binary']['masscan']

    for arg in CONFIG['command']['masscan']:
        if value := config[arg['key']]:
            if option := arg.get('option'):
                command.append(option)
            command.append(str(value))

    run_masscan.logger.info(f'command => {" ".join(command)}')

    output = subprocess.check_output(command)
    run_masscan.logger.info(f'output => {output.decode()}')

    return output.decode()
