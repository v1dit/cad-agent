from typing import Union

from fastapi import APIRouter

from app.core.executor import ExecutionError
from app.core.generator import DEFAULT_ENGINE, execute_generated, generate
from app.core.normalize import normalize_spec
from app.core.parser import parse_prompt
from app.core.validator import validate_spec
from app.models.schema import (
    OutputPayload,
    PipelineExecutionFailureResponse,
    PipelineSuccessResponse,
    PipelineValidationFailureResponse,
    PromptRequest,
)

router = APIRouter()


@router.post(
    "/run",
    response_model=Union[
        PipelineSuccessResponse,
        PipelineValidationFailureResponse,
        PipelineExecutionFailureResponse,
    ],
)
def run_pipeline(
    prompt: PromptRequest,
) -> Union[PipelineSuccessResponse, PipelineValidationFailureResponse, PipelineExecutionFailureResponse]:
    parsed_spec = parse_prompt(prompt.text)

    try:
        spec = normalize_spec(parsed_spec)
    except ValueError as exc:
        return PipelineValidationFailureResponse(
            stage="validation_failed",
            errors=[str(exc)],
            spec=parsed_spec,
        )

    validation = validate_spec(spec)

    if not validation.valid:
        return PipelineValidationFailureResponse(
            stage="validation_failed",
            errors=validation.errors,
            spec=spec,
        )

    scad = generate(spec, engine=DEFAULT_ENGINE)
    output = OutputPayload(code=scad)

    artifact: str | None = None
    if prompt.execute:
        try:
            execution_result = execute_generated(scad, engine=DEFAULT_ENGINE)
        except ExecutionError as exc:
            return PipelineExecutionFailureResponse(
                stage="execution_failed",
                engine=DEFAULT_ENGINE,
                errors=[str(exc)],
                spec=spec,
                output=output,
            )

        artifact = execution_result["artifact"]

    return PipelineSuccessResponse(
        stage="success",
        engine=DEFAULT_ENGINE,
        spec=spec,
        output=output,
        artifact=artifact,
    )
