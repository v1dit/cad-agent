from app.models.schema import (
    CadSpec,
    DesignNode,
    OperationNode,
    PrimitiveNode,
    ValidationResult,
)


def validate_spec(spec: CadSpec | DesignNode) -> ValidationResult:
    if isinstance(spec, CadSpec):
        return _validate_legacy_spec(spec)

    errors: list[str] = []
    _validate_design_node(spec, errors)
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def _validate_legacy_spec(spec: CadSpec) -> ValidationResult:
    errors: list[str] = []

    if spec.shape == "cylinder":
        if spec.inner_radius >= spec.outer_radius:
            errors.append("inner radius must be smaller than outer radius")

        if spec.height <= 0:
            errors.append("height must be positive")

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
    if spec.parameters.radius <= 0:
        errors.append("cylinder radius must be positive")

    if spec.parameters.height <= 0:
        errors.append("cylinder height must be positive")


def _validate_operation(spec: OperationNode, errors: list[str]) -> None:
    if spec.op == "difference" and len(spec.children) != 2:
        errors.append("difference operations must have exactly two children")

    for child in spec.children:
        _validate_design_node(child, errors)

    if len(spec.children) != 2:
        return

    left, right = spec.children
    if isinstance(left, PrimitiveNode) and isinstance(right, PrimitiveNode):
        if left.primitive == right.primitive == "cylinder":
            if right.parameters.radius >= left.parameters.radius:
                errors.append("inner cylinder radius must be smaller than outer cylinder radius")
