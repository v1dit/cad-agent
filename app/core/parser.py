from app.models.schema import CadSpec


def parse_prompt(text: str) -> CadSpec:
    # TODO: Replace this deterministic placeholder with an LLM-backed parser.
    _ = text
    return CadSpec(
        shape="cylinder",
        outer_radius=5,
        inner_radius=3,
        height=10,
    )
