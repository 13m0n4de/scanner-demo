import json

from typing import Dict, List

from app.config import CONFIG


def build_command(name: str, params: Dict[str, str | int]) -> List[str]:
    command = []
    params['binary'] = CONFIG['actors'][name]['binary']

    for part in CONFIG['actors'][name]['command']:
        if isinstance(part, str):
            command.append(part.format(**params))
        else:
            value = part[1].format(**params)
            if value != "None":
                command.append(part[0])
                command.append(value)

    return command


def parse_masscan_output(output: str) -> List[Dict[str, str | int]]:
    if output == '':
        return []
    results = json.loads(output)
    for result in results:
        del result['timestamp']
        for port_result in result['ports']:
            del port_result['status']
            del port_result['reason']
            del port_result['ttl']

    return results
