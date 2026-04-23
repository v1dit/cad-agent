from app.models.schema import (
    CubeParameters,
    CylinderParameters,
    DesignNode,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
)


def normalize_spec(spec: DesignNode) -> DesignNode:
    normalized = _normalize_node(spec, drop_noop_primitives=False)
    if normalized is None:
        raise ValueError("normalization produced an empty design tree")

    return normalized


def _normalize_node(spec: DesignNode, drop_noop_primitives: bool) -> DesignNode | None:
    if isinstance(spec, PrimitiveNode):
        if drop_noop_primitives and _is_noop_primitive(spec):
            return None

        return spec

    if spec.op == "difference":
        return _normalize_difference(spec)

    return _normalize_commutative_operation(spec)


def _normalize_commutative_operation(spec: OperationNode) -> DesignNode | None:
    children: list[DesignNode] = []

    for child in spec.children:
        normalized_child = _normalize_node(child, drop_noop_primitives=True)
        if normalized_child is None:
            continue

        if isinstance(normalized_child, OperationNode) and normalized_child.op == spec.op:
            children.extend(normalized_child.children)
            continue

        children.append(normalized_child)

    if len(children) == 0:
        return OperationNode(type="operation", op=spec.op, children=[])

    if len(children) == 1:
        return children[0]

    return OperationNode(type="operation", op=spec.op, children=children)


def _normalize_difference(spec: OperationNode) -> OperationNode:
    if not spec.children:
        return OperationNode(type="operation", op=spec.op, children=[])

    base = _normalize_node(spec.children[0], drop_noop_primitives=False)
    if base is None:
        return OperationNode(type="operation", op=spec.op, children=[])

    subtractors: list[DesignNode] = []
    for child in spec.children[1:]:
        normalized_child = _normalize_node(child, drop_noop_primitives=True)
        if normalized_child is None:
            continue
        subtractors.append(normalized_child)

    return OperationNode(type="operation", op=spec.op, children=[base, *subtractors])


def _is_noop_primitive(spec: PrimitiveNode) -> bool:
    if spec.primitive == "cylinder" and isinstance(spec.parameters, CylinderParameters):
        return spec.parameters.radius <= 0 or spec.parameters.height <= 0

    if spec.primitive == "sphere" and isinstance(spec.parameters, SphereParameters):
        return spec.parameters.radius <= 0

    if spec.primitive == "cube" and isinstance(spec.parameters, CubeParameters):
        return (
            spec.parameters.width <= 0
            or spec.parameters.depth <= 0
            or spec.parameters.height <= 0
        )

    return False
