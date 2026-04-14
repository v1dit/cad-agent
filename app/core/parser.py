from app.models.schema import CylinderParameters, DesignNode, OperationNode, PrimitiveNode


def parse_prompt(text: str) -> DesignNode:
    # TODO: Replace this deterministic placeholder with an LLM-backed parser.
    _ = text
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
