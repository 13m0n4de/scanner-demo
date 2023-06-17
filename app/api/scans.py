from typing import Union
from dramatiq import pipeline
from fastapi import APIRouter, Depends, HTTPException
from dramatiq.results import ResultMissing, ResultTimeout

from app.models import MasscanParams, HttpxParams
from app.actors import scan_by_masscan, scan_by_httpx, ACTOR_MAPPING

router = APIRouter()


def get_first_params(modules: str, params: Union[MasscanParams, HttpxParams]) -> Union[MasscanParams, HttpxParams]:
    if modules == '':
        raise HTTPException(400, detail="No input modules provided")

    module_name = modules.split('/')
    match module_name:
        case 'masscan':
            return MasscanParams.parse_obj(params)
        case 'httpx':
            return HttpxParams.parse_obj(params)
        case _:
            raise HTTPException(400, detail=f"Module {module_name} not found")


@router.post("/scans/{modules:path}")
async def start_scans(
    modules: str,
    params: Union[MasscanParams, HttpxParams] = Depends(get_first_params)
):
    module_list = modules.split('/')
    pipe = [ACTOR_MAPPING[module_list[0]].message(params)]
    for module_name in module_list[1:]:
        pipe.append(ACTOR_MAPPING[module_name].message())

    pipe = pipeline(pipe)
    pipe.run()
    return None


@router.post("/scans/masscan")
async def start_masscan(params: MasscanParams):
    task = scan_by_masscan.send(params)
    try:
        status = "submitted"
        message_id = task.message_id
    except AttributeError:
        status = "completed"
        message_id = None
    return {
        "status": status,
        "message_id": message_id
    }


@router.get("/scans/masscan/{message_id}")
async def get_masscan_status(message_id: str):
    task_message = scan_by_masscan.message().copy(message_id=message_id)
    try:
        result = task_message.get_result()
    except ResultMissing:
        status = "missing"
        result = None
    except ResultTimeout:
        status = "timeout"
        result = None
    else:
        status = "completed"

    return {
        "status": status,
        "result": result
    }


@router.post("/scans/httpx")
async def start_masscan(config: HttpxParams):
    task = scan_by_httpx.send(config)
    try:
        status = "submitted"
        message_id = task.message_id
    except AttributeError:
        status = "completed"
        message_id = None
    return {
        "status": status,
        "message_id": message_id
    }


@router.get("/scans/httpx/{message_id}")
async def get_httpx_status(message_id: str):
    task_message = scan_by_httpx.message().copy(message_id=message_id)
    try:
        result = task_message.get_result()
    except ResultMissing:
        status = "missing"
        result = None
    except ResultTimeout:
        status = "timeout"
        result = None
    else:
        status = "completed"

    return {
        "status": status,
        "result": result
    }
