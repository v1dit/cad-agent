import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.executor import ExecutionError
from app.core.generator import DEFAULT_ENGINE, execute_generated, generate
from app.core.normalize import normalize_spec
from app.core.parser import parse_prompt
from app.core.validator import validate_spec


def main() -> None:
    args = _parse_args()
    prompt_path = _resolve_prompt_path(args.prompt_path)
    prompt = prompt_path.read_text(encoding="utf-8").strip()

    spec = normalize_spec(parse_prompt(prompt))
    validation = validate_spec(spec)

    if not validation.valid:
        print("Errors:")
        for error in validation.errors:
            print(f"- {error}")
        return

    code = generate(spec, engine=args.engine)
    print(code)

    if not args.execute:
        return

    try:
        result = execute_generated(code, engine=args.engine)
    except ExecutionError as exc:
        print(f"Execution failed: {exc}")
        return

    print(f"Artifact: {result['artifact']}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic CAD pipeline.")
    parser.add_argument("prompt_path", nargs="?", help="Path to a prompt text file.")
    parser.add_argument("--execute", action="store_true", help="Execute generated SCAD with the adapter.")
    parser.add_argument("--engine", default=DEFAULT_ENGINE, help="CAD backend to use.")
    return parser.parse_args()


def _resolve_prompt_path(prompt_path: str | None) -> Path:
    if not prompt_path:
        return PROJECT_ROOT / "examples" / "test_prompt.txt"

    candidate = Path(prompt_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate

    return candidate.resolve()


if __name__ == "__main__":
    main()
