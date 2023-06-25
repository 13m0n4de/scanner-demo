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
        option_command = []

        # name 可选
        if "name" in option:
            option_command.append(option["name"])

        # field 与 fields 二选一，fields 为空列表是合法的（虽然没有任何意义）
        if "fields" in option and "field" in option:
            raise ValueError(
                "The 'fields' and 'field' attributes cannot be used together."
            )

        # 如果使用 field ，当值为 None 时跳过本选项
        # 如果有 value ，使用对应值格式化 value 添加到命令列表
        # 如果没有，就直接添加到命令列表
        if field_name := option.get("field"):
            if params.get(field_name) is None:
                continue

            if "value" in option:
                option_command.append(
                    option["value"].format(**{field_name: str(params[field_name])})
                )
            else:
                option_command.append(str(params[field_name]))

        # 使用 fields 可以指定多个 field，每个 field 同上，
        # 但它要求必须有 value
        elif fields := option.get("fields"):
            if "value" not in option:
                raise ValueError(
                    "The 'value' attribute is required when using 'fields'."
                )

            if any(params.get(field) is None for field in fields):
                continue

            field_values = {field: str(params[field]) for field in fields}
            option_command.append(option["value"].format(**field_values))

        # 只有 value 时，直接添加
        elif "value" in option:
            option_command.append(option["value"])

        command.extend(option_command)

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
