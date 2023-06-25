import subprocess

from logging import Logger
from pydantic import BaseModel
from pydantic.fields import ModelField
from typing import List, Dict, Type, Union, Callable

from app.config import CONFIG
from app.models import MasscanParams, HttpxParams, PortScanResult, ServiceScanResult

ACTORS_CONFIG = CONFIG["actors"]


ScanParams = Union[MasscanParams, PortScanResult, HttpxParams, ServiceScanResult]
ScanParamsType = Type[ScanParams]
ScanResults = List[Union[PortScanResult, ServiceScanResult]]


class ModuleSkip(Exception):
    pass


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


def build_command(_type: str, name: str, params: Dict[str, int | str]) -> List[str]:
    command = []
    params.update(ACTORS_CONFIG[_type][name])

    for option in ACTORS_CONFIG[_type][name]["command"]:
        # 如果对应字段的值为 None 此条参数调过
        if "field" in option and params.get(option["field"]) is None:
            continue

        if "name" in option:
            command.append(option["name"])

        if "field" in option and "value" not in option:
            command.append(str(params[option["field"]]))

        elif "field" not in option and "value" in option:
            command.append(option["value"])

        elif "field" in option and "value" in option:
            field_name = option["field"]
            command.append(
                (option["value"].format(**{field_name: str(params[field_name])}))
            )

    return command


def run_scan(
    params: ScanParams,
    params_type: ScanParamsType,
    build_command_fn: Callable[[ScanParams], List[str]],
    parse_output_fn: Callable[[str], ScanResults],
    logger: Logger,
):
    results = []

    if isinstance(params, params_type):
        command = build_command_fn(params)
        logger.info(f"command => {command}")

        output = subprocess.check_output(command)
        logger.info(f"output => {output}")

        results = parse_output_fn(output.decode())

    elif isinstance(params, list):
        if len(params) == 0:
            raise ModuleSkip

        for param in params:
            if isinstance(param, PortScanResult) and len(param.open_ports) == 0:
                raise ModuleSkip
            elif isinstance(param, ServiceScanResult) and len(param.services) == 0:
                raise ModuleSkip

        for scan_result in params:
            command = build_command_fn(scan_result)
            logger.info(f"command => {command}")

            output = subprocess.check_output(command)
            logger.info(f"output => {output}")

            results.extend(parse_output_fn(output.decode()))

    logger.info(f"results => {results}")
    return results
