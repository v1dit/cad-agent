from app.models.schema import (
    CylinderParameters,
    DesignNode,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
)


def parse_prompt(text: str) -> DesignNode:
    # TODO: Replace this deterministic placeholder with an LLM-backed parser.
    lowered = text.lower()

    if "union" in lowered:
        return _build_union_demo()

    if "sphere" in lowered:
        return PrimitiveNode(
            type="primitive",
            primitive="sphere",
            parameters=SphereParameters(radius=4),
        )

    return _build_hollow_cylinder()


def _build_hollow_cylinder() -> OperationNode:
    outer = PrimitiveNode(
        type="primitive",
        primitive="cylinder",
        parameters=CylinderParameters(radius=5, height=10),
    )
    inner = PrimitiveNode(
        type="primitive",
        primitive="cylinder",
        parameters=CylinderParameters(radius=3, height=10),
    )
    return OperationNode(type="operation", op="difference", children=[outer, inner])


def _build_union_demo() -> OperationNode:
    sphere = PrimitiveNode(
        type="primitive",
        primitive="sphere",
        parameters=SphereParameters(radius=4),
    )
    return OperationNode(
        type="operation",
        op="union",
        children=[_build_hollow_cylinder(), sphere],
    )
