from fastapi import APIRouter

from app import models
from app import actors

router = APIRouter()


@router.post("/scans/masscan")
async def scan_by_masscan(config: models.MasscanConfig):
    task = actors.run_masscan.send(config.dict())
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
