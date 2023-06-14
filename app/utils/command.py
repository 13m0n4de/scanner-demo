import re
from typing import Dict, List

from app.config import CONFIG


BINARY_CONFIG = CONFIG['binary']
COMMAND_CONFIG = CONFIG['command']


def build_command(name: str, params: Dict[str, str]) -> List[str]:
    command = []
    params['binary'] = BINARY_CONFIG[name]

    for arg in COMMAND_CONFIG[name]:
        if value := params[arg['key']]:
            if option := arg.get('option'):
                command.append(option)
            command.append(str(value))

    return command


def parse_masscan_results(text: str) -> List[Dict[str, str | int]]:
    pattern = r"Discovered open port (\d+)/(\w+) on (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    matches = re.findall(pattern, text)

    results = []
    for port, protocol, ip in matches:
        port = int(port)
        results.append({
            'ip': ip,
            'port': port,
            'protocol': protocol,
        })

    return results
