import subprocess

from app.config import get_app_config
from app.actors import dramatiq


CONFIG = get_app_config()


@dramatiq.actor
def run_masscan(target: str):
    command = [
        part.format(
            binary=CONFIG['binary']['masscan'],
            target=target)
        for part in CONFIG['command']['masscan']]
    output = subprocess.check_output(command)
    print(output)
