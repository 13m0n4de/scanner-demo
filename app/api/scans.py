import logging
from typing import Union, Any
from dramatiq.results import ResultMissing, ResultFailure
from fastapi import APIRouter, Depends, HTTPException

from app.models import MasscanParams, HttpxParams
from app.models import JobResponse, JobDetails, Stage, StageResult
from app.actors import ACTOR_MAPPING
from app.utils import StoredPipeline, ModuleSkip

router = APIRouter()


def parse_first_params(
    modules: str, params: Union[MasscanParams, HttpxParams]
) -> Union[MasscanParams, HttpxParams]:
    if modules == "":
        raise HTTPException(400, detail="No input modules provided")

    module_name = modules.split("/")[0]
    match module_name:
        case "masscan":
            return MasscanParams.parse_obj(params)
        case "httpx":
            return HttpxParams.parse_obj(params)
        case _:
            raise HTTPException(400, detail=f"Module {module_name} not found")


@router.post("/scans/{modules:path}")
async def start_scans(
    modules: str,
    params: Union[MasscanParams, HttpxParams] = Depends(parse_first_params),
):
    module_list = modules.split("/")
    pipe = [ACTOR_MAPPING[module_list[0]].message(params)]
    for module_name in module_list[1:]:
        if module_name not in ACTOR_MAPPING:
            raise HTTPException(400, detail=f"Module {module_name} not found")
        pipe.append(ACTOR_MAPPING[module_name].message())

    pipe = StoredPipeline(pipe).run()
    pipe.store_pipeline()

    return {
        "status": "submitted",
        "job_id": pipe.get_id(),
    }


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str) -> Any:
    pipe = StoredPipeline(job_id=job_id)

    final_result = None
    current_stage = None
    results = []
    stopped_at = None
    stage_id = 0

    if pipe.completed:
        status = "completed"
        message = "Job execution completed"
        final_result = pipe.get_result()
    else:
        status = "pending"
        message = "Job execution is still pending"

    for msg in pipe.messages:
        try:
            result = msg.get_result()
        except ResultMissing:
            current_stage = Stage(stage_id=stage_id, stage_name=msg.actor_name)
            break
        except ResultFailure as e:
            if isinstance(e.orig_exc_type, ModuleSkip):
                status = "incomplete"
                stopped_at = Stage(stage_id=stage_id, stage_name=e.orig_exc_msg)
            else:
                status = "failed"
                message = str(e)
            break
        else:
            results.append(
                StageResult(stage_id=stage_id, stage_name=msg.actor_name, result=result)
            )
            stage_id += 1

    details = JobDetails(
        current_stage=current_stage,
        results=results,
        stopped_at=stopped_at,
    )

    response = JobResponse(
        status=status, message=message, result=final_result, details=details
    )
    return response
