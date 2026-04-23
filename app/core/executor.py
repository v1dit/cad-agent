from pathlib import Path
import shutil
import subprocess
import tempfile
from uuid import uuid4


class ExecutionError(RuntimeError):
    pass


def run_openscad(scad_code: str, out_path: str | None = None) -> dict[str, str]:
    openscad_binary = shutil.which("openscad")
    if openscad_binary is None:
        raise ExecutionError("openscad executable not found in PATH")

    artifact_path = Path(out_path) if out_path else _default_artifact_path()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".scad", delete=False, encoding="utf-8") as handle:
        handle.write(scad_code)
        scad_path = Path(handle.name)

    try:
        completed = subprocess.run(
            [openscad_binary, "-o", str(artifact_path), str(scad_path)],
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise ExecutionError(f"openscad execution failed: {stderr}") from exc
    finally:
        scad_path.unlink(missing_ok=True)

    return {
        "artifact": str(artifact_path),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _default_artifact_path() -> Path:
    return Path.cwd() / "artifacts" / f"cad-agent-{uuid4().hex}.stl"
