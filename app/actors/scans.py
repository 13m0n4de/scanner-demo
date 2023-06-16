import subprocess

from typing import Dict, List

from app.actors import dramatiq
from app.utils import build_command, parse_masscan_output


@dramatiq.actor(store_results=True)
def scan_by_masscan(params: Dict[str, str | int]) -> List[Dict[str, str | int]]:
    command = build_command('masscan', params)

    output = subprocess.check_output(command)

    results = parse_masscan_output(output.decode())
    return results
