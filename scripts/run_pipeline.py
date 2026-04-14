import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.generator import generate
from app.core.parser import parse_prompt
from app.core.validator import validate_spec


def main() -> None:
    prompt_path = _resolve_prompt_path()
    prompt = prompt_path.read_text(encoding="utf-8").strip()

    spec = parse_prompt(prompt)
    validation = validate_spec(spec)

    if validation.valid:
        print(generate(spec))
        return

    print("Errors:")
    for error in validation.errors:
        print(f"- {error}")


def _resolve_prompt_path() -> Path:
    if len(sys.argv) < 2:
        return PROJECT_ROOT / "examples" / "test_prompt.txt"

    candidate = Path(sys.argv[1])
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate

    return candidate.resolve()


if __name__ == "__main__":
    main()
