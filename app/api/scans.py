from fastapi import APIRouter
from dramatiq.results import ResultMissing, ResultTimeout

from app.models import MasscanParams
from app.actors import scan_by_masscan

router = APIRouter()


@router.post("/scans/masscan")
async def start_masscan(config: MasscanParams):
    task = scan_by_masscan.send(config)
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
