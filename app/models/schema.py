from typing import Literal, Union

from pydantic import BaseModel


class PromptRequest(BaseModel):
    text: str


class CadSpec(BaseModel):
    shape: Literal["cylinder"]
    outer_radius: float
    inner_radius: float
    height: float


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str]


class PipelineSuccessResponse(BaseModel):
    stage: Literal["success"]
    spec: CadSpec
    scad: str


class PipelineFailureResponse(BaseModel):
    stage: Literal["validation_failed"]
    errors: list[str]
    spec: CadSpec


PipelineResponse = Union[PipelineSuccessResponse, PipelineFailureResponse]
