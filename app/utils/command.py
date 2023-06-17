import json

from pydantic import parse_obj_as, BaseModel
from pydantic.fields import ModelField
from typing import List, Union, Dict, Type

from app.config import CONFIG
from app.models import MasscanParams, HttpxParams, ScanResult


ACTORS_CONFIG = CONFIG['actors']


def get_defaults(model: Type[BaseModel]) -> dict:
    defaults = {}
    for filed_name, filed in model.__fields__.items():
        if isinstance(filed, ModelField):
            if default_factory := filed.default_factory:
                defaults[filed_name] = default_factory()
            elif default := filed.default:
                defaults[filed_name] = default
            else:
                defaults[filed_name] = None

    return defaults


def build_command(name: str, params: Dict[str, str]) -> List[str]:
    command = []
    params['binary'] = ACTORS_CONFIG[name]['binary']

    for part in ACTORS_CONFIG[name]['command']:
        if isinstance(part, str):
            command.append(part.format(**params))
        else:
            value = part[1].format(**params)
            if value != "None":
                command.append(part[0])
                command.append(value)

    return command


def build_masscan_command(params: Union[MasscanParams, ScanResult]) -> List[str]:
    if isinstance(params, MasscanParams):
        params_dict = params.dict()

    elif isinstance(params, ScanResult):
        params_dict = get_defaults(MasscanParams)
        params_dict.update({
            'target': params.ip,
            'port_range': ','.join([str(port_info.port) for port_info in params.ports]),
        })

    else:
        raise TypeError(type(params))

    command = build_command('masscan', params_dict)

    return command


def build_httpx_command(params: Union[HttpxParams, List[ScanResult]]) -> List[str]:
    if isinstance(params, HttpxParams):
        params_dict = params.dict()

    elif isinstance(params, ScanResult):
        params_dict = get_defaults(HttpxParams)
        params_dict.update({
            'target': params.ip,
            'port_range': ','.join([str(port_info.port) for port_info in params.ports]),
        })

    else:
        raise TypeError(type(params))

    command = build_command('httpx', params_dict)

    return command


def parse_masscan_output(output: str) -> List[ScanResult]:
    if output == '':
        return []
    scan_results: List[ScanResult] = []
    results = json.loads(output)
    for result in results:
        scan_result = {'ip': result['ip'], 'ports': []}
        for port_result in result['ports']:
            scan_result['ports'].append({
                'port': port_result['port'],
                'protocol': port_result['proto']
            })
        scan_results.append(parse_obj_as(ScanResult, scan_result))
    return scan_results


def parse_httpx_output(output: str) -> List[ScanResult]:
    if output == '':
        return []
    return json.loads(output)
