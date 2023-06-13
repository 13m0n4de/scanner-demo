from fastapi import APIRouter

from app import models
from app import actors

router = APIRouter()


@router.post("/scan")
async def scan(params: models.ScanCreate):
    task = actors.run_masscan.send(params.target)
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
