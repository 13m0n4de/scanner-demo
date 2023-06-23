from typing import List, Optional, Union
from pydantic import BaseModel

from app.models import PortScanResult, ServiceScanResult


class Stage(BaseModel):
    stage_id: int
    stage_name: str


class StageResult(BaseModel):
    stage_id: int
    stage_name: str
    result: List[Union[PortScanResult, ServiceScanResult]]


class JobDetails(BaseModel):
    current_stage: Optional[Stage]
    stopped_at: Optional[Stage]
    results: List[StageResult]


class JobResponse(BaseModel):
    status: str
    message: str
    result: Optional[List[Union[PortScanResult, ServiceScanResult]]]
    details: JobDetails
