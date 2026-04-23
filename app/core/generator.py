from app.core.adapters.registry import DEFAULT_ENGINE, get_adapter
from app.models.schema import DesignNode


def generate(spec: DesignNode, engine: str = DEFAULT_ENGINE) -> str:
    return get_adapter(engine).generate(spec)


def generate_scad(spec: DesignNode) -> str:
    return generate(spec, engine=DEFAULT_ENGINE)


def execute_generated(code: str, engine: str = DEFAULT_ENGINE, out_path: str | None = None) -> dict[str, str]:
    return get_adapter(engine).execute(code, out_path=out_path)
