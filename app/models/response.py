from typing import List, Optional
from pydantic import BaseModel

from app.models import ScanResult


class Stage(BaseModel):
    stage_id: int
    stage_name: str


class StageResult(BaseModel):
    stage_id: int
    stage_name: str
    result: List[ScanResult]


class JobDetails(BaseModel):
    current_stage: Optional[Stage]
    stopped_at: Optional[Stage]
    results: List[StageResult]


class JobResponse(BaseModel):
    status: str
    message: str
    result: Optional[List[ScanResult]]
    details: JobDetails
