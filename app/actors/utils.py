import subprocess

from pydantic import BaseModel
from pydantic.fields import ModelField
from typing import List, Dict, Type

from app.config import CONFIG

ACTORS_CONFIG = CONFIG["actors"]


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


def build_command(_type: str, name: str, params: Dict[str, str]) -> List[str]:
    command = []
    params["binary"] = ACTORS_CONFIG[_type][name]["binary"]

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


def run_scan(params, params_type, build_command_fn, parse_output_fn, logger):
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

        for scan_result in params:
            command = build_command_fn(scan_result)
            logger.info(f"command => {command}")

            output = subprocess.check_output(command)
            logger.info(f"output => {output}")

            results.extend(parse_output_fn(output.decode()))

    logger.info(f"results => {results}")
    return results
