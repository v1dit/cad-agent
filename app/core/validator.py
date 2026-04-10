from app.models.schema import CadSpec, ValidationResult


def validate_spec(spec: CadSpec) -> ValidationResult:
    errors: list[str] = []

    if spec.shape == "cylinder":
        if spec.inner_radius >= spec.outer_radius:
            errors.append("inner radius must be smaller than outer radius")

        if spec.height <= 0:
            errors.append("height must be positive")

    return ValidationResult(valid=len(errors) == 0, errors=errors)
