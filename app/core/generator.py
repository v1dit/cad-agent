from app.core.adapters.openscad import OpenSCADAdapter
from app.models.schema import (
    CadSpec,
    CylinderParameters,
    DesignNode,
    OperationNode,
    PrimitiveNode,
)

DEFAULT_ENGINE = "openscad"


def generate(spec: DesignNode, engine: str = DEFAULT_ENGINE) -> str:
    if engine == DEFAULT_ENGINE:
        return OpenSCADAdapter().generate(spec)

    raise ValueError(f"unsupported engine: {engine}")


def generate_scad(spec: CadSpec | DesignNode) -> str:
    if isinstance(spec, CadSpec):
        spec = _legacy_spec_to_design_node(spec)

    return generate(spec, engine=DEFAULT_ENGINE)


def _legacy_spec_to_design_node(spec: CadSpec) -> OperationNode:
    outer = PrimitiveNode(
        type="primitive",
        primitive="cylinder",
        parameters=CylinderParameters(radius=spec.outer_radius, height=spec.height),
    )
    inner = PrimitiveNode(
        type="primitive",
        primitive="cylinder",
        parameters=CylinderParameters(radius=spec.inner_radius, height=spec.height),
    )
    return OperationNode(type="operation", op="difference", children=[outer, inner])
