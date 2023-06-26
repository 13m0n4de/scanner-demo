import json

from typing import List, Union, Dict, Any

from app.actors import dramatiq
from app.models import MasscanParams, PortDetail, PortScanResult, ServiceScanResult
from app.config import CONFIG

from .utils import ModuleSkip, get_defaults, build_command, run_scan


MASSCAN_CONFIG = CONFIG["actors"]["port_scan"]["masscan"]


@dramatiq.actor(store_results=True, max_retries=0, throws=(ModuleSkip,))
def masscan(params):
    return run_scan(
        params,
        build_masscan_execution_kwargs,
        parse_masscan_output,
        masscan.logger,
        support_read_targets=False,
    )


def build_masscan_execution_kwargs(
    params: Union[MasscanParams, PortScanResult, ServiceScanResult]
) -> Dict[str, Any]:
    if isinstance(params, MasscanParams):
        params_dict = params.dict()

    elif isinstance(params, PortScanResult):
        params_dict = get_defaults(MasscanParams)
        params_dict.update(
            {
                "target": params.ip,
                "ports": ",".join([str(port) for port in params.open_ports]),
            }
        )

    elif isinstance(params, ServiceScanResult):
        params_dict = get_defaults(MasscanParams)
        params_dict.update(
            {
                "target": params.ip,
                "ports": ",".join([str(service.port) for service in params.services]),
            }
        )

    else:
        raise TypeError(type(params), params)

    return {"args": build_command(MASSCAN_CONFIG, params_dict)}


def parse_masscan_output(output: str) -> List[PortScanResult]:
    if output == "":
        return []

    scan_result_dict: Dict[str, PortScanResult] = {}

    results = json.loads(output)
    for result in results:
        ip = result["ip"]
        if ip not in scan_result_dict:
            scan_result_dict[ip] = PortScanResult(
                ip=result["ip"],
                open_ports=[],
                closed_ports=[],
                filtered_ports=[],
                details=[],
            )

        for port_result in result["ports"]:
            port_detail = PortDetail(
                port=port_result["port"],
                status=port_result["status"],
                protocol=port_result["proto"],
                ttl=port_result["ttl"],
            )

            scan_result_dict[ip].details.append(port_detail)

            match port_result["status"]:
                case "open":
                    scan_result_dict[ip].open_ports.append(port_result["port"])
                case "closed":
                    scan_result_dict[ip].closed_ports.append(port_result["port"])
                case "filtered":
                    scan_result_dict[ip].filtered_ports.append(port_result["port"])

    return list(scan_result_dict.values())
