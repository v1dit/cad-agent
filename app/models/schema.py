from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PromptRequest(StrictModel):
    text: str
    execute: bool = False


class CylinderParameters(StrictModel):
    radius: float
    height: float

    @field_validator("radius", "height", mode="before")
    @classmethod
    def validate_numeric(cls, value: object) -> object:
        return _validate_numeric_input(value)


class SphereParameters(StrictModel):
    radius: float

    @field_validator("radius", mode="before")
    @classmethod
    def validate_numeric(cls, value: object) -> object:
        return _validate_numeric_input(value)


class CubeParameters(StrictModel):
    width: float
    depth: float
    height: float

    @field_validator("width", "depth", "height", mode="before")
    @classmethod
    def validate_numeric(cls, value: object) -> object:
        return _validate_numeric_input(value)


PrimitiveParameters = Union[CylinderParameters, SphereParameters, CubeParameters]


class PrimitiveNode(StrictModel):
    type: Literal["primitive"]
    primitive: Literal["cylinder", "sphere", "cube"]
    parameters: PrimitiveParameters
    operation: Literal["add"] = "add"


class OperationNode(StrictModel):
    type: Literal["operation"]
    op: Literal["difference", "union", "intersection"]
    children: list["DesignNode"]


DesignNode = Annotated[Union[PrimitiveNode, OperationNode], Field(discriminator="type")]

OperationNode.model_rebuild()


class ValidationResult(StrictModel):
    valid: bool
    errors: list[str]


class OutputPayload(StrictModel):
    type: Literal["scad"] = "scad"
    code: str


class PipelineSuccessResponse(StrictModel):
    stage: Literal["success"]
    engine: Literal["openscad"] = "openscad"
    spec: DesignNode
    output: OutputPayload
    artifact: str | None = None


class PipelineValidationFailureResponse(StrictModel):
    stage: Literal["validation_failed"]
    errors: list[str]
    spec: DesignNode


class PipelineExecutionFailureResponse(StrictModel):
    stage: Literal["execution_failed"]
    engine: Literal["openscad"] = "openscad"
    errors: list[str]
    spec: DesignNode
    output: OutputPayload


PipelineResponse = Union[
    PipelineSuccessResponse,
    PipelineValidationFailureResponse,
    PipelineExecutionFailureResponse,
]


def _validate_numeric_input(value: object) -> object:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("numeric parameters must be numbers")

    return value
