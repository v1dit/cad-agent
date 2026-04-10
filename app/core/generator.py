from app.models.schema import CadSpec


def generate_scad(spec: CadSpec) -> str:
    if spec.shape == "cylinder":
        return (
            "difference() {\n"
            f"    cylinder(h={spec.height}, r={spec.outer_radius});\n"
            f"    cylinder(h={spec.height}, r={spec.inner_radius});\n"
            "}"
        )

    raise ValueError(f"unsupported shape: {spec.shape}")
