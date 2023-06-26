import subprocess

from logging import Logger
from pydantic import BaseModel
from pydantic.fields import ModelField
from typing import List, Dict, Type, Union, Callable, Any

from app.config import CONFIG
from app.models import MasscanParams, HttpxParams, PortScanResult, ServiceScanResult

ACTORS_CONFIG = CONFIG["actors"]


ScanParams = Union[MasscanParams, HttpxParams]
ScanResults = Union[PortScanResult, ServiceScanResult]


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


def build_command(
    module_config: Dict[str, Any], params: Dict[str, Any], chains=False
) -> List[str]:
    command = []
    params.update(module_config)

    command_config = (
        module_config["chains_command"] if chains else module_config["command"]
    )

    for config in command_config:
        command_parts = []

        # name 可选
        if "option" in config:
            command_parts.append(config["option"])

        # field 与 fields 二选一，fields 为空列表是合法的（虽然没有任何意义）
        if "fields" in config and "field" in config:
            raise ValueError(
                "The 'fields' and 'field' attributes cannot be used together."
            )

        # 如果使用 field ，当值为 None 时跳过本选项
        # 如果有 value ，使用对应值格式化 value 添加到命令列表
        # 如果没有，就直接添加到命令列表
        if field_name := config.get("field"):
            if params.get(field_name) is None:
                continue

            if "value" in config:
                command_parts.append(
                    config["value"].format(**{field_name: str(params[field_name])})
                )
            else:
                command_parts.append(str(params[field_name]))

        # 使用 fields 可以指定多个 field，每个 field 同上，
        # 但它要求必须有 value
        elif fields := config.get("fields"):
            if "value" not in config:
                raise ValueError(
                    "The 'value' attribute is required when using 'fields'."
                )

            if any(params.get(field) is None for field in fields):
                continue

            field_values = {field: str(params[field]) for field in fields}
            command_parts.append(config["value"].format(**field_values))

        # 只有 value 时，直接添加
        elif "value" in config:
            command_parts.append(config["value"])

        command.extend(command_parts)

    return command


def run_scan(
    scan_data: Union[ScanParams, List[ScanResults]],
    build_execution_kwargs: Callable[
        [Union[ScanParams, List[ScanResults]]], Dict[str, Any]
    ],
    parse_output_fn: Callable[[str], List[ScanResults]],
    logger: Logger,
    support_read_targets: bool,
):
    # 执行单个扫描命令（运行一次 subprocess.check_output）
    def execute_single_scan(
        _scan_data: [Union[ScanParams, List[ScanResults]]]
    ) -> List[ScanResults]:
        execution_kwargs = build_execution_kwargs(_scan_data)
        logger.info(f"execution_kwargs => {execution_kwargs}")

        output = subprocess.check_output(**execution_kwargs)
        logger.info(f"output => {output}")

        return parse_output_fn(output.decode())

    # 如果来自其他模块的 Result 列表
    if isinstance(scan_data, list):
        if all(
            [
                (isinstance(result, PortScanResult) and len(result.open_ports) == 0)
                or (isinstance(result, ServiceScanResult) and len(result.services) == 0)
                for result in scan_data
            ]
        ):
            raise ModuleSkip

        if support_read_targets:
            results = execute_single_scan(scan_data)
        # 模块不支持读入多个扫描目标时，逐个执行拼接结果
        else:
            results = []
            for scan_result in scan_data:
                results.extend(execute_single_scan(scan_result))

    # 如果是本模块的 Params
    else:
        results = execute_single_scan(scan_data)

    logger.info(f"results => {results}")
    return results
