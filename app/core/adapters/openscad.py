from app.core.adapters.base import CADAdapter
from app.models.schema import (
    CylinderParameters,
    DesignNode,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
)


class OpenSCADAdapter(CADAdapter):
    def generate(self, spec: DesignNode) -> str:
        return self._render_node(spec)

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

        raise ValueError(f"unsupported primitive node: {spec.primitive}")

    def _render_operation(self, spec: OperationNode, indent: int) -> str:
        prefix = " " * indent
        child_blocks = [self._render_node(child, indent + 4) for child in spec.children]
        children = "\n".join(child_blocks)
        return f"{prefix}{spec.op}() {{\n{children}\n{prefix}}}"
