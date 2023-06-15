import re
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


def parse_masscan_text_output(output: str) -> List[Dict[str, str | int]]:
    pattern = r"Discovered open port (\d+)/(\w+) on (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    matches = re.findall(pattern, output)

    results_dict = {}  # {'x.x.x.x': {'ip': 'x.x.x.x', 'ports': [...]}}
    for port, protocol, ip in matches:
        if results_dict.get(ip) is None:
            results_dict[ip] = {}
            results_dict[ip]['ports'] = []
            results_dict[ip]['ip'] = ip

        results_dict[ip]['ports'].append({
            "port": int(port),
            "protocol": protocol,
        })

    return list(results_dict.values())


def parse_masscan_json_output(output: str) -> List[Dict[str, str | int]]:
    results = json.loads(output)
    for result in results:
        del result['timestamp']
        for port_result in result['ports']:
            del port_result['status']
            del port_result['reason']
            del port_result['ttl']

    return results
