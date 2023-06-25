import json
from typing import Union, List

from app.actors import dramatiq
from app.models import HttpxParams, PortScanResult, ServiceDetail, ServiceScanResult

from .utils import ModuleSkip, get_defaults, build_command, run_scan


@dramatiq.actor(store_results=True, max_retries=0, throws=(ModuleSkip,))
def httpx(params):
    return run_scan(
        params,
        HttpxParams,
        build_httpx_command,
        parse_httpx_output,
        httpx.logger,
    )


def build_httpx_command(
    params: Union[HttpxParams, PortScanResult, ServiceScanResult]
) -> List[str]:
    if isinstance(params, HttpxParams):
        params_dict = params.dict()

    elif isinstance(params, PortScanResult):
        params_dict = get_defaults(HttpxParams)
        params_dict.update(
            {
                "target": params.ip,
                "ports": ",".join([str(port) for port in params.open_ports]),
            }
        )

    elif isinstance(params, ServiceScanResult):
        params_dict = get_defaults(HttpxParams)
        params_dict.update(
            {
                "target": params.ip,
                "ports": ",".join([str(service.port) for service in params.services]),
            }
        )

    else:
        raise TypeError(type(params), params)

    command = build_command("service_scan", "httpx", params_dict)
    return command


def parse_httpx_output(output: str) -> List[ServiceScanResult]:
    if output == "":
        return []

    scan_result_dict = {}
    for line in output.splitlines():
        result = json.loads(line)
        ip = result["input"]
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
