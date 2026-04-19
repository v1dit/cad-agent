from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PromptRequest(StrictModel):
    text: str


class CylinderParameters(StrictModel):
    radius: float
    height: float


class SphereParameters(StrictModel):
    radius: float


class CubeParameters(StrictModel):
    width: float
    depth: float
    height: float


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


class PipelineSuccessResponse(StrictModel):
    stage: Literal["success"]
    engine: Literal["openscad"] = "openscad"
    spec: DesignNode
    scad: str


class PipelineFailureResponse(StrictModel):
    stage: Literal["validation_failed"]
    errors: list[str]
    spec: DesignNode


PipelineResponse = Union[PipelineSuccessResponse, PipelineFailureResponse]
