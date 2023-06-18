from typing import Union
from dramatiq.results import ResultMissing
from fastapi import APIRouter, Depends, HTTPException

from app.models import MasscanParams, HttpxParams
from app.actors import ACTOR_MAPPING
from app.utils import StoredPipeline

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


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    pipe = StoredPipeline(job_id=job_id)
    current_stage = None
    results = []
    final_result = None

    for message in pipe.messages:
        try:
            result = message.get_result()
        except ResultMissing:
            current_stage = message.actor_name
            break
        else:
            results.append({"stage": message.actor_name, "result": result})

    if pipe.completed:
        status = "completed"
        final_result = pipe.get_result()
    else:
        status = "pending"

    return {
        "status": status,
        "current_stage": current_stage,
        "results": results,
        "final_result": final_result,
    }
