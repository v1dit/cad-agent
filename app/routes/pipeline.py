from typing import Union

from fastapi import APIRouter

from app.core.generator import generate_scad
from app.core.parser import parse_prompt
from app.core.validator import validate_spec
from app.models.schema import (
    PipelineFailureResponse,
    PipelineSuccessResponse,
    PromptRequest,
)

router = APIRouter()


@router.post("/run", response_model=Union[PipelineSuccessResponse, PipelineFailureResponse])
def run_pipeline(prompt: PromptRequest) -> Union[PipelineSuccessResponse, PipelineFailureResponse]:
    spec = parse_prompt(prompt.text)
    validation = validate_spec(spec)

    if not validation.valid:
        return PipelineFailureResponse(
            stage="validation_failed",
            errors=validation.errors,
            spec=spec,
        )

    scad = generate_scad(spec)
    return PipelineSuccessResponse(stage="success", spec=spec, scad=scad)
