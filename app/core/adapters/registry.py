from app.core.adapters.base import CADAdapter
from app.core.adapters.openscad import OpenSCADAdapter

DEFAULT_ENGINE = "openscad"
ADAPTERS: dict[str, CADAdapter] = {DEFAULT_ENGINE: OpenSCADAdapter()}


def get_adapter(name: str = DEFAULT_ENGINE) -> CADAdapter:
    try:
        return ADAPTERS[name]
    except KeyError as exc:
        raise ValueError(f"unsupported engine: {name}") from exc
