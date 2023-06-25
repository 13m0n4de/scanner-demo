import json
from typing import Union, List, Dict, Any

from app.actors import dramatiq
from app.models import HttpxParams, PortScanResult, ServiceDetail, ServiceScanResult
from app.config import CONFIG

from .utils import ModuleSkip, get_defaults, build_command, run_scan


HTTPX_CONFIG = CONFIG["actors"]["service_scan"]["httpx"]


@dramatiq.actor(store_results=True, max_retries=0, throws=(ModuleSkip,))
def httpx(params):
    return run_scan(
        params,
        HttpxParams,
        build_httpx_execution_kwargs,
        parse_httpx_output,
        httpx.logger,
    )


def build_httpx_execution_kwargs(
    params: Union[HttpxParams, List[Union[PortScanResult, ServiceScanResult]]]
) -> Dict[str, Any]:
    if isinstance(params, HttpxParams):
        params_dict = params.dict()
        input_data = None
        command = build_command(HTTPX_CONFIG, params_dict)

    elif isinstance(params, list):
        params_dict = get_defaults(HttpxParams)
        input_data = b""
        for scan_result in params:
            if isinstance(scan_result, PortScanResult):
                ip = scan_result.ip
                targets = "\n".join([f"{ip}:{port}" for port in scan_result.open_ports])
                input_data += targets.encode()

            elif isinstance(scan_result, ServiceScanResult):
                ip = scan_result.ip
                targets = "\n".join(
                    [f"{ip}:{service.port}" for service in scan_result.services]
                )
                input_data += targets.encode()

        command = build_command(HTTPX_CONFIG, params_dict, chains=True)

    else:
        raise TypeError(type(params), params)

    return {"args": command, "input": input_data}


def parse_httpx_output(output: str) -> List[ServiceScanResult]:
    if output == "":
        return []

    scan_result_dict = {}
    for line in output.splitlines():
        result = json.loads(line)
        ip = result["host"]
        if ip not in scan_result_dict:
            scan_result_dict[ip] = ServiceScanResult(ip=ip, services=[])

        if not result.get("webserver"):
            continue

        service_detail = ServiceDetail(
            port=result["port"],
            name=result["webserver"],
            tech=result["tech"],
            banner=result.get("title"),
        )
        scan_result_dict[ip].services.append(service_detail)

    return list(scan_result_dict.values())
