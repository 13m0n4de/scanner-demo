import subprocess

from typing import Dict, List, Union

from app.actors import dramatiq
from app.utils import build_masscan_command, parse_masscan_output, parse_httpx_output
from app.models import MasscanParams, ScanResult


@dramatiq.actor(store_results=True)
def scan_by_masscan(params: Union[MasscanParams, List[ScanResult]]) -> List[ScanResult]:
    command = build_masscan_command(params)
    output = subprocess.check_output(command)
    results = parse_masscan_output(output.decode())
    return results
