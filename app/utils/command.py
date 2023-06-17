import json

from typing import List, Union

from app.config import CONFIG
from app.models import MasscanParams, HttpxParams, ScanResult


ACTORS_CONFIG = CONFIG['actors']


def build_masscan_command(params: Union[MasscanParams, List[ScanResult]]) -> List[str]:
    command = []
    params_dict = params.dict()
    params_dict['binary'] = ACTORS_CONFIG['masscan']['binary']

    if isinstance(params, MasscanParams):
        for part in ACTORS_CONFIG['masscan']['command']:
            if isinstance(part, str):
                command.append(part.format(**params_dict))
            else:
                value = part[1].format(**params_dict)
                if value != "None":
                    command.append(part[0])
                    command.append(value)
    elif isinstance(params, ScanResult):
        pass

    return command


def build_httpx_command(params: Union[HttpxParams, List[ScanResult]]) -> List[str]:
    command = []
    params_dict = params.dict()
    params_dict['binary'] = ACTORS_CONFIG['httpx']['binary']

    if isinstance(params, MasscanParams):
        for part in ACTORS_CONFIG['httpx']['command']:
            if isinstance(part, str):
                command.append(part.format(**params_dict))
            else:
                value = part[1].format(**params_dict)
                if value != "None":
                    command.append(part[0])
                    command.append(value)
    elif isinstance(params, ScanResult):
        pass

    return command


def parse_masscan_output(output: str) -> List[ScanResult]:
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


def parse_httpx_output(output: str) -> List[ScanResult]:
    if output == '':
        return []
    return json.loads(output)

