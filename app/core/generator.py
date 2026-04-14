from app.core.adapters.openscad import OpenSCADAdapter
from app.models.schema import DesignNode

DEFAULT_ENGINE = "openscad"


def generate(spec: DesignNode, engine: str = DEFAULT_ENGINE) -> str:
    if engine == DEFAULT_ENGINE:
        return OpenSCADAdapter().generate(spec)

    raise ValueError(f"unsupported engine: {engine}")


def generate_scad(spec: DesignNode) -> str:
    return generate(spec, engine=DEFAULT_ENGINE)
