import re
import json

from pydantic import parse_obj_as, BaseModel
from pydantic.fields import ModelField
from typing import List, Union, Dict, Type

from app.config import CONFIG
from app.models import MasscanParams, RustscanParams, HttpxParams, ScanResult

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


def build_masscan_command(params: Union[MasscanParams, ScanResult]) -> List[str]:
    if isinstance(params, MasscanParams):
        params_dict = params.dict()

    elif isinstance(params, ScanResult):
        params_dict = get_defaults(MasscanParams)
        params_dict.update(
            {
                "target": params.ip,
                "ports": ",".join([str(port_info.port) for port_info in params.ports]),
            }
        )

    else:
        raise TypeError(type(params), params)

    command = build_command("port_scan", "masscan", params_dict)
    return command


def build_rustscan_command(params: Union[RustscanParams, ScanResult]) -> List[str]:
    if isinstance(params, RustscanParams):
        params_dict = params.dict()

    elif isinstance(params, ScanResult):
        params_dict = get_defaults(RustscanParams)
        params_dict.update(
            {
                "addresses": params.ip,
                "ports": ",".join([str(port_info.port) for port_info in params.ports]),
            }
        )

    else:
        raise TypeError(type(params), params)

    command = build_command("port_scan", "rustscan", params_dict)
    return command


def build_httpx_command(params: Union[HttpxParams, List[ScanResult]]) -> List[str]:
    if isinstance(params, HttpxParams):
        params_dict = params.dict()

    elif isinstance(params, ScanResult):
        params_dict = get_defaults(HttpxParams)
        params_dict.update(
            {
                "target": params.ip,
                "port_range": ",".join(
                    [str(port_info.port) for port_info in params.ports]
                ),
            }
        )

    else:
        raise TypeError(type(params), params)

    command = build_command("port_scan", "httpx", params_dict)
    return command


def parse_masscan_output(output: str) -> List[ScanResult]:
    if output == "":
        return []

    scan_results: List[ScanResult] = []
    results = json.loads(output)
    for result in results:
        scan_result = {"ip": result["ip"], "ports": []}
        for port_result in result["ports"]:
            scan_result["ports"].append(
                {"port": port_result["port"], "protocol": port_result["proto"]}
            )
        scan_results.append(parse_obj_as(ScanResult, scan_result))
    return scan_results


def parse_rustscan_output(output: str) -> List[ScanResult]:
    if output == "":
        return []

    scan_results: List[ScanResult] = []
    for line in output.splitlines():
        matches = re.match(r"(.*?)\s->\s\[(.*?)]", line)
        ip = matches.group(1)
        ports = matches.group(2).split(",")

        ports_result = [{"port": int(port)} for port in ports]
        scan_results.append(ScanResult.parse_obj({"ip": ip, "ports": ports_result}))

    return scan_results


def parse_httpx_output(output: str) -> List[ScanResult]:
    if output == "":
        return []

    # { ip: [{port, service, ...}] }
    scan_results_dict = {}
    for line in output.splitlines():
        result = json.loads(line)
        ip = result["input"]
        if ip not in scan_results_dict:
            scan_results_dict[ip] = []
        scan_results_dict[ip].append(
            {
                "port": result["port"],
                "protocol": "tcp",
                "service": result.get("webserver"),
            }
        )

    scan_results: List[ScanResult] = []
    for ip, port_results in scan_results_dict.items():
        scan_results.append(parse_obj_as(ScanResult, {"ip": ip, "ports": port_results}))

    return scan_results
