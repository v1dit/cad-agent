from app.core.adapters.base import CADAdapter
from app.core.executor import run_openscad
from app.models.schema import (
    CubeParameters,
    CylinderParameters,
    DesignNode,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
)


class OpenSCADAdapter(CADAdapter):
    name = "openscad"

    def generate(self, spec: DesignNode) -> str:
        return self._render_node(spec)

    def execute(self, code: str, out_path: str | None = None) -> dict[str, str]:
        return run_openscad(code, out_path=out_path)

    def _render_node(self, spec: DesignNode, indent: int = 0) -> str:
        if isinstance(spec, PrimitiveNode):
            return self._render_primitive(spec, indent)

        if isinstance(spec, OperationNode):
            return self._render_operation(spec, indent)

        raise ValueError(f"unsupported design node: {type(spec)!r}")

    def _render_primitive(self, spec: PrimitiveNode, indent: int) -> str:
        prefix = " " * indent
        if spec.primitive == "cylinder" and isinstance(spec.parameters, CylinderParameters):
            return (
                f"{prefix}cylinder("
                f"h={spec.parameters.height}, "
                f"r={spec.parameters.radius}"
                ");"
            )

        if spec.primitive == "sphere" and isinstance(spec.parameters, SphereParameters):
            return f"{prefix}sphere(r={spec.parameters.radius});"

        if spec.primitive == "cube" and isinstance(spec.parameters, CubeParameters):
            return (
                f"{prefix}cube("
                f"size=[{spec.parameters.width}, {spec.parameters.depth}, {spec.parameters.height}]"
                ");"
            )

        raise ValueError(f"unsupported primitive node: {spec.primitive}")

    def _render_operation(self, spec: OperationNode, indent: int) -> str:
        prefix = " " * indent
        child_blocks = [self._render_node(child, indent + 4) for child in spec.children]
        children = "\n".join(child_blocks)
        return f"{prefix}{spec.op}() {{\n{children}\n{prefix}}}"
