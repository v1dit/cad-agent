import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.executor import ExecutionError, run_openscad
from app.core.generator import generate
from app.core.normalize import normalize_spec
from app.core.parser import parse_prompt
from app.main import app
from app.models.schema import (
    CubeParameters,
    CylinderParameters,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDENS_PATH = PROJECT_ROOT / "tests" / "goldens" / "scad_snapshots.json"


class PlatformGuaranteesTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.goldens = json.loads(GOLDENS_PATH.read_text(encoding="utf-8"))

    def test_normalize_is_idempotent(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=4),
                ),
                OperationNode(
                    type="operation",
                    op="union",
                    children=[
                        PrimitiveNode(
                            type="primitive",
                            primitive="cube",
                            parameters=CubeParameters(width=6, depth=6, height=6),
                        ),
                        PrimitiveNode(
                            type="primitive",
                            primitive="cylinder",
                            parameters=CylinderParameters(radius=5, height=10),
                        ),
                    ],
                ),
            ],
        )

        once = normalize_spec(spec)
        twice = normalize_spec(once)
        self.assertEqual(once.model_dump(), twice.model_dump())

    def test_normalize_flattens_nested_union(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=4),
                ),
                OperationNode(
                    type="operation",
                    op="union",
                    children=[
                        PrimitiveNode(
                            type="primitive",
                            primitive="cube",
                            parameters=CubeParameters(width=6, depth=6, height=6),
                        ),
                        PrimitiveNode(
                            type="primitive",
                            primitive="cylinder",
                            parameters=CylinderParameters(radius=5, height=10),
                        ),
                    ],
                ),
            ],
        )

        normalized = normalize_spec(spec)
        self.assertIsInstance(normalized, OperationNode)
        self.assertEqual(normalized.op, "union")
        self.assertEqual(len(normalized.children), 3)

    def test_normalize_flattens_nested_intersection(self) -> None:
        spec = OperationNode(
            type="operation",
            op="intersection",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=4),
                ),
                OperationNode(
                    type="operation",
                    op="intersection",
                    children=[
                        PrimitiveNode(
                            type="primitive",
                            primitive="cube",
                            parameters=CubeParameters(width=6, depth=6, height=6),
                        ),
                        PrimitiveNode(
                            type="primitive",
                            primitive="cylinder",
                            parameters=CylinderParameters(radius=5, height=10),
                        ),
                    ],
                ),
            ],
        )

        normalized = normalize_spec(spec)
        self.assertIsInstance(normalized, OperationNode)
        self.assertEqual(normalized.op, "intersection")
        self.assertEqual(len(normalized.children), 3)

    def test_normalize_removes_zero_sized_union_children(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=0),
                ),
                PrimitiveNode(
                    type="primitive",
                    primitive="cube",
                    parameters=CubeParameters(width=6, depth=6, height=6),
                ),
            ],
        )

        normalized = normalize_spec(spec)
        self.assertIsInstance(normalized, PrimitiveNode)
        self.assertEqual(normalized.primitive, "cube")

    def test_normalize_preserves_difference_base_child(self) -> None:
        base = PrimitiveNode(
            type="primitive",
            primitive="cylinder",
            parameters=CylinderParameters(radius=5, height=10),
        )
        spec = OperationNode(
            type="operation",
            op="difference",
            children=[
                base,
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=0),
                ),
                PrimitiveNode(
                    type="primitive",
                    primitive="cylinder",
                    parameters=CylinderParameters(radius=3, height=10),
                ),
            ],
        )

        normalized = normalize_spec(spec)
        self.assertIsInstance(normalized, OperationNode)
        self.assertEqual(normalized.children[0].model_dump(), base.model_dump())
        self.assertEqual(len(normalized.children), 2)

    def test_string_parameters_are_rejected_by_schema(self) -> None:
        with self.assertRaises(ValidationError):
            PrimitiveNode.model_validate(
                {
                    "type": "primitive",
                    "primitive": "sphere",
                    "parameters": {"radius": "4"},
                    "operation": "add",
                }
            )

    def test_generate_matches_scad_goldens(self) -> None:
        cases = {
            "hollow_cylinder": "make a hollow cylinder",
            "sphere": "make a sphere",
            "cube": "make a cube",
            "union_demo": "make a union of a hollow cylinder and a sphere",
            "intersection_demo": "make an intersection of a cube and a sphere",
        }

        for name, prompt in cases.items():
            with self.subTest(name=name):
                spec = normalize_spec(parse_prompt(prompt))
                self.assertEqual(generate(spec), self.goldens[name])

    def test_generate_is_stable_after_double_normalization(self) -> None:
        spec = normalize_spec(parse_prompt("make a union of a hollow cylinder and a sphere"))
        self.assertEqual(generate(spec), generate(normalize_spec(spec)))

    def test_ir_dump_contains_no_adapter_specific_fields(self) -> None:
        spec = normalize_spec(parse_prompt("make an intersection of a cube and a sphere"))
        self._assert_ir_contract(spec.model_dump())

    def test_nested_depth_generation(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                OperationNode(
                    type="operation",
                    op="intersection",
                    children=[
                        PrimitiveNode(
                            type="primitive",
                            primitive="cube",
                            parameters=CubeParameters(width=6, depth=6, height=6),
                        ),
                        PrimitiveNode(
                            type="primitive",
                            primitive="sphere",
                            parameters=SphereParameters(radius=4),
                        ),
                    ],
                ),
                OperationNode(
                    type="operation",
                    op="difference",
                    children=[
                        PrimitiveNode(
                            type="primitive",
                            primitive="cylinder",
                            parameters=CylinderParameters(radius=5, height=10),
                        ),
                        PrimitiveNode(
                            type="primitive",
                            primitive="cylinder",
                            parameters=CylinderParameters(radius=3, height=10),
                        ),
                    ],
                ),
            ],
        )

        code = generate(normalize_spec(spec))
        self.assertIn("union()", code)
        self.assertIn("intersection()", code)
        self.assertIn("difference()", code)

    @patch("app.core.executor.subprocess.run")
    @patch("app.core.executor.shutil.which", return_value="/usr/bin/openscad")
    def test_executor_returns_artifact_metadata(self, _mock_which, mock_run) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["openscad"],
            returncode=0,
            stdout="ok",
            stderr="",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = str(Path(tmpdir) / "demo.stl")
            result = run_openscad("sphere(r=4);", out_path=out_path)

        self.assertEqual(result["artifact"], out_path)
        self.assertEqual(result["stdout"], "ok")

    @patch("app.core.executor.shutil.which", return_value=None)
    def test_executor_raises_clean_error_when_openscad_missing(self, _mock_which) -> None:
        with self.assertRaises(ExecutionError):
            run_openscad("sphere(r=4);")

    @patch("app.routes.pipeline.execute_generated", side_effect=ExecutionError("openscad executable not found in PATH"))
    def test_api_execute_failure_is_surfaced_cleanly(self, _mock_execute) -> None:
        client = TestClient(app)
        response = client.post("/run", json={"text": "make a sphere", "execute": True})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stage"], "execution_failed")
        self.assertEqual(body["engine"], "openscad")
        self.assertEqual(body["errors"], ["openscad executable not found in PATH"])
        self.assertEqual(body["output"]["code"], "sphere(r=4.0);")

    @patch("app.routes.pipeline.execute_generated", return_value={"artifact": "/tmp/out.stl"})
    def test_api_execute_success_returns_artifact(self, _mock_execute) -> None:
        client = TestClient(app)
        response = client.post("/run", json={"text": "make a sphere", "execute": True})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stage"], "success")
        self.assertEqual(body["artifact"], "/tmp/out.stl")
        self.assertEqual(body["output"]["code"], "sphere(r=4.0);")

    def _assert_ir_contract(self, node: dict) -> None:
        allowed_keys = {
            "primitive": {"type", "primitive", "parameters", "operation"},
            "operation": {"type", "op", "children"},
        }

        node_type = node["type"]
        self.assertEqual(set(node.keys()), allowed_keys[node_type])

        if node_type == "operation":
            for child in node["children"]:
                self._assert_ir_contract(child)


if __name__ == "__main__":
    unittest.main()
