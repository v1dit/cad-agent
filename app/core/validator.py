from app.models.schema import (
    CubeParameters,
    CylinderParameters,
    DesignNode,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
    ValidationResult,
)


def validate_spec(spec: DesignNode) -> ValidationResult:
    errors: list[str] = []
    _validate_design_node(spec, errors)
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def _validate_design_node(spec: DesignNode, errors: list[str]) -> None:
    if isinstance(spec, PrimitiveNode):
        _validate_primitive(spec, errors)
        return

    if isinstance(spec, OperationNode):
        _validate_operation(spec, errors)
        return

    errors.append("unsupported design node")


def _validate_primitive(spec: PrimitiveNode, errors: list[str]) -> None:
    if spec.primitive == "cylinder":
        if not isinstance(spec.parameters, CylinderParameters):
            errors.append("cylinder primitives require radius and height parameters")
            return

        if spec.parameters.radius <= 0:
            errors.append("cylinder radius must be positive")

        if spec.parameters.height <= 0:
            errors.append("cylinder height must be positive")
        return

    if spec.primitive == "sphere":
        if not isinstance(spec.parameters, SphereParameters):
            errors.append("sphere primitives require a radius parameter")
            return

        if spec.parameters.radius <= 0:
            errors.append("sphere radius must be positive")
        return

    if spec.primitive == "cube":
        if not isinstance(spec.parameters, CubeParameters):
            errors.append("cube primitives require width, depth, and height parameters")
            return

        if spec.parameters.width <= 0:
            errors.append("cube width must be positive")

        if spec.parameters.depth <= 0:
            errors.append("cube depth must be positive")

        if spec.parameters.height <= 0:
            errors.append("cube height must be positive")
        return

    errors.append(f"unsupported primitive: {spec.primitive}")


def _validate_operation(spec: OperationNode, errors: list[str]) -> None:
    if spec.op == "difference" and len(spec.children) != 2:
        errors.append("difference operations must have exactly two children")

    if spec.op == "union" and len(spec.children) < 2:
        errors.append("union operations must have at least two children")

    if spec.op == "intersection" and len(spec.children) < 2:
        errors.append("intersection operations must have at least two children")

    for child in spec.children:
        _validate_design_node(child, errors)

    if spec.op != "difference" or len(spec.children) != 2:
        return

    left, right = spec.children
    if isinstance(left, PrimitiveNode) and isinstance(right, PrimitiveNode):
        if (
            left.primitive == right.primitive == "cylinder"
            and isinstance(left.parameters, CylinderParameters)
            and isinstance(right.parameters, CylinderParameters)
        ):
            if right.parameters.radius >= left.parameters.radius:
                errors.append("inner cylinder radius must be smaller than outer cylinder radius")
