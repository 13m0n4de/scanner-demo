import subprocess

from typing import Dict, List

from app.actors import dramatiq
from app.utils import build_command, parse_masscan_results


@dramatiq.actor(store_results=True)
def run_masscan(params: Dict[str, str]) -> List[Dict[str, str | int]]:
    command = build_command('masscan', params)
    run_masscan.logger.info(f'command => {" ".join(command)}')

    output = subprocess.check_output(command)
    run_masscan.logger.info(f'output => {output.decode()}')

    results = parse_masscan_results(output.decode())
    return results
