from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    text: str


class CadSpec(BaseModel):
    shape: Literal["cylinder"]
    outer_radius: float
    inner_radius: float
    height: float


class CylinderParameters(BaseModel):
    radius: float
    height: float


class PrimitiveNode(BaseModel):
    type: Literal["primitive"]
    primitive: Literal["cylinder"]
    parameters: CylinderParameters
    operation: Literal["add"] = "add"


class OperationNode(BaseModel):
    type: Literal["operation"]
    op: Literal["difference"]
    children: list["DesignNode"]


DesignNode = Annotated[Union[PrimitiveNode, OperationNode], Field(discriminator="type")]
SpecModel = Union[CadSpec, DesignNode]

OperationNode.model_rebuild()


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str]


class PipelineSuccessResponse(BaseModel):
    stage: Literal["success"]
    engine: Literal["openscad"] = "openscad"
    spec: SpecModel
    scad: str


class PipelineFailureResponse(BaseModel):
    stage: Literal["validation_failed"]
    errors: list[str]
    spec: SpecModel


PipelineResponse = Union[PipelineSuccessResponse, PipelineFailureResponse]
